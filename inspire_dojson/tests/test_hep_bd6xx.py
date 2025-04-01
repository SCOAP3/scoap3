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


def test_keywords_from_084__a_2():
    schema = load_schema('hep')
    subschema = schema['properties']['keywords']

    snippet = (  # record/1590395
        '<datafield tag="084" ind1=" " ind2=" ">'
        '  <subfield code="a">02.20.Sv</subfield>'
        '  <subfield code="2">PACS</subfield>'
        '</datafield>'
    )

    expected = [
        {
            'schema': 'PACS',
            'value': '02.20.Sv',
        },
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['keywords'], subschema) is None
    assert expected == result['keywords']
    assert 'energy_ranges' not in result

    expected = [
        {
            '2': 'PACS',
            'a': '02.20.Sv',
        },
    ]
    result = hep2marc.do(result)

    assert expected == result['084']
    assert '6531' not in result
    assert '695' not in result


def test_keywords_from_084__double_2_does_not_raise():
    snippet = (  # synthetic data
        '<datafield tag="084" ind1=" " ind2=" ">'
        '  <subfield code="a">02.20.Sv</subfield>'
        '  <subfield code="2">PACS</subfield>'
        '  <subfield code="2">PACS</subfield>'
        '</datafield>'
    )

    hep.do(create_record(snippet))


def test_keywords_from_084__a_2_9():
    schema = load_schema('hep')
    subschema = schema['properties']['keywords']

    snippet = (  # record/1421100
        '<datafield tag="084" ind1=" " ind2=" ">'
        '  <subfield code="2">PDG</subfield>'
        '  <subfield code="9">PDG</subfield>'
        '  <subfield code="a">G033M</subfield>'
        '</datafield>'
    )

    expected = [
        {
            'schema': 'PDG',
            'source': 'PDG',
            'value': 'G033M',
        },
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['keywords'], subschema) is None
    assert expected == result['keywords']
    assert 'energy_ranges' not in result

    expected = [
        {
            '2': 'PDG',
            '9': 'PDG',
            'a': 'G033M',
        },
    ]
    result = hep2marc.do(result)

    assert expected == result['084']
    assert '6531' not in result
    assert '695' not in result


def test_keywords_from_084__double_a_2():
    schema = load_schema('hep')
    subschema = schema['properties']['keywords']

    snippet = (  # record/1376406
        '<datafield tag="084" ind1=" " ind2=" ">'
        '  <subfield code="2">PACS</subfield>'
        '  <subfield code="a">04.80.N</subfield>'
        '  <subfield code="a">07.10.Y</subfield>'
        '</datafield>'
    )

    expected = [
        {
            'schema': 'PACS',
            'value': '04.80.N',
        },
        {
            'schema': 'PACS',
            'value': '07.10.Y',
        },
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['keywords'], subschema) is None
    assert expected == result['keywords']
    assert 'energy_ranges' not in result

    expected = [
        {
            '2': 'PACS',
            'a': '04.80.N',
        },
        {
            '2': 'PACS',
            'a': '07.10.Y',
        },
    ]
    result = hep2marc.do(result)

    assert expected == result['084']
    assert '6531' not in result
    assert '695' not in result


def test_keywords_from_6531_a_2():
    schema = load_schema('hep')
    subschema = schema['properties']['keywords']

    snippet = (  # record/1473380
        '<datafield tag="653" ind1="1" ind2=" ">'
        '  <subfield code="2">JACoW</subfield>'
        '  <subfield code="a">experiment</subfield>'
        '</datafield>'
    )

    expected = [
        {
            'schema': 'JACOW',
            'value': 'experiment',
        },
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['keywords'], subschema) is None
    assert expected == result['keywords']
    assert 'energy_ranges' not in result

    expected = [
        {
            '2': 'JACoW',
            'a': 'experiment',
        },
    ]
    result = hep2marc.do(result)

    assert expected == result['6531']
    assert '084' not in result
    assert '695' not in result


def test_keywords_from_6531_a_9():
    schema = load_schema('hep')
    subschema = schema['properties']['keywords']

    snippet = (  # record/1260876
        '<datafield tag="653" ind1="1" ind2=" ">'
        '  <subfield code="9">author</subfield>'
        '  <subfield code="a">Data</subfield>'
        '</datafield>'
    )

    expected = [
        {
            'source': 'author',
            'value': 'Data',
        },
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['keywords'], subschema) is None
    assert expected == result['keywords']
    assert 'energy_ranges' not in result

    expected = [
        {
            '9': 'author',
            'a': 'Data',
        },
    ]
    result = hep2marc.do(result)

    assert expected == result['6531']
    assert '084' not in result
    assert '695' not in result


def test_keywords_from_6531_a_double_9_ignores_values_from_conference():
    snippet = (  # record/1498175
        '<datafield tag="653" ind1="1" ind2=" ">'
        '  <subfield code="9">submitter</subfield>'
        '  <subfield code="9">conference</subfield>'
        '  <subfield code="a">Track reconstruction</subfield>'
        '</datafield>'
    )

    result = hep.do(create_record(snippet))

    assert 'energy_ranges' not in result
    assert 'keywords' not in result


def test_keywords_from_6531_9_ignores_lone_sources():
    snippet = (  # record/1382933
        '<datafield tag="653" ind1="1" ind2=" ">'
        '  <subfield code="9">author</subfield>'
        '</datafield>'
    )

    result = hep.do(create_record(snippet))

    assert 'energy_ranges' not in result
    assert 'keywords' not in result


def test_keywords2marc_does_not_export_magpie_keywords():
    record = {
        'keywords': [
            {
                'source': 'magpie',
                'value': 'cosmological model',
            },
        ],
    }

    result = hep2marc.do(record)

    assert result is None


def test_accelerator_experiments_from_693__a():
    schema = load_schema('hep')
    subschema = schema['properties']['accelerator_experiments']

    snippet = (  # record/1623303
        '<datafield tag="693" ind1=" " ind2=" ">'
        '  <subfield code="a">BATSE</subfield>'
        '</datafield>'
    )

    expected = [
        {'accelerator': 'BATSE'},
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['accelerator_experiments'], subschema) is None
    assert expected == result['accelerator_experiments']

    expected = [
        {'a': 'BATSE'},
    ]
    result = hep2marc.do(result)

    assert expected == result['693']


def test_accelerator_experiments_from_693__a_e():
    schema = load_schema('hep')
    subschema = schema['properties']['accelerator_experiments']

    snippet = (  # record/1517829
        '<datafield tag="693" ind1=" " ind2=" ">'
        '  <subfield code="a">CERN LHC</subfield>'
        '  <subfield code="e">CERN-LHC-CMS</subfield>'
        '  <subfield code="0">1108642</subfield>'
        '</datafield>'
    )

    expected = [
        {
            'legacy_name': 'CERN-LHC-CMS',
            'record': {
                '$ref': 'http://localhost:5000/api/experiments/1108642',
            },
        },
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['accelerator_experiments'], subschema) is None
    assert expected == result['accelerator_experiments']

    expected = [
        {'e': 'CERN-LHC-CMS'},
    ]
    result = hep2marc.do(result)

    assert expected == result['693']


def test_accelerator_experiments_from_693__e_0_and_693__e_discards_single_dashes():
    schema = load_schema('hep')
    subschema = schema['properties']['accelerator_experiments']

    snippet = (  # record/1503527
        '<record>'
        '  <datafield tag="693" ind1=" " ind2=" ">'
        '    <subfield code="e">CERN-LHC-ATLAS</subfield>'
        '    <subfield code="0">1108541</subfield>'
        '  </datafield>'
        '  <datafield tag="693" ind1=" " ind2=" ">'
        '    <subfield code="e">-</subfield>'
        '  </datafield>'
        '</record>'
    )

    expected = [
        {
            'legacy_name': 'CERN-LHC-ATLAS',
            'record': {
                '$ref': 'http://localhost:5000/api/experiments/1108541',
            },
        },
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['accelerator_experiments'], subschema) is None
    assert expected == result['accelerator_experiments']

    expected = [
        {'e': 'CERN-LHC-ATLAS'},
    ]
    result = hep2marc.do(result)

    assert expected == result['693']


def test_keywords_from_695__a_2():
    schema = load_schema('hep')
    subschema = schema['properties']['keywords']

    snippet = (  # record/200123
        '<datafield tag="695" ind1=" " ind2=" ">'
        '  <subfield code="a">REVIEW</subfield>'
        '  <subfield code="2">INSPIRE</subfield>'
        '</datafield>'
    )

    expected = [
        {
            'value': 'REVIEW',
            'schema': 'INSPIRE',
        },
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['keywords'], subschema) is None
    assert expected == result['keywords']
    assert 'energy_ranges' not in result

    expected = [
        {
            '2': 'INSPIRE',
            'a': 'REVIEW',
        },
    ]
    result = hep2marc.do(result)

    assert expected == result['695']
    assert '084' not in result
    assert '6531' not in result


def test_keywords_from_695__a_2_inis():
    schema = load_schema('hep')
    subschema = schema['properties']['keywords']

    snippet = (  # record/1493738
        '<datafield tag="695" ind1=" " ind2=" ">'
        '  <subfield code="a">Accelerators</subfield>'
        '  <subfield code="2">INIS</subfield>'
        '</datafield>'
    )

    expected = [
        {
            'schema': 'INIS',
            'value': 'Accelerators',
        },
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['keywords'], subschema) is None
    assert expected == result['keywords']
    assert 'energy_ranges' not in result

    expected = [
        {
            'a': 'Accelerators',
            '2': 'INIS',
        },
    ]
    result = hep2marc.do(result)

    assert expected == result['695']
    assert '084' not in result
    assert '6531' not in result


def test_energy_ranges_from_695__e_2():
    schema = load_schema('hep')
    subschema = schema['properties']['energy_ranges']

    snippet = (  # record/1124337
        '<datafield tag="695" ind1=" " ind2=" ">'
        '  <subfield code="2">INSPIRE</subfield>'
        '  <subfield code="e">7</subfield>'
        '</datafield>'
    )

    expected = [
        '1-10 TeV',
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['energy_ranges'], subschema) is None
    assert expected == result['energy_ranges']
    assert 'keywords' not in result

    expected = [
        {
            '2': 'INSPIRE',
            'e': '7',
        },
    ]
    result = hep2marc.do(result)

    assert expected == result['695']
    assert '084' not in result
    assert '6531' not in result


def test_keywords_from_multiple_695__a_2():
    schema = load_schema('hep')
    subschema = schema['properties']['keywords']

    snippet = (  # record/363605
        '<record>'
        '  <datafield tag="695" ind1=" " ind2=" ">'
        '    <subfield code="a">programming: Monte Carlo</subfield>'
        '    <subfield code="2">INSPIRE</subfield>'
        '  </datafield>'
        '  <datafield tag="695" ind1=" " ind2=" ">'
        '    <subfield code="a">electron positron: annihilation</subfield>'
        '    <subfield code="2">INSPIRE</subfield>'
        '  </datafield>'
        '</record>'
    )

    expected = [
        {
            'schema': 'INSPIRE',
            'value': 'programming: Monte Carlo',
        },
        {
            'schema': 'INSPIRE',
            'value': 'electron positron: annihilation',
        },
    ]

    result = hep.do(create_record(snippet))

    assert validate(result['keywords'], subschema) is None
    assert expected == result['keywords']
    assert 'energy_ranges' not in result

    expected = [
        {
            'a': 'programming: Monte Carlo',
            '2': 'INSPIRE',
        },
        {
            'a': 'electron positron: annihilation',
            '2': 'INSPIRE',
        },
    ]
    result = hep2marc.do(result)

    assert expected == result['695']
    assert '084' not in result
    assert '6531' not in result


def test_keywords_from_695__a_2_9_automatic_keywords():
    schema = load_schema('hep')
    subschema = schema['properties']['keywords']

    snippet = (  # record/1859815
        '<record>'
        '  <datafield tag="695" ind1=" " ind2=" ">'
        '    <subfield code="2">INSPIRE</subfield>'
        '    <subfield code="a">* Automatic Keywords *</subfield>'
        '  </datafield>'
        '  <datafield tag="695" ind1=" " ind2=" ">'
        '    <subfield code="2">INSPIRE</subfield>'
        '    <subfield code="a">soliton: topological</subfield>'
        '    <subfield code="9">bibclassify</subfield>'
        '  </datafield>'
        '  <datafield tag="695" ind1=" " ind2=" ">'
        '    <subfield code="2">INSPIRE</subfield>'
        '    <subfield code="a">soliton: classical</subfield>'
        '    <subfield code="9">bibclassify</subfield>'
        '  </datafield>'
        '</record>'
    )

    expected = [
        {
            'schema': 'INSPIRE',
            'value': 'soliton: topological',
            'source': 'classifier',
        },
        {
            'schema': 'INSPIRE',
            'value': 'soliton: classical',
            'source': 'classifier',
        },
    ]

    result = hep.do(create_record(snippet))

    assert validate(result['keywords'], subschema) is None
    assert expected == result['keywords']
    assert 'energy_ranges' not in result

    expected = [
        {
            'a': '* Automatic Keywords *',
            '2': 'INSPIRE',
        },
        {
            'a': 'soliton: topological',
            '2': 'INSPIRE',
            '9': 'bibclassify',
        },
        {
            'a': 'soliton: classical',
            '2': 'INSPIRE',
            '9': 'bibclassify',
        },
    ]
    result = hep2marc.do(result)

    assert expected == result['695']
    assert '084' not in result
    assert '6531' not in result
