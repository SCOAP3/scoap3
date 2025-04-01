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

"""DoJSON rules for MARC fields in 2xx."""

from __future__ import absolute_import, division, print_function

import langdetect
from dojson import utils
from inspire_utils.helpers import force_list

from inspire_dojson.hep.model import hep, hep2marc
from inspire_dojson.utils import normalize_date_aggressively


@hep.over('titles', '^(210|245|246|247)..')
@utils.for_each_value
def titles(self, key, value):
    """Populate the ``titles`` key.

    Also populates the ``rpp`` key through side-effects.
    """
    is_rpp = key.startswith('210') and value.get('a', '').split()[0].lower() == 'rpp'
    if is_rpp:
        self['rpp'] = True
        return None

    if not key.startswith('245'):
        return {
            'source': value.get('9'),
            'subtitle': value.get('b'),
            'title': value.get('a'),
        }

    self.setdefault('titles', []).insert(
        0,
        {
            'source': value.get('9'),
            'subtitle': value.get('b'),
            'title': value.get('a'),
        },
    )


@hep.over('title_translations', '^242..')
@utils.for_each_value
def title_translations(self, key, value):
    """Populate the ``title_translations`` key."""
    language = langdetect.detect(value.get('a'))
    if language:
        language = language.split("-")[0]
    return {
        'language': language,
        'source': value.get('9'),
        'subtitle': value.get('b'),
        'title': value.get('a'),
    }


@hep2marc.over('210', '^rpp$')
def rpp2marc(self, key, value):
    if value is True:
        return {
            'a': 'RPP',
        }


@hep2marc.over('246', '^titles$')
def titles2marc(self, key, values):
    """Populate the ``246`` MARC field.

    Also populates the ``245`` MARC field through side effects.
    """
    first, rest = values[0], values[1:]

    self.setdefault('245', []).append(
        {
            'a': first.get('title'),
            'b': first.get('subtitle'),
            '9': first.get('source'),
        }
    )

    return [
        {
            'a': value.get('title'),
            'b': value.get('subtitle'),
            '9': value.get('source'),
        }
        for value in rest
    ]


@hep2marc.over('242', '^title_translations$')
@utils.for_each_value
def title_translations2marc(self, key, value):
    """Populate the ``242`` MARC field."""
    return {
        'a': value.get('title'),
        'b': value.get('subtitle'),
        '9': value.get('source'),
    }


@hep.over('editions', '^250..')
@utils.flatten
@utils.for_each_value
def editions(self, key, value):
    """Populate the ``editions`` key."""
    return force_list(value.get('a'))


@hep2marc.over('250', '^editions$')
@utils.for_each_value
def editions2marc(self, key, value):
    """Populate the ``250`` MARC field."""
    return {'a': value}


@hep.over('imprints', '^260..')
@utils.for_each_value
def imprints(self, key, value):
    """Populate the ``imprints`` key."""
    return {
        'place': value.get('a'),
        'publisher': value.get('b'),
        'date': normalize_date_aggressively(value.get('c')),
    }


@hep2marc.over('260', '^imprints$')
@utils.for_each_value
def imprints2marc(self, key, value):
    """Populate the ``260`` MARC field."""
    return {
        'a': value.get('place'),
        'b': value.get('publisher'),
        'c': value.get('date'),
    }


@hep.over('preprint_date', '^269..')
def preprint_date(self, key, value):
    """Populate the ``preprint_date`` key."""
    return normalize_date_aggressively(value.get('c'))


@hep2marc.over('269', '^preprint_date$')
@utils.for_each_value
def preprint_date2marc(self, key, value):
    """Populate the ``269`` MARC field."""
    return {'c': value}
