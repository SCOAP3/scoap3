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

from dojson.contrib.marc21.utils import create_record
from inspire_schemas.api import load_schema, validate

from inspire_dojson.data import data


def test_dois_from_0247_2_a():
    schema = load_schema('data')
    subschema = schema['properties']['dois']

    snippet = (  # record/1639676
        '<datafield tag="024" ind1="7" ind2=" ">'
        '  <subfield code="a">10.17182/hepdata.77268.v1/t6</subfield>'
        '  <subfield code="2">DOI</subfield>'
        '</datafield>'
    )

    expected = [
        {
            'value': '10.17182/hepdata.77268.v1/t6',
        }
    ]
    result = data.do(create_record(snippet))

    assert validate(result['dois'], subschema) is None
    assert expected == result['dois']


def test_new_record_from_970__d():
    schema = load_schema('data')
    subschema = schema['properties']['new_record']

    snippet = (  # synthetic data
        '<datafield tag="970" ind1=" " ind2=" ">'
        '  <subfield code="d">361769</subfield>'
        '</datafield>'
    )

    expected = {'$ref': 'http://localhost:5000/api/data/361769'}
    result = data.do(create_record(snippet))

    assert validate(result['new_record'], subschema) is None
    assert expected == result['new_record']
