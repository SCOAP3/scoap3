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

from inspire_dojson.conferences import conferences


def test_addresses_from_034__d_f_and_111__c():
    schema = load_schema('conferences')
    subschema = schema['properties']['addresses']

    snippet = (  # record/1707423
        '<record>'
        '  <datafield tag="034" ind1=" " ind2=" ">'
        '    <subfield code="d">11.3426162</subfield>'
        '    <subfield code="f">44.494887</subfield>'
        '  </datafield>'
        '  <datafield tag="111" ind1=" " ind2=" ">'
        '    <subfield code="c">Bologna, Italy</subfield>'
        '  </datafield>'
        '</record>'
    )

    expected = [
        {
            'cities': ['Bologna'],
            'country_code': 'IT',
            'latitude': 44.494887,
            'longitude': 11.3426162,
        }
    ]
    result = conferences.do(create_record(snippet))

    assert validate(result['addresses'], subschema) is None
    assert expected == result['addresses']


def test_acronyms_from_111__a_c_e_g_x_y():
    schema = load_schema('conferences')
    subschema = schema['properties']['acronyms']

    snippet = (  # record/1468357
        '<datafield tag="111" ind1=" " ind2=" ">  <subfield code="a">16th'
        ' Conference on Flavor Physics and CP Violation</subfield>  <subfield'
        ' code="c">Hyderabad, INDIA</subfield>  <subfield code="e">FPCP'
        ' 2018</subfield>  <subfield code="g">C18-07-09</subfield>  <subfield'
        ' code="x">2018-07-09</subfield>  <subfield'
        ' code="y">2018-07-12</subfield></datafield>'
    )

    expected = [
        'FPCP 2018',
    ]
    result = conferences.do(create_record(snippet))

    assert validate(result['acronyms'], subschema) is None
    assert expected == result['acronyms']


def test_acronyms_from_111__a_c_d_double_e_g_x_y():
    schema = load_schema('conferences')
    subschema = schema['properties']['acronyms']

    snippet = (  # record/1308774
        '<datafield tag="111" ind1=" " ind2=" ">  <subfield code="a">11th'
        ' international vacuum congress and 7th international conference on'
        ' solid surfaces</subfield>  <subfield code="c">Cologne,'
        ' Germany</subfield>  <subfield code="d">25 – 29 Sep 1989</subfield> '
        ' <subfield code="e">IVC-11</subfield>  <subfield'
        ' code="e">ICSS-7</subfield>  <subfield code="g">C89-09-25.3</subfield>'
        '  <subfield code="x">1989-09-25</subfield>  <subfield'
        ' code="y">1989-09-29</subfield></datafield>'
    )

    expected = [
        'IVC-11',
        'ICSS-7',
    ]
    result = conferences.do(create_record(snippet))

    assert validate(result['acronyms'], subschema) is None
    assert expected == result['acronyms']


def test_acronyms_from_111__a_c_double_e_g_x_y():
    schema = load_schema('conferences')
    subschema = schema['properties']['acronyms']

    snippet = (  # record/1218346
        '<datafield tag="111" ind1=" " ind2=" ">  <subfield code="a">2013 IEEE'
        ' Nuclear Science Symposium and Medical Imaging Conference and Workshop'
        ' on Room-Temperature Semiconductor Detectors</subfield>  <subfield'
        ' code="c">Seoul, Korea</subfield>  <subfield code="e">NSS/MIC'
        ' 2013</subfield>  <subfield code="e">RTSD 2013</subfield>  <subfield'
        ' code="g">C13-10-26</subfield>  <subfield'
        ' code="x">2013-10-26</subfield>  <subfield'
        ' code="y">2013-11-02</subfield></datafield>'
    )

    expected = [
        'NSS/MIC 2013',
        'RTSD 2013',
    ]
    result = conferences.do(create_record(snippet))

    assert validate(result['acronyms'], subschema) is None
    assert expected == result['acronyms']


def test_addresses_from_111__a_c_d_g_x_y():
    schema = load_schema('conferences')
    subschema = schema['properties']['addresses']

    snippet = (  # record/965081
        '<datafield tag="111" ind1=" " ind2=" ">  <subfield code="a">11th Texas'
        ' Symposium on Relativistic Astrophysics</subfield>  <subfield'
        ' code="c">Austin, Tex.</subfield>  <subfield code="d">13-17 Dec'
        ' 1982</subfield>  <subfield code="g">C82-12-13</subfield>  <subfield'
        ' code="x">1982-12-13</subfield>  <subfield'
        ' code="y">1982-12-17</subfield></datafield>'
    )

    expected = [
        {
            'cities': [
                'Austin',
            ],
            'country_code': 'US',
            'state': 'TX',
        },
    ]
    result = conferences.do(create_record(snippet))

    assert validate(result['addresses'], subschema) is None
    assert expected == result['addresses']


def test_addresses_from_111__a_c_d_g_x_y_and_111__c():
    schema = load_schema('conferences')
    subschema = schema['properties']['addresses']

    snippet = (  # record/1220831
        '<record>  <datafield tag="111" ind1=" " ind2=" ">    <subfield'
        ' code="a">Low dimensional physics and gauge principles</subfield>   '
        ' <subfield code="c">Yerevan, Armenia</subfield>    <subfield'
        ' code="d">21-29 Sep 2011</subfield>    <subfield'
        ' code="g">C11-09-21.2</subfield>    <subfield'
        ' code="x">2011-09-21</subfield>    <subfield'
        ' code="y">2011-09-29</subfield>  </datafield>  <datafield tag="111"'
        ' ind1=" " ind2=" ">    <subfield code="c">Tbilisi, Georgia</subfield> '
        ' </datafield></record>'
    )

    expected = [
        {
            'cities': [
                'Yerevan',
            ],
            'country_code': 'AM',
        },
        {
            'cities': [
                'Tbilisi',
            ],
            'country_code': 'GE',
        },
    ]
    result = conferences.do(create_record(snippet))

    assert validate(result['addresses'], subschema) is None
    assert expected == result['addresses']


def test_addresses_from_111__a_double_c_d_e_g_x_y():
    schema = load_schema('conferences')
    subschema = schema['properties']['addresses']

    snippet = (  # record/1085463
        '<datafield tag="111" ind1=" " ind2=" ">  <subfield code="a">16th'
        ' High-Energy Physics International Conference in Quantum'
        ' Chromodynamics</subfield>  <subfield code="c">QCD 12</subfield> '
        ' <subfield code="c">Montpellier, France</subfield>  <subfield'
        ' code="d">2-7 Jul 2012</subfield>  <subfield code="e">QCD'
        ' 12</subfield>  <subfield code="g">C12-07-02</subfield>  <subfield'
        ' code="x">2012-07-02</subfield>  <subfield'
        ' code="y">2012-07-07</subfield></datafield>'
    )

    expected = [
        {
            'place_name': 'QCD 12',
        },  # XXX: Wrong, but the best we can do.
        {
            'cities': [
                'Montpellier',
            ],
            'country_code': 'FR',
        },
    ]
    result = conferences.do(create_record(snippet))

    assert validate(result['addresses'], subschema) is None
    assert expected == result['addresses']


def test_addresses_from_111__a_c_d_e_g_x_y_three_address_parts():
    schema = load_schema('conferences')
    subschema = schema['properties']['addresses']

    snippet = (  # record/1781388
        '<datafield tag="111" ind1=" " ind2=" ">   <subfield code="a">10th Int.'
        ' Conf. DICE2020: Spacetime - Matter - Quantum Mechanics</subfield>  '
        ' <subfield code="e">DICE2020</subfield>   <subfield'
        ' code="x">2020-09-14</subfield>   <subfield'
        ' code="y">2020-09-18</subfield>   <subfield code="c">Castiglioncello ,'
        ' Tuscany, Italy</subfield>   <subfield'
        ' code="g">C20-09-14.1</subfield></datafield>'
    )

    expected = [
        {
            'cities': [
                'Castiglioncello',
            ],
            'state': 'Tuscany',
            'country_code': 'IT',
        },
    ]
    result = conferences.do(create_record(snippet))

    assert validate(result['addresses'], subschema) is None
    assert expected == result['addresses']


def test_addresses_from_111__a_c_d_e_g_x_y_many_address_parts():
    schema = load_schema('conferences')
    subschema = schema['properties']['addresses']

    snippet = (  # record/1699363
        '<datafield tag="111" ind1=" " ind2=" ">  <subfield code="a">Higher'
        ' structures in Holomorphic and Topological Field Theory</subfield> '
        ' <subfield code="x">2019-01-14</subfield>  <subfield'
        ' code="y">2019-01-18</subfield>  <subfield code="c">IHES,'
        ' Bures-sur-Yvette, Paris area, France</subfield>  <subfield'
        ' code="g">C19-01-14.1</subfield></datafield>'
    )

    expected = [
        {
            'cities': [
                'IHES',
            ],  # XXX: Wrong, but better than dropping data
            'place_name': 'Bures-sur-Yvette',
            'state': 'Paris area',
            'country_code': 'FR',
        },
    ]
    result = conferences.do(create_record(snippet))

    assert validate(result['addresses'], subschema) is None
    assert expected == result['addresses']


def test_addresses_from_270__b():
    schema = load_schema('conferences')
    subschema = schema['properties']['addresses']

    snippet = (  # record/1430104
        '<datafield tag="270" ind1=" " ind2=" ">'
        '  <subfield code="b">British Columbia</subfield>'
        '</datafield>'
    )

    expected = [
        {'place_name': 'British Columbia'},
    ]
    result = conferences.do(create_record(snippet))

    assert validate(result['addresses'], subschema) is None
    assert expected == result['addresses']


def test_addresses_from_111__a_c_e_g_x_y_and_270__b():
    schema = load_schema('conferences')
    subschema = schema['properties']['addresses']

    snippet = (  # record/1353313
        '<record>  <datafield tag="111" ind1=" " ind2=" ">    <subfield'
        ' code="a">2017 International Workshop on Baryon and Lepton Number'
        ' Violation: From the Cosmos to the LHC</subfield>    <subfield'
        ' code="c">Cleveland, Ohio, USA</subfield>    <subfield code="e">BLV'
        ' 2017</subfield>    <subfield code="g">C17-05-15</subfield>   '
        ' <subfield code="x">2017-05-15</subfield>    <subfield'
        ' code="y">2017-05-18</subfield>  </datafield>  <datafield tag="270"'
        ' ind1=" " ind2=" ">    <subfield code="b">Case Western Reserve'
        ' University</subfield>  </datafield></record>'
    )

    expected = [
        {
            'cities': [
                'Cleveland',
            ],
            'country_code': 'US',
            'state': 'OH',
        },
        {'place_name': 'Case Western Reserve University'},
    ]
    result = conferences.do(create_record(snippet))

    assert validate(result['addresses'], subschema) is None
    assert expected == result['addresses']


def test_titles_from_111__a_c_d_g_x_y():
    schema = load_schema('conferences')
    subschema = schema['properties']['titles']

    snippet = (
        '<datafield tag="111" ind1=" " ind2=" ">'
        '  <subfield code="a">NASA Laboratory Astrophysics Workshop</subfield>'
        '  <subfield code="d">14-16 Feb 2006</subfield>'
        '  <subfield code="x">2006-02-14</subfield>'
        '  <subfield code="c">Las Vegas, Nevada</subfield>'
        '  <subfield code="g">C06-02-14</subfield>'
        '  <subfield code="y">2006-02-16</subfield>'
        '</datafield>'
    )

    expected = [
        {'title': 'NASA Laboratory Astrophysics Workshop'},
    ]
    result = conferences.do(create_record(snippet))

    assert validate(result['titles'], subschema) is None
    assert expected == result['titles']


def test_titles_from_111__double_a_b():
    schema = load_schema('conferences')
    subschema = schema['properties']['titles']

    snippet = (
        '<datafield tag="111" ind1=" " ind2=" ">'
        '  <subfield code="a">Conférence IAP 2013</subfield>'
        '  <subfield code="a">75 Anniversary Conference</subfield>'
        '  <subfield code="b">The origin of the Hubble sequence</subfield>'
        '</datafield>'
    )

    expected = [
        {
            'title': u'Conférence IAP 2013',
            'subtitle': 'The origin of the Hubble sequence',
        },
        {
            'title': '75 Anniversary Conference',
            'subtitle': 'The origin of the Hubble sequence',
        },
    ]
    result = conferences.do(create_record(snippet))

    assert validate(result['titles'], subschema) is None
    assert expected == result['titles']


def test_opening_date_from_111__x_handles_incomplete_dates_with_year_and_month():
    schema = load_schema('conferences')
    subschema = schema['properties']['opening_date']

    snippet = (  # record/1442284
        '<datafield tag="111" ind1=" " ind2=" ">'
        '  <subfield code="x">2001-02-00</subfield>'
        '</datafield>'
    )

    expected = '2001-02'
    result = conferences.do(create_record(snippet))

    assert validate(result['opening_date'], subschema) is None
    assert expected == result['opening_date']


def test_opening_date_from_111__x_handles_incomplete_dates():
    schema = load_schema('conferences')
    subschema = schema['properties']['opening_date']

    snippet = (  # record/1477158
        '<datafield tag="111" ind1=" " ind2=" ">'
        '  <subfield code="x">1999-07</subfield>'
        '</datafield>'
    )

    expected = '1999-07'
    result = conferences.do(create_record(snippet))

    assert validate(result['opening_date'], subschema) is None
    assert expected == result['opening_date']


def test_opening_date_from_111__x_handles_unseparated_dates():
    schema = load_schema('conferences')
    subschema = schema['properties']['opening_date']

    snippet = (  # record/1280577
        '<datafield tag="111" ind1=" " ind2=" ">'
        '    <subfield code="x">20140518</subfield>'
        '</datafield>'
    )

    expected = '2014-05-18'
    result = conferences.do(create_record(snippet))

    assert validate(result['opening_date'], subschema) is None
    assert expected == result['opening_date']


def test_closing_date_from_111__y_handles_incomplete_dates_with_only_year():
    schema = load_schema('conferences')
    subschema = schema['properties']['closing_date']

    snippet = (  # record/1372837
        '<datafield tag="111" ind1=" " ind2=" ">'
        '  <subfield code="y">1967-00-00</subfield>'
        '</datafield>'
    )

    expected = '1967'
    result = conferences.do(create_record(snippet))

    assert validate(result['closing_date'], subschema) is None
    assert expected == result['closing_date']


def test_contact_details_from_270__m_p():
    schema = load_schema('conferences')
    subschema = schema['properties']['contact_details']

    snippet = (  # record/1517305
        '<datafield tag="270" ind1=" " ind2=" ">'
        '  <subfield code="m">jonivar@thphys.nuim.ie</subfield>'
        '  <subfield code="p">Jon-Ivar Skullerud</subfield>'
        '</datafield>'
    )

    expected = [
        {
            'email': 'jonivar@thphys.nuim.ie',
            'name': 'Jon-Ivar Skullerud',
        },
    ]
    result = conferences.do(create_record(snippet))

    assert validate(result['contact_details'], subschema) is None
    assert expected == result['contact_details']


def test_series_from_411__a():
    schema = load_schema('conferences')
    subschema = schema['properties']['series']

    snippet = (  # record/1430017
        '<datafield tag="411" ind1=" " ind2=" ">'
        '  <subfield code="a">DPF Series</subfield>'
        '</datafield>'
    )

    expected = [
        {'name': 'DPF Series'},
    ]
    result = conferences.do(create_record(snippet))

    assert validate(result['series'], subschema) is None
    assert expected == result['series']


def test_series_from_411__n():
    snippet = (  # record/1447029
        '<datafield tag="411" ind1=" " ind2=" ">'
        '  <subfield code="n">7</subfield>'
        '</datafield>'
    )

    result = conferences.do(create_record(snippet))

    assert 'series' not in result


def test_series_from_411__a_n():
    schema = load_schema('conferences')
    subschema = schema['properties']['series']

    snippet = (  # record/1468357
        '<datafield tag="411" ind1=" " ind2=" ">'
        '  <subfield code="a">FPCP</subfield>'
        '  <subfield code="n">16</subfield>'
        '</datafield>'
    )

    expected = [
        {
            'name': 'FPCP',
            'number': 16,
        },
    ]
    result = conferences.do(create_record(snippet))

    assert validate(result['series'], subschema) is None
    assert expected == result['series']


def test_series_from_411__a_n_and_411__a():
    schema = load_schema('conferences')
    subschema = schema['properties']['series']

    snippet = (  # record/1404073
        '<record>'
        '  <datafield tag="411" ind1=" " ind2=" ">'
        '    <subfield code="a">Rencontres de Moriond</subfield>'
        '    <subfield code="n">51</subfield>'
        '  </datafield>'
        '  <datafield tag="411" ind1=" " ind2=" ">'
        '    <subfield code="a">Moriond EW</subfield>'
        '  </datafield>'
        '</record>'
    )

    expected = [
        {
            'name': 'Rencontres de Moriond',
            'number': 51,
        },
        {
            'name': 'Moriond EW',
        },
    ]
    result = conferences.do(create_record(snippet))

    assert validate(result['series'], subschema) is None
    assert expected == result['series']


def test_series_from_411__a_n_and_411__n():
    schema = load_schema('conferences')
    subschema = schema['properties']['series']

    snippet = (  # record/963769
        '<record>'
        '  <datafield tag="411" ind1=" " ind2=" ">'
        '    <subfield code="a">SSI</subfield>'
        '    <subfield code="n">x</subfield>'
        '  </datafield>'
        '  <datafield tag="411" ind1=" " ind2=" ">'
        '    <subfield code="n">2</subfield>'
        '  </datafield>'
        '</record>'
    )

    expected = [
        {
            'name': 'SSI',
            'number': 2,
        },
    ]
    result = conferences.do(create_record(snippet))

    assert validate(result['series'], subschema) is None
    assert expected == result['series']


def test_series_from_double_411__a_n():
    schema = load_schema('conferences')
    subschema = schema['properties']['series']

    snippet = (  # record/974856
        '<record>'
        '  <datafield tag="411" ind1=" " ind2=" ">'
        '    <subfield code="a">ICHEP</subfield>'
        '    <subfield code="n">5</subfield>'
        '  </datafield>'
        '  <datafield tag="411" ind1=" " ind2=" ">'
        '    <subfield code="a">Rochester</subfield>'
        '    <subfield code="n">5</subfield>'
        '  </datafield>'
        '</record>'
    )

    expected = [
        {
            'name': 'ICHEP',
            'number': 5,
        },
        {
            'name': 'Rochester',
            'number': 5,
        },
    ]
    result = conferences.do(create_record(snippet))

    assert validate(result['series'], subschema) is None
    assert expected == result['series']


def test_series_from_411__n_and_411__a_n():
    schema = load_schema('conferences')
    subschema = schema['properties']['series']

    snippet = (  # record/963914
        '<record>'
        '  <datafield tag="411" ind1=" " ind2=" ">'
        '    <subfield code="n">3</subfield>'
        '  </datafield>'
        '  <datafield tag="411" ind1=" " ind2=" ">'
        '    <subfield code="a">WIN</subfield>'
        '    <subfield code="n">3</subfield>'
        '  </datafield>'
        '</record>'
    )

    expected = [
        {
            'name': 'WIN',
            'number': 3,
        },
    ]
    result = conferences.do(create_record(snippet))

    assert validate(result['series'], subschema) is None
    assert expected == result['series']


def test_series_from_411__n_and_411__a():
    schema = load_schema('conferences')
    subschema = schema['properties']['series']

    snippet = (  # record/972145
        '<record>'
        '  <datafield tag="411" ind1=" " ind2=" ">'
        '    <subfield code="n">3</subfield>'
        '  </datafield>'
        '  <datafield tag="411" ind1=" " ind2=" ">'
        '    <subfield code="a">Gordon</subfield>'
        '  </datafield>'
        '</record>'
    )

    expected = [
        {
            'name': 'Gordon',
            'number': 3,
        },
    ]
    result = conferences.do(create_record(snippet))

    assert validate(result['series'], subschema) is None
    assert expected == result['series']


def test_series_from_double_411__a():
    schema = load_schema('conferences')
    subschema = schema['properties']['series']

    snippet = (  # record/964177
        '<record>'
        '  <datafield tag="411" ind1=" " ind2=" ">'
        '    <subfield code="a">SNPS</subfield>'
        '  </datafield>'
        '  <datafield tag="411" ind1=" " ind2=" ">'
        '    <subfield code="a">NSS</subfield>'
        '  </datafield>'
        '</record>'
    )

    expected = [
        {
            'name': 'SNPS',
        },
        {
            'name': 'NSS',
        },
    ]
    result = conferences.do(create_record(snippet))

    assert validate(result['series'], subschema) is None
    assert expected == result['series']


def test_series_from_411__a_and_411__a_n():
    schema = load_schema('conferences')
    subschema = schema['properties']['series']

    snippet = (  # record/964448
        '<record>'
        '  <datafield tag="411" ind1=" " ind2=" ">'
        '    <subfield code="a">CEC</subfield>'
        '  </datafield>'
        '  <datafield tag="411" ind1=" " ind2=" ">'
        '    <subfield code="a">ICMC</subfield>'
        '    <subfield code="n">2</subfield>'
        '  </datafield>'
        '</record>'
    )

    expected = [
        {
            'name': 'CEC',
        },
        {
            'name': 'ICMC',
            'number': 2,
        },
    ]
    result = conferences.do(create_record(snippet))

    assert validate(result['series'], subschema) is None
    assert expected == result['series']


def test_public_notes_from_500__a():
    schema = load_schema('conferences')
    subschema = schema['properties']['public_notes']

    snippet = (  # record/963579
        '<datafield tag="500" ind1=" " ind2=" ">  <subfield code="a">Same conf.'
        ' as Kyoto 1975: none in intervening years</subfield></datafield>'
    )

    expected = [
        {'value': 'Same conf. as Kyoto 1975: none in intervening years'},
    ]
    result = conferences.do(create_record(snippet))

    assert validate(result['public_notes'], subschema) is None
    assert expected == result['public_notes']


def test_public_notes_from_double_500__a():
    schema = load_schema('conferences')
    subschema = schema['properties']['public_notes']

    snippet = (  # record/1445071
        '<record>  <datafield tag="500" ind1=" " ind2=" ">    <subfield'
        ' code="a">Marion White, PhD (Argonne) Conference Chair Vladimir'
        ' Shiltsev, PhD (FNAL) Scientific Program Chair Maria Power (Argonne)'
        ' Conference Editor/Scientific Secretariat</subfield>  </datafield> '
        ' <datafield tag="500" ind1=" " ind2=" ">    <subfield code="a">Will be'
        ' published in: JACoW</subfield>  </datafield></record>'
    )

    expected = [
        {
            'value': (
                'Marion White, PhD (Argonne) Conference Chair Vladimir'
                ' Shiltsev, PhD (FNAL) Scientific Program Chair Maria Power'
                ' (Argonne) Conference Editor/Scientific Secretariat'
            )
        },
        {'value': 'Will be published in: JACoW'},
    ]
    result = conferences.do(create_record(snippet))

    assert validate(result['public_notes'], subschema) is None
    assert expected == result['public_notes']


def test_short_description_from_520__a():
    schema = load_schema('conferences')
    subschema = schema['properties']['short_description']

    snippet = (  # record/1326067
        '<datafield tag="520" ind1=" " ind2=" ">  <subfield code="a">QNP2015 is'
        ' the Seventh International Conference on Quarks and Nuclear Physics.'
        ' It is anticipated that QCD practitioners, both experimentalists and'
        ' theorists, will gather at the Universidad Técnica Federico Santa'
        ' María, in Valparaíso, Chile during the week of March 2, 2015 to'
        ' present and discuss the latest advances in the field. The following'
        ' topics will be covered: quarks and gluons content of nucleons and'
        ' nuclei, hadron spectroscopy, non-perturbative methods in QCD'
        ' (including lattice calculations), effective field theories, nuclear'
        ' matter under extreme conditions and nuclear medium. Participants'
        ' should register at the conference website'
        ' https://indico.cern.ch/event/304663/</subfield></datafield>'
    )

    expected = {
        'value': (
            u'QNP2015 is the Seventh International Conference on Quarks and'
            u' Nuclear Physics. It is anticipated that QCD practitioners, both'
            u' experimentalists and theorists, will gather at the Universidad'
            u' Técnica Federico Santa María, in Valparaíso, Chile during the'
            u' week of March 2, 2015 to present and discuss the latest advances'
            u' in the field. The following topics will be covered: quarks and'
            u' gluons content of nucleons and nuclei, hadron spectroscopy,'
            u' non-perturbative methods in QCD (including lattice'
            u' calculations), effective field theories, nuclear matter under'
            u' extreme conditions and nuclear medium. Participants should'
            u' register at the conference website'
            u' https://indico.cern.ch/event/304663/'
        ),
    }
    result = conferences.do(create_record(snippet))

    assert validate(result['short_description'], subschema) is None
    assert expected == result['short_description']


def test_short_description_from_multiple_520__a():
    schema = load_schema('conferences')
    subschema = schema['properties']['short_description']

    snippet = (  # record/1288023
        '<record>  <datafield tag="520" ind1=" " ind2=" ">    <subfield'
        ' code="a">The alliance "Physics at the Terascale" will host "Proton'
        ' Structure in the LHC Era", from 29 September - 2 October, 2014 at'
        ' DESY in Hamburg. The planned structure will be a 2 day SCHOOL'
        ' (Monday-Tuesday) followed by a 2 day WORKSHOP (Wednesday-Thursday)'
        ' devoted to the current problems of the LHC data interpretation,'
        ' related to the particularities of QCD, factorization, proton'
        ' structure and higher order calculations.</subfield>  </datafield> '
        ' <datafield tag="520" ind1=" " ind2=" ">    <subfield code="a">SCHOOL:'
        ' (Monday-Tuesday, September 29-30, 2014) The school will address'
        ' mainly Ph.D. students and postdocs working at the LHC experiments. It'
        ' includes introductory lectures, accompanied by tutorials in'
        ' HERAFitter, FastNLO, Applgrid and further tools.</subfield> '
        ' </datafield>  <datafield tag="520" ind1=" " ind2=" ">    <subfield'
        ' code="a">WORKSHOP: (Wednesday-Thursday, October 1-2, 2014) The'
        ' following workshop will encompass the open issues in theory and'
        ' experiment concerning the determination of PDFs, heavy quark masses'
        ' and strong coupling. The workshop will run as an open session and is'
        ' more expert-oriented</subfield>  </datafield></record>'
    )

    expected = {
        'value': (
            'The alliance "Physics at the Terascale" will host "Proton'
            ' Structure in the LHC Era", from 29 September - 2 October, 2014 at'
            ' DESY in Hamburg. The planned structure will be a 2 day SCHOOL'
            ' (Monday-Tuesday) followed by a 2 day WORKSHOP'
            ' (Wednesday-Thursday) devoted to the current problems of the LHC'
            ' data interpretation, related to the particularities of QCD,'
            ' factorization, proton structure and higher order'
            ' calculations.\nSCHOOL: (Monday-Tuesday, September 29-30, 2014)'
            ' The school will address mainly Ph.D. students and postdocs'
            ' working at the LHC experiments. It includes introductory'
            ' lectures, accompanied by tutorials in HERAFitter, FastNLO,'
            ' Applgrid and further tools.\nWORKSHOP: (Wednesday-Thursday,'
            ' October 1-2, 2014) The following workshop will encompass the open'
            ' issues in theory and experiment concerning the determination of'
            ' PDFs, heavy quark masses and strong coupling. The workshop will'
            ' run as an open session and is more expert-oriented'
        ),
    }
    result = conferences.do(create_record(snippet))

    assert validate(result['short_description'], subschema) is None
    assert expected == result['short_description']


def test_alternative_titles_from_711__a():
    schema = load_schema('conferences')
    subschema = schema['properties']['alternative_titles']

    snippet = (  # record/1436454
        '<datafield tag="711" ind1=" " ind2=" ">'
        '  <subfield code="a">GCACSE16</subfield>'
        '</datafield>'
    )

    expected = [
        {'title': 'GCACSE16'},
    ]
    result = conferences.do(create_record(snippet))

    assert validate(result['alternative_titles'], subschema) is None
    assert expected == result['alternative_titles']


def test_alternative_titles_from_double_711__a():
    schema = load_schema('conferences')
    subschema = schema['properties']['alternative_titles']

    snippet = (  # record/1436454
        '<record>'
        '  <datafield tag="711" ind1=" " ind2=" ">'
        '    <subfield code="a">GCACSE16</subfield>'
        '  </datafield>'
        '  <datafield tag="711" ind1=" " ind2=" ">'
        '    <subfield code="a">GCACSE 2016</subfield>'
        '  </datafield>'
        '</record>'
    )

    expected = [
        {'title': 'GCACSE16'},
        {'title': 'GCACSE 2016'},
    ]
    result = conferences.do(create_record(snippet))

    assert validate(result['alternative_titles'], subschema) is None
    assert expected == result['alternative_titles']


def test_alternative_titles_from_711__a_b():
    schema = load_schema('conferences')
    subschema = schema['properties']['alternative_titles']

    snippet = (  # record/1403856
        '<datafield tag="711" ind1=" " ind2=" ">  <subfield code="a">XX'
        ' Riunione Nazionale di Elettromagnetismo</subfield>  <subfield'
        ' code="b">Padova</subfield></datafield>'
    )

    expected = [
        {'title': 'XX Riunione Nazionale di Elettromagnetismo'},
        {'title': 'Padova'},
    ]
    result = conferences.do(create_record(snippet))

    assert validate(result['alternative_titles'], subschema) is None
    assert expected == result['alternative_titles']


def test_core_from_980__a():
    schema = load_schema('conferences')
    subschema = schema['properties']['core']

    snippet = (  # record/1707423
        '<datafield tag="980" ind1=" " ind2=" ">'
        '  <subfield code="a">CORE</subfield>'
        '</datafield>'
    )

    expected = True
    result = conferences.do(create_record(snippet))

    assert validate(result['core'], subschema) is None
    assert expected == result['core']


def test_core_from_980__a_b():
    schema = load_schema('conferences')
    subschema = schema['properties']['core']

    snippet = (  # record/1726216
        '<record>'
        '  <datafield tag="980" ind1=" " ind2=" ">'
        '    <subfield code="a">CONFERENCES</subfield>'
        '  </datafield>'
        '  <datafield tag="980" ind1=" " ind2=" ">'
        '    <subfield code="a">CORE</subfield>'
        '  </datafield>'
        '</record>'
    )

    expected = True
    result = conferences.do(create_record(snippet))

    assert validate(result['core'], subschema) is None
    assert expected == result['core']


def test_deleted_from_980__c():
    schema = load_schema('conferences')
    subschema = schema['properties']['deleted']

    snippet = (
        '<datafield tag="980" ind1=" " ind2=" ">'
        '  <subfield code="c">DELETED</subfield>'
        '</datafield>'
    )

    expected = True
    result = conferences.do(create_record(snippet))

    assert validate(result['deleted'], subschema) is None
    assert expected == result['deleted']


def test_keywords_from_6531_9_a():
    schema = load_schema('conferences')
    subschema = schema['properties']['keywords']

    snippet = (  # record/1713483
        '<record>'
        '  <datafield tag="653" ind1="1" ind2=" ">'
        '    <subfield code="9">submitter</subfield>'
        '    <subfield code="a">electroweak</subfield>'
        '  </datafield>'
        '  <datafield tag="653" ind1="1" ind2=" ">'
        '    <subfield code="9">submitter</subfield>'
        '    <subfield code="a">standard model</subfield>'
        '  </datafield>'
        '</record>'
    )

    expected = [
        {'source': 'submitter', 'value': 'electroweak'},
        {'source': 'submitter', 'value': 'standard model'},
    ]

    result = conferences.do(create_record(snippet))

    assert validate(result['keywords'], subschema) is None
    assert expected == result['keywords']
