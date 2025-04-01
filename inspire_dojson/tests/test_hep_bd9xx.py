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
from inspire_dojson.hep.rules.bd9xx import (
    COLLECTIONS_MAP,
    COLLECTIONS_REVERSE_MAP,
    DOCUMENT_TYPE_MAP,
    DOCUMENT_TYPE_REVERSE_MAP,
)


def test_collections_map_contains_all_valid_collections():
    schema = load_schema('hep')
    subschema = schema['properties']['_collections']

    expected = subschema['items']['enum']
    result = COLLECTIONS_MAP.values()

    assert sorted(expected) == sorted(result)


def test_collections_reverse_map_contains_all_valid_collections():
    schema = load_schema('hep')
    subschema = schema['properties']['_collections']

    expected = subschema['items']['enum']
    result = COLLECTIONS_REVERSE_MAP.keys()

    assert sorted(expected) == sorted(result)


def test_document_type_map_contains_all_valid_document_types():
    schema = load_schema('elements/document_type')

    expected = schema['enum']
    result = DOCUMENT_TYPE_MAP.values()

    assert sorted(expected) == sorted(result)


def test_document_type_reverse_map_contains_all_valid_document_types():
    schema = load_schema('elements/document_type')

    expected = schema['enum']
    result = DOCUMENT_TYPE_REVERSE_MAP.keys()

    assert sorted(expected) == sorted(result)


def test_record_affiliations_from_902__a_z():
    schema = load_schema('hep')
    subschema = schema['properties']['record_affiliations']

    snippet = (  # record/1216295
        '<datafield tag="902" ind1=" " ind2=" ">'
        '  <subfield code="a">Iowa State U.</subfield>'
        '  <subfield code="z">902893</subfield>'
        '</datafield>'
    )

    expected = [
        {
            'curated_relation': True,
            'record': {
                '$ref': 'http://localhost:5000/api/institutions/902893',
            },
            'value': 'Iowa State U.',
        },
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['record_affiliations'], subschema) is None
    assert expected == result['record_affiliations']

    expected = [
        {'a': 'Iowa State U.'},
    ]
    result = hep2marc.do(result)

    assert expected == result['902']


def test_record_affiliations_from_double_902__a_z():
    schema = load_schema('hep')
    subschema = schema['properties']['record_affiliations']

    snippet = (  # record/1216295
        '<record>'
        '  <datafield tag="902" ind1=" " ind2=" ">'
        '    <subfield code="a">Iowa State U.</subfield>'
        '    <subfield code="z">902893</subfield>'
        '  </datafield>'
        '  <datafield tag="902" ind1=" " ind2=" ">'
        '    <subfield code="a">Antwerp U.</subfield>'
        '    <subfield code="z">902642</subfield>'
        '  </datafield>'
        '</record>'
    )

    expected = [
        {
            'curated_relation': True,
            'record': {
                '$ref': 'http://localhost:5000/api/institutions/902893',
            },
            'value': 'Iowa State U.',
        },
        {
            'curated_relation': True,
            'record': {
                '$ref': 'http://localhost:5000/api/institutions/902642',
            },
            'value': 'Antwerp U.',
        },
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['record_affiliations'], subschema) is None
    assert expected == result['record_affiliations']

    expected = [
        {'a': 'Iowa State U.'},
        {'a': 'Antwerp U.'},
    ]
    result = hep2marc.do(result)

    assert expected == result['902']


def test_citeable_from_980__a_citeable():
    schema = load_schema('hep')
    subschema = schema['properties']['citeable']

    snippet = (  # record/1511471
        '<datafield tag="980" ind1=" " ind2=" ">'
        '  <subfield code="a">Citeable</subfield>'
        '</datafield>'
    )

    expected = True
    result = hep.do(create_record(snippet))

    assert validate(result['citeable'], subschema) is None
    assert expected == result['citeable']

    expected = [
        {'a': 'Citeable'},
    ]
    result = hep2marc.do(result)

    assert expected == result['980']


def test_core_from_980__a_core():
    schema = load_schema('hep')
    subschema = schema['properties']['core']

    snippet = (  # record/1509993
        '<datafield tag="980" ind1=" " ind2=" ">'
        '  <subfield code="a">CORE</subfield>'
        '</datafield>'
    )

    expected = True
    result = hep.do(create_record(snippet))

    assert validate(result['core'], subschema) is None
    assert expected == result['core']

    expected = [
        {'a': 'CORE'},
    ]
    result = hep2marc.do(result)

    assert expected == result['980']


def test_core_from_980__a_noncore():
    schema = load_schema('hep')
    subschema = schema['properties']['core']

    snippet = (  # record/1411887
        '<datafield tag="980" ind1=" " ind2=" ">'
        '  <subfield code="a">NONCORE</subfield>'
        '</datafield>'
    )

    expected = False
    result = hep.do(create_record(snippet))

    assert validate(result['core'], subschema) is None
    assert expected == result['core']

    expected = [
        {'a': 'NONCORE'},
    ]
    result = hep2marc.do(result)

    assert expected == result['980']


def test_deleted_from_980__c():
    schema = load_schema('hep')
    subschema = schema['properties']['deleted']

    snippet = (  # record/1508668
        '<datafield tag="980" ind1=" " ind2=" ">'
        '  <subfield code="c">DELETED</subfield>'
        '</datafield>'
    )

    expected = True
    result = hep.do(create_record(snippet))

    assert validate(result['deleted'], subschema) is None
    assert expected == result['deleted']

    expected = [
        {'c': 'DELETED'},
    ]
    result = hep2marc.do(result)

    assert expected == result['980']


def test_deleted_from_980__a():
    schema = load_schema('hep')
    subschema = schema['properties']['deleted']

    snippet = (  # record/931344
        '<datafield tag="980" ind1=" " ind2=" ">'
        '  <subfield code="a">DELETED</subfield>'
        '</datafield>'
    )

    expected = True
    result = hep.do(create_record(snippet))

    assert validate(result['deleted'], subschema) is None
    assert expected == result['deleted']

    expected = [
        {'c': 'DELETED'},
    ]
    result = hep2marc.do(result)

    assert expected == result['980']


def test_collections_from_980__a():
    schema = load_schema('hep')
    subschema = schema['properties']['_collections']

    snippet = (  # record/1610892
        '<datafield tag="980" ind1=" " ind2=" ">'
        '  <subfield code="a">HEP</subfield>'
        '</datafield>'
    )

    expected = ['Literature']
    result = hep.do(create_record(snippet))

    assert validate(result['_collections'], subschema) is None
    assert expected == result['_collections']

    expected = [
        {'a': 'HEP'},
    ]
    result = hep2marc.do(result)

    assert expected == result['980']


def test_collections_from_980__a_hal_hidden():
    schema = load_schema('hep')
    subschema = schema['properties']['_collections']

    snippet = (  # record/1505341
        '<datafield tag="980" ind1=" " ind2=" ">'
        '  <subfield code="a">HALhidden</subfield>'
        '</datafield>'
    )

    expected = [
        'HAL Hidden',
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['_collections'], subschema) is None
    assert expected == result['_collections']

    expected = [
        {'a': 'HALhidden'},
    ]
    result = hep2marc.do(result)

    assert expected == result['980']


def test_collections_from_980__a_babar_analysis_document():
    schema = load_schema('hep')
    subschema = schema['properties']['_collections']

    snippet = (  # record/1598316
        '<datafield tag="980" ind1=" " ind2=" ">'
        '  <subfield code="a">BABAR-AnalysisDocument</subfield>'
        '</datafield>'
    )

    expected = [
        'BABAR Analysis Documents',
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['_collections'], subschema) is None
    assert expected == result['_collections']

    expected = [
        {'a': 'BABAR-AnalysisDocument'},
    ]
    result = hep2marc.do(result)

    assert expected == result['980']


def test_collections_from_double_980__a():
    schema = load_schema('hep')
    subschema = schema['properties']['_collections']

    snippet = (  # record/1201407
        '<record>'
        '  <datafield tag="980" ind1=" " ind2=" ">'
        '    <subfield code="a">D0-PRELIMINARY-NOTE</subfield>'
        '  </datafield>'
        '  <datafield tag="980" ind1=" " ind2=" ">'
        '    <subfield code="a">HEP</subfield>'
        '  </datafield>'
        '</record>'
    )

    expected = [
        'D0 Preliminary Notes',
        'Literature',
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['_collections'], subschema) is None
    assert sorted(expected) == sorted(result['_collections'])

    expected = [
        {'a': 'HEP'},
        {'a': 'D0-PRELIMINARY-NOTE'},
    ]
    result = hep2marc.do(result)

    for el in expected:
        assert el in result['980']
    for el in result['980']:
        assert el in expected


def test_refereed_from_980__a_published():
    schema = load_schema('hep')
    subschema = schema['properties']['refereed']

    snippet = (  # record/1509992
        '<datafield tag="980" ind1=" " ind2=" ">'
        '  <subfield code="a">Published</subfield>'
        '</datafield>'
    )

    expected = True
    result = hep.do(create_record(snippet))

    assert validate(result['refereed'], subschema) is None
    assert expected == result['refereed']

    expected = [
        {'a': 'Published'},
    ]
    result = hep2marc.do(result)

    assert expected == result['980']


def test_document_type_defaults_to_article():
    schema = load_schema('hep')
    subschema = schema['properties']['document_type']

    snippet = '<record></record>'  # synthetic data

    expected = [
        'article',
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['document_type'], subschema) is None
    assert expected == result['document_type']


def test_document_type_from_980__a():
    schema = load_schema('hep')
    subschema = schema['properties']['document_type']

    snippet = (  # record/1512050
        '<datafield tag="980" ind1=" " ind2=" ">'
        '  <subfield code="a">Book</subfield>'
        '</datafield>'
    )

    expected = [
        'book',
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['document_type'], subschema) is None
    assert expected == result['document_type']

    expected = [
        {'a': 'Book'},
    ]
    result = hep2marc.do(result)

    assert expected == result['980']


def test_document_type_from_980__a_handles_conference_paper():
    schema = load_schema('hep')
    subschema = schema['properties']['document_type']

    snippet = (  # record/1589240
        '<datafield tag="980" ind1=" " ind2=" ">'
        '  <subfield code="a">ConferencePaper</subfield>'
        '</datafield>'
    )

    expected = [
        'conference paper',
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['document_type'], subschema) is None
    assert expected == result['document_type']

    expected = [
        {'a': 'ConferencePaper'},
    ]
    result = hep2marc.do(result)

    assert expected == result['980']


def test_document_type_from_980__a_handles_activity_report():
    schema = load_schema('hep')
    subschema = schema['properties']['document_type']

    snippet = (  # record/1514964
        '<datafield tag="980" ind1=" " ind2=" ">'
        '  <subfield code="a">ActivityReport</subfield>'
        '</datafield>'
    )

    expected = [
        'activity report',
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['document_type'], subschema) is None
    assert expected == result['document_type']

    expected = [
        {'a': 'ActivityReport'},
    ]
    result = hep2marc.do(result)

    assert expected == result['980']


def test_publication_type_from_980__a():
    schema = load_schema('hep')
    subschema = schema['properties']['publication_type']

    snippet = (  # record/1509993
        '<datafield tag="980" ind1=" " ind2=" ">'
        '  <subfield code="a">Review</subfield>'
        '</datafield>'
    )

    expected = [
        'review',
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['publication_type'], subschema) is None
    assert expected == result['publication_type']

    expected = [
        {'a': 'review'},
    ]
    result = hep2marc.do(result)

    assert expected == result['980']


def test_withdrawn_from_980__a_withdrawn():
    schema = load_schema('hep')
    subschema = schema['properties']['withdrawn']

    snippet = (  # record/1486153
        '<datafield tag="980" ind1=" " ind2=" ">'
        '  <subfield code="a">Withdrawn</subfield>'
        '</datafield>'
    )

    expected = True
    result = hep.do(create_record(snippet))

    assert validate(result['withdrawn'], subschema) is None
    assert expected == result['withdrawn']

    expected = [
        {'a': 'Withdrawn'},
    ]
    result = hep2marc.do(result)

    assert expected == result['980']


def test_references_from_999C5r_0():
    schema = load_schema('hep')
    subschema = schema['properties']['references']

    snippet = (  # record/41194
        '<datafield tag="999" ind1="C" ind2="5">'
        '  <subfield code="r">solv-int/9611008</subfield>'
        '  <subfield code="0">433620</subfield>'
        '</datafield>'
    )

    expected = [
        {
            'curated_relation': False,
            'record': {
                '$ref': 'http://localhost:5000/api/literature/433620',
            },
            'reference': {
                'arxiv_eprint': 'solv-int/9611008',
            },
        }
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['references'], subschema) is None
    assert expected == result['references']

    expected = [
        {
            '0': 433620,
            'r': [
                'solv-int/9611008',
            ],
            'z': 0,
        },
    ]
    result = hep2marc.do(result)

    assert expected == result['999C5']


def test_references_from_999C5r_s_0():
    schema = load_schema('hep')
    subschema = schema['properties']['references']

    snippet = (  # record/863300
        '<datafield tag="999" ind1="C" ind2="5">'
        '  <subfield code="r">arXiv:1006.1289</subfield>'
        '  <subfield code="s">Prog.Part.Nucl.Phys.,65,149</subfield>'
        '  <subfield code="0">857206</subfield>'
        '</datafield>'
    )

    expected = [
        {
            'curated_relation': False,
            'record': {
                '$ref': 'http://localhost:5000/api/literature/857206',
            },
            'reference': {
                'arxiv_eprint': '1006.1289',
                'publication_info': {
                    'artid': '149',
                    'journal_title': 'Prog.Part.Nucl.Phys.',
                    'journal_volume': '65',
                    'page_start': '149',
                },
            },
        },
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['references'], subschema) is None
    assert expected == result['references']

    expected = [
        {
            '0': 857206,
            'r': [
                'arXiv:1006.1289',
            ],
            's': 'Prog.Part.Nucl.Phys.,65,149',
            'z': 0,
        },
    ]
    result = hep2marc.do(result)

    assert expected == result['999C5']


def test_references_from_999C5h_m_o_y_z_0_9():
    schema = load_schema('hep')
    subschema = schema['properties']['references']

    snippet = (  # record/1289907
        '<datafield tag="999" ind1="C" ind2="5">  <subfield'
        ' code="0">1242925</subfield>  <subfield code="9">CURATOR</subfield> '
        ' <subfield code="h">M. Schwarz</subfield>  <subfield'
        ' code="m">Nontrivial Spacetime Topology, Modified Dispersion'
        ' Relations, and an SO(3)Skyrme Model, PhD Thesis, KIT (Verlag Dr. Hut,'
        ' Munich, Germany,)</subfield>  <subfield code="o">7</subfield> '
        ' <subfield code="y">2010</subfield>  <subfield'
        ' code="z">1</subfield></datafield>'
    )

    expected = [
        {
            'curated_relation': True,
            'legacy_curated': True,
            'record': {
                '$ref': 'http://localhost:5000/api/literature/1242925',
            },
            'reference': {
                'authors': [
                    {'full_name': 'Schwarz, M.'},
                ],
                'label': '7',
                'misc': [
                    (
                        'Nontrivial Spacetime Topology, Modified Dispersion'
                        ' Relations, and an SO(3)Skyrme Model, PhD Thesis, KIT'
                        ' (Verlag Dr. Hut, Munich, Germany,)'
                    ),
                ],
                'publication_info': {
                    'year': 2010,
                },
            },
        },
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['references'], subschema) is None
    assert expected == result['references']

    expected = [
        {
            '0': 1242925,
            '9': 'CURATOR',
            'h': [
                'Schwarz, M.',
            ],
            'm': (
                'Nontrivial Spacetime Topology, Modified Dispersion Relations,'
                ' and an SO(3)Skyrme Model, PhD Thesis, KIT (Verlag Dr. Hut,'
                ' Munich, Germany,)'
            ),
            'o': '7',
            'y': 2010,
            'z': 1,
        },
    ]
    result = hep2marc.do(result)

    assert expected == result['999C5']


def test_references_from_999C5h_m_o_t_y_repeated_z_0_9():
    schema = load_schema('hep')
    subschema = schema['properties']['references']

    snippet = (  # record/1095388
        '<datafield tag="999" ind1="C" ind2="5">'
        '  <subfield code="0">794379</subfield>'
        '  <subfield code="h">S. Weinberg</subfield>'
        '  <subfield code="m">Oxford University Press, Oxford U.K</subfield>'
        '  <subfield code="o">24</subfield>'
        '  <subfield code="t">Cosmology</subfield>'
        '  <subfield code="y">2008</subfield>'
        '  <subfield code="z">1</subfield>'
        '  <subfield code="9">CURATOR</subfield>'
        '  <subfield code="z">1</subfield>'
        '</datafield>'
    )

    expected = [
        {
            'curated_relation': True,
            'legacy_curated': True,
            'record': {
                '$ref': 'http://localhost:5000/api/literature/794379',
            },
            'reference': {
                'authors': [
                    {'full_name': 'Weinberg, S.'},
                ],
                'label': '24',
                'title': {'title': 'Cosmology'},
                'misc': [
                    'Oxford University Press, Oxford U.K',
                ],
                'publication_info': {
                    'year': 2008,
                },
            },
        },
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['references'], subschema) is None
    assert expected == result['references']

    expected = [
        {
            '0': 794379,
            '9': 'CURATOR',
            'h': [
                'Weinberg, S.',
            ],
            'm': 'Oxford University Press, Oxford U.K',
            'o': '24',
            't': 'Cosmology',
            'y': 2008,
            'z': 1,
        },
    ]
    result = hep2marc.do(result)

    assert expected == result['999C5']


def test_references_from_999C5h_m_o_r_s_y_0():
    schema = load_schema('hep')
    subschema = schema['properties']['references']

    snippet = (  # record/1498589
        '<datafield tag="999" ind1="C" ind2="5">  <subfield'
        ' code="0">857215</subfield>  <subfield code="h">R. C. Myers and A.'
        ' Sinha</subfield>  <subfield code="m">Seeing a c-theorem with'
        ' holography ; [hep-th]</subfield>  <subfield code="o">10</subfield> '
        ' <subfield code="r">arXiv:1006.1263</subfield>  <subfield'
        ' code="s">Phys.Rev.,D82,046006</subfield>  <subfield'
        ' code="y">2010</subfield></datafield>'
    )

    expected = [
        {
            'curated_relation': False,
            'record': {
                '$ref': 'http://localhost:5000/api/literature/857215',
            },
            'reference': {
                'arxiv_eprint': '1006.1263',
                'authors': [
                    {'full_name': u'Myers, R.C.'},
                    {'full_name': u'Sinha, A.'},
                ],
                'label': '10',
                'misc': [
                    'Seeing a c-theorem with holography ; [hep-th]',
                ],
                'publication_info': {
                    'artid': '046006',
                    'journal_title': 'Phys.Rev.D',
                    'journal_volume': '82',
                    'year': 2010,
                },
            },
        },
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['references'], subschema) is None
    assert expected == result['references']

    expected = [
        {
            '0': 857215,
            'h': [
                'Myers, R.C.',
                'Sinha, A.',
            ],
            'm': 'Seeing a c-theorem with holography ; [hep-th]',
            'o': '10',
            'r': [
                'arXiv:1006.1263',
            ],
            's': 'Phys.Rev.,D82,046006',
            'y': 2010,
            'z': 0,
        },
    ]
    result = hep2marc.do(result)

    assert expected == result['999C5']


def test_references_from_999C5a_h_o_s_x_y_0():
    schema = load_schema('hep')
    subschema = schema['properties']['references']

    snippet = (  # record/1478478
        '<datafield tag="999" ind1="C" ind2="5">  <subfield'
        ' code="a">doi:10.1142/S0217751X0804055X</subfield>  <subfield'
        ' code="h">G.K. Leontaris</subfield>  <subfield code="o">15</subfield> '
        ' <subfield code="s">Int.J.Mod.Phys.,A23,2055</subfield>  <subfield'
        ' code="x">Int. J. Mod. Phys. A 23'
        ' (doi:10.1142/S0217751X0804055X)</subfield>  <subfield'
        ' code="y">2008</subfield>  <subfield'
        ' code="0">780399</subfield></datafield>'
    )

    expected = [
        {
            'curated_relation': False,
            'record': {
                '$ref': 'http://localhost:5000/api/literature/780399',
            },
            'raw_refs': [
                {
                    'value': 'Int. J. Mod. Phys. A 23 (doi:10.1142/S0217751X0804055X)',
                    'schema': 'text',
                },
            ],
            'reference': {
                'dois': ['10.1142/S0217751X0804055X'],
                'authors': [
                    {'full_name': u'Leontaris, G.K.'},
                ],
                'label': '15',
                'publication_info': {
                    "artid": '2055',
                    'journal_title': 'Int.J.Mod.Phys.A',
                    'journal_volume': '23',
                    'page_start': '2055',
                    'year': 2008,
                },
            },
        },
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['references'], subschema) is None
    assert expected == result['references']

    expected = [
        {
            'a': [
                'doi:10.1142/S0217751X0804055X',
            ],
            'h': [
                'Leontaris, G.K.',
            ],
            'o': '15',
            's': 'Int.J.Mod.Phys.,A23,2055',
            'x': [
                'Int. J. Mod. Phys. A 23 (doi:10.1142/S0217751X0804055X)',
            ],
            'y': 2008,
            'z': 0,
            '0': 780399,
        }
    ]
    result = hep2marc.do(result)

    assert expected == result['999C5']


def test_references_from_999C50_h_m_o_r_y():
    schema = load_schema('hep')
    subschema = schema['properties']['references']

    snippet = (  # record/1478478
        '<datafield tag="999" ind1="C" ind2="5">  <subfield'
        ' code="0">701721</subfield>  <subfield code="h">A. Ferrari, P.R. Sala,'
        ' A. Fasso, and J. Ranft</subfield>  <subfield code="m">FLUKA: a'
        ' multi-particle transport code, CERN-10 , INFN/TC_05/11</subfield> '
        ' <subfield code="o">13</subfield>  <subfield'
        ' code="r">SLAC-R-773</subfield>  <subfield'
        ' code="y">2005</subfield></datafield>'
    )

    expected = [
        {
            'curated_relation': False,
            'record': {
                '$ref': 'http://localhost:5000/api/literature/701721',
            },
            'reference': {
                'authors': [
                    {'full_name': 'Ferrari, A.'},
                    {'full_name': 'Sala, P.R.'},
                    {'full_name': 'Fasso, A.'},
                    {'full_name': 'Ranft, J.'},
                ],
                'label': '13',
                'misc': [
                    'FLUKA: a multi-particle transport code, CERN-10 , INFN/TC_05/11',
                ],
                'publication_info': {'year': 2005},
                'report_numbers': [
                    'SLAC-R-773',
                ],
            },
        },
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['references'], subschema) is None
    assert expected == result['references']

    expected = [
        {
            '0': 701721,
            'h': [
                'Ferrari, A.',
                'Sala, P.R.',
                'Fasso, A.',
                'Ranft, J.',
            ],
            'm': 'FLUKA: a multi-particle transport code, CERN-10 , INFN/TC_05/11',
            'r': [
                'SLAC-R-773',
            ],
            'o': '13',
            'y': 2005,
            'z': 0,
        }
    ]
    result = hep2marc.do(result)

    assert expected == result['999C5']


def test_references_from_999C59_h_m_o_double_r_y():
    schema = load_schema('hep')
    subschema = schema['properties']['references']

    snippet = (  # record/1449990
        '<datafield tag="999" ind1="C" ind2="5">'
        '  <subfield code="9">CURATOR</subfield>'
        '  <subfield code="h">Bennett, J</subfield>'
        '  <subfield code="m">Roger J. et al.</subfield>'
        '  <subfield code="o">9</subfield>'
        '  <subfield code="r">CERN-INTC-2004-016</subfield>'
        '  <subfield code="r">CERN-INTCP-186</subfield>'
        '  <subfield code="y">2004</subfield>'
        '</datafield>'
    )

    expected = [
        {
            'legacy_curated': True,
            'reference': {
                'authors': [
                    {'full_name': 'Bennett, J.'},
                ],
                'label': '9',
                'misc': [
                    'Roger J. et al.',
                ],
                'publication_info': {'year': 2004},
                'report_numbers': [
                    'CERN-INTC-2004-016',
                    'CERN-INTCP-186',
                ],
            },
        },
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['references'], subschema) is None
    assert expected == result['references']

    expected = [
        {
            '9': 'CURATOR',
            'h': [
                'Bennett, J.',
            ],
            'r': [
                'CERN-INTC-2004-016',
                'CERN-INTCP-186',
            ],
            'm': 'Roger J. et al.',
            'o': '9',
            'y': 2004,
            'z': 0,
        },
    ]
    result = hep2marc.do(result)

    assert expected == result['999C5']


def test_references_from_999C50_9_r_u_h_m_o():
    schema = load_schema('hep')
    subschema = schema['properties']['references']

    snippet = (  # record/1504897
        '<datafield tag="999" ind1="C" ind2="5">  <subfield code="0">1511470</subfield>'
        '  <subfield code="9">CURATOR</subfield>  <subfield'
        ' code="r">urn:nbn:de:hebis:77-diss-1000009520</subfield>  <subfield'
        ' code="u">http://www.diss.fu-berlin.de/diss/receive/FUDISS_thesis_000000094316</subfield>'
        '  <subfield code="h">K. Wiebe</subfield>  <subfield code="m">Ph.D. thesis,'
        ' University of Mainz, in preparation</subfield>  <subfield'
        ' code="o">51</subfield></datafield>'
    )

    expected = [
        {
            'curated_relation': False,
            'legacy_curated': True,
            'record': {
                '$ref': 'http://localhost:5000/api/literature/1511470',
            },
            'reference': {
                'authors': [
                    {'full_name': 'Wiebe, K.'},
                ],
                'label': '51',
                'misc': [
                    'Ph.D. thesis, University of Mainz, in preparation',
                ],
                'report_numbers': [
                    'urn:nbn:de:hebis:77-diss-1000009520',
                ],
                'urls': [
                    {
                        'value': 'http://www.diss.fu-berlin.de/diss/receive/FUDISS_thesis_000000094316'
                    },
                ],
            },
        },
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['references'], subschema) is None
    assert expected == result['references']

    expected = [
        {
            '0': 1511470,
            '9': 'CURATOR',
            'h': [
                'Wiebe, K.',
            ],
            'r': [
                'urn:nbn:de:hebis:77-diss-1000009520',
            ],
            'm': 'Ph.D. thesis, University of Mainz, in preparation',
            'o': '51',
            'u': [
                'http://www.diss.fu-berlin.de/diss/receive/FUDISS_thesis_000000094316',
            ],
            'z': 0,
        },
    ]
    result = hep2marc.do(result)

    assert expected == result['999C5']


def test_reference_from_999C5t_p_y_e_o():
    schema = load_schema('hep')
    subschema = schema['properties']['references']

    snippet = (  # record/1590099
        '<datafield tag="999" ind1="C" ind2="5">  <subfield code="t">Higher'
        ' Transcendetal Functions Vol. I, Bateman Manuscript Project</subfield>'
        '  <subfield code="p">New York: McGraw-Hill Book Company,'
        ' Inc.</subfield>  <subfield code="y">1953</subfield>  <subfield'
        ' code="e">Erdélyi,A.</subfield>  <subfield'
        ' code="o">16</subfield></datafield>'
    )

    expected = [
        {
            'reference': {
                'authors': [
                    {
                        'full_name': u'Erdélyi, A.',
                        'inspire_role': 'editor',
                    },
                ],
                'imprint': {'publisher': 'New York: McGraw-Hill Book Company, Inc.'},
                'label': '16',
                'publication_info': {'year': 1953},
                'title': {
                    'title': (
                        'Higher Transcendetal Functions Vol. I, Bateman'
                        ' Manuscript Project'
                    )
                },
            },
        },
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['references'], subschema) is None
    assert expected == result['references']

    expected = [
        {
            'e': [
                u'Erdélyi, A.',
            ],
            'o': '16',
            'p': 'New York: McGraw-Hill Book Company, Inc.',
            't': 'Higher Transcendetal Functions Vol. I, Bateman Manuscript Project',
            'y': 1953,
            'z': 0,
        }
    ]
    result = hep2marc.do(result)

    assert expected == result['999C5']


def test_reference_from_999C5o_h_c_t_s_r_y_0():
    schema = load_schema('hep')
    subschema = schema['properties']['references']

    snippet = (  # record/1591975
        '<datafield tag="999" ind1="C" ind2="5">  <subfield'
        ' code="o">36</subfield>  <subfield code="h">S. Chatrchyan et'
        ' al.</subfield>  <subfield code="c">CMS Collaboration</subfield> '
        ' <subfield code="t">Angular analysis and branching fraction'
        ' measurement of the decay B0 → K∗0 µ+ µ-</subfield>  <subfield'
        ' code="s">Phys.Lett.,B727,77</subfield>  <subfield'
        ' code="r">arXiv:1308.3409 [hep-ex]</subfield>  <subfield'
        ' code="y">2013</subfield>  <subfield'
        ' code="0">1247976</subfield></datafield>'
    )

    expected = [
        {
            'curated_relation': False,
            'record': {'$ref': 'http://localhost:5000/api/literature/1247976'},
            'reference': {
                'arxiv_eprint': '1308.3409',
                'authors': [{'full_name': u'Chatrchyan, S.'}],
                'collaborations': ['CMS Collaboration'],
                'label': '36',
                'publication_info': {
                    'artid': '77',
                    'journal_title': 'Phys.Lett.B',
                    'journal_volume': '727',
                    'page_start': '77',
                    'year': 2013,
                },
                'title': {
                    'title': (
                        u'Angular analysis and branching fraction measurement'
                        u' of the decay B0 → K∗0 µ+ µ-'
                    )
                },
            },
        }
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['references'], subschema) is None
    assert expected == result['references']

    expected = [
        {
            '0': 1247976,
            'c': [
                'CMS Collaboration',
            ],
            'h': [
                'Chatrchyan, S.',
            ],
            'o': '36',
            'r': [
                'arXiv:1308.3409',
            ],
            's': 'Phys.Lett.,B727,77',
            't': (
                u'Angular analysis and branching fraction measurement of the'
                u' decay B0 → K∗0 µ+ µ-'
            ),
            'y': 2013,
            'z': 0,
        }
    ]
    result = hep2marc.do(result)

    assert expected == result['999C5']


def test_references_from_999C5b_h_m_o_p_t_y_9():
    schema = load_schema('hep')
    subschema = schema['properties']['references']

    snippet = (  # record/1481519
        '<datafield tag="999" ind1="C" ind2="5">  <subfield'
        ' code="9">CURATOR</subfield>  <subfield code="b">C93-06-08</subfield> '
        ' <subfield code="h">C. Gaspar</subfield>  <subfield code="m">Real Time'
        ' Conference,, Vancouver, Canada</subfield>  <subfield'
        ' code="o">7</subfield>  <subfield code="p">IEEE</subfield>  <subfield'
        ' code="t">DIM - A Distributed Information Management System for the'
        ' Delphi experiment at CERN</subfield>  <subfield'
        ' code="y">1993</subfield></datafield>'
    )

    expected = [
        {
            'legacy_curated': True,
            'reference': {
                'authors': [
                    {'full_name': 'Gaspar, C.'},
                ],
                'imprint': {'publisher': 'IEEE'},
                'label': '7',
                'misc': [
                    'Real Time Conference,, Vancouver, Canada',
                ],
                'publication_info': {
                    'cnum': 'C93-06-08',
                    'year': 1993,
                },
                'title': {
                    'title': (
                        'DIM - A Distributed Information Management System for'
                        ' the Delphi experiment at CERN'
                    )
                },
            },
        },
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['references'], subschema) is None
    assert expected == result['references']

    expected = [
        {
            '9': 'CURATOR',
            'b': 'C93-06-08',
            'h': [
                'Gaspar, C.',
            ],
            'm': 'Real Time Conference,, Vancouver, Canada',
            'o': '7',
            'p': 'IEEE',
            't': (
                'DIM - A Distributed Information Management System for the'
                ' Delphi experiment at CERN'
            ),
            'y': 1993,
            'z': 0,
        },
    ]
    result = hep2marc.do(result)

    assert expected == result['999C5']


def test_references_from_999C5a_h_i_m_o_p_y_9():
    schema = load_schema('hep')
    subschema = schema['properties']['references']

    snippet = (  # record/1593684
        '<datafield tag="999" ind1="C" ind2="5">  <subfield'
        ' code="o">16</subfield>  <subfield code="h">A. Del Guerra</subfield> '
        ' <subfield code="m">Ionizing Radiation Detectors for Medical Imaging'
        ' Crossref:</subfield>  <subfield code="p">World Scientific</subfield> '
        ' <subfield code="i">9812562621</subfield>  <subfield'
        ' code="a">doi:10.1142/5408</subfield>  <subfield'
        ' code="y">2004</subfield>  <subfield'
        ' code="9">refextract</subfield></datafield>'
    )

    expected = [
        {
            'reference': {
                'authors': [
                    {'full_name': 'Del Guerra, A.'},
                ],
                'dois': [
                    '10.1142/5408',
                ],
                'imprint': {'publisher': 'World Scientific'},
                'isbn': '9789812562623',
                'label': '16',
                'misc': [
                    'Ionizing Radiation Detectors for Medical Imaging Crossref:',
                ],
                'publication_info': {'year': 2004},
            },
        },
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['references'], subschema) is None
    assert expected == result['references']

    expected = [
        {
            'a': [
                'doi:10.1142/5408',
            ],
            'h': [
                'Del Guerra, A.',
            ],
            'i': '9789812562623',
            'm': 'Ionizing Radiation Detectors for Medical Imaging Crossref:',
            'o': '16',
            'p': 'World Scientific',
            'y': 2004,
            'z': 0,
        },
    ]
    result = hep2marc.do(result)

    assert expected == result['999C5']


def test_references_from_999C5h_o_q_t_y():
    schema = load_schema('hep')
    subschema = schema['properties']['references']

    snippet = (  # record/1592189
        '<datafield tag="999" ind1="C" ind2="5">'
        '  <subfield code="h">Gromov, M.</subfield>'
        '  <subfield code="t">Spaces and questions</subfield>'
        '  <subfield code="y">2000</subfield>'
        '  <subfield code="q">Geom. Funct. Anal., GAFA 2000</subfield>'
        '  <subfield code="o">16</subfield>'
        '</datafield>'
    )

    expected = [
        {
            'reference': {
                'authors': [
                    {'full_name': 'Gromov, M.'},
                ],
                'label': '16',
                'publication_info': {
                    'parent_title': 'Geom. Funct. Anal., GAFA 2000',
                    'year': 2000,
                },
                'title': {'title': 'Spaces and questions'},
            },
        },
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['references'], subschema) is None
    assert expected == result['references']

    expected = [
        {
            'h': [
                'Gromov, M.',
            ],
            'o': '16',
            'q': 'Geom. Funct. Anal., GAFA 2000',
            't': 'Spaces and questions',
            'y': 2000,
            'z': 0,
        },
    ]
    result = hep2marc.do(result)

    assert expected == result['999C5']


def test_references_from_999C5k():
    schema = load_schema('hep')
    subschema = schema['properties']['references']

    snippet = (  # synthetic data
        '<datafield tag="999" ind1="C" ind2="5">'
        '  <subfield code="k">Robilotta:2008js</subfield>'
        '</datafield>'
    )

    expected = [
        {
            'reference': {
                'texkey': 'Robilotta:2008js',
            },
        },
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['references'], subschema) is None
    assert expected == result['references']

    expected = [
        {
            'k': 'Robilotta:2008js',
            'z': 0,
        },
    ]
    result = hep2marc.do(result)

    assert expected == result['999C5']


def test_references_from_999C5d_multiple_h_o_r_0_9():
    schema = load_schema('hep')
    subschema = schema['properties']['references']

    snippet = (  # record/1410105
        '<datafield tag="999" ind1="C" ind2="5">'
        '  <subfield code="0">568216</subfield>'
        '  <subfield code="9">CURATOR</subfield>'
        '  <subfield code="d">eprint</subfield>'
        '  <subfield code="h">Y. Yan</subfield>'
        '  <subfield code="h">R. Tegen</subfield>'
        '  <subfield code="h">T. Gutsche</subfield>'
        '  <subfield code="h">V. E. Lyubovitskij</subfield>'
        '  <subfield code="h">A. Faessler</subfield>'
        '  <subfield code="o">20</subfield>'
        '  <subfield code="r">hep-ph/0112168v2</subfield>'
        '</datafield>'
    )

    expected = [
        {
            'legacy_curated': True,
            'curated_relation': False,
            'record': {
                '$ref': 'http://localhost:5000/api/literature/568216',
            },
            'reference': {
                'arxiv_eprint': 'hep-ph/0112168',
                'authors': [
                    {'full_name': 'Yan, Y.'},
                    {'full_name': 'Tegen, R.'},
                    {'full_name': 'Gutsche, T.'},
                    {'full_name': 'Lyubovitskij, V.E.'},
                    {'full_name': 'Faessler, A.'},
                ],
                'label': '20',
            },
        },
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['references'], subschema) is None
    assert expected == result['references']

    expected = [
        {
            '0': 568216,
            '9': 'CURATOR',
            'h': [
                'Yan, Y.',
                'Tegen, R.',
                'Gutsche, T.',
                'Lyubovitskij, V.E.',
                'Faessler, A.',
            ],
            'o': '20',
            'r': [
                'hep-ph/0112168',
            ],
            'z': 0,
        },
    ]
    result = hep2marc.do(result)

    assert expected == result['999C5']


def test_references_from_999C5h_k_double_m_o_s_y_0():
    schema = load_schema('hep')
    subschema = schema['properties']['references']

    snippet = (  # record/1613562
        '<datafield tag="999" ind1="C" ind2="5">'
        '  <subfield code="h">W, Schoutens.</subfield>'
        '  <subfield code="k">Bouwknegt:1992wg</subfield>'
        '  <subfield code="m">Peter Bouwknegt and Kareljan</subfield>'
        '  <subfield code="m">symmetry in conformal field theory</subfield>'
        '  <subfield code="o">12</subfield>'
        '  <subfield code="s">Phys.Rept.,223,183-276</subfield>'
        '  <subfield code="y">1993</subfield>'
        '  <subfield code="0">338634</subfield>'
        '</datafield>'
    )

    expected = [
        {
            'curated_relation': False,
            'record': {
                '$ref': 'http://localhost:5000/api/literature/338634',
            },
            'reference': {
                'authors': [
                    {'full_name': 'Schoutens.'},  # XXX: wrong, but the best we can do.
                ],
                'label': '12',
                'misc': [
                    'Peter Bouwknegt and Kareljan',
                    'symmetry in conformal field theory',
                ],
                'publication_info': {
                    'journal_title': 'Phys.Rept.',
                    'journal_volume': '223',
                    'page_start': '183',
                    'page_end': '276',
                    'year': 1993,
                },
                'texkey': 'Bouwknegt:1992wg',
            },
        },
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['references'], subschema) is None
    assert expected == result['references']

    expected = [
        {
            '0': 338634,
            'h': [
                'Schoutens.',  # XXX: wrong, but the best we can do.
            ],
            'k': 'Bouwknegt:1992wg',
            'm': 'Peter Bouwknegt and Kareljan / symmetry in conformal field theory',
            'o': '12',
            's': 'Phys.Rept.,223,183-276',
            'y': 1993,
            'z': 0,
        },
    ]
    result = hep2marc.do(result)

    assert expected == result['999C5']


def test_references_from_999C5_0_h_m_o_r_t_y():
    schema = load_schema('hep')
    subschema = schema['properties']['references']

    snippet = (  # record/1615506
        '<datafield tag="999" ind1="C" ind2="5">  <subfield'
        ' code="0">674429</subfield>  <subfield code="h">R. Ardito et'
        ' al.</subfield>  <subfield code="m">66</subfield>  <subfield'
        ' code="o">57</subfield>  <subfield code="r">hep-ex/0501010</subfield> '
        ' <subfield code="t">CUORE: A Cryogenic underground Observatory for'
        ' Rare Events</subfield>  <subfield'
        ' code="y">2005</subfield></datafield>'
    )

    expected = [
        {
            'curated_relation': False,
            'record': {
                '$ref': 'http://localhost:5000/api/literature/674429',
            },
            'reference': {
                'arxiv_eprint': 'hep-ex/0501010',
                'authors': [
                    {'full_name': 'Ardito, R.'},
                ],
                'label': '57',
                'misc': [
                    '66',
                ],
                'publication_info': {'year': 2005},
                'title': {
                    'title': (
                        'CUORE: A Cryogenic underground Observatory for Rare Events'
                    )
                },
            },
        },
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['references'], subschema) is None
    assert expected == result['references']

    expected = [
        {
            '0': 674429,
            'h': [
                'Ardito, R.',
            ],
            'm': '66',
            'o': '57',
            'r': [
                'hep-ex/0501010',
            ],
            't': 'CUORE: A Cryogenic underground Observatory for Rare Events',
            'y': 2005,
            'z': 0,
        },
    ]
    result = hep2marc.do(result)

    assert expected == result['999C5']


def test_references_from_999C5_0_z():
    schema = load_schema('hep')
    subschema = schema['properties']['references']

    snippet = (  # record/374213
        '<datafield tag="999" ind1="C" ind2="5">'
        '  <subfield code="0">351013</subfield>'
        '  <subfield code="z">1</subfield>'
        '</datafield>'
    )

    expected = [
        {
            'curated_relation': True,
            'record': {
                '$ref': 'http://localhost:5000/api/literature/351013',
            },
        },
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['references'], subschema) is None
    assert expected == result['references']

    expected = [
        {
            '0': 351013,
            'z': 1,
        },
    ]
    result = hep2marc.do(result)

    assert expected == result['999C5']


def test_references_from_999C5u_as_cds_system_identifiers():
    schema = load_schema('hep')
    subschema = schema['properties']['references']

    snippet = (  # record/1665526
        '<datafield tag="999" ind1="C" ind2="5">  <subfield'
        ' code="o">59</subfield>  <subfield code="c">ATLAS'
        ' Collaboration</subfield>  <subfield code="c">CMS'
        ' Collaboration</subfield>  <subfield code="m">The LHC Higgs'
        ' Combination Group Collaboration Tech. Rep CERN, Geneva,'
        ' Aug</subfield>  <subfield code="h">G. Aad et al.</subfield> '
        ' <subfield code="t">Procedure for the LHC Higgs boson search'
        ' combination in Summer 2011</subfield>  <subfield'
        ' code="r">CMS-NOTE-2011-005</subfield>  <subfield'
        ' code="r">ATL-PHYS-PUB-2011-11</subfield>  <subfield'
        ' code="u">http://cds.cern.ch/record/1379837</subfield>  <subfield'
        ' code="y">2011</subfield>  <subfield'
        ' code="0">1196797</subfield></datafield>'
    )

    expected = [
        {
            'record': {
                '$ref': u'http://localhost:5000/api/literature/1196797',
            },
            'reference': {
                'report_numbers': [
                    'CMS-NOTE-2011-005',
                    'ATL-PHYS-PUB-2011-11',
                ],
                'title': {
                    'title': (
                        'Procedure for the LHC Higgs boson search combination'
                        ' in Summer 2011'
                    ),
                },
                'collaborations': [
                    'ATLAS Collaboration',
                    'CMS Collaboration',
                ],
                'misc': [
                    (
                        'The LHC Higgs Combination Group Collaboration Tech.'
                        ' Rep CERN, Geneva, Aug'
                    ),
                ],
                'label': '59',
                'publication_info': {
                    'year': 2011,
                },
                'authors': [
                    {
                        'full_name': u'Aad, G.',
                    },
                ],
                'external_system_identifiers': [
                    {
                        'value': '1379837',
                        'schema': 'CDS',
                    },
                ],
            },
            'curated_relation': False,
        }
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['references'], subschema) is None
    assert expected == result['references']

    expected = [
        {
            'c': [
                'ATLAS Collaboration',
                'CMS Collaboration',
            ],
            'h': [
                u'Aad, G.',
            ],
            'm': (
                'The LHC Higgs Combination Group Collaboration Tech. Rep CERN,'
                ' Geneva, Aug'
            ),
            'o': '59',
            '0': 1196797,
            'r': [
                'CMS-NOTE-2011-005',
                'ATL-PHYS-PUB-2011-11',
            ],
            'u': [
                'http://cds.cern.ch/record/1379837',
            ],
            't': 'Procedure for the LHC Higgs boson search combination in Summer 2011',
            'y': 2011,
            'z': 0,
        },
    ]
    result = hep2marc.do(result)

    assert expected == result['999C5']


def test_references_from_999C5u_as_ads_system_identifiers():
    schema = load_schema('hep')
    subschema = schema['properties']['references']

    snippet = (  # record/1663135
        '<datafield tag="999" ind1="C" ind2="5">  <subfield'
        ' code="o">25</subfield>  <subfield code="m">Kragh, Helge'
        ' Bibcode:PhP...17..107K</subfield>  <subfield code="t">Pascual Jordan,'
        ' Varying Gravity, and the Expanding Earth</subfield>  <subfield'
        ' code="s">Phys.Perspect.,17,107</subfield>  <subfield'
        ' code="u">http://adsabs.harvard.edu/abs/2015PhP...17..107K</subfield> '
        ' <subfield code="a">doi:10.1007/s00016-015-0157-9</subfield> '
        ' <subfield code="y">2015</subfield></datafield>'
    )

    expected = [
        {
            'reference': {
                'title': {
                    'title': 'Pascual Jordan, Varying Gravity, and the Expanding Earth',
                },
                'misc': [
                    'Kragh, Helge Bibcode:PhP...17..107K',
                ],
                'label': '25',
                'publication_info': {
                    'artid': '107',
                    'journal_volume': '17',
                    'page_start': '107',
                    'journal_title': 'Phys.Perspect.',
                    'year': 2015,
                },
                'external_system_identifiers': [
                    {
                        'value': '2015PhP...17..107K',
                        'schema': 'ADS',
                    },
                ],
                'dois': [
                    '10.1007/s00016-015-0157-9',
                ],
            },
        }
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['references'], subschema) is None
    assert expected == result['references']

    expected = [
        {
            'a': [
                'doi:10.1007/s00016-015-0157-9',
            ],
            'm': 'Kragh, Helge Bibcode:PhP...17..107K',
            'o': '25',
            's': 'Phys.Perspect.,17,107',
            'u': [
                'http://adsabs.harvard.edu/abs/2015PhP...17..107K',
            ],
            't': 'Pascual Jordan, Varying Gravity, and the Expanding Earth',
            'y': 2015,
            'z': 0,
        },
    ]
    result = hep2marc.do(result)

    assert expected == result['999C5']


def test_references_from_999C5u_duplicated_u():
    schema = load_schema('hep')
    subschema = schema['properties']['references']

    snippet = (  # record/1663135
        '<datafield tag="999" ind1="C" ind2="5">  <subfield'
        ' code="o">25</subfield>  <subfield code="m">Kragh, Helge'
        ' Bibcode:PhP...17..107K</subfield>  <subfield code="t">Pascual Jordan,'
        ' Varying Gravity, and the Expanding Earth</subfield>  <subfield'
        ' code="s">Phys.Perspect.,17,107</subfield>  <subfield'
        ' code="u">http://adsabs.harvard.edu/abs/2015PhP...17..107K</subfield> '
        ' <subfield'
        ' code="u">http://adsabs.harvard.edu/abs/2015PhP...17..107K</subfield> '
        ' <subfield code="a">doi:10.1007/s00016-015-0157-9</subfield> '
        ' <subfield code="y">2015</subfield></datafield>'
    )

    expected = [
        {
            'reference': {
                'title': {
                    'title': 'Pascual Jordan, Varying Gravity, and the Expanding Earth',
                },
                'misc': [
                    'Kragh, Helge Bibcode:PhP...17..107K',
                ],
                'label': '25',
                'publication_info': {
                    'artid': '107',
                    'journal_volume': '17',
                    'page_start': '107',
                    'journal_title': 'Phys.Perspect.',
                    'year': 2015,
                },
                'external_system_identifiers': [
                    {
                        'value': '2015PhP...17..107K',
                        'schema': 'ADS',
                    },
                ],
                'dois': [
                    '10.1007/s00016-015-0157-9',
                ],
            },
        }
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['references'], subschema) is None
    assert expected == result['references']

    expected = [
        {
            'a': [
                'doi:10.1007/s00016-015-0157-9',
            ],
            'm': 'Kragh, Helge Bibcode:PhP...17..107K',
            'o': '25',
            's': 'Phys.Perspect.,17,107',
            'u': [
                'http://adsabs.harvard.edu/abs/2015PhP...17..107K',
            ],
            't': 'Pascual Jordan, Varying Gravity, and the Expanding Earth',
            'y': 2015,
            'z': 0,
        },
    ]
    result = hep2marc.do(result)

    assert expected == result['999C5']
