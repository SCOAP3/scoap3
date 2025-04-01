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

"""DoJSON rules for MARC fields in 1xx."""

from __future__ import absolute_import, division, print_function

import re

from dojson import utils
from inspire_utils.dedupers import dedupe_list
from inspire_utils.helpers import force_list, maybe_int

from inspire_dojson.hep.model import hep, hep2marc
from inspire_dojson.utils import force_single_element, get_record_ref

ORCID = re.compile(r'\d{4}-\d{4}-\d{4}-\d{3}[0-9Xx]')


def _authors(key, value):
    def _get_affiliations(value):
        result = []

        u_values = force_list(value.get('u'))
        z_values = force_list(value.get('z'))

        # XXX: we zip only when they have the same length, otherwise
        #      we might match a value with the wrong recid.
        if len(u_values) == len(z_values):
            for u_value, z_value in zip(u_values, z_values):
                result.append(
                    {
                        'record': get_record_ref(z_value, 'institutions'),
                        'value': u_value,
                    }
                )
        else:
            for u_value in u_values:
                result.append({'value': u_value})

        return dedupe_list(result)

    def _get_affiliations_identifiers(value):
        t_values = (
            t_value.split(':', 1) for t_value in dedupe_list(force_list(value.get('t')))
        )

        return [
            {'schema': schema.upper(), 'value': identifier}
            for schema, identifier in t_values
        ]

    def _get_curated_relation(value):
        return value.get('y') == '1' or None

    def _get_emails(value):
        return [
            el[6:] if el.startswith('email:') else el
            for el in force_list(value.get('m'))
        ]

    def _get_full_names(value):
        return [full_name.strip(', ') for full_name in force_list(value.get('a'))]

    def _get_ids(value):
        def _is_jacow(j_value):
            return j_value.upper().startswith('JACOW-')

        def _is_orcid(j_value):
            return j_value.upper().startswith('ORCID:') and len(j_value) > 6

        def _is_naked_orcid(j_value):
            return ORCID.match(j_value)

        def _is_cern(j_value):
            return j_value.startswith('CCID-')

        result = []

        i_values = force_list(value.get('i'))
        for i_value in i_values:
            result.append(
                {
                    'schema': 'INSPIRE ID',
                    'value': i_value,
                }
            )

        j_values = force_list(value.get('j'))
        for j_value in j_values:
            if _is_jacow(j_value):
                result.append(
                    {
                        'schema': 'JACOW',
                        'value': 'JACoW-' + j_value[6:],
                    }
                )
            elif _is_orcid(j_value):
                result.append(
                    {
                        'schema': 'ORCID',
                        'value': j_value[6:].replace('.', ''),
                    }
                )
            elif _is_naked_orcid(j_value):
                result.append(
                    {
                        'schema': 'ORCID',
                        'value': j_value,
                    }
                )
            elif _is_cern(j_value):
                result.append(
                    {
                        'schema': 'CERN',
                        'value': 'CERN-' + j_value[5:],
                    }
                )

        w_values = force_list(value.get('w'))
        for w_value in w_values:
            result.append(
                {
                    'schema': 'INSPIRE BAI',
                    'value': w_value,
                }
            )

        return dedupe_list(result)

    def _get_inspire_roles(value):
        result = []

        e_values = force_list(value.get('e'))
        if any(el.lower().startswith('ed') for el in e_values):
            result.append('editor')

        if key.startswith('701'):
            result.append('supervisor')

        return result

    def _get_raw_affiliations(value):
        return dedupe_list([{'value': el} for el in force_list(value.get('v'))])

    def _get_record(value):
        return get_record_ref(
            maybe_int(force_single_element(value.get('x'))), 'authors'
        )

    full_names = _get_full_names(value)
    if len(full_names) == 1:
        return [
            {
                'affiliations': _get_affiliations(value),
                'affiliations_identifiers': _get_affiliations_identifiers(value),
                'alternative_names': force_list(value.get('q')),
                'curated_relation': _get_curated_relation(value),
                'emails': _get_emails(value),
                'full_name': full_names[0],
                'ids': _get_ids(value),
                'inspire_roles': _get_inspire_roles(value),
                'raw_affiliations': _get_raw_affiliations(value),
                'record': _get_record(value),
            },
        ]
    else:
        return [
            {
                'affiliations': _get_affiliations(value),
                'affiliations_identifiers': _get_affiliations_identifiers(value),
                'full_name': full_name,
                'inspire_roles': _get_inspire_roles(value),
                'raw_affiliations': _get_raw_affiliations(value),
            }
            for full_name in full_names
        ]


@hep.over('authors', '^100..')
@utils.flatten
@utils.for_each_value
def authors(self, key, value):
    """Populate the ``authors`` key."""
    return _authors(key, value)


@hep.over('authors_second', '^700..', '^701..')
@utils.flatten
@utils.for_each_value
def authors_second(self, key, value):
    """Populate the ``authors`` key."""
    return _authors(key, value)


@hep2marc.over('100', '^authors$')
def authors2marc(self, key, value):
    """Populate the ``100`` MARC field.

    Also populates the ``700`` and the ``701`` MARC fields through side effects.
    """
    value = force_list(value)

    def _get_ids(value):
        ids = {
            'i': [],
            'j': [],
        }
        if value.get('ids'):
            for _id in value.get('ids'):
                if _id.get('schema') == 'INSPIRE ID':
                    ids['i'].append(_id.get('value'))
                elif _id.get('schema') == 'ORCID':
                    ids['j'].append('ORCID:' + _id.get('value'))
                elif _id.get('schema') == 'JACOW':
                    ids['j'].append(_id.get('value'))
                elif _id.get('schema') == 'CERN':
                    ids['j'].append('CCID-' + _id.get('value')[5:])
        return ids

    def _get_affiliations(value):
        return [aff.get('value') for aff in value.get('affiliations', [])]

    def _get_affiliations_identifiers(value):
        return [
            u'{}:{}'.format(aff.get('schema'), aff.get('value'))
            for aff in value.get('affiliations_identifiers', [])
        ]

    def _get_inspire_roles(value):
        values = force_list(value.get('inspire_roles'))
        return ['ed.' for role in values if role == 'editor']

    def _get_raw_affiliations(value):
        return [aff.get('value') for aff in value.get('raw_affiliations', [])]

    def get_value_100_700(value):
        ids = _get_ids(value)
        return {
            'a': value.get('full_name'),
            'e': _get_inspire_roles(value),
            'q': value.get('alternative_names'),
            'i': ids.get('i'),
            'j': ids.get('j'),
            'm': value.get('emails'),
            't': _get_affiliations_identifiers(value),
            'u': _get_affiliations(value),
            'v': _get_raw_affiliations(value),
        }

    def get_value_701(value):
        ids = _get_ids(value)
        return {
            'a': value.get('full_name'),
            'q': value.get('alternative_names'),
            'i': ids.get('i'),
            'j': ids.get('j'),
            'u': _get_affiliations(value),
            'v': _get_raw_affiliations(value),
        }

    if len(value) > 1:
        self["700"] = []
        self["701"] = []

    for author in value[1:]:
        is_supervisor = 'supervisor' in author.get('inspire_roles', [])
        if is_supervisor:
            self["701"].append(get_value_701(author))
        else:
            self["700"].append(get_value_100_700(author))
    return get_value_100_700(value[0])


@hep.over('corporate_author', '^110..')
@utils.for_each_value
def corporate_author(self, key, value):
    """Populate the ``corporate_author`` key."""
    return value.get('a')


@hep2marc.over('110', '^corporate_author$')
@utils.for_each_value
def corporate_author2marc(self, key, value):
    """Populate the ``110`` MARC field."""
    return {'a': value}
