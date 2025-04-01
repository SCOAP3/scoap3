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


def test_isbns_from_020__a():
    schema = load_schema('hep')
    subschema = schema['properties']['isbns']

    snippet = (  # record/1510325
        '<datafield tag="020" ind1=" " ind2=" ">'
        '  <subfield code="a">9780198759713</subfield>'
        '</datafield>'
    )

    expected = [
        {'value': '9780198759713'},
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['isbns'], subschema) is None
    assert expected == result['isbns']

    expected = [
        {'a': '9780198759713'},
    ]
    result = hep2marc.do(result)

    assert expected == result['020']


def test_isbns_from_020__a_handles_capital_x():
    schema = load_schema('hep')
    subschema = schema['properties']['isbns']

    snippet = (  # record/1230427
        '<datafield tag="020" ind1=" " ind2=" ">'
        '  <subfield code="a">069114558X</subfield>'
        '</datafield>'
    )

    expected = [
        {'value': '9780691145587'},
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['isbns'], subschema) is None
    assert expected == result['isbns']

    expected = [
        {'a': '9780691145587'},
    ]
    result = hep2marc.do(result)

    assert expected == result['020']


def test_isbns_from_020__a_b_normalizes_online():
    schema = load_schema('hep')
    subschema = schema['properties']['isbns']

    snippet = (  # record/1504286
        '<datafield tag="020" ind1=" " ind2=" ">'
        '  <subfield code="a">978-94-024-0999-4</subfield>'
        '  <subfield code="b">Online</subfield>'
        '</datafield>'
    )

    expected = [
        {
            'value': '9789402409994',
            'medium': 'online',
        },
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['isbns'], subschema) is None
    assert expected == result['isbns']

    expected = [
        {
            'a': '9789402409994',
            'b': 'online',
        },
    ]
    result = hep2marc.do(result)

    assert expected == result['020']


def test_isbns_from_020__a_b_normalizes_print():
    schema = load_schema('hep')
    subschema = schema['properties']['isbns']

    snippet = (  # record/1509456
        '<datafield tag="020" ind1=" " ind2=" ">'
        '  <subfield code="a">9781786341105</subfield>'
        '  <subfield code="b">Print</subfield>'
        '</datafield>'
    )

    expected = [
        {
            'value': '9781786341105',
            'medium': 'print',
        },
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['isbns'], subschema) is None
    assert expected == result['isbns']

    expected = [
        {
            'a': '9781786341105',
            'b': 'print',
        },
    ]
    result = hep2marc.do(result)

    assert expected == result['020']


def test_isbns_from_020__a_b_normalizes_electronic():
    schema = load_schema('hep')
    subschema = schema['properties']['isbns']

    snippet = (  # record/1292006
        '<datafield tag="020" ind1=" " ind2=" ">'
        '  <subfield code="a">9783319006260</subfield>'
        '  <subfield code="b">electronic version</subfield>'
        '</datafield>'
    )

    expected = [
        {
            'value': '9783319006260',
        },
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['isbns'], subschema) is None
    assert expected == result['isbns']

    expected = [
        {
            'a': '9783319006260',
        },
    ]
    result = hep2marc.do(result)

    assert expected == result['020']


def test_isbns_from_020__a_b_normalizes_ebook():
    schema = load_schema('hep')
    subschema = schema['properties']['isbns']

    snippet = (  # record/1430829
        '<datafield tag="020" ind1=" " ind2=" ">'
        '  <subfield code="a">9783319259017</subfield>'
        '  <subfield code="b">eBook</subfield>'
        '</datafield>'
    )

    expected = [
        {
            'value': '9783319259017',
            'medium': 'online',
        },
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['isbns'], subschema) is None
    assert expected == result['isbns']

    expected = [
        {
            'a': '9783319259017',
            'b': 'online',
        },
    ]
    result = hep2marc.do(result)

    assert expected == result['020']


def test_isbns_from_020__a_b_normalizes_hardcover():
    schema = load_schema('hep')
    subschema = schema['properties']['isbns']

    snippet = (  # record/1351311
        '<datafield tag="020" ind1=" " ind2=" ">'
        '  <subfield code="a">978-981-4571-66-1</subfield>'
        '  <subfield code="b">hardcover</subfield>'
        '</datafield>'
    )

    expected = [
        {
            'value': '9789814571661',
            'medium': 'hardcover',
        },
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['isbns'], subschema) is None
    assert expected == result['isbns']

    expected = [
        {
            'a': '9789814571661',
            'b': 'hardcover',
        },
    ]
    result = hep2marc.do(result)

    assert expected == result['020']


def test_isbns_from_020__a_b_handles_dots():
    schema = load_schema('hep')
    subschema = schema['properties']['isbns']

    snippet = (  # record/1426768
        '<datafield tag="020" ind1=" " ind2=" ">'
        '  <subfield code="a">978.90.9023556.1</subfield>'
        '  <subfield code="b">Online</subfield>'
        '</datafield>'
    )

    result = hep.do(create_record(snippet))

    assert validate(result['isbns'], subschema) is None


def test_dois_from_0247_a_2_double_9_ignores_curator_source():
    schema = load_schema('hep')
    subschema = schema['properties']['dois']

    snippet = (  # record/1117362
        '<datafield tag="024" ind1="7" ind2=" ">'
        '  <subfield code="2">DOI</subfield>'
        '  <subfield code="9">bibcheck</subfield>'
        '  <subfield code="9">CURATOR</subfield>'
        '  <subfield code="a">10.1590/S1806-11172008005000006</subfield>'
        '</datafield>'
    )

    expected = [
        {
            'source': 'bibcheck',
            'value': '10.1590/S1806-11172008005000006',
        },
    ]
    result = hep.do(create_record(snippet))  # no roundtrip

    assert validate(result['dois'], subschema) is None
    assert expected == result['dois']

    expected = [
        {
            'a': '10.1590/S1806-11172008005000006',
            '9': 'bibcheck',
            '2': 'DOI',
        },
    ]
    result = hep2marc.do(result)

    assert expected == result['0247']


def test_dois_from_0247_a_2():
    schema = load_schema('hep')
    subschema = schema['properties']['dois']

    snippet = (  # record/1302395
        '<datafield tag="024" ind1="7" ind2=" ">'
        '  <subfield code="2">DOI</subfield>'
        '  <subfield code="a">10.1088/0264-9381/31/24/245004</subfield>'
        '</datafield>'
    )

    expected = [
        {'value': '10.1088/0264-9381/31/24/245004'},
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['dois'], subschema) is None
    assert expected == result['dois']

    expected = [
        {
            'a': '10.1088/0264-9381/31/24/245004',
            '2': 'DOI',
        },
    ]
    result = hep2marc.do(result)

    assert expected == result['0247']


def test_dois_from_0247_a_2_9_and_0247_a_2():
    schema = load_schema('hep')
    subschema = schema['properties']['dois']

    snippet = (  # record/1286727
        '<record>'
        '  <datafield tag="024" ind1="7" ind2=" ">'
        '    <subfield code="2">DOI</subfield>'
        '    <subfield code="9">bibmatch</subfield>'
        '    <subfield code="a">10.1088/1475-7516/2015/03/044</subfield>'
        '  </datafield>'
        '  <datafield tag="024" ind1="7" ind2=" ">'
        '    <subfield code="2">DOI</subfield>'
        '    <subfield code="a">10.1088/1475-7516/2015/03/044</subfield>'
        '  </datafield>'
        '</record>'
    )

    expected = [
        {
            'source': 'bibmatch',
            'value': '10.1088/1475-7516/2015/03/044',
        },
        {
            'value': '10.1088/1475-7516/2015/03/044',
        },
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['dois'], subschema) is None
    assert expected == result['dois']

    expected = [
        {
            'a': '10.1088/1475-7516/2015/03/044',
            '9': 'bibmatch',
            '2': 'DOI',
        },
        {
            'a': '10.1088/1475-7516/2015/03/044',
            '2': 'DOI',
        },
    ]
    result = hep2marc.do(result)

    assert expected == result['0247']


def test_dois_from_0247_a_2_and_0247_a_2_9():
    schema = load_schema('hep')
    subschema = schema['properties']['dois']

    snippet = (  # record/1273665
        '<record>'
        '  <datafield tag="024" ind1="7" ind2=" ">'
        '    <subfield code="2">DOI</subfield>'
        '    <subfield code="a">10.1103/PhysRevD.89.072002</subfield>'
        '  </datafield>'
        '  <datafield tag="024" ind1="7" ind2=" ">'
        '    <subfield code="2">DOI</subfield>'
        '    <subfield code="9">bibmatch</subfield>'
        '    <subfield code="a">10.1103/PhysRevD.91.019903</subfield>'
        '  </datafield>'
        '</record>'
    )

    expected = [
        {
            'value': '10.1103/PhysRevD.89.072002',
        },
        {
            'source': 'bibmatch',
            'value': '10.1103/PhysRevD.91.019903',
        },
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['dois'], subschema) is None
    assert expected == result['dois']

    expected = [
        {
            'a': '10.1103/PhysRevD.89.072002',
            '2': 'DOI',
        },
        {
            'a': '10.1103/PhysRevD.91.019903',
            '9': 'bibmatch',
            '2': 'DOI',
        },
    ]
    result = hep2marc.do(result)

    assert expected == result['0247']


def test_dois_from_0247_a_q_2_9_normalizes_erratum():
    schema = load_schema('hep')
    subschema = schema['properties']['dois']

    snippet = (  # record/898839
        '<datafield tag="024" ind1="7" ind2=" ">'
        '  <subfield code="2">DOI</subfield>'
        '  <subfield code="9">bibmatch</subfield>'
        '  <subfield code="a">10.1103/PhysRevC.93.049901</subfield>'
        '  <subfield code="q">Erratum</subfield>'
        '</datafield>'
    )

    expected = [
        {
            'material': 'erratum',
            'value': '10.1103/PhysRevC.93.049901',
            'source': 'bibmatch',
        },
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['dois'], subschema) is None
    assert expected == result['dois']

    expected = [
        {
            'a': '10.1103/PhysRevC.93.049901',
            'q': 'erratum',
            '2': 'DOI',
            '9': 'bibmatch',
        },
    ]
    result = hep2marc.do(result)

    assert expected == result['0247']


def test_dois_from_0247_a_q_2_normalizes_ebook():
    schema = load_schema('hep')
    subschema = schema['properties']['dois']

    snippet = (  # record/1509573
        '<datafield tag="024" ind1="7" ind2=" ">'
        '  <subfield code="2">DOI</subfield>'
        '  <subfield code="a">10.1017/CBO9780511813924</subfield>'
        '  <subfield code="q">ebook</subfield>'
        '</datafield>'
    )

    expected = [
        {
            'material': 'publication',
            'value': '10.1017/CBO9780511813924',
        },
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['dois'], subschema) is None
    assert expected == result['dois']

    expected = [
        {
            'a': '10.1017/CBO9780511813924',
            'q': 'publication',
            '2': 'DOI',
        },
    ]
    result = hep2marc.do(result)

    assert expected == result['0247']


def test_persistent_identifiers_from_0247_a_2():
    schema = load_schema('hep')
    subschema = schema['properties']['persistent_identifiers']

    snippet = (  # record/1623117
        '<datafield tag="024" ind1="7" ind2=" ">'
        '  <subfield code="2">HDL</subfield>'
        '  <subfield code="a">10150/625467</subfield>'
        '</datafield>'
    )

    expected = [
        {
            'schema': 'HDL',
            'value': '10150/625467',
        },
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['persistent_identifiers'], subschema) is None
    assert expected == result['persistent_identifiers']

    expected = [
        {
            'a': '10150/625467',
            '2': 'HDL',
        },
    ]
    result = hep2marc.do(result)

    assert expected == result['0247']


def test_texkeys_from_035__a_9():
    schema = load_schema('hep')
    subschema = schema['properties']['texkeys']

    snippet = (  # record/1403324
        '<datafield tag="035" ind1=" " ind2=" ">'
        '  <subfield code="9">INSPIRETeX</subfield>'
        '  <subfield code="a">Hagedorn:1963hdh</subfield>'
        '</datafield>'
    )

    expected = [
        'Hagedorn:1963hdh',
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['texkeys'], subschema) is None
    assert expected == result['texkeys']

    expected = [
        {
            '9': 'INSPIRETeX',
            'a': 'Hagedorn:1963hdh',
        }
    ]
    result = hep2marc.do(result)

    assert expected == result['035']


def test_texkeys_from_035__z_9_and_035__a_9():
    schema = load_schema('hep')
    subschema = schema['properties']['texkeys']

    snippet = (  # record/1498308
        '<record>'
        '  <datafield tag="035" ind1=" " ind2=" ">'
        '    <subfield code="9">SPIRESTeX</subfield>'
        '    <subfield code="z">N.Cartiglia:2015cn</subfield>'
        '  </datafield>'
        '  <datafield tag="035" ind1=" " ind2=" ">'
        '    <subfield code="9">INSPIRETeX</subfield>'
        '    <subfield code="a">Akiba:2016ofq</subfield>'
        '  </datafield>'
        '</record>'
    )

    expected = [
        'Akiba:2016ofq',  # XXX: the first one is the one coming
        'N.Cartiglia:2015cn',  # from the "a" field.
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['texkeys'], subschema) is None
    assert expected == result['texkeys']

    expected = [
        {
            '9': 'INSPIRETeX',
            'a': 'Akiba:2016ofq',
        },
        {
            '9': 'INSPIRETeX',
            'z': 'N.Cartiglia:2015cn',
        },
    ]
    result = hep2marc.do(result)

    assert expected == result['035']


def test_desy_bookkeekping_from_035__z_9_DESY():
    schema = load_schema('hep')
    subschema = schema['properties']['_desy_bookkeeping']

    snippet = (  # record/1635310
        '<datafield tag="035" ind1=" " ind2=" ">'
        '  <subfield code="9">DESY</subfield>'
        '  <subfield code="z">DA17-kp47ch</subfield>'
        '</datafield>'
    )

    expected = [
        {
            'identifier': 'DA17-kp47ch',
        },
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['_desy_bookkeeping'], subschema) is None
    assert expected == result['_desy_bookkeeping']

    expected = [
        {
            '9': 'DESY',
            'z': 'DA17-kp47ch',
        },
    ]
    result = hep2marc.do(result)

    assert expected == result['035']


def test_desy_bookkeekping_from_035__z_9_DESY_and_595_Da_d_s():
    schema = load_schema('hep')
    subschema = schema['properties']['_desy_bookkeeping']

    snippet = (  # record/1635310
        '<record>'
        '  <datafield tag="035" ind1=" " ind2=" ">'
        '    <subfield code="9">DESY</subfield>'
        '    <subfield code="z">DA17-kp46cm</subfield>'
        '  </datafield>'
        '  <datafield tag="595" ind1=" " ind2="D">'
        '    <subfield code="a">8</subfield>'
        '    <subfield code="d">2017-11-15</subfield>'
        '    <subfield code="s">abs</subfield>'
        '  </datafield>'
        '</record>'
    )

    expected = [
        {
            'identifier': 'DA17-kp46cm',
        },
        {
            'expert': '8',
            'date': '2017-11-15',
            'status': 'abs',
        },
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['_desy_bookkeeping'], subschema) is None
    assert expected == result['_desy_bookkeeping']

    expected_035 = [
        {
            '9': 'DESY',
            'z': 'DA17-kp46cm',
        },
    ]
    expected_595_D = [
        {
            'a': '8',
            'd': '2017-11-15',
            's': 'abs',
        },
    ]
    result = hep2marc.do(result)

    assert expected_035 == result['035']
    assert expected_595_D == result['595_D']


def test_external_system_identifiers_from_035__a_9_discards_arxiv():
    snippet = (  # record/1498308
        '<datafield tag="035" ind1=" " ind2=" ">'
        '  <subfield code="9">arXiv</subfield>'
        '  <subfield code="a">oai:arXiv.org:1611.05079</subfield>'
        '</datafield>'
    )

    result = hep.do(create_record(snippet))

    assert 'external_system_identifiers' not in result


def test_external_system_identifiers_from_035__z_9_handles_cernkey():
    schema = load_schema('hep')
    subschema = schema['properties']['external_system_identifiers']

    snippet = (  # record/451647
        '<datafield tag="035" ind1=" " ind2=" ">'
        '  <subfield code="9">CERNKEY</subfield>'
        '  <subfield code="z">0263439</subfield>'
        '</datafield>'
    )

    expected = [
        {
            'schema': 'CERNKEY',
            'value': '0263439',
        },
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['external_system_identifiers'], subschema) is None
    assert expected == result['external_system_identifiers']

    expected = [
        {
            '9': 'CERNKEY',
            'z': '0263439',
        },
    ]
    result = hep2marc.do(result)

    assert expected == result['035']


def test_external_system_numbers_from_035__a_d_h_m_9_ignores_oai():
    snippet = (  # record/1403324
        '<datafield tag="035" ind1=" " ind2=" ">'
        '  <subfield code="9">http://cds.cern.ch/oai2d</subfield>'
        '  <subfield code="a">oai:cds.cern.ch:325030</subfield>'
        '  <subfield code="d">2015-06-05T13:24:42Z</subfield>'
        '  <subfield code="h">2015-11-09T16:22:48Z</subfield>'
        '  <subfield code="m">marcxml</subfield>'
        '</datafield>'
    )

    result = hep.do(create_record(snippet))

    assert 'external_system_identifiers' not in result


def test_external_system_numbers_from_035__9_discards_incomplete_datafields():
    snippet = (
        '<datafield tag="035" ind1=" " ind2=" ">'
        '  <subfield code="9">OSTI</subfield>'
        '</datafield>'
    )

    result = hep.do(create_record(snippet))

    assert 'external_system_identifiers' not in result


def test_external_system_numbers_from_035__a_9_hepdata():
    schema = load_schema('hep')
    subschema = schema['properties']['external_system_identifiers']

    snippet = (  # record/1498566
        '  <datafield tag="035" ind1=" " ind2=" ">'
        '    <subfield code="a">ins1498566</subfield>'
        '    <subfield code="9">HEPDATA</subfield>'
        '  </datafield>'
    )

    expected = [
        {
            'value': 'ins1498566',
            'schema': 'HEPDATA',
        },
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['external_system_identifiers'], subschema) is None
    assert expected == result['external_system_identifiers']

    expected = [
        {
            'a': 'ins1498566',
            '9': 'HEPDATA',
        },
    ]
    result = hep2marc.do(result)

    assert expected == result['035']


def test_external_system_numbers_from_035__a_9_and_035__z_9():
    schema = load_schema('hep')
    subschema = schema['properties']['external_system_identifiers']

    snippet = (  # record/700376
        '<record>'
        '  <datafield tag="035" ind1=" " ind2=" ">'
        '    <subfield code="9">OSTI</subfield>'
        '    <subfield code="a">892532</subfield>'
        '  </datafield>'
        '  <datafield tag="035" ind1=" " ind2=" ">'
        '    <subfield code="9">OSTI</subfield>'
        '    <subfield code="z">897192</subfield>'
        '  </datafield>'
        '</record>'
    )

    expected = [
        {
            'value': '892532',
            'schema': 'OSTI',
        },
        {
            'value': '897192',
            'schema': 'OSTI',
        },
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['external_system_identifiers'], subschema) is None
    assert expected == result['external_system_identifiers']

    expected = [
        {
            'a': '892532',
            '9': 'OSTI',
        },
        {
            'z': '897192',
            '9': 'OSTI',
        },
    ]
    result = hep2marc.do(result)

    assert expected == result['035']
    assert 'id_dict' not in result


def test_035_from_arxiv_eprints_and_texkeys():
    schema = load_schema('hep')
    subschema_arxiv_eprints = schema['properties']['arxiv_eprints']
    subschema_texkeys = schema['properties']['texkeys']
    snippet = {
        'arxiv_eprints': [{'value': '2212.04977', 'categories': ['hep-ex']}],
        'texkeys': ['LHCb:2022diq'],
    }  # literature/2612668

    assert validate(snippet['arxiv_eprints'], subschema_arxiv_eprints) is None
    assert validate(snippet['texkeys'], subschema_texkeys) is None

    expected = [
        {
            'a': 'oai:arXiv.org:2212.04977',
            '9': 'arXiv',
        },
        {
            'a': 'LHCb:2022diq',
            '9': 'INSPIRETeX',
        },
    ]
    result = hep2marc.do(snippet)

    assert sorted(expected, key=str) == sorted(result['035'], key=str)


def test_arxiv_eprints_from_037__a_c_9():
    schema = load_schema('hep')
    subschema = schema['properties']['arxiv_eprints']

    snippet = (  # record/1368891
        '<datafield tag="037" ind1=" " ind2=" ">'
        '  <subfield code="9">arXiv</subfield>'
        '  <subfield code="a">arXiv:1505.01843</subfield>'
        '  <subfield code="c">hep-ph</subfield>'
        '</datafield>'
    )

    expected = [
        {
            'categories': [
                'hep-ph',
            ],
            'value': '1505.01843',
        },
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['arxiv_eprints'], subschema) is None
    assert expected == result['arxiv_eprints']

    expected = [
        {
            '9': 'arXiv',
            'a': 'arXiv:1505.01843',
            'c': 'hep-ph',
        },
    ]
    result = hep2marc.do(result)

    assert expected == result['037']


def test_arxiv_eprints_from_037__a_c_9_old_identifier():
    schema = load_schema('hep')
    subschema = schema['properties']['arxiv_eprints']

    snippet = (  # record/782187
        '<datafield tag="037" ind1=" " ind2=" ">'
        '  <subfield code="a">hep-th/0110148</subfield>'
        '  <subfield code="9">arXiv</subfield>'
        '  <subfield code="c">hep-th</subfield>'
        '</datafield>'
    )

    expected = [
        {
            'categories': [
                'hep-th',
            ],
            'value': 'hep-th/0110148',
        },
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['arxiv_eprints'], subschema) is None
    assert expected == result['arxiv_eprints']

    expected = [
        {
            '9': 'arXiv',
            'a': 'hep-th/0110148',
            'c': 'hep-th',
        },
    ]
    result = hep2marc.do(result)

    assert expected == result['037']


def test_arxiv_eprints_from_037__a_c_9_obsolete_category():
    schema = load_schema('hep')
    subschema = schema['properties']['arxiv_eprints']

    snippet = (  # record/450571
        '<datafield tag="037" ind1=" " ind2=" ">'
        '  <subfield code="a">funct-an/9710003</subfield>'
        '  <subfield code="9">arXiv</subfield>'
        '  <subfield code="c">funct-an</subfield>'
        '</datafield>'
    )

    expected = [
        {
            'categories': [
                'math.FA',
            ],
            'value': 'funct-an/9710003',
        },
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['arxiv_eprints'], subschema) is None
    assert expected == result['arxiv_eprints']

    expected = [
        {
            '9': 'arXiv',
            'a': 'funct-an/9710003',
            'c': 'math.FA',
        },
    ]
    result = hep2marc.do(result)

    assert expected == result['037']


def test_report_numbers_from_037__a():
    schema = load_schema('hep')
    subschema = schema['properties']['report_numbers']

    snippet = (  # record/1511277
        '<datafield tag="037" ind1=" " ind2=" ">'
        '  <subfield code="a">CERN-EP-2016-319</subfield>'
        '</datafield>'
    )

    expected = [
        {'value': 'CERN-EP-2016-319'},
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['report_numbers'], subschema) is None
    assert expected == result['report_numbers']

    expected = [
        {'a': 'CERN-EP-2016-319'},
    ]
    result = hep2marc.do(result)

    assert expected == result['037']


def test_report_numbers_from_two_037__a():
    schema = load_schema('hep')
    subschema = schema['properties']['report_numbers']

    snippet = (  # record/26564
        '<record>'
        '  <datafield tag="037" ind1=" " ind2=" ">'
        '    <subfield code="a">UTPT-89-27</subfield>'
        '  </datafield>'
        '  <datafield tag="037" ind1=" " ind2=" ">'
        '    <subfield code="a">CALT-68-1585</subfield>'
        '  </datafield>'
        '</record>'
    )

    expected = [
        {
            'value': 'UTPT-89-27',
        },
        {
            'value': 'CALT-68-1585',
        },
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['report_numbers'], subschema) is None
    assert expected == result['report_numbers']

    expected = [
        {'a': 'UTPT-89-27'},
        {'a': 'CALT-68-1585'},
    ]
    result = hep2marc.do(result)

    assert expected == result['037']


def test_report_numbers_hidden_from_037__z():
    schema = load_schema('hep')
    subschema = schema['properties']['report_numbers']

    snippet = (  # record/1508174
        '<datafield tag="037" ind1=" " ind2=" ">'
        '  <subfield code="z">FERMILAB-PUB-17-011-CMS</subfield>'
        '</datafield>'
    )

    expected = [
        {
            'hidden': True,
            'value': 'FERMILAB-PUB-17-011-CMS',
        },
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['report_numbers'], subschema) is None
    assert expected == result['report_numbers']

    expected = [{'z': 'FERMILAB-PUB-17-011-CMS'}]
    result = hep2marc.do(result)

    assert expected == result['037']


def test_report_numbers_from_037__z_9():
    schema = load_schema('hep')
    subschema = schema['properties']['report_numbers']

    snippet = (  # record/1326454
        '<datafield tag="037" ind1=" " ind2=" ">'
        '  <subfield code="9">SLAC</subfield>'
        '  <subfield code="a">SLAC-PUB-16140</subfield>'
        '</datafield>'
    )

    expected = [
        {
            'source': 'SLAC',
            'value': 'SLAC-PUB-16140',
        },
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['report_numbers'], subschema) is None
    assert expected == result['report_numbers']

    expected = [
        {
            '9': 'SLAC',
            'a': 'SLAC-PUB-16140',
        },
    ]
    result = hep2marc.do(result)

    assert expected == result['037']


def test_report_numbers_from_037__a_9_arXiv_reportnumber():
    schema = load_schema('hep')
    subschema = schema['properties']['report_numbers']

    snippet = (  # record/1618037
        '<datafield tag="037" ind1=" " ind2=" ">'
        '  <subfield code="9">arXiv:reportnumber</subfield>'
        '  <subfield code="a">LIGO-P1500247</subfield>'
        '</datafield>'
    )

    expected = [
        {
            'source': 'arXiv',
            'value': 'LIGO-P1500247',
        },
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['report_numbers'], subschema) is None
    assert expected == result['report_numbers']

    expected = [
        {
            '9': 'arXiv:reportnumber',
            'a': 'LIGO-P1500247',
        },
    ]
    result = hep2marc.do(result)

    assert expected == result['037']
    assert '035' not in result


def test_arxiv_eprints_from_037__a_c_9_and_multiple_65017_a_2():
    schema = load_schema('hep')
    subschema = schema['properties']['arxiv_eprints']

    snippet = (  # record/1511862
        '<record>'
        '  <datafield tag="037" ind1=" " ind2=" ">'
        '    <subfield code="9">arXiv</subfield>'
        '    <subfield code="a">arXiv:1702.00702</subfield>'
        '    <subfield code="c">math-ph</subfield>'
        '  </datafield>'
        '  <datafield tag="650" ind1="1" ind2="7">'
        '    <subfield code="a">math-ph</subfield>'
        '    <subfield code="2">arXiv</subfield>'
        '  </datafield>'
        '  <datafield tag="650" ind1="1" ind2="7">'
        '    <subfield code="a">gr-qc</subfield>'
        '    <subfield code="2">arXiv</subfield>'
        '  </datafield>'
        '</record>'
    )

    expected = [
        {
            'categories': [
                'math-ph',
                'gr-qc',
            ],
            'value': '1702.00702',
        }
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['arxiv_eprints'], subschema) is None
    assert expected == result['arxiv_eprints']

    expected_035 = [
        {
            '9': 'arXiv',
            'a': 'oai:arXiv.org:1702.00702',
        },
    ]
    expected_037 = [
        {
            '9': 'arXiv',
            'a': 'arXiv:1702.00702',
            'c': 'math-ph',
        },
    ]
    expected_65017 = [
        {
            '2': 'arXiv',
            'a': 'math-ph',
        },
        {
            '2': 'arXiv',
            'a': 'gr-qc',
        },
    ]
    result = hep2marc.do(result)

    assert expected_035 == result['035']
    assert expected_037 == result['037']
    assert expected_65017 == result['65017']


def test_arxiv_eprints_037__a_9_lowercase_arxiv():
    schema = load_schema('hep')
    subschema = schema['properties']['arxiv_eprints']

    snippet = (
        "<datafield tag='037' ind1=' ' ind2=' '>"
        "  <subfield code='a'>1703.09086</subfield>"
        "  <subfield code='9'>arxiv</subfield>"
        "</datafield>"
    )

    expected = [{'value': '1703.09086'}]
    result = hep.do(create_record(snippet))

    assert validate(result['arxiv_eprints'], subschema) is None
    assert expected == result['arxiv_eprints']

    expected = [
        {
            '9': 'arXiv',
            'a': 'arXiv:1703.09086',
        }
    ]
    result = hep2marc.do(result)

    assert expected == result['037']


def test_languages_from_041__a():
    schema = load_schema('hep')
    subschema = schema['properties']['languages']

    snippet = (  # record/1503566
        '<datafield tag="041" ind1=" " ind2=" ">'
        '  <subfield code="a">Italian</subfield>'
        '</datafield>'
    )

    expected = [
        'it',
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['languages'], subschema) is None
    assert expected == result['languages']

    expected = [
        {'a': 'italian'},
    ]
    result = hep2marc.do(result)

    assert expected == result['041']


def test_languages_from_041__a_handles_multiple_languages_in_one_a():
    schema = load_schema('hep')
    subschema = schema['properties']['languages']

    snippet = (  # record/116959
        '<datafield tag="041" ind1=" " ind2=" ">'
        '  <subfield code="a">Russian / English</subfield>'
        '</datafield>'
    )

    expected = [
        'ru',
        'en',
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['languages'], subschema) is None
    assert expected == result['languages']

    expected = [
        {'a': 'russian'},
        {'a': 'english'},
    ]
    result = hep2marc.do(result)

    assert expected == result['041']


def test_languages_from_double_041__a():
    schema = load_schema('hep')
    subschema = schema['properties']['languages']

    snippet = (  # record/1231408
        '<record>'
        '  <datafield tag="041" ind1=" " ind2=" ">'
        '    <subfield code="a">French</subfield>'
        '  </datafield>'
        '  <datafield tag="041" ind1=" " ind2=" ">'
        '    <subfield code="a">German</subfield>'
        '  </datafield>'
        '</record>'
    )

    expected = [
        'fr',
        'de',
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['languages'], subschema) is None
    assert expected == result['languages']

    expected = [
        {'a': 'french'},
        {'a': 'german'},
    ]
    result = hep2marc.do(result)

    assert expected == result['041']
