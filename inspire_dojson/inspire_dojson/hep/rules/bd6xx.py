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

"""DoJSON rules for MARC fields in 6xx."""

from __future__ import absolute_import, division, print_function

import six
from dojson import utils
from inspire_utils.helpers import force_list

from inspire_dojson.hep.model import hep, hep2marc
from inspire_dojson.utils import force_single_element, get_record_ref

ENERGY_RANGES_MAP = {
    '1': '0-3 GeV',
    '2': '3-10 GeV',
    '3': '10-30 GeV',
    '4': '30-100 GeV',
    '5': '100-300 GeV',
    '6': '300-1000 GeV',
    '7': '1-10 TeV',
    '8': '> 10 TeV',
}

ENERGY_RANGES_REVERSE_MAP = {v: k for k, v in six.iteritems(ENERGY_RANGES_MAP)}


@hep.over('accelerator_experiments', '^693..')
@utils.flatten
@utils.for_each_value
def accelerator_experiments(self, key, value):
    """Populate the ``accelerator_experiments`` key."""
    result = []

    a_value = force_single_element(value.get('a'))
    e_values = [el for el in force_list(value.get('e')) if el != '-']
    zero_values = force_list(value.get('0'))

    if a_value and not e_values:
        result.append({'accelerator': a_value})

    # XXX: we zip only when they have the same length, otherwise
    #      we might match a value with the wrong recid.
    if len(e_values) == len(zero_values):
        for e_value, zero_value in zip(e_values, zero_values):
            result.append(
                {
                    'legacy_name': e_value,
                    'record': get_record_ref(zero_value, 'experiments'),
                }
            )
    else:
        for e_value in e_values:
            result.append({'legacy_name': e_value})

    return result


@hep2marc.over('693', '^accelerator_experiments$')
@utils.for_each_value
def accelerator_experiments2marc(self, key, value):
    """Populate the ``693`` MARC field."""
    return {
        'a': value.get('accelerator'),
        'e': value.get('legacy_name'),
    }


@hep.over('keywords', '^(084|653|695)..')
def keywords(self, key, values):
    """Populate the ``keywords`` key.

    Also populates the ``energy_ranges`` key through side effects.
    """

    def _get_source(value):
        sources = force_list(value.get('9'))
        if 'conference' in sources:
            return 'conference'
        if automatic_keywords or 'bibclassify' in sources:
            return 'classifier'
        return force_single_element(sources)

    keywords = self.get('keywords', [])
    energy_ranges = self.get('energy_ranges', [])
    values = force_list(values)
    automatic_keywords = any(
        a_value.lower() == '* automatic keywords *'
        for value in values
        for a_value in force_list(value.get('a'))
    )

    for value in values:
        if value.get('a'):
            schema = force_single_element(value.get('2', '')).upper()
            source = _get_source(value)

            a_values = force_list(value.get('a'))

            if source == 'conference':
                continue
            for a_value in a_values:
                if a_value.lower() == '* automatic keywords *':
                    continue
                keywords.append(
                    {
                        'schema': schema,
                        'source': source,
                        'value': a_value,
                    }
                )

        if value.get('e'):
            energy_ranges.append(ENERGY_RANGES_MAP.get(value.get('e')))

    self['energy_ranges'] = energy_ranges
    return keywords


@hep2marc.over('695', '^energy_ranges$')
@utils.for_each_value
def energy_ranges2marc(self, key, value):
    """Populate the ``695`` MARC field."""
    if value in ENERGY_RANGES_REVERSE_MAP:
        return {
            '2': 'INSPIRE',
            'e': ENERGY_RANGES_REVERSE_MAP[value],
        }


@hep2marc.over('695', '^keywords$')
def keywords2marc(self, key, values):
    """Populate the ``695`` MARC field.

    Also populates the ``084`` and ``6531`` MARC fields through side effects.
    """
    result_695 = self.get('695', [])
    result_084 = self.get('084', [])
    result_6531 = self.get('6531', [])
    automatic_keywords = False

    for value in values:
        schema = value.get('schema')
        source = value.get('source')
        if source == 'classifier':
            source = 'bibclassify'
            automatic_keywords = True
        keyword = value.get('value')

        if schema == 'PACS' or schema == 'PDG':
            result_084.append(
                {
                    '2': schema,
                    '9': source,
                    'a': keyword,
                }
            )
        elif schema == 'JACOW':
            result_6531.append(
                {
                    '2': 'JACoW',
                    '9': source,
                    'a': keyword,
                }
            )
        elif schema == 'INSPIRE':
            result_695.append(
                {
                    '2': 'INSPIRE',
                    '9': source,
                    'a': keyword,
                }
            )
        elif schema == 'INIS':
            result_695.append(
                {
                    '2': 'INIS',
                    '9': source,
                    'a': keyword,
                }
            )
        elif source != 'magpie':
            result_6531.append(
                {
                    '9': source,
                    'a': keyword,
                }
            )

    if automatic_keywords:
        result_695.insert(
            0,
            {
                '2': 'INSPIRE',
                'a': '* Automatic Keywords *',
            },
        )

    self['6531'] = result_6531
    self['084'] = result_084
    return result_695
