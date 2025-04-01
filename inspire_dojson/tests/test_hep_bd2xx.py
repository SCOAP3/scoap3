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
from dojson.contrib.marc21.utils import create_record
from inspire_schemas.api import load_schema, validate

from inspire_dojson.hep import hep, hep2marc


def test_rpp_from_210__a():
    schema = load_schema('hep')
    subschema = schema['properties']['rpp']

    snippet = (  # record/875948
        '<datafield tag="210" ind1=" " ind2=" ">'
        '  <subfield code="a">RPP</subfield>'
        '</datafield>'
    )

    expected = True
    result = hep.do(create_record(snippet))

    assert validate(result['rpp'], subschema) is None
    assert expected == result['rpp']

    expected = {'a': 'RPP'}
    result = hep2marc.do(result)

    assert expected == result['210']


def test_rpp_from_210__a__RPP_section():
    schema = load_schema('hep')
    subschema = schema['properties']['rpp']

    snippet = (  # record/806134
        '<datafield tag="210" ind1=" " ind2=" ">'
        '  <subfield code="a">RPP section</subfield>'
        '</datafield>'
    )

    expected = True
    result = hep.do(create_record(snippet))

    assert validate(result['rpp'], subschema) is None
    assert expected == result['rpp']

    expected = {'a': 'RPP'}
    result = hep2marc.do(result)

    assert expected == result['210']


def test_titles_from_245__a_9():
    schema = load_schema('hep')
    subschema = schema['properties']['titles']

    snippet = (  # record/001511698
        '<datafield tag="245" ind1=" " ind2=" ">  <subfield code="a">Exact Form'
        ' of Boundary Operators Dual to Interacting Bulk Scalar Fields in the'
        ' AdS/CFT Correspondence</subfield>  <subfield'
        ' code="9">arXiv</subfield></datafield>'
    )

    expected = [
        {
            'title': (
                'Exact Form of Boundary Operators Dual to Interacting '
                'Bulk Scalar Fields in the AdS/CFT Correspondence'
            ),
            'source': 'arXiv',
        },
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['titles'], subschema) is None
    assert expected == result['titles']

    expected = [
        {
            'a': (
                'Exact Form of Boundary Operators Dual to Interacting '
                'Bulk Scalar Fields in the AdS/CFT Correspondence'
            ),
            '9': 'arXiv',
        },
    ]
    result = hep2marc.do(result)

    assert expected == result['245']


def test_titles_from_246__a_9():
    schema = load_schema('hep')
    subschema = schema['properties']['titles']

    snippet = (  # record/1511471
        '<datafield tag="246" ind1=" " ind2=" ">'
        '  <subfield code="a">Superintegrable relativistic systems in'
        ' spacetime-dependent background fields</subfield>'
        '  <subfield code="9">arXiv</subfield>'
        '</datafield>'
    )

    expected = [
        {
            'source': 'arXiv',
            'title': (
                'Superintegrable relativistic systems in '
                'spacetime-dependent background fields'
            ),
        },
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['titles'], subschema) is None
    assert expected == result['titles']

    expected = [
        {
            'a': (
                'Superintegrable relativistic systems in spacetime-dependent'
                ' background fields'
            ),
            '9': 'arXiv',
        },
    ]
    result = hep2marc.do(result)

    assert expected == result['245']


def test_titles_from_245__a_b():
    schema = load_schema('hep')
    subschema = schema['properties']['titles']

    snippet = (  # record/1510141
        '<datafield tag="245" ind1=" " ind2=" ">  <subfield'
        ' code="a">Proceedings, New Observables in Quarkonium'
        ' Production</subfield>  <subfield code="b">Trento,'
        ' Italy</subfield></datafield>'
    )

    expected = [
        {
            'title': 'Proceedings, New Observables in Quarkonium Production',
            'subtitle': 'Trento, Italy',
        },
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['titles'], subschema) is None
    assert expected == result['titles']

    expected = [
        {
            'a': 'Proceedings, New Observables in Quarkonium Production',
            'b': 'Trento, Italy',
        },
    ]
    result = hep2marc.do(result)

    assert expected == result['245']


@pytest.mark.usefixtures(name='_stable_langdetect')
def test_title_translations_from_242__a():
    schema = load_schema('hep')
    subschema = schema['properties']['title_translations']

    snippet = (  # record/8352
        '<datafield tag="242" ind1=" " ind2=" ">'
        '  <subfield code="a">The redshift of extragalactic nebulae</subfield>'
        '</datafield>'
    )

    expected = [
        {
            'language': 'en',
            'title': 'The redshift of extragalactic nebulae',
        },
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['title_translations'], subschema) is None
    assert expected == result['title_translations']

    expected = [
        {
            'a': 'The redshift of extragalactic nebulae',
        },
    ]
    result = hep2marc.do(result)

    assert expected == result['242']


@pytest.mark.usefixtures(name='_stable_langdetect')
def test_title_translations_from_242__a_handles_chinese_correctly():
    schema = load_schema('hep')
    subschema = schema['properties']['title_translations']

    snippet = (
        '<datafield tag="242" ind1=" " ind2=" ">'
        '  <subfield code="a">LHCb上底介子含粲衰变过程中强子谱学的实验研究</subfield>'
        '</datafield>'
    )

    expected = [
        {
            'language': 'zh',
            'title': 'LHCb上底介子含粲衰变过程中强子谱学的实验研究',
        },
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['title_translations'], subschema) is None
    assert expected == result['title_translations']

    expected = [
        {
            'a': 'LHCb上底介子含粲衰变过程中强子谱学的实验研究',
        },
    ]
    result = hep2marc.do(result)

    assert expected == result['242']


@pytest.mark.usefixtures(name='_stable_langdetect')
def test_title_translations_from_242__a_b():
    schema = load_schema('hep')
    subschema = schema['properties']['title_translations']

    snippet = (  # record/1501064
        '<datafield tag="242" ind1=" " ind2=" ">  <subfield'
        ' code="a">Generalized Hamilton-Jacobi Formalism</subfield>  <subfield'
        ' code="b">Field Theories with Upper-Order'
        ' Derivatives</subfield></datafield>'
    )

    expected = [
        {
            'language': 'en',
            'title': 'Generalized Hamilton-Jacobi Formalism',
            'subtitle': 'Field Theories with Upper-Order Derivatives',
        },
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['title_translations'], subschema) is None
    assert expected == result['title_translations']

    expected = [
        {
            'a': 'Generalized Hamilton-Jacobi Formalism',
            'b': 'Field Theories with Upper-Order Derivatives',
        },
    ]
    result = hep2marc.do(result)

    assert expected == result['242']


def test_editions_from_250__a():
    schema = load_schema('hep')
    subschema = schema['properties']['editions']

    snippet = (  # record/1383727
        '<datafield tag="250" ind1=" " ind2=" ">'
        '  <subfield code="a">2nd ed.</subfield>'
        '</datafield>'
    )

    expected = [
        '2nd ed.',
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['editions'], subschema) is None
    assert expected == result['editions']

    expected = [
        {'a': '2nd ed.'},
    ]
    result = hep2marc.do(result)

    assert expected == result['250']


def test_imprints_from_260__a_b_c():
    schema = load_schema('hep')
    subschema = schema['properties']['imprints']

    snippet = (  # record/1614215
        '<datafield tag="260" ind1=" " ind2=" ">'
        '  <subfield code="a">Geneva</subfield>'
        '  <subfield code="b">CERN</subfield>'
        '  <subfield code="c">2017</subfield>'
        '</datafield>'
    )

    expected = [
        {
            'date': '2017',
            'place': 'Geneva',
            'publisher': 'CERN',
        },
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['imprints'], subschema) is None
    assert expected == result['imprints']

    expected = [
        {
            'a': 'Geneva',
            'b': 'CERN',
            'c': '2017',
        },
    ]
    result = hep2marc.do(result)

    assert expected == result['260']


def test_imprints_from_260__c_wrong_date():
    schema = load_schema('hep')
    subschema = schema['properties']['imprints']

    snippet = (  # record/1314991
        '<datafield tag="260" ind1=" " ind2=" ">'
        '  <subfield code="c">2014-00-01</subfield>'
        '</datafield>'
    )

    expected = [{'date': '2014'}]
    result = hep.do(create_record(snippet))

    assert validate(result['imprints'], subschema) is None
    assert expected == result['imprints']

    expected = [
        {'c': '2014'},
    ]
    result = hep2marc.do(result)

    assert expected == result['260']


def test_preprint_date_from_269__c():
    schema = load_schema('hep')
    subschema = schema['properties']['preprint_date']

    snippet = (  # record/1375944
        '<datafield tag="269" ind1=" " ind2=" ">'
        '  <subfield code="c">2015-05-03</subfield>'
        '</datafield>'
    )

    expected = '2015-05-03'
    result = hep.do(create_record(snippet))

    assert validate(result['preprint_date'], subschema) is None
    assert expected == result['preprint_date']

    expected = [
        {'c': '2015-05-03'},
    ]
    result = hep2marc.do(result)

    assert expected == result['269']


def test_preprint_date_from_269__c_wrong_date():
    schema = load_schema('hep')
    subschema = schema['properties']['preprint_date']

    snippet = (  # record/1194517
        '<datafield tag="269" ind1=" " ind2=" ">'
        '  <subfield code="c">2001-02-31</subfield>'
        '</datafield>'
    )

    expected = '2001-02'
    result = hep.do(create_record(snippet))

    assert validate(result['preprint_date'], subschema) is None
    assert expected == result['preprint_date']

    expected = [
        {'c': '2001-02'},
    ]
    result = hep2marc.do(result)

    assert expected == result['269']
