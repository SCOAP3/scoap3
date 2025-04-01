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

from inspire_dojson.hep import hep, hep2marc


def test_book_series_from_490__a():
    schema = load_schema('hep')
    subschema = schema['properties']['book_series']

    snippet = (  # record/1508903
        '<datafield tag="490" ind1=" " ind2=" ">'
        '  <subfield code="a">Graduate Texts in Physics</subfield>'
        '</datafield>'
    )

    expected = [
        {'title': 'Graduate Texts in Physics'},
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['book_series'], subschema) is None
    assert expected == result['book_series']

    expected = [
        {'a': 'Graduate Texts in Physics'},
    ]
    result = hep2marc.do(result)

    assert expected == result['490']
