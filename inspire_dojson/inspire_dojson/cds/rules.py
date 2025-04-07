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

"""DoJSON rules for CDS to INSPIRE HEP MARC."""

from __future__ import absolute_import, division, print_function

import contextlib
import os
import re
from itertools import chain

import pycountry
import rfc3987
import six
from dojson import utils
from idutils import is_arxiv
from inspire_utils.helpers import force_list
from inspire_utils.name import normalize_name
from six.moves import urllib

from inspire_dojson.cds.model import cds2hep_marc
from inspire_dojson.utils import force_single_element, quote_url

CATEGORIES = {
    'Accelerators and Storage Rings': 'Accelerators',
    'Astrophysics and Astronomy': 'Astrophysics',
    'Biography, Geography, History': 'Other',
    'Chemical Physics and Chemistry': 'Other',
    'Commerce, Economics, Social Science': 'Other',
    'Computing and Computers': 'Computing',
    'Condensed Matter': 'Condensed Matter',
    'Detectors and Experimental Techniques': 'Instrumentation',
    'Engineering': 'Instrumentation',
    'General Relativity and Cosmology': 'Gravitation and Cosmology',
    'General Theoretical Physics': 'General Physics',
    'Information Transfer and Management': 'Other',
    'Mathematical Physics and Mathematics': 'Math and Math Physics',
    'Nuclear Physics - Experiment': 'Experiment-Nucl',
    'Nuclear Physics - Theory': 'Theory-Nucl',
    'Other': 'Other',
    'Particle Physics - Experiment': 'Experiment-HEP',
    'Particle Physics - Lattice': 'Lattice',
    'Particle Physics - Phenomenology': 'Phenomenology-HEP',
    'Particle Physics - Theory': 'Theory-HEP',
    'Physics in General': 'General Physics',
    'Quantum Technology': 'Quantum Physics',
    'Science in General': 'Other',
}


EXPERIMENTS = {
    ('CERN LEP', None): 'CERN-LEP',
    ('CERN LEP', 'L3'): 'CERN-LEP-L3',
    ('CERN LEP', 'OPAL'): 'CERN-LEP-OPAL',
    ('CERN LHC', None): 'CERN-LHC',
    ('CERN LHC', 'ALICE'): 'CERN-LHC-ALICE',
    ('CERN LHC', 'ATLAS'): 'CERN-LHC-ATLAS',
    ('CERN LHC', 'CMS'): 'CERN-LHC-CMS',
    ('CERN LHC', 'LHCb'): 'CERN-LHC-LHCb',
    ('CERN LHC', 'LHCf'): 'CERN-LHC-LHCf',
    ('CERN LHC', 'MoEDAL'): 'CERN-LHC-MoEDAL',
    ('CERN LHC', 'TOTEM'): 'CERN-LHC-TOTEM',
    ('CERN PS', None): 'CERN-PS',
    ('CERN PS', 'nTOF'): 'CERN-nTOF',
    ('CERN SPS', None): 'CERN-SPS',
    ('CERN SPS', 'ICARUS CNGS2'): 'ICARUS',
    ('CERN SPS', 'OPERA CNGS1'): 'OPERA',
    ('DESY HERA', 'ZEUS'): 'DESY-HERA-ZEUS',
}


RE_IDS = re.compile(r'\((?P<schema>.*?)\)(?P<id>.*)')


def add_source(field, source='CDS'):
    if not field.get('9'):
        field['9'] = source


def vanilla_dict(god):
    return {k: v for (k, v) in six.iteritems(god) if k != '__order__'}


def ignore_not_applicable(text):
    if not text:
        return None

    return text if text.lower() != 'not applicable' else None


def escape_url(url):
    try:
        rfc3987.parse(url, rule="URI")
        return url
    except ValueError:
        if url.lower().startswith('https://'):
            scheme = 'https://'
        elif url.lower().startswith('http://'):
            scheme = 'http://'
        else:
            scheme = ''

        url = quote_url(url[len(scheme) :])
        return scheme + url


@cds2hep_marc.over('0247_', '^0247.')
@utils.for_each_value
def persistent_identifiers(self, key, value):
    value = vanilla_dict(value)
    add_source(value)
    return value


@cds2hep_marc.over('035__', '^035..')
@utils.for_each_value
def external_sytem_identifiers(self, key, value):
    ignored = {
        'cercer',
        'inspire',
        'xx',
        'cern annual report',
        'cmscms',
        'wai01',
        'spires',
    }
    if any(
        val.lower() in ignored
        for val in chain(force_list(value.get('9')), force_list(value.get('a')))
    ):
        return
    if any(val.lower().endswith('cercer') for val in force_list(value.get('a'))):
        return

    return vanilla_dict(value)


@cds2hep_marc.over('037__', '^037..', '^088..')
def secondary_report_numbers(self, key, value):
    """Populate the ``037`` MARC field.

    Also populates the ``500``, ``595`` and ``980`` MARC field through side effects.
    """
    preliminary_results_prefixes = [
        'ATLAS-CONF-',
        'CMS-PAS-',
        'CMS-DP-',
        'LHCB-CONF-',
    ]
    note_prefixes = [
        'ALICE-INT-',
        'ATL-',
        'ATLAS-CONF-',
        'CMS-DP-',
        'CMS-PAS-',
        'LHCB-CONF-',
        'LHCB-PUB-',
    ]

    result_037 = self.get('037__', [])
    result_500 = self.get('500__', [])
    result_595 = self.get('595__', [])
    result_980 = self.get('980__', [])

    report = force_single_element(value.get('a', ''))
    hidden_report = force_single_element(value.get('9') or value.get('z', ''))
    source = 'CDS' if not is_arxiv(report) else 'arXiv'

    if any(report.upper().startswith(prefix) for prefix in note_prefixes):
        result_980.append({'a': 'NOTE'})

    if any(
        report.upper().startswith(prefix) for prefix in preliminary_results_prefixes
    ):
        result_500.append({'9': 'CDS', 'a': 'Preliminary results'})

    is_barcode = hidden_report.startswith('P0') or hidden_report.startswith('CM-P0')
    if not report.startswith('SIS-') and not is_barcode:
        result_037.append(
            {
                '9': source,
                'a': report,
                'c': value.get('c'),
                'z': hidden_report if source == 'CDS' else None,
            }
        )

    self['500__'] = result_500
    self['595__'] = result_595
    self['980__'] = result_980
    return result_037


@cds2hep_marc.over('041__', '^041..')
@utils.flatten
@utils.for_each_value
def languages(self, key, value):
    languages = []
    values = force_list(value.get('a'))

    for language in values:
        alpha_3 = language.strip().lower()
        try:
            languages.append({'a': pycountry.languages.get(alpha_3=alpha_3).name})
        except KeyError:
            with contextlib.suppress(KeyError):
                languages.append(
                    {'a': pycountry.languages.get(bibliographic=alpha_3).name}
                )

    return languages


def _converted_author(value):
    def _get_ids_from_0(subfield):
        """Transform IDs from CDS into INSPIRE-style IDs."""
        ids = {}
        ids_i = []
        ids_j = []
        segments = subfield.split('|')

        for segment in segments:
            match = RE_IDS.match(segment)
            if match:
                ids[match.group('schema').upper()] = match.group('id')

        for schema, id_ in ids.items():
            if schema == 'INSPIRE':
                ids_i.append(id_)
            elif schema == 'SZGECERN':
                ids_j.append(u'CCID-{}'.format(id_))
            elif schema == 'CDS':
                continue
            else:
                ids_j.append(id_)

        return ids_i, ids_j

    value = vanilla_dict(value)

    if 'beard' in value.get('9', '').lower():
        value.pop('0', None)
        return value

    subfields_i = force_list(value.get('i'))
    subfields_j = force_list(value.get('j'))

    for id_ in force_list(value.pop('0', None)):
        ids_i, ids_j = _get_ids_from_0(id_)
        subfields_i.extend(ids_i)
        subfields_j.extend(ids_j)

    value['a'] = normalize_name(value['a'])
    value['i'] = subfields_i
    value['j'] = subfields_j

    return value


@cds2hep_marc.over('100__', '^100..')
@utils.for_each_value
def first_author(self, key, value):
    return _converted_author(value)


@cds2hep_marc.over('700__', '^700..')
def nonfirst_authors(self, key, value):
    """Populate ``700`` MARC field.

    Also populates the ``701`` MARC field through side-effects.
    """
    field_700 = self.get('700__', [])
    field_701 = self.get('701__', [])

    is_supervisor = any(
        el.lower().startswith('dir') for el in force_list(value.get('e', ''))
    )
    if is_supervisor:
        field_701.append(_converted_author(value))
    else:
        field_700.append(_converted_author(value))

    self['701__'] = field_701
    return field_700


@cds2hep_marc.over('110__', '^110..')
@utils.for_each_value
def corporate_authors(self, key, value):
    if 'a' in value:
        return vanilla_dict(value)


@cds2hep_marc.over('242__', '^242..')
def translated_title(self, key, value):
    value = vanilla_dict(value)
    add_source(value)
    return value


@cds2hep_marc.over('245__', '^245..')
def title(self, key, value):
    value = vanilla_dict(value)
    add_source(value)
    return value


@cds2hep_marc.over('246__', '^246..')
@utils.for_each_value
def other_titles(self, key, value):
    value = vanilla_dict(value)
    add_source(value)
    return value


@cds2hep_marc.over('260__', '^260..')
def imprint(self, key, value):
    return vanilla_dict(value)


@cds2hep_marc.over('300__', '^300..')
def number_of_pages(self, key, value):
    match = re.match(r'(?P<pages>\d+)', value.get('a', ''))
    if match:
        return {'a': match.group('pages')}


@cds2hep_marc.over('502__', '^502..')
def thesis_info(self, key, value):
    return {
        'b': value.get('a'),
        'c': value.get('b'),
        'd': value.get('c'),
    }


@cds2hep_marc.over('500__', '^500..')
@utils.for_each_value
def public_notes(self, key, value):
    value = vanilla_dict(value)
    add_source(value)
    return value


@cds2hep_marc.over('520__', '^520..')
@utils.for_each_value
def abstracts(self, key, value):
    value = vanilla_dict(value)
    add_source(value)
    return value


@cds2hep_marc.over('65017', '^65017')
@utils.for_each_value
def categories(self, key, value):
    schema = value.get('2', '')
    if schema.lower() == 'szgecern':
        result = {
            '2': 'INSPIRE',
            # XXX: will fail validation and be logged if invalid category
            'a': CATEGORIES.get(value.get('a'), value.get('a')),
        }
    else:
        result = vanilla_dict(value)

    add_source(result)
    return result


@cds2hep_marc.over('6531_', '^6531.')
@utils.for_each_value
def keywords(self, key, value):
    value = vanilla_dict(value)
    add_source(value)
    return value


@cds2hep_marc.over('693__', '^693..')
@utils.for_each_value
def accelerator_experiments(self, key, value):
    accelerator = ignore_not_applicable(value.get('a'))
    experiment = ignore_not_applicable(value.get('e'))
    experiment = EXPERIMENTS.get((accelerator, experiment), experiment)
    return {
        'a': accelerator,
        'e': experiment,
    }


@cds2hep_marc.over('65017', '^695..')
@utils.for_each_value
def arxiv_categories(self, key, value):
    is_arxiv = value.get('9', '').lower() == 'lanl eds'
    if is_arxiv:
        return {
            '2': 'arXiv',
            'a': value.get('a'),
        }


@cds2hep_marc.over('710__', '^710..')
@utils.for_each_value
def collaborations(self, key, value):
    if 'g' in value:
        return vanilla_dict(value)


@cds2hep_marc.over('773__', '^773..')
@utils.for_each_value
def publication_info(self, key, value):
    return vanilla_dict(value)


@cds2hep_marc.over('8564_', '^8564.')
def urls(self, key, value):
    """Populate the ``8564`` MARC field.

    Also populate the ``FFT`` field through side effects.
    """

    def _is_preprint(value):
        return value.get('y', '').lower() == 'preprint'

    def _is_fulltext(value):
        return value['u'].endswith('.pdf') and value['u'].startswith(
            'http://cds.cern.ch'
        )

    def _is_local_copy(value):
        return 'local copy' in value.get('y', '')

    def _is_ignored_domain(value):
        ignored_domains = [
            'http://cdsweb.cern.ch',
            'http://cms.cern.ch',
            'http://cmsdoc.cern.ch',
            'http://documents.cern.ch',
            'http://preprints.cern.ch',
            'http://cds.cern.ch',
            'http://arxiv.org',
        ]
        return any(value['u'].startswith(domain) for domain in ignored_domains)

    field_8564 = self.get('8564_', [])
    field_FFT = self.get('FFT__', [])

    if 'u' not in value:
        return field_8564

    url = escape_url(value['u'])

    if _is_fulltext(value) and not _is_preprint(value):
        if _is_local_copy(value):
            description = value.get('y', '').replace(
                'local copy', 'on CERN Document Server'
            )
            field_8564.append(
                {
                    'u': url,
                    'y': description,
                }
            )
        else:
            _, file_name = os.path.split(urllib.parse.urlparse(value['u']).path)
            _, extension = os.path.splitext(file_name)
            field_FFT.append(
                {
                    't': 'CDS',
                    'a': url,
                    'd': value.get('y', ''),
                    'n': file_name,
                    'f': extension,
                }
            )
    elif not _is_ignored_domain(value):
        field_8564.append(
            {
                'u': url,
                'y': value.get('y'),
            }
        )

    self['FFT__'] = field_FFT
    return field_8564


@cds2hep_marc.over('980__', '^980..')
@utils.for_each_value
def collections(self, key, value):
    allowed_collections = {'note', 'thesis', 'conferencepaper'}
    collection = value.get('a', '').lower()

    if collection not in allowed_collections:
        return
    return vanilla_dict(value)


@cds2hep_marc.over('980__', '^962..')
@utils.for_each_value
def conference_paper(self, key, value):
    is_conference_paper = value.get('n', '')[-2:].isdigit()
    if is_conference_paper:
        return {'a': 'ConferencePaper'}
