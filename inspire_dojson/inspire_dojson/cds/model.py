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

"""DoJSON model definition for CDS MARC to INSPIRE HEP MARC."""

from __future__ import absolute_import, division, print_function

from itertools import chain

from inspire_utils.helpers import force_list
from inspire_utils.record import get_value

from inspire_dojson.model import FilterOverdo, clean_record


def add_control_number(record, blob):
    if '001' not in blob:
        return record

    collections = (
        value.lower()
        for value in chain(
            force_list(get_value(blob, '980__.a', default=[])),
            force_list(get_value(blob, '980__.c', default=[])),
        )
    )
    if 'hidden' in collections:
        record.setdefault('595__', []).append(
            {'9': 'CDS', 'a': u'CDS-{}'.format(blob['001'])}
        )
    else:
        record.setdefault('035__', []).append(
            {
                '9': 'CDS',
                'a': blob['001'],
            }
        )

    return record


def add_collections(record, blob):
    def _add_collection(value):
        record.setdefault('980__', []).append({'a': value})

    _add_collection('HEP')
    _add_collection('CORE')

    return record


def remove_english_language(record, blob):
    if '041__' not in record:
        return record

    languages = force_list(get_value(blob, '041__.a'))
    if languages == ['eng']:
        del record['041__']

    return record


filters = [
    add_control_number,
    add_collections,
    remove_english_language,
    clean_record(),
]

cds2hep_marc = FilterOverdo(filters=filters)
