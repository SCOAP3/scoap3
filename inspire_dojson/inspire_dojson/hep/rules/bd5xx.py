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

"""DoJSON rules for MARC fields in 5xx."""

from __future__ import absolute_import, division, print_function

import re

from dojson import utils
from inspire_utils.date import normalize_date
from inspire_utils.helpers import force_list, maybe_int

from inspire_dojson.hep.model import hep, hep2marc
from inspire_dojson.utils import force_single_element, get_record_ref

IS_DEFENSE_DATE = re.compile('Presented (on )?(?P<defense_date>.*)', re.IGNORECASE)


@hep.over('public_notes', '^500..')
def public_notes(self, key, value):
    """Populate the ``public_notes`` key.

    Also populates the ``curated`` and ``thesis_info`` keys through side effects.
    """

    def _means_not_curated(public_note):
        return public_note in [
            '*Brief entry*',
            '* Brief entry *',
            '*Temporary entry*',
            '* Temporary entry *',
            '*Temporary record*',
            '* Temporary record *',
        ]

    public_notes = self.get('public_notes', [])
    thesis_info = self.get('thesis_info', {})

    source = force_single_element(value.get('9', ''))
    for current_value in force_list(value):
        for public_note in force_list(current_value.get('a')):
            match = IS_DEFENSE_DATE.match(public_note)
            if match:
                try:
                    thesis_info['defense_date'] = normalize_date(
                        match.group('defense_date')
                    )
                except ValueError:
                    public_notes.append(
                        {
                            'source': source,
                            'value': public_note,
                        }
                    )
            elif _means_not_curated(public_note):
                self['curated'] = False
            else:
                public_notes.append(
                    {
                        'source': source,
                        'value': public_note,
                    }
                )

    self['thesis_info'] = thesis_info
    return public_notes


@hep.over('thesis_info', '^502..')
def thesis_info(self, key, value):
    """Populate the ``thesis_info`` key."""

    def _get_degree_type(value):
        DEGREE_TYPES_MAP = {
            'RAPPORT DE STAGE': 'other',
            'INTERNSHIP REPORT': 'other',
            'DIPLOMA': 'diploma',
            'BACHELOR': 'bachelor',
            'LAUREA': 'laurea',
            'MASTER': 'master',
            'THESIS': 'other',
            'PHD': 'phd',
            'PDF': 'phd',
            'PH.D. THESIS': 'phd',
            'HABILITATION': 'habilitation',
        }

        b_value = force_single_element(value.get('b', ''))
        if b_value:
            return DEGREE_TYPES_MAP.get(b_value.upper(), 'other')

    def _get_institutions(value):
        c_values = force_list(value.get('c'))
        z_values = force_list(value.get('z'))

        # XXX: we zip only when they have the same length, otherwise
        #      we might match a value with the wrong recid.
        if len(c_values) != len(z_values):
            return [{'name': c_value} for c_value in c_values]
        else:
            return [
                {
                    'curated_relation': True,
                    'name': c_value,
                    'record': get_record_ref(z_value, 'institutions'),
                }
                for c_value, z_value in zip(c_values, z_values)
            ]

    thesis_info = self.get('thesis_info', {})

    thesis_info['date'] = normalize_date(force_single_element(value.get('d')))
    thesis_info['degree_type'] = _get_degree_type(value)
    thesis_info['institutions'] = _get_institutions(value)

    return thesis_info


@hep2marc.over('502', '^thesis_info$')
def thesis_info2marc(self, key, value):
    """Populate the ``502`` MARC field.

    Also populates the ``500`` MARC field through side effects.
    """

    def _get_b_value(value):
        DEGREE_TYPES_MAP = {
            'bachelor': 'Bachelor',
            'diploma': 'Diploma',
            'habilitation': 'Habilitation',
            'laurea': 'Laurea',
            'master': 'Master',
            'other': 'Thesis',
            'phd': 'PhD',
        }

        degree_type = value.get('degree_type')
        if degree_type:
            return DEGREE_TYPES_MAP.get(degree_type)

    result_500 = self.get('500', [])
    result_502 = self.get('502', {})

    if value.get('defense_date'):
        result_500.append(
            {
                'a': u'Presented on {}'.format(value.get('defense_date')),
            }
        )

    result_502 = {
        'b': _get_b_value(value),
        'c': [el['name'] for el in force_list(value.get('institutions'))],
        'd': value.get('date'),
    }

    self['500'] = result_500
    return result_502


@hep.over('abstracts', '^520..')
@utils.flatten
@utils.for_each_value
def abstracts(self, key, value):
    """Populate the ``abstracts`` key."""
    result = []

    source = force_single_element(value.get('9'))

    for a_value in force_list(value.get('a')):
        result.append(
            {
                'source': source,
                'value': a_value,
            }
        )

    return result


@hep2marc.over('520', '^abstracts$')
@utils.for_each_value
def abstract2marc(self, key, value):
    """Populate the ``520`` MARC field."""
    return {
        '9': value.get('source'),
        'a': value.get('value'),
    }


@hep.over('funding_info', '^536..')
@utils.for_each_value
def funding_info(self, key, value):
    """Populate the ``funding_info`` key."""
    return {
        'agency': value.get('a'),
        'grant_number': value.get('c'),
        'project_number': value.get('f'),
    }


@hep2marc.over('536', '^funding_info$')
@utils.for_each_value
def funding_info2marc(self, key, value):
    """Populate the ``536`` MARC field."""
    return {
        'a': value.get('agency'),
        'c': value.get('grant_number'),
        'f': value.get('project_number'),
    }


@hep.over('license', '^540..')
@utils.for_each_value
def license(self, key, value):
    """Populate the ``license`` key."""

    def _get_license(value):
        a_values = force_list(value.get('a'))

        oa_licenses = [el for el in a_values if el == 'OA' or el == 'Open Access']
        other_licenses = [el for el in a_values if el != 'OA' and el != 'Open Access']

        if not other_licenses:
            return force_single_element(oa_licenses)
        return force_single_element(other_licenses)

    def _get_material(value):
        material = value.get('3', '').lower()
        if material == 'article':
            return 'publication'
        return material

    return {
        'imposing': value.get('b'),
        'license': _get_license(value),
        'material': _get_material(value),
        'url': value.get('u'),
    }


@hep2marc.over('540', '^license$')
@utils.for_each_value
def license2marc(self, key, value):
    """Populate the ``540`` MARC field."""
    return {
        'a': value.get('license'),
        'b': value.get('imposing'),
        'u': value.get('url'),
        '3': value.get('material'),
    }


@hep.over('copyright', '^542..')
@utils.for_each_value
def copyright(self, key, value):
    """Populate the ``copyright`` key."""
    MATERIAL_MAP = {
        'Article': 'publication',
        'Published thesis as a book': 'publication',
    }

    material = value.get('e') or value.get('3')

    return {
        'holder': value.get('d'),
        'material': MATERIAL_MAP.get(material),
        'statement': value.get('f'),
        'url': value.get('u'),
        'year': maybe_int(value.get('g')),
    }


@hep2marc.over('542', '^copyright$')
@utils.for_each_value
def copyright2marc(self, key, value):
    """Populate the ``542`` MARC field."""
    E_MAP = {
        'publication': 'Article',
    }

    e_value = value.get('material')

    return {
        'd': value.get('holder'),
        'e': E_MAP.get(e_value),
        'f': value.get('statement'),
        'g': value.get('year'),
        'u': value.get('url'),
    }


@hep.over('_private_notes', '^595.[^DH]')
def _private_notes(self, key, value):
    """Populate the ``_private_notes`` key.

    Also populates the ``_export_to`` key through side effects.
    """

    def _is_for_cds(value):
        normalized_c_values = [el.upper() for el in force_list(value.get('c'))]
        return 'CDS' in normalized_c_values

    def _is_for_hal(value):
        normalized_c_values = [el.upper() for el in force_list(value.get('c'))]
        return 'HAL' in normalized_c_values

    def _is_not_for_hal(value):
        normalized_c_values = [el.upper() for el in force_list(value.get('c'))]
        return 'NOT HAL' in normalized_c_values

    _private_notes = self.get('_private_notes', [])
    _export_to = self.get('_export_to', {})

    for current_value in force_list(value):
        if _is_for_cds(current_value):
            _export_to['CDS'] = True

        if _is_for_hal(current_value):
            _export_to['HAL'] = True
        elif _is_not_for_hal(current_value):
            _export_to['HAL'] = False

        source = force_single_element(current_value.get('9'))
        for _private_note in force_list(current_value.get('a')):
            _private_notes.append(
                {
                    'source': source,
                    'value': _private_note,
                }
            )

    self['_export_to'] = _export_to
    return _private_notes


@hep2marc.over('595', '^_private_notes$')
@utils.for_each_value
def _private_notes2marc(self, key, value):
    """Populate the ``595`` MARC key.

    Also populates the `595_H` MARC key through side effects.
    """

    def _is_from_hal(value):
        return value.get('source') == 'HAL'

    if not _is_from_hal(value):
        return {
            '9': value.get('source'),
            'a': value.get('value'),
        }

    self.setdefault('595_H', []).append({'a': value.get('value')})


@hep2marc.over('595', '^_export_to$')
def _export_to2marc(self, key, value):
    """Populate the ``595`` MARC field."""

    def _is_for_cds(value):
        return 'CDS' in value

    def _is_for_hal(value):
        return 'HAL' in value and value['HAL']

    def _is_not_for_hal(value):
        return 'HAL' in value and not value['HAL']

    result = []

    if _is_for_cds(value):
        result.append({'c': 'CDS'})

    if _is_for_hal(value):
        result.append({'c': 'HAL'})
    elif _is_not_for_hal(value):
        result.append({'c': 'not HAL'})

    return result


@hep.over('_desy_bookkeeping', '^595.D')
@utils.for_each_value
def _desy_bookkeeping(self, key, value):
    """Populate the ``_desy_bookkeeping`` key."""
    return {
        'date': normalize_date(value.get('d')),
        'expert': force_single_element(value.get('a')),
        'status': value.get('s'),
    }


@hep2marc.over('595_D', '^_desy_bookkeeping$')
@utils.for_each_value
def _desy_bookkeeping2marc(self, key, value):
    """Populate the ``595_D`` MARC field.

    Also populates the ``035`` MARC field through side effects.
    """
    if 'identifier' not in value:
        return {
            'a': value.get('expert'),
            'd': value.get('date'),
            's': value.get('status'),
        }

    self.setdefault('035', []).append({'9': 'DESY', 'z': value['identifier']})


@hep.over('_private_notes', '^595.H')
@utils.flatten
@utils.for_each_value
def _private_notes_hal(self, key, value):
    """Populate the ``_private_notes`` key."""
    return [
        {
            'source': 'HAL',
            'value': _private_note,
        }
        for _private_note in force_list(value.get('a'))
    ]
