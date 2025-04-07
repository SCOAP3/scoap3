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

from inspire_dojson.hepnames import hepnames, hepnames2marc

EXPERIMENTS_DATA = [
    [
        'current_curated',
        '''
        <datafield tag="693" ind1=" " ind2=" ">
            <subfield code="d">2020</subfield>
            <subfield code="e">CERN-ALPHA</subfield>
            <subfield code="0">1</subfield>
            <subfield code="s">2014</subfield>
            <subfield code="z">current</subfield>
        </datafield>
        ''',
        [
            {
                'curated_relation': True,
                'current': True,
                'end_date': '2020',
                'name': 'CERN-ALPHA',
                'record': {
                    '$ref': 'http://localhost:5000/api/experiments/1',
                },
                'start_date': '2014',
            }
        ],
        [
            {
                '0': 1,
                'd': '2020',
                'e': 'CERN-ALPHA',
                's': '2014',
                'z': 'current',
            }
        ],
    ],
    [
        'current_curated_hidden',
        '''
        <datafield tag="693" ind1=" " ind2=" ">
            <subfield code="d">2020</subfield>
            <subfield code="e">CERN-ALPHA</subfield>
            <subfield code="0">1</subfield>
            <subfield code="s">2014</subfield>
            <subfield code="z">current</subfield>
            <subfield code="h">HIDDEN</subfield>
        </datafield>
        ''',
        [
            {
                'curated_relation': True,
                'current': True,
                'end_date': '2020',
                'name': 'CERN-ALPHA',
                'record': {
                    '$ref': 'http://localhost:5000/api/experiments/1',
                },
                'start_date': '2014',
                'hidden': True,
            }
        ],
        [
            {
                '0': 1,
                'd': '2020',
                'e': 'CERN-ALPHA',
                's': '2014',
                'z': 'current',
                'h': 'HIDDEN',
            }
        ],
    ],
    [
        'notcurrent_curated',
        '''
        <datafield tag="693" ind1=" " ind2=" ">
            <subfield code="e">SDSS</subfield>
            <subfield code="0">3</subfield>
        </datafield>
        ''',
        [
            {
                'curated_relation': True,
                'current': False,
                'name': 'SDSS',
                'record': {
                    '$ref': 'http://localhost:5000/api/experiments/3',
                },
            }
        ],
        [
            {
                '0': 3,
                'e': 'SDSS',
            }
        ],
    ],
    [
        'notcurrent_notcurated',
        '''
        <datafield tag="693" ind1=" " ind2=" ">
            <subfield code="e">NOTCURATED</subfield>
        </datafield>
        ''',
        [
            {
                'name': 'NOTCURATED',
                'curated_relation': False,
                'current': False,
            }
        ],
        [
            {
                'e': 'NOTCURATED',
            }
        ],
    ],
    [
        'repeated_experiment',
        '''
        <datafield tag="693" ind1=" " ind2=" ">
            <subfield code="d">2020</subfield>
            <subfield code="e">CERN-ALPHA</subfield>
            <subfield code="0">1</subfield>
            <subfield code="s">2014</subfield>
            <subfield code="z">current</subfield>
        </datafield>
        <datafield tag="693" ind1=" " ind2=" ">
            <subfield code="d">2012</subfield>
            <subfield code="e">CERN-ALPHA</subfield>
            <subfield code="0">1</subfield>
            <subfield code="s">2010</subfield>
        </datafield>
        ''',
        [
            {
                'curated_relation': True,
                'current': True,
                'end_date': '2020',
                'name': 'CERN-ALPHA',
                'record': {
                    '$ref': 'http://localhost:5000/api/experiments/1',
                },
                'start_date': '2014',
            },
            {
                'curated_relation': True,
                'current': False,
                'end_date': '2012',
                'name': 'CERN-ALPHA',
                'record': {
                    '$ref': 'http://localhost:5000/api/experiments/1',
                },
                'start_date': '2010',
            },
        ],
        [
            {
                '0': 1,
                'd': '2020',
                'e': 'CERN-ALPHA',
                's': '2014',
                'z': 'current',
            },
            {
                '0': 1,
                'd': '2012',
                'e': 'CERN-ALPHA',
                's': '2010',
            },
        ],
    ],
    [
        'simultaneous_experiments',
        '''
        <datafield tag="693" ind1=" " ind2=" ">
            <subfield code="d">2013</subfield>
            <subfield code="e">FIRST-SIMULTANEOUS</subfield>
            <subfield code="e">SECOND-SIMULTANEOUS</subfield>
            <subfield code="0">1</subfield>
            <subfield code="0">2</subfield>
            <subfield code="s">2015</subfield>
        </datafield>
        ''',
        [
            {
                'curated_relation': True,
                'current': False,
                'end_date': '2013',
                'name': 'FIRST-SIMULTANEOUS',
                'record': {
                    '$ref': 'http://localhost:5000/api/experiments/1',
                },
                'start_date': '2015',
            },
            {
                'curated_relation': True,
                'current': False,
                'end_date': '2013',
                'name': 'SECOND-SIMULTANEOUS',
                'record': {
                    '$ref': 'http://localhost:5000/api/experiments/2',
                },
                'start_date': '2015',
            },
        ],
        [
            {
                '0': 1,
                'd': '2013',
                'e': 'FIRST-SIMULTANEOUS',
                's': '2015',
            },
            {
                '0': 2,
                'd': '2013',
                'e': 'SECOND-SIMULTANEOUS',
                's': '2015',
            },
        ],
    ],
]


@pytest.mark.parametrize(
    ('test_name', 'xml_snippet', 'expected_json', 'expected_marc'),
    EXPERIMENTS_DATA,
    ids=[test_data[0] for test_data in EXPERIMENTS_DATA],
)
def test_project_membership(test_name, xml_snippet, expected_json, expected_marc):
    schema = load_schema('authors')
    subschema = schema['properties']['project_membership']

    if not xml_snippet.strip().startswith('<record>'):
        xml_snippet = '<record>%s</record>' % xml_snippet

    json_data = hepnames.do(create_record(xml_snippet))
    json_experiments = json_data['project_membership']
    marc_experiments = hepnames2marc.do(json_data)['693']

    assert validate(json_experiments, subschema) is None
    assert marc_experiments == expected_marc
    assert json_experiments == expected_json


def test_ids_from_double_035__a_9():
    schema = load_schema('authors')
    subschema = schema['properties']['ids']

    snippet = (  # record/984519
        '<record>'
        '  <datafield tag="035" ind1=" " ind2=" ">'
        '    <subfield code="a">INSPIRE-00134135</subfield>'
        '    <subfield code="9">INSPIRE</subfield>'
        '  </datafield>'
        '  <datafield tag="035" ind1=" " ind2=" ">'
        '    <subfield code="a">H.Vogel.1</subfield>'
        '    <subfield code="9">BAI</subfield>'
        '  </datafield>'
        '</record>'
    )

    expected = [
        {
            'schema': 'INSPIRE BAI',
            'value': 'H.Vogel.1',
        },
        {
            'schema': 'INSPIRE ID',
            'value': 'INSPIRE-00134135',
        },
    ]
    result = hepnames.do(create_record(snippet))

    assert validate(result['ids'], subschema) is None
    assert expected == result['ids']

    expected = [
        {'a': 'H.Vogel.1', '9': 'BAI'},
        {'a': 'INSPIRE-00134135', '9': 'INSPIRE'},
    ]
    result = hepnames2marc.do(result)

    for el in expected:
        assert el in result['035']
    for el in result['035']:
        assert el in expected


def test_ids_from_035__a_9_with_orcid():
    schema = load_schema('authors')
    subschema = schema['properties']['ids']

    snippet = (
        '<datafield tag="035" ind1=" " ind2=" ">'
        '  <subfield code="9">ORCID</subfield>'
        '  <subfield code="a">0000-0001-6771-2174</subfield>'
        '</datafield>'
    )

    expected = [
        {
            'schema': 'ORCID',
            'value': '0000-0001-6771-2174',
        },
    ]
    result = hepnames.do(create_record(snippet))

    assert validate(result['ids'], subschema) is None
    assert expected == result['ids']

    expected = [
        {
            '9': 'ORCID',
            'a': '0000-0001-6771-2174',
        }
    ]
    result = hepnames2marc.do(result)

    assert expected == result['035']


def test_ids_from_035__a_9_with_cern():
    schema = load_schema('authors')
    subschema = schema['properties']['ids']

    snippet = (  # record/1064570
        '<datafield tag="035" ind1=" " ind2=" ">'
        '  <subfield code="9">CERN</subfield>'
        '  <subfield code="a">CERN-622961</subfield>'
        '</datafield>'
    )

    expected = [
        {
            'schema': 'CERN',
            'value': 'CERN-622961',
        },
    ]
    result = hepnames.do(create_record(snippet))

    assert validate(result['ids'], subschema) is None
    assert expected == result['ids']

    expected = [{'9': 'CERN', 'a': 'CERN-622961'}]
    result = hepnames2marc.do(result)

    assert expected == result['035']


def test_ids_from_035__a_9_with_cern_malformed():
    schema = load_schema('authors')
    subschema = schema['properties']['ids']

    snippet = (
        '<record>'
        '  <datafield tag="035" ind1=" " ind2=" ">'
        '    <subfield code="9">CERN</subfield>'
        '    <subfield code="a">CERN-CERN-645257</subfield>'
        '  </datafield>'  # record/1030771
        '  <datafield tag="035" ind1=" " ind2=" ">'
        '    <subfield code="9">CERN</subfield>'
        '    <subfield code="a">cern-783683</subfield>'
        '  </datafield>'  # record/1408145
        '  <datafield tag="035" ind1=" " ind2=" ">'
        '    <subfield code="9">CERN</subfield>'
        '    <subfield code="a">CERM-724319</subfield>'
        '  </datafield>'  # record/1244430
        '  <datafield tag="035" ind1=" " ind2=" ">'
        '    <subfield code="9">CERN</subfield>'
        '    <subfield code="a">CNER-727986</subfield>'
        '  </datafield>'  # record/1068077
        '  <datafield tag="035" ind1=" " ind2=" ">'
        '    <subfield code="9">CERN</subfield>'
        '    <subfield code="a">CVERN-765559</subfield>'
        '  </datafield>'  # record/1340631
        '</record>'
    )

    expected = [
        {
            'schema': 'CERN',
            'value': 'CERN-765559',
        },
        {
            'schema': 'CERN',
            'value': 'CERN-727986',
        },
        {
            'schema': 'CERN',
            'value': 'CERN-724319',
        },
        {
            'schema': 'CERN',
            'value': 'CERN-783683',
        },
        {
            'schema': 'CERN',
            'value': 'CERN-645257',
        },
    ]
    result = hepnames.do(create_record(snippet))

    assert validate(result['ids'], subschema) is None
    assert expected == result['ids']

    expected = [
        {
            '9': 'CERN',
            'a': 'CERN-765559',
        },
        {
            '9': 'CERN',
            'z': 'CERN-727986',
        },
        {
            '9': 'CERN',
            'z': 'CERN-724319',
        },
        {
            '9': 'CERN',
            'z': 'CERN-783683',
        },
        {
            '9': 'CERN',
            'z': 'CERN-645257',
        },
    ]
    result = hepnames2marc.do(result)

    assert expected == result['035']


def test_ids_from_035__a_9_with_desy():
    schema = load_schema('authors')
    subschema = schema['properties']['ids']

    snippet = (  # record/993224
        '<datafield tag="035" ind1=" " ind2=" ">'
        '  <subfield code="a">DESY-1001805</subfield>'
        '  <subfield code="9">DESY</subfield>'
        '</datafield>'
    )

    expected = [
        {
            'schema': 'DESY',
            'value': 'DESY-1001805',
        },
    ]
    result = hepnames.do(create_record(snippet))

    assert validate(result['ids'], subschema) is None
    assert expected == result['ids']

    expected = [
        {
            '9': 'DESY',
            'a': 'DESY-1001805',
        },
    ]
    result = hepnames2marc.do(result)

    assert expected == result['035']


def test_ids_from_035__a_9_with_wikipedia():
    schema = load_schema('authors')
    subschema = schema['properties']['ids']

    snippet = (  # record/985898
        '<datafield tag="035" ind1=" " ind2=" ">'
        '  <subfield code="9">Wikipedia</subfield>'
        '  <subfield code="a">Guido_Tonelli</subfield>'
        '</datafield>'
    )

    expected = [
        {
            'schema': 'WIKIPEDIA',
            'value': 'Guido_Tonelli',
        },
    ]
    result = hepnames.do(create_record(snippet))

    assert validate(result['ids'], subschema) is None
    assert expected == result['ids']

    expected = [
        {
            '9': 'WIKIPEDIA',
            'a': 'Guido_Tonelli',
        },
    ]
    result = hepnames2marc.do(result)

    assert expected == result['035']


def test_ids_from_035__a_9_with_slac():
    schema = load_schema('authors')
    subschema = schema['properties']['ids']

    snippet = (  # record/1028379
        '<datafield tag="035" ind1=" " ind2=" ">'
        '  <subfield code="9">SLAC</subfield>'
        '  <subfield code="a">SLAC-218626</subfield>'
        '</datafield>'
    )

    expected = [
        {
            'schema': 'SLAC',
            'value': 'SLAC-218626',
        },
    ]
    result = hepnames.do(create_record(snippet))

    assert validate(result['ids'], subschema) is None
    assert expected == result['ids']

    expected = [
        {
            '9': 'SLAC',
            'a': 'SLAC-218626',
        },
    ]
    result = hepnames2marc.do(result)

    assert expected == result['035']


def test_ids_from_035__a_with_bai():
    schema = load_schema('authors')
    subschema = schema['properties']['ids']

    snippet = (  # record/1464894
        '<datafield tag="035" ind1=" " ind2=" ">'
        '  <subfield code="a">Jian.Long.Han.1</subfield>'
        '</datafield>'
    )

    expected = [
        {
            'schema': 'INSPIRE BAI',
            'value': 'Jian.Long.Han.1',
        },
    ]
    result = hepnames.do(create_record(snippet))

    assert validate(result['ids'], subschema) is None
    assert expected == result['ids']

    expected = [
        {
            '9': 'BAI',
            'a': 'Jian.Long.Han.1',
        },
    ]
    result = hepnames2marc.do(result)

    assert expected == result['035']


def test_ids_from_double_035__a_9_with_kaken():
    schema = load_schema('authors')
    subschema = schema['properties']['ids']

    snippet = (  # record/1474271
        '<record>'
        '  <datafield tag="035" ind1=" " ind2=" ">'
        '    <subfield code="9">BAI</subfield>'
        '    <subfield code="a">Toshio.Suzuki.2</subfield>'
        '  </datafield>'
        '  <datafield tag="035" ind1=" " ind2=" ">'
        '    <subfield code="9">KAKEN</subfield>'
        '    <subfield code="a">70139070</subfield>'
        '  </datafield>'
        '</record>'
    )

    expected = [
        {
            'schema': 'KAKEN',
            'value': 'KAKEN-70139070',
        },
        {
            'schema': 'INSPIRE BAI',
            'value': 'Toshio.Suzuki.2',
        },
    ]
    result = hepnames.do(create_record(snippet))

    assert validate(result['ids'], subschema) is None
    assert expected == result['ids']

    expected = [
        {
            '9': 'KAKEN',
            'a': 'KAKEN-70139070',
        },
        {
            '9': 'BAI',
            'a': 'Toshio.Suzuki.2',
        },
    ]
    result = hepnames2marc.do(result)

    assert expected == result['035']


def test_ids_from_035__a_9_with_googlescholar():
    schema = load_schema('authors')
    subschema = schema['properties']['ids']

    snippet = (  # record/1467553
        '<datafield tag="035" ind1=" " ind2=" ">'
        '  <subfield code="9">GoogleScholar</subfield>'
        '  <subfield code="a">Tnl-9KoAAAAJ</subfield>'
        '</datafield>'
    )

    expected = [
        {
            'schema': 'GOOGLESCHOLAR',
            'value': 'Tnl-9KoAAAAJ',
        },
    ]
    result = hepnames.do(create_record(snippet))

    assert validate(result['ids'], subschema) is None
    assert expected == result['ids']

    expected = [
        {
            '9': 'GOOGLESCHOLAR',
            'a': 'Tnl-9KoAAAAJ',
        },
    ]
    result = hepnames2marc.do(result)

    assert expected == result['035']


def test_ids_from_035__a_9_with_viaf():
    schema = load_schema('authors')
    subschema = schema['properties']['ids']

    snippet = (  # record/1008109
        '<datafield tag="035" ind1=" " ind2=" ">'
        '  <subfield code="9">VIAF</subfield>'
        '  <subfield code="a">34517183</subfield>'
        '</datafield>'
    )

    expected = [
        {
            'schema': 'VIAF',
            'value': '34517183',
        },
    ]
    result = hepnames.do(create_record(snippet))

    assert validate(result['ids'], subschema) is None
    assert expected == result['ids']

    expected = [
        {
            '9': 'VIAF',
            'a': '34517183',
        },
    ]
    result = hepnames2marc.do(result)

    assert expected == result['035']


def test_ids_from_035__a_9_with_researcherid():
    schema = load_schema('authors')
    subschema = schema['properties']['ids']

    snippet = (  # record/1051026
        '<datafield tag="035" ind1=" " ind2=" ">'
        '  <subfield code="9">RESEARCHERID</subfield>'
        '  <subfield code="a">B-4717-2008</subfield>'
        '</datafield>'
    )

    expected = [
        {
            'schema': 'RESEARCHERID',
            'value': 'B-4717-2008',
        },
    ]
    result = hepnames.do(create_record(snippet))

    assert validate(result['ids'], subschema) is None
    assert expected == result['ids']

    expected = [
        {
            '9': 'RESEARCHERID',
            'a': 'B-4717-2008',
        },
    ]
    result = hepnames2marc.do(result)

    assert expected == result['035']


def test_ids_from_035__a_9_with_scopus():
    schema = load_schema('authors')
    subschema = schema['properties']['ids']

    snippet = (  # record/1017182
        '<datafield tag="035" ind1=" " ind2=" ">'
        '  <subfield code="9">SCOPUS</subfield>'
        '  <subfield code="a">7103280792</subfield>'
        '</datafield>'
    )

    expected = [
        {
            'schema': 'SCOPUS',
            'value': '7103280792',
        },
    ]
    result = hepnames.do(create_record(snippet))

    assert validate(result['ids'], subschema) is None
    assert expected == result['ids']

    expected = [
        {
            '9': 'SCOPUS',
            'a': '7103280792',
        },
    ]
    result = hepnames2marc.do(result)

    assert expected == result['035']


def test_ids_from_035__9():
    snippet = (
        # record/edit/?ln=en#state=edit&recid=1474355&recrev=20160707223728
        '<record>'
        '  <datafield tag="035" ind1=" " ind2=" ">'
        '    <subfield code="9">INSPIRE</subfield>'
        '  </datafield>'
        '  <datafield tag="035" ind1=" " ind2=" ">'
        '    <subfield code="9">CERN</subfield>'
        '  </datafield>'  # record/1364570
        '  <datafield tag="035" ind1=" " ind2=" ">'
        '    <subfield code="9">KAKEN</subfield>'
        '  </datafield>'  # record/1480252
        '</record>'
    )

    result = hepnames.do(create_record(snippet))

    assert 'ids' not in result


def test_ids_from_035__a_z_same_field_9():
    schema = load_schema('authors')
    subschema = schema['properties']['ids']

    snippet = (  # record/1709705
        '<record>'
        '  <datafield tag="035" ind1=" " ind2=" ">'
        '    <subfield code="9">INSPIRE</subfield>'
        '    <subfield code="a">INSPIRE-00791106</subfield>'
        '    <subfield code="z">INSPIRE-00739854</subfield>'
        '  </datafield>'
        '  <datafield tag="035" ind1=" " ind2=" ">'
        '    <subfield code="9">ORCID</subfield>'
        '    <subfield code="a">0000-0001-8415-6720</subfield>'
        '  </datafield>'
        '  <datafield tag="035" ind1=" " ind2=" ">'
        '    <subfield code="9">BAI</subfield>'
        '    <subfield code="a">Yen.Chen.Pan.1</subfield>'
        '  </datafield>'
        '</record>'
    )

    expected = [
        {
            'schema': 'INSPIRE BAI',
            'value': 'Yen.Chen.Pan.1',
        },
        {
            'schema': 'ORCID',
            'value': '0000-0001-8415-6720',
        },
        {
            'schema': 'INSPIRE ID',
            'value': 'INSPIRE-00791106',
        },
        {
            'schema': 'INSPIRE ID',
            'value': 'INSPIRE-00739854',
        },
    ]
    result = hepnames.do(create_record(snippet))

    assert validate(result['ids'], subschema) is None
    assert expected == result['ids']

    expected = [
        {
            '9': 'BAI',
            'a': 'Yen.Chen.Pan.1',
        },
        {
            '9': 'ORCID',
            'a': '0000-0001-8415-6720',
        },
        {
            '9': 'INSPIRE',
            'a': 'INSPIRE-00791106',
        },
        {
            '9': 'INSPIRE',
            'z': 'INSPIRE-00739854',
        },
    ]
    result = hepnames2marc.do(result)

    assert expected == result['035']


def test_ids_from_035__a_z_different_fields_9():
    schema = load_schema('authors')
    subschema = schema['properties']['ids']

    snippet = (  # record/1357501
        '<record>'
        '  <controlfield tag="001">1357501</controlfield>'
        '  <datafield tag="035" ind1=" " ind2=" ">'
        '    <subfield code="9">INSPIRE</subfield>'
        '    <subfield code="a">INSPIRE-00513748</subfield>'
        '  </datafield>'
        '  <datafield tag="035" ind1=" " ind2=" ">'
        '    <subfield code="9">BAI</subfield>'
        '    <subfield code="a">Lei.Wu.1</subfield>'
        '  </datafield>'
        '  <datafield tag="035" ind1=" " ind2=" ">'
        '    <subfield code="9">ORCID</subfield>'
        '    <subfield code="z">0000-0002-5310-8213</subfield>'
        '  </datafield>'
        '  <datafield tag="035" ind1=" " ind2=" ">'
        '    <subfield code="9">ORCID</subfield>'
        '    <subfield code="a">0000-0001-5010-7517</subfield>'
        '  </datafield>'
        '</record>'
    )

    expected = [
        {
            'schema': 'ORCID',
            'value': '0000-0001-5010-7517',
        },
        {
            'schema': 'INSPIRE BAI',
            'value': 'Lei.Wu.1',
        },
        {
            'schema': 'INSPIRE ID',
            'value': 'INSPIRE-00513748',
        },
        {
            'schema': 'ORCID',
            'value': '0000-0002-5310-8213',
        },
    ]
    result = hepnames.do(create_record(snippet))

    assert validate(result['ids'], subschema) is None
    assert expected == result['ids']

    expected = [
        {
            '9': 'ORCID',
            'a': '0000-0001-5010-7517',
        },
        {
            '9': 'BAI',
            'a': 'Lei.Wu.1',
        },
        {
            '9': 'INSPIRE',
            'a': 'INSPIRE-00513748',
        },
        {
            '9': 'ORCID',
            'z': '0000-0002-5310-8213',
        },
    ]
    result = hepnames2marc.do(result)

    assert expected == result['035']


def test_name_from_100__a_g_q():
    schema = load_schema('authors')
    subschema = schema['properties']['name']

    snippet = (  # record/1019100
        '<datafield tag="100" ind1=" " ind2=" ">'
        '  <subfield code="a">Abarbanel, Henry D.I.</subfield>'
        '  <subfield code="q">Henry D.I. Abarbanel</subfield>'
        '  <subfield code="g">ACTIVE</subfield>'
        '</datafield>'
    )

    expected = {
        'value': 'Abarbanel, Henry D.I.',
        'preferred_name': 'Henry D.I. Abarbanel',
    }
    result = hepnames.do(create_record(snippet))

    assert validate(result['name'], subschema) is None
    assert expected == result['name']

    expected = {
        'a': 'Abarbanel, Henry D.I.',
        'q': 'Henry D.I. Abarbanel',
        'g': 'active',
    }
    result = hepnames2marc.do(result)

    assert expected == result['100']


def test_name_from_100__g_q_populates_value_from_preferred_name():
    schema = load_schema('authors')
    subschema = schema['properties']['name']

    snippet = (  # record/1259075
        '<datafield tag="100" ind1=" " ind2=" ">'
        '  <subfield code="g">ACTIVE</subfield>'
        '  <subfield code="q">Vyacheslav I. Yukalova</subfield>'
        '</datafield>'
    )

    expected = {
        'preferred_name': 'Vyacheslav I. Yukalova',
        'value': 'Yukalova, Vyacheslav I.',
    }
    result = hepnames.do(create_record(snippet))

    assert validate(result['name'], subschema) is None
    assert expected == result['name']

    expected = {
        'a': 'Yukalova, Vyacheslav I.',
        'g': 'active',
        'q': 'Vyacheslav I. Yukalova',
    }
    result = hepnames2marc.do(result)

    assert expected == result['100']


def test_title_from_100__a_c_q_discards_default_title():
    schema = load_schema('authors')
    subschema = schema['properties']['name']

    snippet = (  # record/1270441
        '<datafield tag="100" ind1=" " ind2=" ">'
        '  <subfield code="a">Joosten, Sylvester Johannes</subfield>'
        '  <subfield code="c">title (e.g. Sir)</subfield>'
        '  <subfield code="q">Sylvester Johannes Joosten</subfield>'
        '</datafield>'
    )

    expected = {
        'preferred_name': 'Sylvester Johannes Joosten',
        'value': 'Joosten, Sylvester Johannes',
    }
    result = hepnames.do(create_record(snippet))

    assert validate(result['name'], subschema) is None
    assert expected == result['name']

    expected = {
        'a': 'Joosten, Sylvester Johannes',
        'q': 'Sylvester Johannes Joosten',
    }
    result = hepnames2marc.do(result)

    assert expected == result['100']


def test_status_from_100__a_g_q():
    schema = load_schema('authors')
    subschema = schema['properties']['status']

    snippet = (  # record/1019100
        '<datafield tag="100" ind1=" " ind2=" ">'
        '  <subfield code="a">Abarbanel, Henry D.I.</subfield>'
        '  <subfield code="q">Henry D.I. Abarbanel</subfield>'
        '  <subfield code="g">ACTIVE</subfield>'
        '</datafield>'
    )

    expected = 'active'
    result = hepnames.do(create_record(snippet))

    assert validate(result['status'], subschema) is None
    assert expected == result['status']

    expected = {
        'a': 'Abarbanel, Henry D.I.',
        'q': 'Henry D.I. Abarbanel',
        'g': 'active',
    }
    result = hepnames2marc.do(result)

    assert expected == result['100']


def test_birth_date_death_date_from_100__a_d_g_q():
    schema = load_schema('authors')
    subschema_birth = schema['properties']['birth_date']
    subschema_death = schema['properties']['death_date']

    snippet = (  # record/1017374
        '<datafield tag="100" ind1=" " ind2=" ">'
        '  <subfield code="a">Bardeen, John</subfield>'
        '  <subfield code="d">1908-05-23 - 1991-01-30</subfield>'
        '  <subfield code="g">DECEASED</subfield>'
        '  <subfield code="q">John Bardeen</subfield>'
        '</datafield>'
    )

    expected_birth = '1908-05-23'
    expected_death = '1991-01-30'
    result = hepnames.do(create_record(snippet))

    assert validate(result['birth_date'], subschema_birth) is None
    assert validate(result['death_date'], subschema_death) is None
    assert expected_birth == result['birth_date']
    assert expected_death == result['death_date']

    expected = {
        'a': 'Bardeen, John',
        'd': '1908-05-23 - 1991-01-30',
        'g': 'deceased',
        'q': 'John Bardeen',
    }
    result = hepnames2marc.do(result)

    assert expected == result['100']


def test_birth_date_death_date_from_100__a_d_g_q_only_years():
    schema = load_schema('authors')
    subschema_birth = schema['properties']['birth_date']
    subschema_death = schema['properties']['death_date']

    snippet = (  # record/983266
        '<datafield tag="100" ind1=" " ind2=" ">'
        '  <subfield code="a">Wolfenstein, Lincoln</subfield>'
        '  <subfield code="d">1923-2015</subfield>'
        '  <subfield code="g">DECEASED</subfield>'
        '  <subfield code="q">Lincoln Wolfenstein</subfield>'
        '</datafield>'
    )

    expected_birth = '1923'
    expected_death = '2015'
    result = hepnames.do(create_record(snippet))

    assert validate(result['birth_date'], subschema_birth) is None
    assert validate(result['death_date'], subschema_death) is None
    assert expected_birth == result['birth_date']
    assert expected_death == result['death_date']

    expected = {
        'a': 'Wolfenstein, Lincoln',
        'd': '1923 - 2015',
        'g': 'deceased',
        'q': 'Lincoln Wolfenstein',
    }
    result = hepnames2marc.do(result)

    assert expected == result['100']


def test_death_date_from_100__a_d_g_q():
    schema = load_schema('authors')
    subschema = schema['properties']['death_date']

    snippet = (  # record/1046337
        '<datafield tag="100" ind1=" " ind2=" ">'
        '  <subfield code="a">Blosser, Henry G.</subfield>'
        '  <subfield code="d">-2013-03-20</subfield>'
        '  <subfield code="g">DECEASED</subfield>'
        '  <subfield code="q">Henry G. Blosser</subfield>'
        '</datafield>'
    )

    expected = '2013-03-20'
    result = hepnames.do(create_record(snippet))

    assert validate(result['death_date'], subschema) is None
    assert expected == result['death_date']

    expected = {
        'a': 'Blosser, Henry G.',
        'd': '2013-03-20',
        'g': 'deceased',
        'q': 'Henry G. Blosser',
    }
    result = hepnames2marc.do(result)

    assert expected == result['100']


def test_name_variants_from_400__triple_a():
    schema = load_schema('authors')
    subschema = schema['properties']['name']['properties']['name_variants']

    snippet = (  # record/1292399
        '<datafield tag="400" ind1=" " ind2=" ">'
        '  <subfield code="a">Yosef Cohen, Hadar</subfield>'
        '  <subfield code="a">Josef Cohen, Hadar</subfield>'
        '  <subfield code="a">Cohen, Hadar Josef</subfield>'
        '</datafield>'
    )

    expected = {
        'name_variants': [
            'Yosef Cohen, Hadar',
            'Josef Cohen, Hadar',
            'Cohen, Hadar Josef',
        ]
    }
    result = hepnames.do(create_record(snippet))

    assert validate(result['name']['name_variants'], subschema) is None
    assert expected == result['name']

    expected = [
        {'a': 'Yosef Cohen, Hadar'},
        {'a': 'Josef Cohen, Hadar'},
        {'a': 'Cohen, Hadar Josef'},
    ]
    result = hepnames2marc.do(result)

    assert expected == result['400']


def test_advisors_from_701__a_g_i():
    schema = load_schema('authors')
    subschema = schema['properties']['advisors']

    snippet = (  # record/1474091
        '<datafield tag="701" ind1=" " ind2=" ">'
        '  <subfield code="a">Rivelles, Victor O.</subfield>'
        '  <subfield code="g">PhD</subfield>'
        '  <subfield code="i">INSPIRE-00120420</subfield>'
        '  <subfield code="x">991627</subfield>'
        '  <subfield code="y">1</subfield>'
        '</datafield>'
    )

    expected = [
        {
            'name': 'Rivelles, Victor O.',
            'degree_type': 'phd',
            'ids': [{'schema': 'INSPIRE ID', 'value': 'INSPIRE-00120420'}],
            'record': {
                '$ref': 'http://localhost:5000/api/authors/991627',
            },
            'curated_relation': True,
        },
    ]
    result = hepnames.do(create_record(snippet))

    assert validate(result['advisors'], subschema) is None
    assert expected == result['advisors']

    expected = [
        {
            'a': 'Rivelles, Victor O.',
            'g': 'phd',
            'i': ['INSPIRE-00120420'],
        },
    ]
    result = hepnames2marc.do(result)

    assert expected == result['701']


def test_advisors_from_701__a_g_i_h():
    schema = load_schema('authors')
    subschema = schema['properties']['advisors']

    snippet = (  # synthetic data
        '<datafield tag="701" ind1=" " ind2=" ">'
        '  <subfield code="a">Rivelles, Victor O.</subfield>'
        '  <subfield code="g">PhD</subfield>'
        '  <subfield code="i">INSPIRE-00120420</subfield>'
        '  <subfield code="x">991627</subfield>'
        '  <subfield code="y">1</subfield>'
        '  <subfield code="h">HIDDEN</subfield>'
        '</datafield>'
    )

    expected = [
        {
            'name': 'Rivelles, Victor O.',
            'degree_type': 'phd',
            'ids': [{'schema': 'INSPIRE ID', 'value': 'INSPIRE-00120420'}],
            'record': {
                '$ref': 'http://localhost:5000/api/authors/991627',
            },
            'curated_relation': True,
            'hidden': True,
        },
    ]
    result = hepnames.do(create_record(snippet))

    assert validate(result['advisors'], subschema) is None
    assert expected == result['advisors']

    expected = [
        {
            'a': 'Rivelles, Victor O.',
            'g': 'phd',
            'i': ['INSPIRE-00120420'],
            'h': 'HIDDEN',
        },
    ]
    result = hepnames2marc.do(result)

    assert expected == result['701']


def test_advisors_from_701__a_g_i_orcid():
    schema = load_schema('authors')
    subschema = schema['properties']['advisors']

    snippet = (  # record/1413663
        '<datafield tag="701" ind1=" " ind2=" ">'
        '  <subfield code="a">Riccioni, Fabio</subfield>'
        '  <subfield code="g">PhD</subfield>'
        '  <subfield code="i">0000-0003-4702-3632</subfield>'
        '</datafield>'
    )

    expected = [
        {
            'name': 'Riccioni, Fabio',
            'degree_type': 'phd',
            'ids': [{'schema': 'ORCID', 'value': '0000-0003-4702-3632'}],
        },
    ]
    result = hepnames.do(create_record(snippet))

    assert validate(result['advisors'], subschema) is None
    assert expected == result['advisors']

    expected = [
        {
            'a': 'Riccioni, Fabio',
            'g': 'phd',
            'i': ['0000-0003-4702-3632'],
        },
    ]
    result = hepnames2marc.do(result)

    assert expected == result['701']


def test_email_addresses_from_371__a_m_z():
    schema = load_schema('authors')
    subschema = schema['properties']['email_addresses']

    snippet = (  # record/1222902
        '<datafield tag="371" ind1=" " ind2=" ">'
        '  <subfield code="a">Siegen U.</subfield>'
        '  <subfield code="m">test@hep.physik.uni-siegen.de</subfield>'
        '  <subfield code="z">current</subfield>'
        '</datafield>'
    )

    expected = [{'current': True, 'value': 'test@hep.physik.uni-siegen.de'}]
    result = hepnames.do(create_record(snippet))

    assert validate(result['email_addresses'], subschema) is None
    assert expected == result['email_addresses']

    expected = [
        {"a": "Siegen U.", "z": "Current"},
        {
            "m": "test@hep.physik.uni-siegen.de",
        },
    ]

    result = hepnames2marc.do(result)

    assert sorted(expected, key=str) == sorted(result['371'], key=str)


def test_email_addresses_from_371__a_repeated_m_z():
    schema = load_schema('authors')
    subschema = schema['properties']['email_addresses']

    snippet = (  # record/1019084
        '<datafield tag="371" ind1=" " ind2=" ">'
        '  <subfield code="a">Sao Paulo U.</subfield>'
        '  <subfield code="m">test@usp.br</subfield>'
        '  <subfield code="m">test@fma.if.usp.br</subfield>'
        '  <subfield code="z">Current</subfield>'
        '</datafield>'
    )

    expected = [
        {'current': True, 'value': 'test@usp.br'},
        {'current': True, 'value': 'test@fma.if.usp.br'},
    ]
    result = hepnames.do(create_record(snippet))

    assert validate(result['email_addresses'], subschema) is None
    assert expected == result['email_addresses']

    expected = [
        {"a": "Sao Paulo U.", "z": "Current"},
        {
            "m": "test@usp.br",
        },
        {
            "m": "test@fma.if.usp.br",
        },
    ]

    result = hepnames2marc.do(result)

    assert sorted(expected, key=str) == sorted(result['371'], key=str)


def test_email_addresses_from_371__a_o_r_s_t():
    schema = load_schema('authors')
    subschema = schema['properties']['email_addresses']

    snippet = (  # record/1060782
        '<datafield tag="371" ind1=" " ind2=" ">'
        '   <subfield code="a">IMSc, Chennai</subfield>'
        '   <subfield code="o">test@imsc.res.in</subfield>'
        '   <subfield code="r">PD</subfield>'
        '   <subfield code="s">2012</subfield>'
        '   <subfield code="t">2013</subfield>'
        '</datafield>'
    )

    expected = [{'current': False, 'value': 'test@imsc.res.in'}]
    result = hepnames.do(create_record(snippet))

    assert validate(result['email_addresses'], subschema) is None
    assert expected == result['email_addresses']

    expected = [
        {"a": "IMSc, Chennai", "s": "2012", "r": "PD", "t": "2013"},
        {
            "o": "test@imsc.res.in",
        },
    ]

    result = hepnames2marc.do(result)

    assert sorted(expected, key=str) == sorted(result['371'], key=str)


def test_email_addresses_from_595__m():
    schema = load_schema('authors')
    subschema = schema['properties']['email_addresses']

    snippet = (  # record/1021896
        '<datafield tag="595" ind1=" " ind2=" ">'
        '   <subfield code="m">test@pnnl.gov</subfield>'
        '</datafield>'
    )

    expected = [{'current': True, 'hidden': True, 'value': 'test@pnnl.gov'}]
    result = hepnames.do(create_record(snippet))

    assert validate(result['email_addresses'], subschema) is None
    assert expected == result['email_addresses']

    expected = [
        {
            "m": "test@pnnl.gov",
        }
    ]

    result = hepnames2marc.do(result)

    assert expected == result['595']


def test_email_addresses_from_595__o():
    schema = load_schema('authors')
    subschema = schema['properties']['email_addresses']

    snippet = (  # record/1021896
        '<datafield tag="595" ind1=" " ind2=" ">'
        '   <subfield code="o">test@pnl.gov</subfield>'
        '</datafield>'
    )

    expected = [{'current': False, 'hidden': True, 'value': 'test@pnl.gov'}]
    result = hepnames.do(create_record(snippet))

    assert validate(result['email_addresses'], subschema) is None
    assert expected == result['email_addresses']

    expected = [
        {
            "o": "test@pnl.gov",
        }
    ]

    result = hepnames2marc.do(result)

    assert expected == result['595']


def test_positions_from_371__a():
    schema = load_schema('authors')
    subschema = schema['properties']['positions']

    snippet = (  # record/997958
        '<datafield tag="371" ind1=" " ind2=" ">'
        '  <subfield code="a">Aachen, Tech. Hochsch.</subfield>'
        '</datafield>'
    )

    expected = [
        {
            'institution': 'Aachen, Tech. Hochsch.',
        },
    ]
    result = hepnames.do(create_record(snippet))

    assert validate(result['positions'], subschema) is None
    assert expected == result['positions']

    expected = [{'a': 'Aachen, Tech. Hochsch.'}]
    result = hepnames2marc.do(result)

    assert expected == result['371']


def test_positions_from_371__a_z():
    schema = load_schema('authors')
    subschema = schema['properties']['positions']

    snippet = (  # record/1408378
        '<datafield tag="371" ind1=" " ind2=" ">'
        '  <subfield code="a">Argonne</subfield>'
        '  <subfield code="z">current</subfield>'
        '</datafield>'
    )

    expected = [
        {
            'current': True,
            'institution': 'Argonne',
        }
    ]
    result = hepnames.do(create_record(snippet))

    assert validate(result['positions'], subschema) is None
    assert expected == result['positions']

    expected = [{'a': 'Argonne', 'z': 'Current'}]

    result = hepnames2marc.do(result)

    assert expected == result['371']


def test_positions_from_371__a_r_z():
    schema = load_schema('authors')
    subschema = schema['properties']['positions']

    snippet = (  # record/997958
        '<datafield tag="371" ind1=" " ind2=" ">'
        '  <subfield code="a">Antwerp U.</subfield>'
        '  <subfield code="r">SENIOR</subfield>'
        '  <subfield code="z">Current</subfield>'
        '</datafield>'
    )

    expected = [
        {
            'current': True,
            'institution': 'Antwerp U.',
            'rank': 'SENIOR',
        },
    ]
    result = hepnames.do(create_record(snippet))

    assert validate(result['positions'], subschema) is None
    assert expected == result['positions']

    expected = [{'a': 'Antwerp U.', 'r': 'SENIOR', 'z': 'Current'}]
    result = hepnames2marc.do(result)

    assert expected == result['371']


def test_positions_from_371__a_r_z_h():
    schema = load_schema('authors')
    subschema = schema['properties']['positions']

    snippet = (  # synthetic data
        '<datafield tag="371" ind1=" " ind2=" ">'
        '  <subfield code="a">Antwerp U.</subfield>'
        '  <subfield code="r">SENIOR</subfield>'
        '  <subfield code="z">Current</subfield>'
        '  <subfield code="h">HIDDEN</subfield>'
        '</datafield>'
    )

    expected = [
        {
            'current': True,
            'institution': 'Antwerp U.',
            'rank': 'SENIOR',
            'hidden': True,
        },
    ]
    result = hepnames.do(create_record(snippet))

    assert validate(result['positions'], subschema) is None
    assert expected == result['positions']

    expected = [
        {
            'a': 'Antwerp U.',
            'r': 'SENIOR',
            'z': 'Current',
            'h': 'HIDDEN',
        }
    ]
    result = hepnames2marc.do(result)

    assert expected == result['371']


def test_positions_from_371__a_r_t_z():
    schema = load_schema('authors')
    subschema = schema['properties']['positions']

    snippet = (  # record/1037568
        '<datafield tag="371" ind1=" " ind2=" ">'
        '  <subfield code="a">San Luis Potosi U.</subfield>'
        '  <subfield code="r">Master</subfield>'
        '  <subfield code="t">2007</subfield>'
        '  <subfield code="z">903830</subfield>'
        '</datafield>'
    )

    expected = [
        {
            'end_date': '2007',
            'institution': 'San Luis Potosi U.',
            'rank': 'MASTER',
            'record': {'$ref': 'http://localhost:5000/api/institutions/903830'},
            'curated_relation': True,
        },
    ]
    result = hepnames.do(create_record(snippet))

    assert validate(result['positions'], subschema) is None
    assert expected == result['positions']

    expected = [
        {
            'a': 'San Luis Potosi U.',
            'r': 'MAS',
            't': '2007',
        },
    ]
    result = hepnames2marc.do(result)

    assert expected == result['371']


def test_positions_from_371__r_t():
    snippet = (  # record/1038489
        '<datafield tag="371" ind1=" " ind2=" ">'
        '  <subfield code="r">UG</subfield>'
        '  <subfield code="t">1970</subfield>'
        '</datafield>'
    )

    result = hepnames.do(create_record(snippet))

    assert 'positions' not in result


def test_positions_from_371__a_r_t():
    schema = load_schema('authors')
    subschema = schema['properties']['positions']

    snippet = (  # record/1590188
        '<datafield tag="371" ind1=" " ind2=" ">'
        '  <subfield code="a">Case Western Reserve U.</subfield>'
        '  <subfield code="r">UNDERGRADUATE</subfield>'
        '  <subfield code="t">2011</subfield>'
        '</datafield>'
    )

    expected = [
        {
            'end_date': '2011',
            'institution': 'Case Western Reserve U.',
            'rank': 'UNDERGRADUATE',
        },
    ]
    result = hepnames.do(create_record(snippet))

    assert validate(result['positions'], subschema) is None
    assert expected == result['positions']

    expected = [
        {
            'a': 'Case Western Reserve U.',
            'r': 'UG',
            't': '2011',
        },
    ]
    result = hepnames2marc.do(result)

    assert expected == result['371']


def test_arxiv_categories_from_65017a_2():
    schema = load_schema('authors')
    subschema = schema['properties']['arxiv_categories']

    snippet = (  # record/1010819
        '<datafield tag="650" ind1="1" ind2="7">'
        '  <subfield code="2">INSPIRE</subfield>'
        '  <subfield code="a">HEP-TH</subfield>'
        '</datafield>'
    )

    expected = [
        'hep-th',
    ]
    result = hepnames.do(create_record(snippet))

    assert validate(result['arxiv_categories'], subschema) is None
    assert expected == result['arxiv_categories']

    expected = [
        {
            '2': 'arXiv',
            'a': 'hep-th',
        },
    ]
    result = hepnames2marc.do(result)

    assert expected == result['65017']


def test_arxiv_categories_from_65017a_2_obsolete_category():
    schema = load_schema('authors')
    subschema = schema['properties']['arxiv_categories']

    snippet = (  # record/1010819
        '<datafield tag="650" ind1="1" ind2="7">'
        '  <subfield code="2">INSPIRE</subfield>'
        '  <subfield code="a">ATOM-PH</subfield>'
        '</datafield>'
    )

    expected = [
        'physics.atom-ph',
    ]
    result = hepnames.do(create_record(snippet))

    assert validate(result['arxiv_categories'], subschema) is None
    assert expected == result['arxiv_categories']

    expected = [
        {
            '2': 'arXiv',
            'a': 'physics.atom-ph',
        },
    ]
    result = hepnames2marc.do(result)

    assert expected == result['65017']


def test_inspire_categories_from_65017a_2():
    schema = load_schema('authors')
    subschema = schema['properties']['inspire_categories']

    snippet = (  # record/1271076
        '<datafield tag="650" ind1="1" ind2="7">'
        '  <subfield code="2">INSPIRE</subfield>'
        '  <subfield code="a">Computing</subfield>'
        '</datafield>'
    )

    expected = [
        {'term': 'Computing'},
    ]
    result = hepnames.do(create_record(snippet))

    assert validate(result['inspire_categories'], subschema) is None
    assert expected == result['inspire_categories']

    expected = [
        {
            '2': 'INSPIRE',
            'a': 'Computing',
        },
    ]
    result = hepnames2marc.do(result)

    assert expected == result['65017']


def test_inspire_categories_from_65017a_2_E():
    schema = load_schema('authors')
    subschema = schema['properties']['inspire_categories']

    snippet = (  # record/1019112
        '<datafield tag="650" ind1="1" ind2="7">'
        '  <subfield code="2">INSPIRE</subfield>'
        '  <subfield code="a">E</subfield>'
        '</datafield>'
    )

    expected = [
        {'term': 'Experiment-HEP'},
    ]
    result = hepnames.do(create_record(snippet))

    assert validate(result['inspire_categories'], subschema) is None
    assert expected == result['inspire_categories']

    expected = [
        {
            '2': 'INSPIRE',
            'a': 'Experiment-HEP',
        },
    ]
    result = hepnames2marc.do(result)

    assert expected == result['65017']


def test_public_notes_from_667__a():
    schema = load_schema('authors')
    subschema = schema['properties']['public_notes']

    snippet = (  # record/1018999
        '<datafield tag="667" ind1=" " ind2=" ">  <subfield code="a">Do not'
        ' confuse with Acharya, Bannanje Sripath</subfield></datafield>'
    )

    expected = [{'value': 'Do not confuse with Acharya, Bannanje Sripath'}]
    result = hepnames.do(create_record(snippet))

    assert validate(result['public_notes'], subschema) is None
    assert expected == result['public_notes']

    expected = [
        {'a': 'Do not confuse with Acharya, Bannanje Sripath'},
    ]

    result = hepnames2marc.do(result)

    assert expected == result['667']


def test_previous_names_from_667__a():
    snippet = (  # record/1281982
        '<datafield tag="667" ind1=" " ind2=" ">'
        '  <subfield code="a">Formerly Tomoko Furukawa</subfield>'
        '</datafield>'
    )

    expected = ['Tomoko Furukawa']

    result = hepnames.do(create_record(snippet))

    assert expected == result['name']['previous_names']


def test_previous_names_to_667__a():
    schema = load_schema('authors')
    subschema = schema['properties']['name']

    expected = [
        {'a': 'Formerly Tomoko Furukawa'},
        {'a': 'Formerly Second previous name'},
    ]
    # record/1281982

    metadata = {
        'name': {
            'value': 'Tomoko Ariga',
            'previous_names': [
                'Tomoko Furukawa',
                'Second previous name',
            ],
        }
    }
    assert validate(metadata['name'], subschema) is None

    result = hepnames2marc.do(metadata)

    assert expected == result['667']


def test_awards_from_678__a():
    schema = load_schema('authors')
    subschema = schema['properties']['awards']

    snippet = (  # record/1050484
        '<datafield tag="678" ind1=" " ind2=" ">'
        '   <subfield code="a">Nobel Prize Physics 2003</subfield>'
        ' </datafield>'
    )

    expected = [
        {
            'name': 'Nobel Prize Physics',
            'year': 2003,
        }
    ]
    result = hepnames.do(create_record(snippet))

    assert validate(result['awards'], subschema) is None
    assert expected == result['awards']

    expected = [
        {
            'a': 'Nobel Prize Physics 2003',
        }
    ]
    result = hepnames2marc.do(result)

    assert expected == result['678']


def test_private_notes_from_595__a_9():
    schema = load_schema('authors')
    subschema = schema['properties']['_private_notes']

    snippet = (  # record/1050484
        '<datafield tag="595" ind1=" " ind2=" ">'
        '  <subfield code="a">Author prefers Alexandrov, A.S.</subfield>'
        '  <subfield code="9">SPIRES-HIDDEN</subfield>'
        '</datafield>'
    )

    expected = [
        {
            'source': 'SPIRES-HIDDEN',
            'value': 'Author prefers Alexandrov, A.S.',
        }
    ]
    result = hepnames.do(create_record(snippet))

    assert validate(result['_private_notes'], subschema) is None
    assert expected == result['_private_notes']

    expected = [
        {
            '9': 'SPIRES-HIDDEN',
            'a': 'Author prefers Alexandrov, A.S.',
        }
    ]
    result = hepnames2marc.do(result)

    assert expected == result['595']


def test_private_notes_from_595__double_a():
    schema = load_schema('authors')
    subschema = schema['properties']['_private_notes']

    snippet = (  # record/1279232
        '<datafield tag="595" ind1=" " ind2=" ">  <subfield code="a">"I want to'
        ' hide my personal information on REDACTED" 7/2017</subfield> '
        ' <subfield code="a">REDACTED</subfield></datafield>'
    )

    expected = [
        {'value': '"I want to hide my personal information on REDACTED" 7/2017'},
        {'value': 'REDACTED'},
    ]
    result = hepnames.do(create_record(snippet))

    assert validate(result['_private_notes'], subschema) is None
    assert expected == result['_private_notes']

    expected = [
        {'a': '"I want to hide my personal information on REDACTED" 7/2017'},
        {'a': 'REDACTED'},
    ]
    result = hepnames2marc.do(result)

    assert expected == result['595']


def test_urls_from_8564_u_and_8564_g_u_y():
    schema = load_schema('authors')
    subschema = schema['properties']['urls']

    snippet = (  # record/1073331
        '<record>  <datafield tag="856" ind1="4" ind2=" ">    <subfield'
        ' code="u">http://www.haydenplanetarium.org/tyson/</subfield> '
        ' </datafield>  <datafield tag="856" ind1="4" ind2=" ">    <subfield'
        ' code="g">active</subfield>    <subfield'
        ' code="u">https://twitter.com/neiltyson</subfield>    <subfield'
        ' code="y">TWITTER</subfield>  </datafield></record>'
    )

    expected = [
        {'value': 'http://www.haydenplanetarium.org/tyson/'},
    ]
    result = hepnames.do(create_record(snippet))

    assert validate(result['urls'], subschema) is None
    assert expected == result['urls']

    expected = [
        {'u': 'http://www.haydenplanetarium.org/tyson/'},
        {
            'u': 'https://twitter.com/neiltyson',
            'y': 'TWITTER',
        },
    ]
    result = hepnames2marc.do(result)

    assert sorted(expected, key=str) == sorted(result['8564'], key=str)


def test_ids_from_8564_g_u_y_twitter():
    schema = load_schema('authors')
    subschema = schema['properties']['ids']

    snippet = (  # record/1073331
        '<record>  <datafield tag="856" ind1="4" ind2=" ">    <subfield'
        ' code="u">http://www.haydenplanetarium.org/tyson/</subfield> '
        ' </datafield>  <datafield tag="856" ind1="4" ind2=" ">    <subfield'
        ' code="g">active</subfield>    <subfield'
        ' code="u">https://twitter.com/neiltyson</subfield>    <subfield'
        ' code="y">TWITTER</subfield>  </datafield></record>'
    )

    expected = [
        {'schema': 'TWITTER', 'value': 'neiltyson'},
    ]
    result = hepnames.do(create_record(snippet))

    assert validate(result['ids'], subschema) is None
    assert expected == result['ids']

    expected = [
        {'u': 'http://www.haydenplanetarium.org/tyson/'},
        {
            'u': 'https://twitter.com/neiltyson',
            'y': 'TWITTER',
        },
    ]
    result = hepnames2marc.do(result)

    assert sorted(expected, key=str) == sorted(result['8564'], key=str)


def test_ids_from_8564_u_wikipedia():
    schema = load_schema('authors')
    subschema = schema['properties']['ids']

    snippet = (  # record/1018793
        '<datafield tag="856" ind1="4" ind2=" ">'
        '  <subfield'
        ' code="u">https://en.wikipedia.org/wiki/Torsten_%C3%85kesson</subfield>'
        '</datafield>'
    )

    expected = [
        {'schema': 'WIKIPEDIA', 'value': u'Torsten_Åkesson'},
    ]
    result = hepnames.do(create_record(snippet))

    assert validate(result['ids'], subschema) is None
    assert expected == result['ids']

    expected = [
        {
            '9': 'WIKIPEDIA',
            'a': u'Torsten_Åkesson',
        },
    ]
    result = hepnames2marc.do(result)

    assert expected == result['035']


def test_ids_from_8564_u_y_linkedin():
    schema = load_schema('authors')
    subschema = schema['properties']['ids']

    snippet = (  # record/1423251
        '<datafield tag="856" ind1="4" ind2=" ">  <subfield'
        ' code="u">https://www.linkedin.com/in/silvia-adri%C3%A1n-mart%C3%ADnez-ab1a548b</subfield>'
        '  <subfield code="y">LINKEDIN</subfield></datafield>'
    )

    expected = [
        {'schema': 'LINKEDIN', 'value': u'silvia-adrián-martínez-ab1a548b'},
    ]
    result = hepnames.do(create_record(snippet))

    assert validate(result['ids'], subschema) is None
    assert expected == result['ids']

    expected = [
        {
            'u': (
                'https://www.linkedin.com/in/silvia-adri%C3%A1n-mart%C3%ADnez-ab1a548b'
            ),
            'y': 'LINKEDIN',
        },
    ]
    result = hepnames2marc.do(result)

    assert expected == result['8564']


def test_native_names_from_880__a():
    schema = load_schema('authors')
    subschema = schema['properties']['name']['properties']['native_names']

    snippet = (  # record/1019097
        '<datafield tag="880" ind1=" " ind2=" ">'
        '  <subfield code="a">Գեւորգ Ն. Աբազաջիան</subfield>'
        '</datafield>'
    )

    expected = [u'Գեւորգ Ն. Աբազաջիան']

    result = hepnames.do(create_record(snippet))

    assert validate(result['name']['native_names'], subschema) is None
    assert expected == result['name']['native_names']

    expected = [
        {'a': u'Գեւորգ Ն. Աբազաջիան'},
    ]
    result = hepnames2marc.do(result)

    assert expected == result['880']


def test_ids_from_970__a():
    schema = load_schema('authors')
    subschema = schema['properties']['ids']

    snippet = (  # record/1498151
        '<datafield tag="970" ind1=" " ind2=" ">'
        '  <subfield code="a">HEPNAMES-646482</subfield>'
        '</datafield>'
    )

    expected = [
        {
            'schema': 'SPIRES',
            'value': 'HEPNAMES-646482',
        },
    ]
    result = hepnames.do(create_record(snippet))

    assert validate(result['ids'], subschema) is None
    assert expected == result['ids']

    expected = [
        {'a': 'HEPNAMES-646482'},
    ]
    result = hepnames2marc.do(result)

    assert expected == result['970']


def test_new_record_from_970__d():
    schema = load_schema('authors')
    subschema = schema['properties']['new_record']

    snippet = (  # record/1271254
        '<datafield tag="970" ind1=" " ind2=" ">'
        '  <subfield code="d">1039458</subfield>'
        '</datafield>'
    )

    expected = {'$ref': 'http://localhost:5000/api/authors/1039458'}
    result = hepnames.do(create_record(snippet))

    assert validate(result['new_record'], subschema) is None
    assert expected == result['new_record']

    expected = {'d': 1039458}
    result = hepnames2marc.do(result)

    assert expected == result['970']


def test_stub_from_980__a_useful():
    schema = load_schema('authors')
    subschema = schema['properties']['stub']

    snippet = (  # record/1222902
        '<datafield tag="980" ind1=" " ind2=" ">'
        '  <subfield code="a">USEFUL</subfield>'
        '</datafield>'
    )

    expected = False
    result = hepnames.do(create_record(snippet))

    assert validate(result['stub'], subschema) is None
    assert expected == result['stub']

    expected = [
        {'a': 'USEFUL'},
        {'a': 'HEPNAMES'},
    ]
    result = hepnames2marc.do(result)

    for el in expected:
        assert el in result['980']
    for el in result['980']:
        assert el in expected


def test_stub_from_980__a_not_useful():
    schema = load_schema('authors')
    subschema = schema['properties']['stub']

    snippet = (  # record/1019103
        '<datafield tag="980" ind1=" " ind2=" ">'
        '  <subfield code="a">HEPNAMES</subfield>'
        '</datafield>'
    )

    expected = True
    result = hepnames.do(create_record(snippet))

    assert validate(result['stub'], subschema) is None
    assert expected == result['stub']

    expected = [
        {'a': 'HEPNAMES'},
    ]
    result = hepnames2marc.do(result)

    assert expected == result['980']


def test_deleted_from_980__c():
    schema = load_schema('authors')
    subschema = schema['properties']['deleted']

    snippet = (  # record/1511071
        '<datafield tag="980" ind1=" " ind2=" ">'
        '  <subfield code="c">DELETED</subfield>'
        '</datafield>'
    )

    expected = True
    result = hepnames.do(create_record(snippet))

    assert validate(result['deleted'], subschema) is None
    assert expected == result['deleted']

    expected = [
        {'c': 'DELETED'},
        {'a': 'HEPNAMES'},
    ]
    result = hepnames2marc.do(result)

    for el in expected:
        assert el in result['980']
    for el in result['980']:
        assert el in expected
