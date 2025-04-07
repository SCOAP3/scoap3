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

from __future__ import absolute_import, division, print_function

import pytest

from inspire_dojson import DoJsonError, marcxml2record, record2marcxml
from inspire_dojson.model import FilterOverdo, add_schema


def test_filteroverdo_works_without_filters():
    model = FilterOverdo()

    expected = {}
    result = model.do({})

    assert expected == result


def test_filteroverdo_wraps_exceptions():
    record = (  # synthetic data
        '<record>'
        '  <datafield tag="269" ind1=" " ind2=" ">'
        '    <subfield code="c">Ceci n’est pas une dâte</subfield>'
        '  </datafield>'
        '  <datafield tag="980" ind1=" " ind2=" ">'
        '    <subfield code="a">HEP</subfield>'
        '  </datafield>'
        '</record>'
    )

    with pytest.raises(DoJsonError) as exc:
        marcxml2record(record)
    assert 'Error in rule "preprint_date" for field "269__"' in str(exc.value)


def test_filteroverdo_handles_exceptions_in_non_dicts():
    record = {
        '$schema': 'hep.json',
        'titles': None,
    }  # synthetic data

    with pytest.raises(DoJsonError) as exc:
        record2marcxml(record)
    assert 'Error in rule "246" for field "titles"' in str(exc.value)


def test_add_schema():
    model = FilterOverdo(filters=[add_schema('hep.json')])

    expected = {'$schema': 'hep.json'}
    result = model.do({})

    assert expected == result
