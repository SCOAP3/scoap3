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

"""DoJSON rules for Data."""

from __future__ import absolute_import, division, print_function

from dojson import utils
from idutils import normalize_doi

from inspire_dojson.data.model import data
from inspire_dojson.utils import force_single_element, get_record_ref


@data.over('dois', '^0247.')
@utils.for_each_value
def dois(self, key, value):
    return {
        'source': value.get('9'),
        'value': normalize_doi(value.get('a')),
    }


@data.over('new_record', '^970..')
def new_record(self, key, value):
    new_recid = force_single_element(value.get('d'))
    if new_recid:
        return get_record_ref(new_recid, 'data')
