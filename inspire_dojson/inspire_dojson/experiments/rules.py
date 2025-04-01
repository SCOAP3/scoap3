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

"""DoJSON rules for experiments."""

from __future__ import absolute_import, division, print_function

from dojson import utils
from dojson.errors import IgnoreKey
from inspire_utils.date import normalize_date
from inspire_utils.helpers import force_list, maybe_int

from inspire_dojson.experiments.model import experiments
from inspire_dojson.utils import force_single_element, get_record_ref

EXPERIMENT_CATEGORIES_MAP = {
    '1': 'Collider Experiments',
    '1.1': 'Collider Experiments|Hadrons',
    '1.1.1': 'Collider Experiments|Hadrons|p anti-p',
    '1.1.2': 'Collider Experiments|Hadrons|p p',
    '1.2': 'Collider Experiments|e+ e-',
    '1.3': 'Collider Experiments|e p',
    '1.4': 'Collider Experiments|Heavy Flavor Factory',
    '1.5': 'Collider Experiments|Heavy ion',
    '1.6': 'Collider Experiments|Detector development',
    '2': 'Fixed Target Experiments',
    '2.1': 'Fixed Target Experiments|High-momentum transfer',
    '2.2': 'Fixed Target Experiments|Hadron Spectroscopy',
    '2.3': 'Fixed Target Experiments|Deep inelastic scattering',
    '2.4': 'Fixed Target Experiments|Drell-Yan/Dilepton production',
    '2.5': 'Fixed Target Experiments|Flavor physics',
    '2.6': 'Fixed Target Experiments|Lepton precision experiments',
    '2.7': 'Fixed Target Experiments|Neutron/proton precision experiments',
    '3': 'Neutrino (flavor) experiments',
    '3.1': 'Neutrino (flavor) experiments|Accelerator',
    '3.1.1': 'Neutrino (flavor) experiments|Accelerator|short-baseline',
    '3.1.2': 'Neutrino (flavor) experiments|Accelerator|long-baseline',
    '3.2': 'Neutrino (flavor) experiments|Reactor',
    '3.2.1': 'Neutrino (flavor) experiments|Reactor|ultra-short-baseline',
    '3.2.2': 'Neutrino (flavor) experiments|Reactor|longer baselines',
    '3.3': 'Neutrino (flavor) experiments|Non terrestrial',
    '3.3.1': 'Neutrino (flavor) experiments|Non terrestrial|Atmospheric',
    '3.3.2': 'Neutrino (flavor) experiments|Non terrestrial|Solar',
    '3.3.3': 'Neutrino (flavor) experiments|Non terrestrial|Cosmic',
    '3.4': 'Neutrino (flavor) experiments|Neutrinoless double beta decay',
    '3.5': 'Neutrino (flavor) experiments|Neutrino mass',
    '4': 'Dark matter search experiments',
    '4.1': 'Dark matter search experiments|Non-accelerator',
    '4.2': 'Dark matter search experiments|Axion search experiments',
    '4.3': 'Dark matter search experiments|Dark Forces',
    '5': 'Cosmic ray/Gamma ray experiments',
    '5.1': 'Cosmic ray/Gamma ray experiments|Ground array',
    '5.2': 'Cosmic ray/Gamma ray experiments|Cerenkov array',
    '5.3': 'Cosmic ray/Gamma ray experiments|Satellite',
    '5.4': 'Cosmic ray/Gamma ray experiments|Balloon',
    '6': 'Other Rare-process/exotic experiments',
    '6.1': 'Other Rare-process/exotic experiments|Proton decay',
    '6.2': 'Other Rare-process/exotic experiments|Modified gravity and space-time',
    '6.3': 'Other Rare-process/exotic experiments|Magnetic monopoles',
    '6.4': 'Other Rare-process/exotic experiments|Fractionally charged particles',
    '7': 'Accelerator Test Facility Experiments',
    '7.1': 'Accelerator Test Facility Experiments|Electron and positron beams',
    '7.2': 'Accelerator Test Facility Experiments|Muon beams',
    '7.3': 'Accelerator Test Facility Experiments|Proton beams',
    '7.4': 'Accelerator Test Facility Experiments|Neutrino beams',
    '8': 'Astronomy experiments',
    '8.1': 'Astronomy experiments|CMB',
    '8.2': 'Astronomy experiments|Survey',
    '8.3': 'Astronomy experiments|Supernovae',
    '8.4': 'Astronomy experiments|Gravitational waves',
    '8.5': 'Astronomy experiments|Gravitational lensing/Dark matter',
    '9': 'Non-experimental',
    '9.1': 'Non-experimental|Data Analysis',
    '9.2': 'Non-experimental|Simulation tools',
    '9.2.1': 'Non-experimental|Simulation tools|Detector Simulation',
    '9.2.2': 'Non-experimental|Simulation tools|Event Simulation',
    '9.3': 'Non-experimental|Parton Distribution Fits',
    '9.4': 'Non-experimental|Lattice Gauge Theory',
    '9.5': 'Non-experimental|Neutrino Physics',
}


@experiments.over('_dates', '^046..')
@utils.for_each_value
def _dates(self, key, value):
    """Don't populate any key through the return value.

    On the other hand, populates the ``date_proposed``, ``date_approved``,
    ``date_started``, ``date_cancelled``, and the ``date_completed`` keys
    through side effects.
    """
    if value.get('q'):
        self['date_proposed'] = normalize_date(value['q'])
    if value.get('r'):
        self['date_approved'] = normalize_date(value['r'])
    if value.get('s'):
        self['date_started'] = normalize_date(value['s'])
    if value.get('c'):
        self['date_cancelled'] = normalize_date(value['c'])
    if value.get('t'):
        self['date_completed'] = normalize_date(value['t'])

    raise IgnoreKey


@experiments.over('experiment', '^119..')
def experiment(self, key, values):
    """Populate the ``experiment`` key.

    Also populates the ``legacy_name``, the ``accelerator``, and the
    ``institutions`` keys through side effects.
    """
    experiment = self.get('experiment', {})
    legacy_name = self.get('legacy_name', '')
    accelerator = self.get('accelerator', {})
    institutions = self.get('institutions', [])

    for value in force_list(values):
        if value.get('c'):
            experiment['value'] = value.get('c')
        if value.get('d'):
            experiment['short_name'] = value.get('d')

        if value.get('a'):
            legacy_name = value.get('a')

        if value.get('b'):
            accelerator['value'] = value.get('b')

        institution = {}
        if value.get('u'):
            institution['value'] = value.get('u')
        if value.get('z'):
            record = get_record_ref(maybe_int(value.get('z')), 'institutions')
            if record:
                institution['curated_relation'] = True
                institution['record'] = record
        institutions.append(institution)

    self['legacy_name'] = legacy_name
    self['accelerator'] = accelerator
    self['institutions'] = institutions
    return experiment


@experiments.over('long_name', '^245..')
def long_name(self, key, value):
    return value.get('a')


@experiments.over('inspire_classification', '^372..')
@utils.for_each_value
def inspire_classification(self, key, value):
    def _get_category(value):
        return EXPERIMENT_CATEGORIES_MAP.get(value.get('a'))

    return _get_category(value)


@experiments.over('name_variants', '^419..')
@utils.for_each_value
def name_variants(self, key, value):
    return value.get('a')


@experiments.over('related_records', '^510..')
@utils.for_each_value
def related_records(self, key, value):
    def _get_relation(value):
        RELATIONS_MAP = {'a': 'predecessor', 'b': 'successor'}

        return RELATIONS_MAP.get(value.get('w'))

    record = get_record_ref(maybe_int(value.get('0')), 'experiments')
    relation = _get_relation(value)

    if record and relation:
        return {
            'curated_relation': record is not None,
            'record': record,
            'relation': relation,
        }


@experiments.over('description', '^520..')
def description(self, key, value):
    result = self.get('description', '')

    if result and value.get('a'):
        result += '\n' + value.get('a')
    elif value.get('a'):
        result = value.get('a')

    return result


@experiments.over('collaboration', '^710..')
def collaboration(self, key, value):
    record = get_record_ref(maybe_int(value.get('0')), 'experiments')

    return {
        'curated_relation': record is not None,
        'record': record,
        'value': force_single_element(value.get('g')),
        'subgroup_names': force_list(value.get('q')),
    }


@experiments.over('core', '^980..')
def core(self, key, value):
    """Populate the ``core`` key.

    Also populates the ``deleted`` and ``project_type`` keys through side
    effects.
    """
    core = self.get('core')
    deleted = self.get('deleted')
    project_type = self.get('project_type', [])

    if not core:
        normalized_a_values = [el.upper() for el in force_list(value.get('a'))]
        if 'CORE' in normalized_a_values:
            core = True

    if not deleted:
        normalized_c_values = [el.upper() for el in force_list(value.get('c'))]
        if 'DELETED' in normalized_c_values:
            deleted = True

    if not project_type:
        normalized_a_values = [el.upper() for el in force_list(value.get('a'))]
        if 'ACCELERATOR' in normalized_a_values:
            project_type.append('accelerator')

    self['project_type'] = project_type
    self['deleted'] = deleted
    return core
