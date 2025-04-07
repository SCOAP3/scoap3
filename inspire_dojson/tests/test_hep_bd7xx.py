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


def test_collaborations_from_710__g():
    schema = load_schema('hep')
    subschema = schema['properties']['collaborations']

    snippet = (  # record/1510404
        '<datafield tag="710" ind1=" " ind2=" ">'
        '  <subfield code="g">Pierre Auger</subfield>'
        '</datafield>'
    )

    expected = [
        {'value': 'Pierre Auger'},
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['collaborations'], subschema) is None
    assert expected == result['collaborations']

    expected = [
        {'g': 'Pierre Auger'},
    ]
    result = hep2marc.do(result)

    assert expected == result['710']


def test_collaborations_from_710__g_normalizes_value():
    schema = load_schema('hep')
    subschema = schema['properties']['collaborations']

    snippet = (  # http://cds.cern.ch/record/2293683
        '<datafield tag="710" ind1=" " ind2=" ">'
        '  <subfield code="g">on behalf of the CMS Collaboration</subfield>'
        '</datafield>'
    )

    expected = [
        {'value': 'CMS'},
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['collaborations'], subschema) is None
    assert expected == result['collaborations']

    expected = [
        {'g': 'CMS'},
    ]
    result = hep2marc.do(result)

    assert expected == result['710']


def test_collaborations_from_710__g_0():
    schema = load_schema('hep')
    subschema = schema['properties']['collaborations']

    snippet = (  # record/1422032
        '<datafield tag="710" ind1=" " ind2=" ">'
        '  <subfield code="g">ANTARES</subfield>'
        '  <subfield code="0">1110619</subfield>'
        '</datafield>'
    )

    expected = [
        {
            'record': {
                '$ref': 'http://localhost:5000/api/experiments/1110619',
            },
            'value': 'ANTARES',
        },
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['collaborations'], subschema) is None
    assert expected == result['collaborations']

    expected = [
        {'g': 'ANTARES'},
    ]
    result = hep2marc.do(result)

    assert expected == result['710']


def test_collaborations_from_multiple_710__g_0_and_710__g():
    schema = load_schema('hep')
    subschema = schema['properties']['collaborations']

    snippet = (  # record/1422032
        '<record>'
        '  <datafield tag="710" ind1=" " ind2=" ">'
        '    <subfield code="g">ANTARES</subfield>'
        '    <subfield code="0">1110619</subfield>'
        '  </datafield>'
        '  <datafield tag="710" ind1=" " ind2=" ">'
        '    <subfield code="g">IceCube</subfield>'
        '    <subfield code="0">1108514</subfield>'
        '  </datafield>'
        '  <datafield tag="710" ind1=" " ind2=" ">'
        '    <subfield code="g">LIGO Scientific</subfield>'
        '  </datafield>'
        '  <datafield tag="710" ind1=" " ind2=" ">'
        '    <subfield code="g">Virgo</subfield>'
        '    <subfield code="0">1110601</subfield>'
        '  </datafield>'
        '</record>'
    )

    expected = [
        {
            'record': {
                '$ref': 'http://localhost:5000/api/experiments/1110619',
            },
            'value': 'ANTARES',
        },
        {
            'record': {
                '$ref': 'http://localhost:5000/api/experiments/1108514',
            },
            'value': 'IceCube',
        },
        {
            'value': 'LIGO Scientific',
        },
        {
            'record': {
                '$ref': 'http://localhost:5000/api/experiments/1110601',
            },
            'value': 'Virgo',
        },
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['collaborations'], subschema) is None
    assert expected == result['collaborations']

    expected = [
        {'g': 'ANTARES'},
        {'g': 'IceCube'},
        {'g': 'LIGO Scientific'},
        {'g': 'Virgo'},
    ]
    result = hep2marc.do(result)

    assert expected == result['710']


def test_collaborations_from_710__double_g_does_not_raise():
    schema = load_schema('hep')
    subschema = schema['properties']['collaborations']

    snippet = (  # record/1665755
        '<datafield tag="710" ind1=" " ind2=" ">'
        '  <subfield code="g">ATLAS</subfield>'
        '  <subfield code="g">CMS</subfield>'
        '</datafield>'
    )

    expected = [
        {'value': 'ATLAS'},
        {'value': 'CMS'},
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['collaborations'], subschema) is None
    assert expected == result['collaborations']

    expected = [
        {'g': 'ATLAS'},
        {'g': 'CMS'},
    ]
    result = hep2marc.do(result)

    assert expected == result['710']


def test_publication_info_from_773_c_m_p_v_y_1():
    schema = load_schema('hep')
    subschema = schema['properties']['publication_info']

    snippet = (  # record/1104
        '<datafield tag="773" ind1=" " ind2=" ">'
        '  <subfield code="m">Erratum</subfield>'
        '  <subfield code="p">Phys.Rev.Lett.</subfield>'
        '  <subfield code="v">35</subfield>'
        '  <subfield code="c">130</subfield>'
        '  <subfield code="y">1975</subfield>'
        '  <subfield code="1">1214495</subfield>'
        '</datafield>'
    )

    expected = [
        {
            'artid': '130',
            'material': 'erratum',
            'journal_record': {
                '$ref': 'http://localhost:5000/api/journals/1214495',
            },
            'journal_title': 'Phys.Rev.Lett.',
            'journal_volume': '35',
            'page_start': '130',
            'year': 1975,
        },
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['publication_info'], subschema) is None
    assert expected == result['publication_info']

    expected = [
        {
            'c': [
                '130',
            ],
            'm': 'erratum',
            'p': 'Phys.Rev.Lett.',
            'v': '35',
            'y': 1975,
        },
    ]
    result = hep2marc.do(result)

    assert expected == result['773']


def test_publication_info_from_773_c_p_w_double_v_double_y_0_1_2():
    schema = load_schema('hep')
    subschema = schema['properties']['publication_info']

    snippet = (  # record/820763
        '<datafield tag="773" ind1=" " ind2=" ">'
        '  <subfield code="p">IAU Symp.</subfield>'
        '  <subfield code="w">C08-06-09</subfield>'
        '  <subfield code="v">354</subfield>'
        '  <subfield code="y">2008</subfield>'
        '  <subfield code="v">254</subfield>'
        '  <subfield code="y">2009</subfield>'
        '  <subfield code="c">45</subfield>'
        '  <subfield code="1">1212883</subfield>'
        '  <subfield code="2">978924</subfield>'
        '  <subfield code="0">1408366</subfield>'
        '</datafield>'
    )

    expected = [
        {
            'journal_title': 'IAU Symp.',
            'cnum': 'C08-06-09',
            'journal_volume': '354',
            'year': 2008,
            'artid': '45',
            'page_start': '45',
            'journal_record': {
                '$ref': 'http://localhost:5000/api/journals/1212883',
            },
            'parent_record': {
                '$ref': 'http://localhost:5000/api/literature/1408366',
            },
            'conference_record': {
                '$ref': 'http://localhost:5000/api/conferences/978924',
            },
        },
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['publication_info'], subschema) is None
    assert expected == result['publication_info']

    expected = [
        {
            '0': 1408366,
            'c': [
                '45',
            ],
            'p': 'IAU Symp.',
            'v': '354',
            'w': 'C08-06-09',
            'y': 2008,
        },
    ]
    result = hep2marc.do(result)

    assert expected == result['773']


def test_publication_info_from_773__c_w_y_z_0_2():
    schema = load_schema('hep')
    subschema = schema['properties']['publication_info']

    snippet = (  # record/1501319
        '<datafield tag="773" ind1=" " ind2=" ">'
        '  <subfield code="c">95-104</subfield>'
        '  <subfield code="w">C16-03-17</subfield>'
        '  <subfield code="y">2016</subfield>'
        '  <subfield code="z">9783945931080</subfield>'
        '  <subfield code="2">1407887</subfield>'
        '  <subfield code="0">1500425</subfield>'
        '</datafield>'
    )

    expected = [
        {
            'cnum': 'C16-03-17',
            'conference_record': {
                '$ref': 'http://localhost:5000/api/conferences/1407887',
            },
            'page_end': '104',
            'page_start': '95',
            'parent_isbn': '9783945931080',
            'parent_record': {
                '$ref': 'http://localhost:5000/api/literature/1500425',
            },
            'year': 2016,
        },
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['publication_info'], subschema) is None
    assert expected == result['publication_info']

    expected = [
        {
            '0': 1500425,
            'c': [
                '95-104',
            ],
            'w': 'C16-03-17',
            'y': 2016,
            'z': '9783945931080',
        },
    ]
    result = hep2marc.do(result)

    assert expected == result['773']


def test_publication_info_from_773__c_r_w_triple_0_2():
    schema = load_schema('hep')
    subschema = schema['properties']['publication_info']

    snippet = (  # record/1513005
        '<datafield tag="773" ind1=" " ind2=" ">'
        '  <subfield code="0">1512294</subfield>'
        '  <subfield code="c">122-127</subfield>'
        '  <subfield code="r">arXiv:1702.01329</subfield>'
        '  <subfield code="w">C16-11-21.1</subfield>'
        '  <subfield code="0">1512294</subfield>'
        '  <subfield code="2">1484403</subfield>'
        '  <subfield code="0">1512294</subfield>'
        '</datafield>'
    )

    expected = [
        {
            'cnum': 'C16-11-21.1',
            'conference_record': {
                '$ref': 'http://localhost:5000/api/conferences/1484403',
            },
            'page_end': '127',
            'page_start': '122',
            'parent_record': {
                '$ref': 'http://localhost:5000/api/literature/1512294',
            },
            'parent_report_number': 'arXiv:1702.01329',
        },
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['publication_info'], subschema) is None
    assert expected == result['publication_info']

    expected = [
        {
            '0': 1512294,
            'c': [
                '122-127',
            ],
            'r': 'arXiv:1702.01329',
            'w': 'C16-11-21.1',
        },
    ]
    result = hep2marc.do(result)

    assert expected == result['773']


def test_publication_info_from_773__q_t():
    schema = load_schema('hep')
    subschema = schema['properties']['publication_info']

    snippet = (  # record/1598069
        '<datafield tag="773" ind1=" " ind2=" ">  <subfield'
        ' code="q">LENPIC2017</subfield>  <subfield code="t">Chiral Forces in'
        ' Low Energy Nuclear Physics</subfield></datafield>'
    )

    expected = [
        {'conf_acronym': 'LENPIC2017'},
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['publication_info'], subschema) is None
    assert expected == result['publication_info']

    expected = [
        {'q': 'LENPIC2017'},
    ]
    result = hep2marc.do(result)

    assert expected == result['773']


def test_publication_info_from_773__w_x_0_2_handles_lowercase_cnums():
    schema = load_schema('hep')
    subschema = schema['properties']['publication_info']

    snippet = (  # record/1264637
        '<datafield tag="773" ind1=" " ind2=" ">  <subfield'
        ' code="w">c12-07-09.10</subfield>  <subfield code="x">Proceedings of'
        ' the 57th Annual Conference of the South African Institute of Physics,'
        ' edited by Johan Janse van Rensburg (2014), pp. 362 - 367</subfield> '
        ' <subfield code="2">1423475</subfield>  <subfield'
        ' code="0">1424370</subfield></datafield>'
    )

    expected = [
        {
            'cnum': 'C12-07-09.10',
            'conference_record': {
                '$ref': 'http://localhost:5000/api/conferences/1423475',
            },
            'parent_record': {
                '$ref': 'http://localhost:5000/api/literature/1424370',
            },
            'pubinfo_freetext': (
                'Proceedings of the 57th Annual Conference of the South African'
                ' Institute of Physics, edited by Johan Janse van Rensburg'
                ' (2014), pp. 362 - 367'
            ),
        },
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['publication_info'], subschema) is None
    assert expected == result['publication_info']

    expected = [
        {
            'w': 'C12-07-09.10',
            'x': (
                'Proceedings of the 57th Annual Conference of the South African'
                ' Institute of Physics, edited by Johan Janse van Rensburg'
                ' (2014), pp. 362 - 367'
            ),
            '0': 1424370,
        },
    ]
    result = hep2marc.do(result)

    assert expected == result['773']


def test_publication_info_from_773__w_handles_slashes_in_cnums():
    schema = load_schema('hep')
    subschema = schema['properties']['publication_info']

    snippet = (  # record/1622968
        '<datafield tag="773" ind1=" " ind2=" ">'
        '  <subfield code="w">C17/05/14</subfield>'
        '</datafield>'
    )

    expected = [
        {'cnum': 'C17-05-14'},
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['publication_info'], subschema) is None
    assert expected == result['publication_info']

    expected = [
        {'w': 'C17-05-14'},
    ]
    result = hep2marc.do(result)

    assert expected == result['773']


def test_publication_info_from_773__c_z_handles_dashes_in_isbns():
    schema = load_schema('hep')
    subschema = schema['properties']['publication_info']

    snippet = (  # record/1334853
        '<datafield tag="773" ind1=" " ind2=" ">'
        '  <subfield code="c">110-125</subfield>'
        '  <subfield code="z">978-1-4684-7552-4</subfield>'
        '</datafield>'
    )

    expected = [
        {
            'page_end': '125',
            'page_start': '110',
            'parent_isbn': '9781468475524',
        },
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['publication_info'], subschema) is None
    assert expected == result['publication_info']

    expected = [
        {
            'c': [
                '110-125',
            ],
            'z': '9781468475524',
        },
    ]
    result = hep2marc.do(result)

    assert expected == result['773']


def test_publication_info_from_773__p_populates_public_notes():
    schema = load_schema('hep')
    subschema = schema['properties']['public_notes']

    snippet = (  # record/1631620
        '<datafield tag="773" ind1=" " ind2=" ">'
        '  <subfield code="p">Phys.Rev.D</subfield>'
        '</datafield>'
    )

    expected = [
        {'value': 'Submitted to Phys.Rev.D'},
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['public_notes'], subschema) is None
    assert expected == result['public_notes']
    assert 'publication_info' not in result


def test_publication_info_from_773__p_1_populates_public_notes():
    schema = load_schema('hep')
    subschema = schema['properties']['public_notes']

    snippet = (  # record/1470899
        '<datafield tag="773" ind1=" " ind2=" ">'
        '  <subfield code="p">Phys.Rev.Lett.</subfield>'
        '  <subfield code="1">1214495</subfield>'
        '</datafield>'
    )

    expected = [
        {'value': 'Submitted to Phys.Rev.Lett.'},
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['public_notes'], subschema) is None
    assert expected == result['public_notes']
    assert 'publication_info' not in result


def test_publication_info_from_773__t_doesnt_populate_public_notes():
    snippet = (  # record/1763998
        '<datafield tag="773" ind1=" " ind2=" ">  <subfield code="t">Indian'
        ' Particle Accelerator Conference (InPAC)</subfield></datafield>'
    )

    result = hep.do(create_record(snippet))

    assert 'public_notes' not in result
    assert 'publication_info' not in result


def test_publication_info_from_773__p_and_773__c_p_v_y_1_also_populates_public_notes():
    schema = load_schema('hep')
    publication_info_schema = schema['properties']['publication_info']
    public_notes_schema = schema['properties']['public_notes']

    snippet = (  # record/769448
        '<record>'
        '  <datafield tag="773" ind1=" " ind2=" ">'
        '    <subfield code="p">Eur.Phys.J.A</subfield>'
        '  </datafield>'
        '  <datafield tag="773" ind1=" " ind2=" ">'
        '    <subfield code="p">Eur.Phys.J.</subfield>'
        '    <subfield code="v">B64</subfield>'
        '    <subfield code="c">615</subfield>'
        '    <subfield code="y">2008</subfield>'
        '    <subfield code="1">1212905</subfield>'
        '  </datafield>'
        '</record>'
    )

    expected_public_notes = [{'value': 'Submitted to Eur.Phys.J.A'}]
    expected_publication_info = [
        {
            'artid': '615',
            'journal_title': 'Eur.Phys.J.B',
            'journal_volume': '64',
            'page_start': '615',
            'year': 2008,
        },
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['publication_info'], publication_info_schema) is None
    assert expected_publication_info == result['publication_info']

    assert validate(result['public_notes'], public_notes_schema) is None
    assert expected_public_notes == result['public_notes']


def test_publication_info_from_double_773__p():
    schema = load_schema('hep')
    subschema = schema['properties']['public_notes']

    snippet = (  # record/920292
        '<record>  <datafield tag="773" ind1=" " ind2=" ">    <subfield'
        ' code="p">Proc.HELAS Workshop on `New insights into the'
        ' Sun\'</subfield>  </datafield>  <datafield tag="773" ind1=" " ind2="'
        ' ">    <subfield code="p">&amp; M.J.Thompson (2009)</subfield> '
        ' </datafield></record>'
    )

    expected = [
        {'value': 'Submitted to Proc.HELAS Workshop on `New insights into the Sun\''},
        {'value': 'Submitted to & M.J.Thompson (2009)'},
    ]
    result = hep.do(create_record(snippet))

    assert 'publication_info' not in result

    assert validate(result['public_notes'], subschema) is None
    assert expected == result['public_notes']


def test_publication_info_from_773__c_p_v_x_y_1_discards_done_x():
    schema = load_schema('hep')
    subschema = schema['properties']['publication_info']

    snippet = (  # record/1479030
        '<datafield tag="773" ind1=" " ind2=" ">'
        '  <subfield code="c">134516</subfield>'
        '  <subfield code="p">Phys.Rev.</subfield>'
        '  <subfield code="v">B93</subfield>'
        '  <subfield code="x">#DONE: Phys. Rev. B 93, 134516 (2016)</subfield>'
        '  <subfield code="y">2016</subfield>'
        '  <subfield code="1">1214516</subfield>'
        '</datafield>'
    )

    expected = [
        {
            'artid': '134516',
            'journal_title': 'Phys.Rev.B',
            'journal_volume': '93',
            'year': 2016,
        },
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['publication_info'], subschema) is None
    assert expected == result['publication_info']

    expected = [
        {
            'c': [
                '134516',
            ],
            'p': 'Phys.Rev.',
            'v': 'B93',
            'y': 2016,
        },
    ]
    result = hep2marc.do(result)

    assert expected == result['773']


def test_publication_info_from_7731_c_p_v_y():
    schema = load_schema('hep')
    subschema = schema['properties']['publication_info']

    snippet = (  # record/697133
        '<datafield tag="773" ind1="1" ind2=" ">'
        '  <subfield code="c">948-979</subfield>'
        '  <subfield code="p">Adv.Theor.Math.Phys.</subfield>'
        '  <subfield code="v">12</subfield>'
        '  <subfield code="y">2008</subfield>'
        '</datafield>'
    )

    expected = [
        {
            'hidden': True,
            'journal_title': 'Adv.Theor.Math.Phys.',
            'journal_volume': '12',
            'page_end': '979',
            'page_start': '948',
            'year': 2008,
        },
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['publication_info'], subschema) is None
    assert expected == result['publication_info']

    expected = [
        {
            'c': [
                '948-979',
            ],
            'p': 'Adv.Theor.Math.Phys.',
            'v': '12',
            'y': 2008,
        },
    ]
    result = hep2marc.do(result)

    assert expected == result['7731']


def test_publication_info_from_7731_c_p_v_y_and_773__c_p_v_y_1():
    schema = load_schema('hep')
    subschema = schema['properties']['publication_info']

    snippet = (  # record/1439897
        '<record>'
        '  <datafield tag="773" ind1="1" ind2=" ">'
        '    <subfield code="c">602-604</subfield>'
        '    <subfield code="p">Phys.Lett.</subfield>'
        '    <subfield code="v">B40</subfield>'
        '    <subfield code="y">1972</subfield>'
        '  </datafield>'
        '  <datafield tag="773" ind1=" " ind2=" ">'
        '    <subfield code="c">602-604</subfield>'
        '    <subfield code="p">Phys.Lett.</subfield>'
        '    <subfield code="v">40B</subfield>'
        '    <subfield code="y">1972</subfield>'
        '    <subfield code="1">1214521</subfield>'
        '  </datafield>'
        '</record>'
    )

    expected = [
        {
            'journal_title': 'Phys.Lett.B',
            'journal_volume': '40',
            'page_start': '602',
            'page_end': '604',
            'year': 1972,
        },
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['publication_info'], subschema) is None
    assert expected == result['publication_info']

    expected_773 = [
        {
            'c': [
                '602-604',
            ],
            'p': 'Phys.Lett.',
            'v': '40B',
            'y': 1972,
        },
    ]
    expected_7731 = [
        {
            'c': [
                '602-604',
            ],
            'p': 'Phys.Lett.',
            'v': 'B40',
            'y': 1972,
        },
    ]
    result = hep2marc.do(result)

    assert expected_773 == result['773']
    assert expected_7731 == result['7731']


def test_publication_info2marc_handles_unicode():
    schema = load_schema('hep')
    subschema = schema['properties']['publication_info']

    record = {
        'publication_info': [
            {
                'artid': u'207–214',
                'journal_issue': '36',
                'journal_title': 'Electronic Journal of Theoretical Physics',
                'journal_volume': '13',
                'year': 2016,
            },
        ],
    }  # holdingpen/650664
    assert validate(record['publication_info'], subschema) is None

    expected = [
        {
            'c': [
                u'207–214',
            ],
            'n': '36',
            'p': 'Electronic Journal of Theoretical Physics',
            'v': '13',
            'y': 2016,
        },
    ]
    result = hep2marc.do(record)

    assert expected == result['773']


def test_related_records_from_78002i_r_w():
    schema = load_schema('hep')
    subschema = schema['properties']['related_records']

    snippet = (  # record/1510564
        '<datafield tag="780" ind1="0" ind2="2">'
        '  <subfield code="i">supersedes</subfield>'
        '  <subfield code="r">ATLAS-CONF-2016-113</subfield>'
        '  <subfield code="w">1503270</subfield>'
        '</datafield>'
    )

    expected = [
        {
            'curated_relation': True,
            'record': {
                '$ref': 'http://localhost:5000/api/literature/1503270',
            },
            'relation': 'predecessor',
        },
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['related_records'], subschema) is None
    assert expected == result['related_records']

    expected = [
        {
            'i': 'supersedes',
            'w': 1503270,
        },
    ]
    result = hep2marc.do(result)

    assert expected == result['78002']


def test_related_superseding_records_78502r_w_z():
    schema = load_schema('hep')
    subschema = schema['properties']['related_records']
    snippet = (  # record/1503270
        '<datafield tag="785" ind1="0" ind2="2">'
        '<subfield code="i">superseded by</subfield>'
        '<subfield code="r">CERN-EP-2016-305</subfield>'
        '<subfield code="w">1510564</subfield>'
        '</datafield>'
    )

    expected = [
        {
            'curated_relation': True,
            'record': {
                '$ref': 'http://localhost:5000/api/literature/1510564',
            },
            'relation': 'successor',
        },
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['related_records'], subschema) is None
    assert expected == result['related_records']
    expected = [
        {
            'i': 'superseded by',
            'w': 1510564,
        },
    ]
    result = hep2marc.do(result)

    assert expected == result['78502']


def test_related_records_from_78708i_w():
    schema = load_schema('hep')
    subschema = schema['properties']['related_records']

    snippet = (  # record/1415979
        '<datafield tag="787" ind1="0" ind2="8">'
        '  <subfield code="i">Addendum</subfield>'
        '  <subfield code="w">1474710</subfield>'
        '</datafield>'
    )

    expected = [
        {
            'curated_relation': True,
            'record': {
                '$ref': 'http://localhost:5000/api/literature/1474710',
            },
            'relation_freetext': 'Addendum',
        },
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['related_records'], subschema) is None
    assert expected == result['related_records']

    expected = [
        {
            'i': 'Addendum',
            'w': 1474710,
        },
    ]
    result = hep2marc.do(result)

    assert expected == result['78708']
