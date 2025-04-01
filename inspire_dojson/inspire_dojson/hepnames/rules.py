# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2014-2017 CERN.
#
# INSPIRE is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# INSPIRE is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with INSPIRE. If not, see <http://www.gnu.org/licenses/>.
#
# In applying this license, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as an Intergovernmental Organization
# or submit itself to any jurisdiction.

"""DoJSON rules for HEPNames."""

from __future__ import absolute_import, division, print_function

import re

from dojson import utils
from inspire_schemas.api import load_schema
from inspire_schemas.utils import (
    normalize_arxiv_category,
    valid_arxiv_categories,
)
from inspire_utils.date import normalize_date
from inspire_utils.helpers import force_list, maybe_int
from inspire_utils.name import normalize_name

from inspire_dojson.hepnames.model import hepnames, hepnames2marc
from inspire_dojson.utils import (
    force_single_element,
    get_recid_from_ref,
    get_record_ref,
    normalize_rank,
    quote_url,
    unquote_url,
)

AWARD_YEAR = re.compile(r'\(?(?P<year>\d{4})\)?')
INSPIRE_BAI = re.compile(r'(\w+\.)+\d+')
LOOKS_LIKE_CERN = re.compile(r'^\d+$|^CER[MN]?-|^CNER-|^CVERN-', re.I)
NON_DIGIT = re.compile(r'[^\d]+')
LINKEDIN_URL = re.compile(
    r'https?://(\w+\.)?linkedin\.com/in/(?P<page>[\w%-]+)', re.UNICODE
)
TWITTER_URL = re.compile(r'https?://(www\.)?twitter\.com/(?P<handle>\w+)')
WIKIPEDIA_URL = re.compile(r'https?://(?P<lang>\w+)\.wikipedia\.org/wiki/(?P<page>.*)')


@hepnames.over('ids', '^035..')
def ids(self, key, value):
    def _get_schema(value):
        IDS_MAP = {
            'ARXIV': 'ARXIV',
            'BAI': 'INSPIRE BAI',
            'CERN': 'CERN',
            'DESY': 'DESY',
            'GOOGLESCHOLAR': 'GOOGLESCHOLAR',
            'INSPIRE': 'INSPIRE ID',
            'KAKEN': 'KAKEN',
            'ORCID': 'ORCID',
            'RESEARCHID': 'RESEARCHERID',
            'RESEARCHERID': 'RESEARCHERID',
            'SLAC': 'SLAC',
            'SCOPUS': 'SCOPUS',
            'TWITTER': 'TWITTER',
            'VIAF': 'VIAF',
            'WIKIPEDIA': 'WIKIPEDIA',
        }

        return IDS_MAP.get(value.get('9', '').upper())

    def _guess_schema_from_value(a_value):
        if a_value is None:
            return None

        if INSPIRE_BAI.match(a_value):
            return 'INSPIRE BAI'

    def _try_to_correct_value(schema, value):
        if value is None:
            return value

        if schema == 'CERN' and LOOKS_LIKE_CERN.match(value):
            return 'CERN-' + NON_DIGIT.sub('', value)
        elif schema == 'KAKEN':
            return 'KAKEN-' + value
        else:
            return value

    ids = self.get("ids", [])

    a_value = force_single_element(value.get('a'))
    z_value = force_single_element(value.get('z'))

    schema = _get_schema(value)
    if schema is None:
        schema = _guess_schema_from_value(a_value)

    a_value = _try_to_correct_value(schema, a_value)
    z_value = _try_to_correct_value(schema, z_value)

    if schema and a_value:
        ids.insert(
            0,
            {
                'schema': schema,
                'value': a_value,
            },
        )
    if schema and z_value:
        ids.append(
            {
                'schema': schema,
                'value': z_value,
            }
        )

    return ids


@hepnames2marc.over('035', '^ids$')
def ids2marc(self, key, values):
    """Populate the ``035`` MARC field.

    Also populates the ``8564`` and ``970`` MARC field through side effects.
    """

    def _convert_schema(schema):
        conversion = {'INSPIRE BAI': 'BAI', 'INSPIRE ID': 'INSPIRE'}
        return conversion.get(schema, schema)

    def _is_schema_spires(id_, schema):
        return schema == 'SPIRES'

    def _is_schema_linkedin(id, schema):
        return schema == 'LINKEDIN'

    def _is_schema_twitter(id, schema):
        return schema == 'TWITTER'

    seen_schemas = set()
    result = []

    for value in values:
        id_ = value.get('value')
        schema = value.get('schema')

        if _is_schema_spires(id_, schema):
            self.setdefault('970', []).append({'a': id_})
        elif _is_schema_linkedin(id_, schema):
            self.setdefault('8564', []).append(
                {
                    'u': u'https://www.linkedin.com/in/{id}'.format(id=quote_url(id_)),
                    'y': 'LINKEDIN',
                }
            )
        elif _is_schema_twitter(id_, schema):
            self.setdefault('8564', []).append(
                {
                    'u': u'https://twitter.com/{id}'.format(id=id_),
                    'y': 'TWITTER',
                }
            )
        else:
            if schema not in seen_schemas:
                seen_schemas.add(schema)
                field = 'a'
            else:
                field = 'z'
            result.append(
                {
                    field: id_,
                    '9': _convert_schema(schema),
                }
            )

    return result


@hepnames.over('name', '^100..')
def name(self, key, value):
    """Populate the ``name`` key.

    Also populates the ``status``, ``birth_date`` and ``death_date``
    keys through side effects.
    """

    def _get_title(value):
        c_value = force_single_element(value.get('c', ''))
        if c_value != 'title (e.g. Sir)':
            return c_value

    def _get_value(value):
        a_value = force_single_element(value.get('a', ''))
        q_value = force_single_element(value.get('q', ''))
        return a_value or normalize_name(q_value)

    if value.get('d'):
        dates = value['d']
        try:
            self['death_date'] = normalize_date(dates)
        except ValueError:
            dates = dates.split(' - ')
            if len(dates) == 1:
                dates = dates[0].split('-')
            self['birth_date'] = normalize_date(dates[0])
            self['death_date'] = normalize_date(dates[1])

    self['status'] = force_single_element(value.get('g', '')).lower()

    return {
        'numeration': force_single_element(value.get('b', '')),
        'preferred_name': force_single_element(value.get('q', '')),
        'title': _get_title(value),
        'value': _get_value(value),
    }


@hepnames2marc.over('100', '^name$')
def name2marc(self, key, value):
    """Populates the ``100`` field.

    Also populates the ``400``, ``880``, and ``667`` fields through side
    effects.
    """
    result = self.get('100', {})

    result['a'] = value.get('value')
    result['b'] = value.get('numeration')
    result['c'] = value.get('title')
    result['q'] = value.get('preferred_name')

    if 'name_variants' in value:
        self['400'] = [{'a': el} for el in value['name_variants']]
    if 'native_names' in value:
        self['880'] = [{'a': el} for el in value['native_names']]
    if 'previous_names' in value:
        prev_names = [
            {'a': u'Formerly {}'.format(prev_name)}
            for prev_name in value['previous_names']
        ]
        self['667'] = prev_names

    return result


@hepnames2marc.over('100', '^status$')
def status2marc(self, key, value):
    result = self.get('100', {})

    result['g'] = value

    return result


@hepnames.over('positions', '^371..')
@utils.for_each_value
def positions(self, key, value):
    """Populate the positions field.

    Also populates the email_addresses field by side effect.
    """
    email_addresses = self.get("email_addresses", [])
    current = None
    record = None

    recid_or_status = force_list(value.get('z'))
    for el in recid_or_status:
        if el.lower() == 'current':
            current = True if value.get('a') else None
        else:
            record = get_record_ref(maybe_int(el), 'institutions')

    rank = normalize_rank(value.get('r'))

    current_email_addresses = force_list(value.get('m'))
    non_current_email_addresses = force_list(value.get('o'))

    email_addresses.extend(
        {
            'value': address,
            'current': True,
        }
        for address in current_email_addresses
    )
    email_addresses.extend(
        {
            'value': address,
            'current': False,
        }
        for address in non_current_email_addresses
    )

    self['email_addresses'] = email_addresses

    if 'a' not in value:
        return None

    hidden = value.get('h') == 'HIDDEN' or None

    return {
        'institution': value['a'],
        'record': record,
        'curated_relation': True if record is not None else None,
        'rank': rank,
        'hidden': hidden,
        'start_date': normalize_date(value.get('s')),
        'end_date': normalize_date(value.get('t')),
        'current': current,
    }


@hepnames2marc.over('371', '^positions$')
@utils.for_each_value
def positions2marc(self, key, value):
    def _get_r_value(value):
        RANK_MAP = {
            'JUNIOR': 'JUNIOR',
            'MASTER': 'MAS',
            'PHD': 'PHD',
            'POSTDOC': 'PD',
            'SENIOR': 'SENIOR',
            'STAFF': 'STAFF',
            'UNDERGRADUATE': 'UG',
            'VISITOR': 'VISITOR',
        }

        rank = value.get('rank')
        if rank:
            return RANK_MAP.get(rank)

    return {
        'a': value.get('institution'),
        'r': _get_r_value(value),
        's': value.get('start_date'),
        't': value.get('end_date'),
        'z': 'Current' if value.get('current') else None,
        'h': 'HIDDEN' if value.get('hidden') else None,
    }


@hepnames2marc.over('595', '^email_addresses$')
@utils.for_each_value
def email_addresses2marc(self, key, value):
    """Populate the 595 MARCXML field.

    Also populates the 371 field as a side effect.
    """
    m_or_o = 'm' if value.get('current') else 'o'
    element = {m_or_o: value.get('value')}

    if value.get('hidden'):
        return element
    else:
        self.setdefault('371', []).append(element)
        return None


@hepnames.over('email_addresses', '^595..')
def email_addresses595(self, key, value):
    """Populates the ``email_addresses`` field using the 595 MARCXML field.

    Also populates ``_private_notes`` as a side effect.
    """
    emails = self.get('email_addresses', [])

    if value.get('o'):
        emails.append(
            {
                'value': value.get('o'),
                'current': False,
                'hidden': True,
            }
        )

    if value.get('m'):
        emails.append(
            {
                'value': value.get('m'),
                'current': True,
                'hidden': True,
            }
        )

    notes = self.get('_private_notes', [])
    new_note = (
        {
            'source': value.get('9'),
            'value': _private_note,
        }
        for _private_note in force_list(value.get('a'))
    )
    notes.extend(new_note)
    self['_private_notes'] = notes

    return emails


@hepnames.over('name', '^400..')
def name_variants(self, key, value):
    name_item = self.get('name', {})
    name_variants_list = name_item.get('name_variants', [])

    name_variants_list.extend(force_list(value.get('a')))
    name_item['name_variants'] = name_variants_list

    return name_item


@hepnames.over('arxiv_categories', '^65017')
def arxiv_categories(self, key, value):
    """Populate the ``arxiv_categories`` key.

    Also populates the ``inspire_categories`` key through side effects.
    """

    def _is_arxiv(category):
        return category in valid_arxiv_categories()

    def _is_inspire(category):
        schema = load_schema('elements/inspire_field')
        valid_inspire_categories = schema['properties']['term']['enum']

        return category in valid_inspire_categories

    def _normalize(a_value):
        for category in valid_arxiv_categories():
            if a_value.lower() == category.lower():
                return normalize_arxiv_category(category)

        schema = load_schema('elements/inspire_field')
        valid_inspire_categories = schema['properties']['term']['enum']

        for category in valid_inspire_categories:
            if a_value.lower() == category.lower():
                return category

        field_codes_to_inspire_categories = {
            'a': 'Astrophysics',
            'b': 'Accelerators',
            'c': 'Computing',
            'e': 'Experiment-HEP',
            'g': 'Gravitation and Cosmology',
            'i': 'Instrumentation',
            'l': 'Lattice',
            'm': 'Math and Math Physics',
            'n': 'Theory-Nucl',
            'o': 'Other',
            'p': 'Phenomenology-HEP',
            'q': 'General Physics',
            't': 'Theory-HEP',
            'x': 'Experiment-Nucl',
        }

        return field_codes_to_inspire_categories.get(a_value.lower())

    arxiv_categories = self.get('arxiv_categories', [])
    inspire_categories = self.get('inspire_categories', [])

    for current_value in force_list(value):
        for a_value in force_list(current_value.get('a')):
            normalized_a_value = _normalize(a_value)

            if _is_arxiv(normalized_a_value):
                arxiv_categories.append(normalized_a_value)
            elif _is_inspire(normalized_a_value):
                inspire_categories.append({'term': normalized_a_value})

    self['inspire_categories'] = inspire_categories
    return arxiv_categories


@hepnames2marc.over('65017', '^arxiv_categories$')
@utils.for_each_value
def arxiv_categories2marc(self, key, value):
    return {
        '2': 'arXiv',
        'a': value,
    }


@hepnames2marc.over('65017', '^inspire_categories$')
@utils.for_each_value
def inspire_categories2marc(self, key, value):
    return {
        '2': 'INSPIRE',
        'a': value.get('term'),
    }


@hepnames.over('public_notes', '^667..')
@utils.for_each_value
def _public_notes(self, key, value):
    if 'Formerly' in value.get('a'):
        name_item = self.get('name', {})
        previous_names_list = name_item.get('previous_names', [])
        previous_name = value.get('a').replace('Formerly ', '')
        previous_names_list.extend(force_list(previous_name))
        self.setdefault('name', {})['previous_names'] = previous_names_list
    else:
        return {
            'source': value.get('9'),
            'value': value.get('a'),
        }


@hepnames2marc.over('667', '^public_notes$')
@utils.for_each_value
def _public_notes2marc(self, key, value):
    return {
        'a': value.get('value'),
        '9': value.get('source'),
    }


@hepnames2marc.over('100', '^(birth_date|death_date)$')
def birth_and_death_date2marc(self, key, value):
    """Populate the ``100__d`` MARC field, which includes the birth and the death date.

    By not using the decorator ```for_each_value```, the values of the fields
    ```birth_date``` and ```death_date``` are both added to ```values``` as a list.
    """
    name_field = self.get('100', {})

    if 'd' in name_field:
        if int(name_field['d'].split('-')[0]) > int(value.split('-')[0]):
            dates_field = ' - '.join([value, name_field['d']])
        else:
            dates_field = ' - '.join([name_field['d'], value])
    else:
        dates_field = value

    name_field['d'] = dates_field

    return name_field


@hepnames.over('awards', '^678..')
@utils.for_each_value
def awards(self, key, value):
    award = AWARD_YEAR.sub('', value.get('a')).strip()
    year_match = AWARD_YEAR.search(value.get('a'))
    year = int(year_match.group('year')) if year_match else None

    return {
        'name': award,
        'url': value.get('u'),
        'year': year,
    }


@hepnames2marc.over('678', '^awards$')
@utils.for_each_value
def awards2marc(self, key, value):
    return {
        'a': ' '.join([value.get('name', ''), str(value.get('year', ''))]).strip(),
        'u': value.get('url'),
    }


@hepnames.over('project_membership', '^693..')
def project_membership(self, key, values):
    def _get_json_experiments(marc_dict):
        start_year = marc_dict.get('s')
        end_year = marc_dict.get('d')

        names = force_list(marc_dict.get('e'))
        recids = force_list(marc_dict.get('0'))
        name_recs = zip(names, recids or [None] * len(names))
        hidden = marc_dict.get('h') == 'HIDDEN' or None

        for name, recid in name_recs:
            record = get_record_ref(recid, 'experiments')
            yield {
                'curated_relation': record is not None,
                'current': (marc_dict.get('z', '').lower() == 'current'),
                'end_date': end_year,
                'name': name,
                'record': record,
                'hidden': hidden,
                'start_date': start_year,
            }

    values = force_list(values)
    json_experiments = self.get('project_membership', [])
    for experiment in values:
        if experiment:
            json_experiments.extend(_get_json_experiments(experiment))

    return json_experiments


@hepnames2marc.over('693', '^project_membership$')
def project_membership2marc(self, key, values):
    def _get_marc_experiment(json_dict):
        marc = {
            'e': json_dict.get('name'),
            's': json_dict.get('start_date'),
            'd': json_dict.get('end_date'),
        }
        status = 'current' if json_dict.get('current') else None
        if status:
            marc['z'] = status
        recid = get_recid_from_ref(json_dict.get('record', None))
        if recid:
            marc['0'] = recid
        if json_dict.get('hidden'):
            marc['h'] = 'HIDDEN'
        return marc

    marc_experiments = self.get('693', [])
    values = force_list(values)
    for experiment in values:
        if experiment:
            marc_experiments.append(_get_marc_experiment(experiment))

    return marc_experiments


@hepnames.over('advisors', '^701..')
@utils.for_each_value
def advisors(self, key, value):
    DEGREE_TYPES_MAP = {
        'Bachelor': 'bachelor',
        'UG': 'bachelor',
        'MAS': 'master',
        'master': 'master',
        'Master': 'master',
        'PhD': 'phd',
        'PHD': 'phd',
    }

    def _get_id_schema(id_):
        if id_.lower().startswith('inspire-'):
            return 'INSPIRE ID'
        else:  # assuming ORCID
            return 'ORCID'

    _degree_type = force_single_element(value.get('g'))
    degree_type = DEGREE_TYPES_MAP.get(_degree_type, 'other')

    recid = force_single_element(value.get('x'))
    record = get_record_ref(recid, 'authors')

    ids = [
        {
            'schema': _get_id_schema(id_),
            'value': id_,
        }
        for id_ in force_list(value.get('i'))
    ]

    hidden = value.get('h') == 'HIDDEN' or None

    return {
        'name': value.get('a'),
        'degree_type': degree_type,
        'ids': ids,
        'record': record,
        'hidden': hidden,
        'curated_relation': value.get('y') == '1' if record else None,
    }


@hepnames2marc.over('701', '^advisors$')
@utils.for_each_value
def advisors2marc(self, key, value):
    allowed_ids = ('INSPIRE ID', 'ORCID')
    ids = [id_['value'] for id_ in value.get('ids', []) if id_['schema'] in allowed_ids]

    return {
        'a': value.get('name'),
        'g': value.get('degree_type'),
        'i': ids,
        'h': 'HIDDEN' if value.get('hidden') else None,
    }


@hepnames.over('urls', '^8564.')
@utils.for_each_value
def urls(self, key, value):
    """Populate the ``url`` key.

    Also populates the ``ids`` key through side effects.
    """
    description = force_single_element(value.get('y'))
    url = value.get('u')

    linkedin_match = LINKEDIN_URL.match(url)
    twitter_match = TWITTER_URL.match(url)
    wikipedia_match = WIKIPEDIA_URL.match(url)
    if linkedin_match:
        self.setdefault('ids', []).append(
            {
                'schema': 'LINKEDIN',
                'value': unquote_url(linkedin_match.group('page')),
            }
        )
    elif twitter_match:
        self.setdefault('ids', []).append(
            {
                'schema': 'TWITTER',
                'value': twitter_match.group('handle'),
            }
        )
    elif wikipedia_match:
        lang = wikipedia_match.group('lang')
        page = unquote_url(wikipedia_match.group('page'))
        if lang != 'en':
            page = ':'.join([lang, page])
        self.setdefault('ids', []).append(
            {
                'schema': 'WIKIPEDIA',
                'value': page,
            }
        )
    else:
        return {
            'description': description,
            'value': url,
        }


@hepnames.over('name', '^880..')
def native_name(self, key, value):
    name = self.get('name', {})
    name.setdefault('native_names', []).append(value.get('a'))
    return name


@hepnames.over('new_record', '^970..')
def new_record(self, key, value):
    """Populate the ``new_record`` key.

    Also populates the ``ids`` key through side effects.
    """
    new_record = self.get('new_record', {})
    ids = self.get('ids', [])

    for current_value in force_list(value):
        for id_ in force_list(current_value.get('a')):
            ids.append(
                {
                    'schema': 'SPIRES',
                    'value': id_,
                }
            )

        new_recid = force_single_element(current_value.get('d', ''))
        if new_recid:
            new_record = get_record_ref(new_recid, 'authors')

    self['ids'] = ids
    return new_record


@hepnames.over('deleted', '^980..')
def deleted(self, key, value):
    """Populate the ``deleted`` key.

    Also populates the ``stub`` key through side effects.
    """

    def _is_deleted(value):
        return force_single_element(value.get('c', '')).upper() == 'DELETED'

    def _is_stub(value):
        return force_single_element(value.get('a', '')).upper() != 'USEFUL'

    deleted = self.get('deleted')
    stub = self.get('stub')

    for current_value in force_list(value):
        deleted = not deleted and _is_deleted(current_value)
        stub = not stub and _is_stub(current_value)

    self['stub'] = stub
    return deleted


@hepnames2marc.over('980', '^_collections$')
@utils.for_each_value
def _collections2marc(self, key, value):
    if value == 'Authors':
        return {'a': 'HEPNAMES'}


@hepnames2marc.over('980', '^deleted$')
@utils.for_each_value
def deleted2marc(self, key, value):
    if value:
        return {'c': 'DELETED'}


@hepnames2marc.over('980', '^stub$')
@utils.for_each_value
def stub2marc(self, key, value):
    if not value:
        return {'a': 'USEFUL'}
