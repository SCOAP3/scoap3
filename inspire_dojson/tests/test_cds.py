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

from inspire_dojson.cds import cds2hep_marc
from inspire_dojson.hep import hep
from inspire_dojson.utils import create_record_from_dict


def test_external_system_identifiers_from_001():
    schema = load_schema('hep')
    subschema = schema['properties']['external_system_identifiers']

    snippet = (  # cds.cern.ch/record/2270264
        '<controlfield tag="001">2270264</controlfield>'
    )

    expected = [
        {
            'a': '2270264',
            '9': 'CDS',
        },
    ]
    result = cds2hep_marc.do(create_record(snippet))

    assert expected == result['035__']

    expected = [
        {
            'schema': 'CDS',
            'value': '2270264',
        },
    ]
    result = hep.do(create_record_from_dict(result))

    assert validate(result['external_system_identifiers'], subschema) is None
    assert expected == result['external_system_identifiers']


def test_private_notes_from_001_and_980__c_hidden():
    schema = load_schema('hep')
    subschema = schema['properties']['_private_notes']

    snippet = (  # cds.cern.ch/record/1355275
        '<record>'
        '  <controlfield tag="001">1355275</controlfield>'
        '  <datafield tag="980" ind1=" " ind2=" ">'
        '    <subfield code="c">Hidden</subfield>'
        '  </datafield>'
        '</record>'
    )

    expected = [
        {
            'a': 'CDS-1355275',
            '9': 'CDS',
        },
    ]
    result = cds2hep_marc.do(create_record(snippet))

    assert expected == result['595__']

    expected = [
        {
            'source': 'CDS',
            'value': 'CDS-1355275',
        },
    ]
    result = hep.do(create_record_from_dict(result))

    assert validate(result['_private_notes'], subschema) is None
    assert expected == result['_private_notes']


def test_dois_from_0247_a_2():
    schema = load_schema('hep')
    subschema = schema['properties']['dois']

    snippet = (  # cds.cern.ch/record/2297288
        '<datafield tag="024" ind1="7" ind2=" ">'
        '  <subfield code="2">DOI</subfield>'
        '  <subfield code="a">10.1016/j.nima.2017.11.093</subfield>'
        '</datafield>'
    )

    expected = [
        {
            '2': 'DOI',
            '9': 'CDS',
            'a': '10.1016/j.nima.2017.11.093',
        },
    ]
    result = cds2hep_marc.do(create_record(snippet))

    assert expected == result['0247_']

    expected = [
        {
            'source': 'CDS',
            'value': '10.1016/j.nima.2017.11.093',
        },
    ]
    result = hep.do(create_record_from_dict(result))

    assert validate(result['dois'], subschema) is None
    assert expected == result['dois']


def test_dois_from_0247_a_2_9():
    schema = load_schema('hep')
    subschema = schema['properties']['dois']

    snippet = (  # cds.cern.ch/record/2295116
        '<datafield tag="024" ind1="7" ind2=" ">'
        '  <subfield code="2">DOI</subfield>'
        '  <subfield code="9">submitter</subfield>'
        '  <subfield code="a">10.1098/rsta.2014.0044</subfield>'
        '</datafield>'
    )

    expected = [
        {
            '2': 'DOI',
            '9': 'submitter',
            'a': '10.1098/rsta.2014.0044',
        },
    ]
    result = cds2hep_marc.do(create_record(snippet))

    assert expected == result['0247_']

    expected = [
        {
            'source': 'submitter',
            'value': '10.1098/rsta.2014.0044',
        },
    ]
    result = hep.do(create_record_from_dict(result))

    assert validate(result['dois'], subschema) is None
    assert expected == result['dois']


def test_external_sytem_identifiers_from_035__a_9():
    schema = load_schema('hep')
    subschema = schema['properties']['external_system_identifiers']

    snippet = (  # cds.cern.ch/record/2295073
        '<record>'
        '  <datafield tag="035" ind1=" " ind2=" ">'
        '    <subfield code="9">OSTI</subfield>'
        '    <subfield code="a">1358095</subfield>'
        '  </datafield>'
        '</record>'
    )

    expected = [
        {
            '9': 'OSTI',
            'a': '1358095',
        },
    ]
    result = cds2hep_marc.do(create_record(snippet))

    assert expected == result['035__']

    expected = [
        {
            'schema': 'OSTI',
            'value': '1358095',
        },
    ]
    result = hep.do(create_record_from_dict(result))

    assert validate(result['external_system_identifiers'], subschema) is None
    assert expected == result['external_system_identifiers']


def test_external_sytem_identifiers_from_035__a_9_ignores_inspire():
    snippet = (  # cds.cern.ch/record/2295116
        '<record>'
        '  <datafield tag="035" ind1=" " ind2=" ">'
        '    <subfield code="9">Inspire</subfield>'
        '    <subfield code="a">1640199</subfield>'
        '  </datafield>'
        '</record>'
    )

    result = cds2hep_marc.do(create_record(snippet))

    assert '035__' not in result


def test_external_sytem_identifiers_from_035__a_ignores_cercer():
    snippet = (  # cds.cern.ch/record/2307509
        '<record>'
        '  <datafield tag="035" ind1=" " ind2=" ">'
        '    <subfield code="a">0148182CERCER</subfield>'
        '  </datafield>'
        '</record>'
    )

    result = cds2hep_marc.do(create_record(snippet))

    assert '035__' not in result


def test_report_numbers_from_037__a():
    schema = load_schema('hep')
    subschema = schema['properties']['report_numbers']

    snippet = (  # cds.cern.ch/record/2270264
        '<datafield tag="037" ind1=" " ind2=" ">'
        '  <subfield code="a">CLICDP-PUB-2017-002</subfield>'
        '</datafield> '
    )

    expected = [
        {
            '9': 'CDS',
            'a': 'CLICDP-PUB-2017-002',
        },
    ]
    result = cds2hep_marc.do(create_record(snippet))

    assert expected == result['037__']

    expected = [
        {
            'source': 'CDS',
            'value': 'CLICDP-PUB-2017-002',
        },
    ]
    result = hep.do(create_record_from_dict(result))

    assert validate(result['report_numbers'], subschema) is None
    assert expected == result['report_numbers']


def test_report_numbers_from_037__z():
    schema = load_schema('hep')
    subschema = schema['properties']['report_numbers']

    snippet = (  # cds.cern.ch/record/2299967
        '<datafield tag="037" ind1=" " ind2=" ">'
        '  <subfield code="z">CERN-THESIS-2018-004</subfield>'
        '</datafield> '
    )

    expected = [
        {
            '9': 'CDS',
            'z': 'CERN-THESIS-2018-004',
        },
    ]
    result = cds2hep_marc.do(create_record(snippet))

    assert expected == result['037__']

    expected = [
        {
            'source': 'CDS',
            'value': 'CERN-THESIS-2018-004',
            'hidden': True,
        },
    ]
    result = hep.do(create_record_from_dict(result))

    assert validate(result['report_numbers'], subschema) is None
    assert expected == result['report_numbers']


def test_report_numbers_from_088__9():
    schema = load_schema('hep')
    subschema = schema['properties']['report_numbers']

    snippet = (  # cds.cern.ch/record/2255823
        '<datafield tag="088" ind1=" " ind2=" ">'
        '  <subfield code="9">ATL-COM-PHYS-2017-030</subfield>'
        '</datafield>'
    )

    expected = [
        {
            '9': 'CDS',
            'z': 'ATL-COM-PHYS-2017-030',
        }
    ]
    result = cds2hep_marc.do(create_record(snippet))

    assert expected == result['037__']
    assert {'a': 'NOTE'} not in result['980__']

    expected = [
        {
            'source': 'CDS',
            'value': 'ATL-COM-PHYS-2017-030',
            'hidden': True,
        },
    ]
    result = hep.do(create_record_from_dict(result))

    assert validate(result['report_numbers'], subschema) is None
    assert expected == result['report_numbers']


def test_report_numbers_and_document_type_from_multiple_088__a():
    schema = load_schema('hep')
    subschema_report_numbers = schema['properties']['report_numbers']
    subschema_document_type = schema['properties']['document_type']

    snippet = (  # cds.cern.ch/record/2275456
        '<record>'
        '  <datafield tag="088" ind1=" " ind2=" ">'
        '    <subfield code="a">ATL-PHYS-CONF-2008-015</subfield>'
        '  </datafield>'
        '  <datafield tag="088" ind1=" " ind2=" ">'
        '    <subfield code="a">ATL-COM-PHYS-2008-052</subfield>'
        '  </datafield>'
        '<record>'
    )

    expected = {
        '037__': [
            {
                '9': 'CDS',
                'a': 'ATL-PHYS-CONF-2008-015',
            },
            {
                '9': 'CDS',
                'a': 'ATL-COM-PHYS-2008-052',
            },
        ],
        '980__': [
            {
                'a': 'NOTE',
            },
            {
                'a': 'HEP',
            },
            {
                'a': 'CORE',
            },
        ],
    }
    result = cds2hep_marc.do(create_record(snippet))

    assert expected['037__'] == result['037__']
    assert expected['980__'] == result['980__']

    expected = {
        'document_type': [
            'note',
        ],
        'public_notes': [
            {
                'source': 'CDS',
                'value': 'Preliminary results',
            },
        ],
        'report_numbers': [
            {
                'source': 'CDS',
                'value': 'ATL-PHYS-CONF-2008-015',
            },
            {
                'source': 'CDS',
                'value': 'ATL-COM-PHYS-2008-052',
            },
        ],
    }
    result = hep.do(create_record_from_dict(result))

    assert validate(result['report_numbers'], subschema_report_numbers) is None
    assert validate(result['document_type'], subschema_document_type) is None
    assert expected['report_numbers'] == result['report_numbers']
    assert expected['document_type'] == result['document_type']


def test_report_numbers_and_document_type_and_publicate_notes_from_037__a():
    schema = load_schema('hep')
    subschema_report_numbers = schema['properties']['report_numbers']
    subschema_document_type = schema['properties']['document_type']
    subschema_public_notes = schema['properties']['public_notes']

    snippet = (  # cds.cern.ch/record/2202807
        '<datafield tag="088" ind1=" " ind2=" ">'
        '   <subfield code="a">CMS-PAS-SMP-15-001</subfield>'
        '</datafield>'
    )

    expected = {
        '037__': [
            {
                '9': 'CDS',
                'a': 'CMS-PAS-SMP-15-001',
            },
        ],
        '500__': [
            {
                '9': 'CDS',
                'a': 'Preliminary results',
            },
        ],
        '980__': [
            {
                'a': 'NOTE',
            },
            {
                'a': 'HEP',
            },
            {
                'a': 'CORE',
            },
        ],
    }
    result = cds2hep_marc.do(create_record(snippet))

    assert expected['037__'] == result['037__']
    assert expected['500__'] == result['500__']
    assert expected['980__'] == result['980__']

    expected = {
        'document_type': [
            'note',
        ],
        'public_notes': [
            {
                'source': 'CDS',
                'value': 'Preliminary results',
            },
        ],
        'report_numbers': [
            {
                'source': 'CDS',
                'value': 'CMS-PAS-SMP-15-001',
            },
        ],
    }
    result = hep.do(create_record_from_dict(result))

    assert validate(result['report_numbers'], subschema_report_numbers) is None
    assert validate(result['public_notes'], subschema_public_notes) is None
    assert validate(result['document_type'], subschema_document_type) is None
    assert expected['report_numbers'] == result['report_numbers']
    assert expected['public_notes'] == result['public_notes']
    assert expected['document_type'] == result['document_type']


def test_languages_from_multiple_041__a():
    schema = load_schema('hep')
    subschema = schema['properties']['languages']

    snippet = (  # cds.cern.ch/record/2258299
        '<record>'
        '  <datafield tag="041" ind1=" " ind2=" ">'
        '    <subfield code="a">eng</subfield>'
        '  </datafield>'
        '  <datafield tag="041" ind1=" " ind2=" ">'
        '    <subfield code="a">fre</subfield>'
        '  </datafield>'
        '</record>'
    )

    expected = [
        {'a': 'English'},
        {'a': 'French'},
    ]
    result = cds2hep_marc.do(create_record(snippet))

    assert expected == result['041__']

    expected = ['en', 'fr']
    result = hep.do(create_record_from_dict(result))

    assert validate(result['languages'], subschema) is None
    assert expected == result['languages']


def test_languages_from_041__a_ignores_english():
    snippet = (  # cds.cern.ch/record/2295270
        '<datafield tag="041" ind1=" " ind2=" ">'
        '  <subfield code="a">eng</subfield>'
        '</datafield>'
    )

    result = cds2hep_marc.do(create_record(snippet))

    assert '041__' not in result


def test_authors_from_100__a_0_u_m_and_700__a_0_u_m():
    schema = load_schema('hep')
    subschema = schema['properties']['authors']

    snippet = (  # record/2295263
        '<record>'
        '  <datafield tag="100" ind1=" " ind2=" ">'
        '    <subfield code="a">Joram, Christian</subfield>'
        '    <subfield code="0">AUTHOR|(INSPIRE)INSPIRE-00093928</subfield>'
        '    <subfield code="0">AUTHOR|(SzGeCERN)403463</subfield>'
        '    <subfield code="0">AUTHOR|(CDS)2068232</subfield>'
        '    <subfield code="u">CERN</subfield>'
        '    <subfield code="m">Christian.Joram@cern.ch</subfield>'
        '  </datafield>'
        '  <datafield tag="700" ind1=" " ind2=" ">'
        '    <subfield code="a">Pons, Xavier</subfield>'
        '    <subfield code="0">AUTHOR|(CDS)2067681</subfield>'
        '    <subfield code="0">AUTHOR|(SzGeCERN)531402</subfield>'
        '    <subfield code="u">CERN</subfield>'
        '    <subfield code="m">Xavier.Pons@cern.ch</subfield>'
        '  </datafield>'
        '</record>'
    )

    expected = {
        '100__': [
            {
                'a': 'Joram, Christian',
                'i': ['INSPIRE-00093928'],
                'j': ['CCID-403463'],
                'u': 'CERN',
                'm': 'Christian.Joram@cern.ch',
            },
        ],
        '700__': [
            {
                'a': 'Pons, Xavier',
                'j': ['CCID-531402'],
                'u': 'CERN',
                'm': 'Xavier.Pons@cern.ch',
            },
        ],
    }
    result = cds2hep_marc.do(create_record(snippet))

    assert expected['100__'] == result['100__']
    assert expected['700__'] == result['700__']

    expected = [
        {
            'full_name': 'Joram, Christian',
            'ids': [
                {
                    'schema': 'INSPIRE ID',
                    'value': 'INSPIRE-00093928',
                },
                {
                    'schema': 'CERN',
                    'value': 'CERN-403463',
                },
            ],
            'affiliations': [{'value': 'CERN'}],
            'emails': ['Christian.Joram@cern.ch'],
        },
        {
            'full_name': 'Pons, Xavier',
            'ids': [
                {
                    'schema': 'CERN',
                    'value': 'CERN-531402',
                },
            ],
            'affiliations': [{'value': 'CERN'}],
            'emails': ['Xavier.Pons@cern.ch'],
        },
    ]
    result = hep.do(create_record_from_dict(result))

    assert validate(result['authors'], subschema) is None
    assert expected == result['authors']


def test_authors_from_100_a_i_j_u_0_9_ignores_beard():
    schema = load_schema('hep')
    subschema = schema['properties']['authors']

    snippet = (  # cds.cern.ch/record/2285529
        '<datafield tag="100" ind1=" " ind2=" ">'
        '  <subfield code="0">AUTHOR|(CDS)2077287</subfield>'
        '  <subfield code="9">#BEARD#</subfield>'
        '  <subfield code="a">Dietz-Laursonn, Erik</subfield>'
        '  <subfield code="i">INSPIRE-00271239</subfield>'
        '  <subfield code="j">CCID-695565</subfield>'
        '  <subfield code="u">Aachen, Tech. Hochsch.</subfield>'
        '</datafield>'
    )

    expected = [
        {
            '9': '#BEARD#',
            'a': 'Dietz-Laursonn, Erik',
            'i': 'INSPIRE-00271239',
            'j': 'CCID-695565',
            'u': 'Aachen, Tech. Hochsch.',
        }
    ]
    result = cds2hep_marc.do(create_record(snippet))

    assert expected == result['100__']

    expected = [
        {
            'full_name': 'Dietz-Laursonn, Erik',
            'ids': [
                {
                    'schema': 'INSPIRE ID',
                    'value': 'INSPIRE-00271239',
                },
                {
                    'schema': 'CERN',
                    'value': 'CERN-695565',
                },
            ],
            'affiliations': [
                {'value': 'Aachen, Tech. Hochsch.'},
            ],
        },
    ]
    result = hep.do(create_record_from_dict(result))

    assert validate(result['authors'], subschema) is None
    assert expected == result['authors']


def test_authors_from_100__a_u_and_multiple_700__a_u_e():
    schema = load_schema('hep')
    subschema = schema['properties']['authors']

    snippet = (  # record/2295265
        '<record>'
        '  <datafield tag="100" ind1=" " ind2=" ">'
        '    <subfield code="a">Aichinger, Ida</subfield>'
        '    <subfield code="u">Linz U.</subfield>'
        '  </datafield>'
        '  <datafield tag="700" ind1=" " ind2=" ">'
        '    <subfield code="a">Larcher, Gerhard</subfield>'
        '    <subfield code="u">Linz U.</subfield>'
        '    <subfield code="e">dir.</subfield>'
        '  </datafield>'
        '  <datafield tag="700" ind1=" " ind2=" ">'
        '    <subfield code="a">Kersevan, Roberto</subfield>'
        '    <subfield code="u">Linz U.</subfield>'
        '    <subfield code="e">dir.</subfield>'
        '  </datafield>'
        '</record>'
    )

    expected = {
        '100__': [
            {
                'a': 'Aichinger, Ida',
                'u': 'Linz U.',
            },
        ],
        '701__': [
            {
                'a': 'Larcher, Gerhard',
                'e': 'dir.',
                'u': 'Linz U.',
            },
            {
                'a': 'Kersevan, Roberto',
                'e': 'dir.',
                'u': 'Linz U.',
            },
        ],
    }
    result = cds2hep_marc.do(create_record(snippet))

    assert expected['100__'] == result['100__']
    assert expected['701__'] == result['701__']

    expected = [
        {
            'full_name': 'Aichinger, Ida',
            'affiliations': [{'value': 'Linz U.'}],
        },
        {
            'full_name': 'Larcher, Gerhard',
            'inspire_roles': ['supervisor'],
            'affiliations': [{'value': 'Linz U.'}],
        },
        {
            'full_name': 'Kersevan, Roberto',
            'inspire_roles': ['supervisor'],
            'affiliations': [{'value': 'Linz U.'}],
        },
    ]
    result = hep.do(create_record_from_dict(result))

    assert validate(result['authors'], subschema) is None
    assert expected == result['authors']


def test_authors_from_100__a_normalizes_name():
    schema = load_schema('hep')
    subschema = schema['properties']['authors']

    snippet = (  # cds.cern.ch/record/1099557
        '<datafield tag="100" ind1=" " ind2=" ">'
        '  <subfield code="a">Tagliente, G</subfield>'
        '</datafield>'
    )

    expected = [
        {
            'a': 'Tagliente, G.',
        },
    ]
    result = cds2hep_marc.do(create_record(snippet))

    assert expected == result['100__']

    expected = [
        {
            'full_name': 'Tagliente, G.',
        },
    ]
    result = hep.do(create_record_from_dict(result))

    assert validate(result['authors'], subschema) is None
    assert expected == result['authors']


def test_corporate_author_from_110__a():
    schema = load_schema('hep')
    subschema = schema['properties']['corporate_author']

    snippet = (  # cds.cern.ch/record/2292626
        '<datafield tag="110" ind1=" " ind2=" ">'
        '  <subfield code="a">CERN. Geneva. Research Board Committee</subfield>'
        '</datafield>'
    )

    expected = [
        {'a': 'CERN. Geneva. Research Board Committee'},
    ]
    result = cds2hep_marc.do(create_record(snippet))

    assert expected == result['110__']

    expected = ['CERN. Geneva. Research Board Committee']
    result = hep.do(create_record_from_dict(result))

    assert validate(result['corporate_author'], subschema) is None
    assert expected == result['corporate_author']


def test_title_translations_from_242__a():
    schema = load_schema('hep')
    subschema = schema['properties']['title_translations']

    snippet = (  # cds.cern.ch/record/2293251
        '<datafield tag="242" ind1=" " ind2=" ">  <subfield'
        ' code="a">Reconstruction of the invariant masses of bosons of the'
        ' Standard Model using public data from ATLAS Open'
        ' Data</subfield></datafield>'
    )

    expected = {
        '9': 'CDS',
        'a': (
            'Reconstruction of the invariant masses of bosons of the Standard'
            ' Model using public data from ATLAS Open Data'
        ),
    }
    result = cds2hep_marc.do(create_record(snippet))

    assert expected == result['242__']

    expected = [
        {
            'source': 'CDS',
            'language': 'en',
            'title': (
                'Reconstruction of the invariant masses of bosons of the'
                ' Standard Model using public data from ATLAS Open Data'
            ),
        },
    ]
    result = hep.do(create_record_from_dict(result))

    assert validate(result['title_translations'], subschema) is None
    assert expected == result['title_translations']


def test_titles_from_245__a():
    schema = load_schema('hep')
    subschema = schema['properties']['titles']

    snippet = (  # cds.cern.ch/record/2293251
        '<datafield tag="245" ind1=" " ind2=" ">  <subfield'
        ' code="a">Reconstrucción de masas invariantes de bosones del Modelo'
        ' Estándar usando datos públicos de ATLAS Open'
        ' Data</subfield></datafield>'
    )

    expected = {
        '9': 'CDS',
        'a': (
            u'Reconstrucción de masas invariantes de bosones del Modelo'
            u' Estándar usando datos públicos de ATLAS Open Data'
        ),
    }
    result = cds2hep_marc.do(create_record(snippet))

    assert expected == result['245__']

    expected = [
        {
            'source': 'CDS',
            'title': (
                u'Reconstrucción de masas invariantes de bosones del Modelo'
                u' Estándar usando datos públicos de ATLAS Open Data'
            ),
        },
    ]
    result = hep.do(create_record_from_dict(result))

    assert validate(result['titles'], subschema) is None
    assert expected == result['titles']


def test_titles_from_246__a_b():
    schema = load_schema('hep')
    subschema = schema['properties']['titles']

    snippet = (  # cds.cern.ch/record/1999859
        '<datafield tag="246" ind1=" " ind2=" ">  <subfield'
        ' code="a">v.2</subfield>  <subfield code="b">Advances and applications'
        ' the deterministic case</subfield></datafield>'
    )

    expected = [
        {
            '9': 'CDS',
            'a': 'v.2',
            'b': 'Advances and applications the deterministic case',
        }
    ]
    result = cds2hep_marc.do(create_record(snippet))

    assert expected == result['246__']

    expected = [
        {
            'source': 'CDS',
            'title': 'v.2',
            'subtitle': 'Advances and applications the deterministic case',
        },
    ]
    result = hep.do(create_record_from_dict(result))

    assert validate(result['titles'], subschema) is None
    assert expected == result['titles']


def test_imprints_from_260__a_b_c():
    schema = load_schema('hep')
    subschema = schema['properties']['imprints']

    snippet = (  # cds.cern.ch/record/1999859
        '<datafield tag="260" ind1=" " ind2=" ">'
        '  <subfield code="a">Hoboken, NJ</subfield>'
        '  <subfield code="b">Wiley</subfield>'
        '  <subfield code="c">2015</subfield>'
        '</datafield>'
    )

    expected = {
        'a': 'Hoboken, NJ',
        'b': 'Wiley',
        'c': '2015',
    }
    result = cds2hep_marc.do(create_record(snippet))

    assert expected == result['260__']

    expected = [
        {
            'place': 'Hoboken, NJ',
            'publisher': 'Wiley',
            'date': '2015',
        }
    ]
    result = hep.do(create_record_from_dict(result))

    assert validate(result['imprints'], subschema) is None
    assert expected == result['imprints']


def test_number_of_pages_from_300__a():
    schema = load_schema('hep')
    subschema = schema['properties']['number_of_pages']

    snippet = (  # cds.cern.ch/record/2292558
        '<datafield tag="300" ind1=" " ind2=" ">'
        '  <subfield code="a">20 p</subfield>'
        '</datafield>'
    )

    expected = {
        'a': '20',
    }
    result = cds2hep_marc.do(create_record(snippet))

    assert expected == result['300__']

    expected = 20
    result = hep.do(create_record_from_dict(result))

    assert validate(result['number_of_pages'], subschema) is None
    assert expected == result['number_of_pages']


def test_thesis_info_from_502__a_b_c_and_500__a():
    schema = load_schema('hep')
    subschema = schema['properties']['thesis_info']

    snippet = (  # cds.cern.ch/record/2295265
        '<record>'
        '  <datafield tag="500" ind1=" " ind2=" ">'
        '    <subfield code="a">Presented 2017</subfield>'
        '  </datafield>'
        '  <datafield tag="502" ind1=" " ind2=" ">'
        '    <subfield code="a">PhD</subfield>'
        '    <subfield code="b">Linz U.</subfield>'
        '    <subfield code="c">2017</subfield>'
        '  </datafield>'
        '</record>'
    )

    expected = {
        '500__': [
            {
                '9': 'CDS',
                'a': 'Presented 2017',
            },
        ],
        '502__': {
            'b': 'PhD',
            'c': 'Linz U.',
            'd': '2017',
        },
    }
    result = cds2hep_marc.do(create_record(snippet))

    assert expected['500__'] == result['500__']
    assert expected['502__'] == result['502__']

    expected = {
        'institutions': [
            {'name': 'Linz U.'},
        ],
        'degree_type': 'phd',
        'date': '2017',
        'defense_date': '2017',
    }
    result = hep.do(create_record_from_dict(result))

    assert validate(result['thesis_info'], subschema) is None
    assert expected == result['thesis_info']


def test_abstracts_from_520__a():
    schema = load_schema('hep')
    subschema = schema['properties']['abstracts']

    snippet = (  # cds.cern.ch/record/2295265
        '<datafield tag="520" ind1=" " ind2=" ">  <subfield code="a">The'
        ' underlying thesis on mathematical simulation methods in application'
        ' and theory is structured into three parts. The first part sets up a'
        ' mathematical model capable of predicting the performance and'
        ' operation of an accelerator’s vacuum system based on analytical'
        ' methods. A coupled species-balance equation system describes the'
        ' distribution of the gas dynamics in an ultra-high vacuum system'
        ' considering impacts of conductance limitations, beam induced effects'
        ' (ion-, electron-, and photon-induced de- sorption), thermal'
        ' outgassing and sticking probabilities of the chamber materials. A new'
        ' solving algorithm based on sparse matrix representations, is'
        ' introduced and presents a closed form solution of the equation'
        ' system. The model is implemented in a Python environment, named'
        ' PyVasco, and is supported by a graphical user interface to make it'
        ' easy available for everyone. A sensitivity analysis, a cross-check'
        ' with the Test-Particle Monte Carlo simulation program Molflow+ and a'
        ' comparison of the simulation results to readings of the Large Hadron'
        ' Colliders (LHC) pressure gauges validate the code. The computation of'
        ' density profiles considering several effects (as men- tioned above)'
        ' is performed within a short computation time for indefinitely long'
        ' vacuum systems. This is in particular interesting for the design of a'
        ' stable vacuum system for new large accelerat- ors like the Future'
        ' Circular Colliders (FCC) with 100 km in circumference. A simulation'
        ' of the FCC is shown at the end of this part. Additionally, PyVasco'
        ' was presented twice at international conferences in Rome and Berlin'
        ' and has been submitted in July with the title “Analytical vacuum'
        ' simulations in high energy accelerators for future machines based on'
        ' the LHC performance” to the Journal “Physical Review Accelerator and'
        ' Beams”. The second and third part of the thesis study properties of'
        ' quasi-Monte Carlo (QMC) methods in the scope of the special research'
        ' project “Quasi-Monte Carlo methods: Theory and Applications”. Instead'
        ' of solving a complex integral analytically, its value is approximated'
        ' by function evaluation at specific points. The choice of a good point'
        ' set is critical for a good result. It turned out that continuous'
        ' curves provide a good tool to define these point sets. So called'
        ' “bounded remainder sets” (BRS) define a measure for the quality of'
        ' the uniform distribution of a curve in the unit- square. The'
        ' trajectory of a billiard path with an irrational slope is especially'
        ' well distributed. Certain criteria to the BRS are defined and'
        ' analysed in regard to the distribution error. The idea of the proofs'
        ' is based on Diophantine approximations of irrational numbers and on'
        ' the unfolding technique of the billiard path to a straight line in'
        ' the plane. New results of the BRS for the billiard path are reported'
        ' to the “Journal of Uniform Distribution”. The third part analyses the'
        ' distribution of the energy levels of quantum systems. It was stated'
        ' that the eigenvalues of the energy spectra for almost all integrable'
        ' quantum systems are uncor- related and Poisson distributed. The'
        ' harmonic oscillator presents already one counter example to this'
        ' assertion. The particle in a box on the other hand obtains these'
        ' properties. This thesis formulates a general statement that describes'
        ' under which conditions the eigenvalues do not follow the poissonian'
        ' property. The concept of the proofs is based on the analysis of the'
        ' pair correlations of sequences. The former particle physicist Ian'
        ' Sloan also exposed this topic and he became spe- cialized as a'
        ' skilled mathematician in this field. To honour his achievements a'
        ' Festschrift for his 80th birthday is written and the results of the'
        ' work of this thesis are published there. The book will appear in'
        ' 2018.</subfield></datafield>'
    )

    expected = [
        {
            '9': 'CDS',
            'a': (
                u'The underlying thesis on mathematical simulation methods in'
                u' application and theory is structured into three parts. The'
                u' first part sets up a mathematical model capable of'
                u' predicting the performance and operation of an accelerator’s'
                u' vacuum system based on analytical methods. A coupled'
                u' species-balance equation system describes the distribution'
                u' of the gas dynamics in an ultra-high vacuum system'
                u' considering impacts of conductance limitations, beam induced'
                u' effects (ion-, electron-, and photon-induced de- sorption),'
                u' thermal outgassing and sticking probabilities of the chamber'
                u' materials. A new solving algorithm based on sparse matrix'
                u' representations, is introduced and presents a closed form'
                u' solution of the equation system. The model is implemented in'
                u' a Python environment, named PyVasco, and is supported by a'
                u' graphical user interface to make it easy available for'
                u' everyone. A sensitivity analysis, a cross-check with the'
                u' Test-Particle Monte Carlo simulation program Molflow+ and a'
                u' comparison of the simulation results to readings of the'
                u' Large Hadron Colliders (LHC) pressure gauges validate the'
                u' code. The computation of density profiles considering'
                u' several effects (as men- tioned above) is performed within a'
                u' short computation time for indefinitely long vacuum systems.'
                u' This is in particular interesting for the design of a stable'
                u' vacuum system for new large accelerat- ors like the Future'
                u' Circular Colliders (FCC) with 100 km in circumference. A'
                u' simulation of the FCC is shown at the end of this part.'
                u' Additionally, PyVasco was presented twice at international'
                u' conferences in Rome and Berlin and has been submitted in'
                u' July with the title “Analytical vacuum simulations in high'
                u' energy accelerators for future machines based on the LHC'
                u' performance” to the Journal “Physical Review Accelerator and'
                u' Beams”. The second and third part of the thesis study'
                u' properties of quasi-Monte Carlo (QMC) methods in the scope'
                u' of the special research project “Quasi-Monte Carlo methods:'
                u' Theory and Applications”. Instead of solving a complex'
                u' integral analytically, its value is approximated by function'
                u' evaluation at specific points. The choice of a good point'
                u' set is critical for a good result. It turned out that'
                u' continuous curves provide a good tool to define these point'
                u' sets. So called “bounded remainder sets” (BRS) define a'
                u' measure for the quality of the uniform distribution of a'
                u' curve in the unit- square. The trajectory of a billiard path'
                u' with an irrational slope is especially well distributed.'
                u' Certain criteria to the BRS are defined and analysed in'
                u' regard to the distribution error. The idea of the proofs is'
                u' based on Diophantine approximations of irrational numbers'
                u' and on the unfolding technique of the billiard path to a'
                u' straight line in the plane. New results of the BRS for the'
                u' billiard path are reported to the “Journal of Uniform'
                u' Distribution”. The third part analyses the distribution of'
                u' the energy levels of quantum systems. It was stated that the'
                u' eigenvalues of the energy spectra for almost all integrable'
                u' quantum systems are uncor- related and Poisson distributed.'
                u' The harmonic oscillator presents already one counter example'
                u' to this assertion. The particle in a box on the other hand'
                u' obtains these properties. This thesis formulates a general'
                u' statement that describes under which conditions the'
                u' eigenvalues do not follow the poissonian property. The'
                u' concept of the proofs is based on the analysis of the pair'
                u' correlations of sequences. The former particle physicist Ian'
                u' Sloan also exposed this topic and he became spe- cialized as'
                u' a skilled mathematician in this field. To honour his'
                u' achievements a Festschrift for his 80th birthday is written'
                u' and the results of the work of this thesis are published'
                u' there. The book will appear in 2018.'
            ),
        },
    ]
    result = cds2hep_marc.do(create_record(snippet))

    assert expected == result['520__']

    expected = [
        {
            'source': 'CDS',
            'value': (
                u'The underlying thesis on mathematical simulation methods in'
                u' application and theory is structured into three parts. The'
                u' first part sets up a mathematical model capable of'
                u' predicting the performance and operation of an accelerator’s'
                u' vacuum system based on analytical methods. A coupled'
                u' species-balance equation system describes the distribution'
                u' of the gas dynamics in an ultra-high vacuum system'
                u' considering impacts of conductance limitations, beam induced'
                u' effects (ion-, electron-, and photon-induced de- sorption),'
                u' thermal outgassing and sticking probabilities of the chamber'
                u' materials. A new solving algorithm based on sparse matrix'
                u' representations, is introduced and presents a closed form'
                u' solution of the equation system. The model is implemented in'
                u' a Python environment, named PyVasco, and is supported by a'
                u' graphical user interface to make it easy available for'
                u' everyone. A sensitivity analysis, a cross-check with the'
                u' Test-Particle Monte Carlo simulation program Molflow+ and a'
                u' comparison of the simulation results to readings of the'
                u' Large Hadron Colliders (LHC) pressure gauges validate the'
                u' code. The computation of density profiles considering'
                u' several effects (as men- tioned above) is performed within a'
                u' short computation time for indefinitely long vacuum systems.'
                u' This is in particular interesting for the design of a stable'
                u' vacuum system for new large accelerat- ors like the Future'
                u' Circular Colliders (FCC) with 100 km in circumference. A'
                u' simulation of the FCC is shown at the end of this part.'
                u' Additionally, PyVasco was presented twice at international'
                u' conferences in Rome and Berlin and has been submitted in'
                u' July with the title “Analytical vacuum simulations in high'
                u' energy accelerators for future machines based on the LHC'
                u' performance” to the Journal “Physical Review Accelerator and'
                u' Beams”. The second and third part of the thesis study'
                u' properties of quasi-Monte Carlo (QMC) methods in the scope'
                u' of the special research project “Quasi-Monte Carlo methods:'
                u' Theory and Applications”. Instead of solving a complex'
                u' integral analytically, its value is approximated by function'
                u' evaluation at specific points. The choice of a good point'
                u' set is critical for a good result. It turned out that'
                u' continuous curves provide a good tool to define these point'
                u' sets. So called “bounded remainder sets” (BRS) define a'
                u' measure for the quality of the uniform distribution of a'
                u' curve in the unit- square. The trajectory of a billiard path'
                u' with an irrational slope is especially well distributed.'
                u' Certain criteria to the BRS are defined and analysed in'
                u' regard to the distribution error. The idea of the proofs is'
                u' based on Diophantine approximations of irrational numbers'
                u' and on the unfolding technique of the billiard path to a'
                u' straight line in the plane. New results of the BRS for the'
                u' billiard path are reported to the “Journal of Uniform'
                u' Distribution”. The third part analyses the distribution of'
                u' the energy levels of quantum systems. It was stated that the'
                u' eigenvalues of the energy spectra for almost all integrable'
                u' quantum systems are uncor- related and Poisson distributed.'
                u' The harmonic oscillator presents already one counter example'
                u' to this assertion. The particle in a box on the other hand'
                u' obtains these properties. This thesis formulates a general'
                u' statement that describes under which conditions the'
                u' eigenvalues do not follow the poissonian property. The'
                u' concept of the proofs is based on the analysis of the pair'
                u' correlations of sequences. The former particle physicist Ian'
                u' Sloan also exposed this topic and he became spe- cialized as'
                u' a skilled mathematician in this field. To honour his'
                u' achievements a Festschrift for his 80th birthday is written'
                u' and the results of the work of this thesis are published'
                u' there. The book will appear in 2018.'
            ),
        },
    ]
    result = hep.do(create_record_from_dict(result))

    assert validate(result['abstracts'], subschema) is None
    assert expected == result['abstracts']


def test_inspire_categories_from_65017a_2():
    schema = load_schema('hep')
    subschema = schema['properties']['inspire_categories']

    snippet = (  # cds.cern.ch/record/2276097
        '<datafield tag="650" ind1="1" ind2="7">'
        '  <subfield code="2">SzGeCERN</subfield>'
        '  <subfield code="a">Engineering</subfield>'
        '</datafield>'
    )

    expected = [
        {
            '2': 'INSPIRE',
            '9': 'CDS',
            'a': 'Instrumentation',
        },
    ]
    result = cds2hep_marc.do(create_record(snippet))

    assert expected == result['65017']

    expected = [
        {
            'source': 'cds',
            'term': 'Instrumentation',
        },
    ]
    result = hep.do(create_record_from_dict(result))

    assert validate(result['inspire_categories'], subschema) is None
    assert expected == result['inspire_categories']


def test_keywords_from_6531_a_9():
    schema = load_schema('hep')
    subschema = schema['properties']['keywords']

    snippet = (  # cds.cern.ch/record/1123149
        '<datafield tag="653" ind1="1" ind2=" ">'
        '  <subfield code="9">CERN</subfield>'
        '  <subfield code="a">QCD</subfield>'
        '</datafield>'
    )

    expected = [
        {
            '9': 'CERN',
            'a': 'QCD',
        },
    ]
    result = cds2hep_marc.do(create_record(snippet))

    assert expected == result['6531_']

    expected = [
        {
            'source': 'CERN',
            'value': 'QCD',
        },
    ]
    result = hep.do(create_record_from_dict(result))

    assert validate(result['keywords'], subschema) is None
    assert expected == result['keywords']


def test_accelerator_experiments_from_693__a():
    schema = load_schema('hep')
    subschema = schema['properties']['accelerator_experiments']

    snippet = (  # regression test, unknown record
        '<datafield tag="693" ind1=" " ind2=" ">'
        '  <subfield code="a">CERN LHC</subfield>'
        '</datafield>'
    )

    expected = [
        {
            'a': 'CERN LHC',
            'e': 'CERN-LHC',
        },
    ]
    result = cds2hep_marc.do(create_record(snippet))

    assert expected == result['693__']

    expected = [
        {
            'legacy_name': 'CERN-LHC',
        },
    ]
    result = hep.do(create_record_from_dict(result))

    assert validate(result['accelerator_experiments'], subschema) is None
    assert expected == result['accelerator_experiments']


def test_accelerator_experiments_from_693__a_e():
    schema = load_schema('hep')
    subschema = schema['properties']['accelerator_experiments']

    snippet = (  # cds.cern.ch/record/2295080
        '<datafield tag="693" ind1=" " ind2=" ">'
        '  <subfield code="a">CERN LHC</subfield>'
        '  <subfield code="e">ALICE</subfield>'
        '</datafield>'
    )

    expected = [
        {
            'a': 'CERN LHC',
            'e': 'CERN-LHC-ALICE',
        },
    ]
    result = cds2hep_marc.do(create_record(snippet))

    assert expected == result['693__']

    expected = [
        {
            'legacy_name': 'CERN-LHC-ALICE',
        },
    ]
    result = hep.do(create_record_from_dict(result))

    assert validate(result['accelerator_experiments'], subschema) is None
    assert expected == result['accelerator_experiments']


def test_accelerator_experiments_from_693__a_e_ignores_not_applicable():
    snippet = (  # cds.cern.ch/record/329074
        '<datafield tag="693" ind1=" " ind2=" ">'
        '  <subfield code="a">Not applicable</subfield>'
        '  <subfield code="e">Not applicable</subfield>'
        '</datafield>'
    )

    result = cds2hep_marc.do(create_record(snippet))

    assert '693__' not in result


def test_accelerator_experiments_from_693__a_e_ignores_not_applicable_only_one_field():
    schema = load_schema('hep')
    subschema = schema['properties']['accelerator_experiments']

    snippet = (
        '<datafield tag="693" ind1=" " ind2=" ">'
        '  <subfield code="a">CERN SPS</subfield>'
        '  <subfield code="e">Not applicable</subfield>'
        '</datafield>'
    )

    expected = [
        {
            'a': 'CERN SPS',
            'e': 'CERN-SPS',
        },
    ]
    result = cds2hep_marc.do(create_record(snippet))

    assert expected == result['693__']

    expected = [
        {
            'legacy_name': 'CERN-SPS',
        },
    ]
    result = hep.do(create_record_from_dict(result))

    assert validate(result['accelerator_experiments'], subschema) is None
    assert expected == result['accelerator_experiments']


def test_arxiv_eprints_from_037__a_b_9_and_695__a_9():
    schema = load_schema('hep')
    subschema = schema['properties']['arxiv_eprints']

    snippet = (  # cds.cern.ch/record/2270264
        '<record>'
        '  <datafield tag="037" ind1=" " ind2=" ">'
        '    <subfield code="9">arXiv</subfield>'
        '    <subfield code="a">arXiv:1607.05039</subfield>'
        '    <subfield code="c">hep-ex</subfield>'
        '  </datafield>'
        '  <datafield tag="695" ind1=" " ind2=" ">'
        '    <subfield code="9">LANL EDS</subfield>'
        '    <subfield code="a">hep-ex</subfield>'
        '  </datafield>'
        '  <datafield tag="695" ind1=" " ind2=" ">'
        '    <subfield code="9">LANL EDS</subfield>'
        '    <subfield code="a">hep-ph</subfield>'
        '  </datafield>'
        '</record>'
    )

    expected = {
        '037__': [
            {
                '9': 'arXiv',
                'a': 'arXiv:1607.05039',
                'c': 'hep-ex',
            },
        ],
        '65017': [
            {
                '2': 'arXiv',
                'a': 'hep-ex',
            },
            {
                '2': 'arXiv',
                'a': 'hep-ph',
            },
        ],
    }
    result = cds2hep_marc.do(create_record(snippet))

    assert expected['037__'] == result['037__']
    assert expected['65017'] == result['65017']

    expected = [
        {
            'value': '1607.05039',
            'categories': ['hep-ex', 'hep-ph'],
        },
    ]
    result = hep.do(create_record_from_dict(result))

    assert validate(result['arxiv_eprints'], subschema) is None
    assert expected == result['arxiv_eprints']


def test_collaboration_from_710__g():
    schema = load_schema('hep')
    subschema = schema['properties']['collaborations']

    snippet = (  # cds.cern.ch/2295739
        '<datafield tag="710" ind1=" " ind2=" ">'
        '  <subfield code="g">ATLAS Collaboration</subfield>'
        '</datafield>'
    )

    expected = [{'g': 'ATLAS Collaboration'}]
    result = cds2hep_marc.do(create_record(snippet))

    assert expected == result['710__']

    expected = [{'value': 'ATLAS'}]
    result = hep.do(create_record_from_dict(result))

    assert validate(result['collaborations'], subschema) is None
    assert expected == result['collaborations']


def test_publication_info_from_773__c_w_0():
    schema = load_schema('hep')
    subschema = schema['properties']['publication_info']

    snippet = (  # cds.cern.ch/record/2294664
        '<datafield tag="773" ind1=" " ind2=" ">'
        '  <subfield code="0">1217633</subfield>'
        '  <subfield code="c">3-6</subfield>'
        '  <subfield code="w">C07-03-17</subfield>'
        '</datafield>'
    )

    expected = [
        {
            '0': '1217633',
            'c': '3-6',
            'w': 'C07-03-17',
        },
    ]
    result = cds2hep_marc.do(create_record(snippet))

    assert expected == result['773__']

    expected = [
        {
            'cnum': 'C07-03-17',
            'page_start': '3',
            'page_end': '6',
            'parent_record': {
                '$ref': 'http://localhost:5000/api/literature/1217633',
            },
        },
    ]
    result = hep.do(create_record_from_dict(result))

    assert validate(result['publication_info'], subschema) is None
    assert expected == result['publication_info']


def test_documents_from_8564_s_u_y_8():
    schema = load_schema('hep')
    subschema = schema['properties']['documents']

    snippet = (  # cds.cern.ch/record/2294664
        '<datafield tag="856" ind1="4" ind2=" ">  <subfield'
        ' code="8">1369908</subfield>  <subfield code="s">76482</subfield> '
        ' <subfield'
        ' code="u">http://cds.cern.ch/record/2294664/files/James.pdf</subfield>'
        '  <subfield code="y">Fulltext</subfield></datafield>'
    )

    expected = [
        {
            't': 'CDS',
            'a': 'http://cds.cern.ch/record/2294664/files/James.pdf',
            'd': 'Fulltext',
            'n': 'James.pdf',
            'f': '.pdf',
        },
    ]
    result = cds2hep_marc.do(create_record(snippet))

    assert expected == result['FFT__']

    expected = [
        {
            'key': 'James.pdf',
            'fulltext': True,
            'source': 'CDS',
            'url': 'http://cds.cern.ch/record/2294664/files/James.pdf',
        },
    ]
    result = hep.do(create_record_from_dict(result))

    assert validate(result['documents'], subschema) is None
    assert expected == result['documents']


def test_documents_from_8564_s_u_y_8_escapes_spaces():
    schema = load_schema('hep')
    subschema = schema['properties']['documents']

    snippet = (  # cds.cern.ch/record/2636102
        '<datafield tag="856" ind1="4" ind2=" ">  <subfield'
        ' code="8">1427610</subfield>  <subfield code="s">8265196</subfield> '
        ' <subfield code="u">http://cds.cern.ch/record/2636102/files/Thesis'
        ' Fiorendi.pdf</subfield>  <subfield'
        ' code="y">Fulltext</subfield></datafield>'
    )

    expected = [
        {
            't': 'CDS',
            'a': 'http://cds.cern.ch/record/2636102/files/Thesis%20Fiorendi.pdf',
            'd': 'Fulltext',
            'n': 'Thesis Fiorendi.pdf',
            'f': '.pdf',
        },
    ]
    result = cds2hep_marc.do(create_record(snippet))

    assert expected == result['FFT__']

    expected = [
        {
            'key': 'Thesis Fiorendi.pdf',
            'fulltext': True,
            'source': 'CDS',
            'url': 'http://cds.cern.ch/record/2636102/files/Thesis%20Fiorendi.pdf',
        },
    ]
    result = hep.do(create_record_from_dict(result))

    assert validate(result['documents'], subschema) is None
    assert expected == result['documents']


def test_documents_from_8564_s_u_8_escapes_encoded_characters():
    schema = load_schema('hep')
    subschema = schema['properties']['documents']

    snippet = (  # cds.cern.ch/record/148555
        '<datafield tag="856" ind1="4" ind2=" ">'
        '  <subfield code="8">200773</subfield>'
        '  <subfield code="s">5978977</subfield>'
        '  <subfield'
        ' code="u">http://cds.cern.ch/record/148555/files/Rückl.pdf</subfield>'
        '</datafield>'
    )

    expected = [
        {
            't': 'CDS',
            'a': 'http://cds.cern.ch/record/148555/files/R%C3%BCckl.pdf',
            'n': u'R\xfcckl.pdf',
            'f': '.pdf',
        },
    ]
    result = cds2hep_marc.do(create_record(snippet))

    assert expected == result['FFT__']

    expected = [
        {
            'key': u'R\xfcckl.pdf',
            'source': 'CDS',
            'url': 'http://cds.cern.ch/record/148555/files/R%C3%BCckl.pdf',
        },
    ]
    result = hep.do(create_record_from_dict(result))

    assert validate(result['documents'], subschema) is None
    assert expected == result['documents']


def test_documents_from_8564_s_u_y_8_ignores_preprint():
    snippet = (  # cds.cern.ch/record/2295716
        '<datafield tag="856" ind1="4" ind2=" ">  <subfield code="8">1371451</subfield>'
        '  <subfield code="s">4446886</subfield>  <subfield'
        ' code="u">http://cds.cern.ch/record/2295716/files/arXiv:1711.07494.pdf</subfield>'
        '  <subfield code="y">Preprint</subfield></datafield>'
    )

    result = cds2hep_marc.do(create_record(snippet))

    assert '8564_' not in result


def test_urls_from_8564_s_u_y_8_local_copy():
    schema = load_schema('hep')
    subschema = schema['properties']['urls']

    snippet = (  # cds.cern.ch/record/2159118
        '<datafield tag="856" ind1="4" ind2=" ">  <subfield code="s">1119425</subfield>'
        '  <subfield'
        ' code="u">http://cds.cern.ch/record/1979225/files/1748-0221_10_01_C01003.pdf</subfield>'
        '  <subfield code="y">Published version from IOP, local copy</subfield> '
        ' <subfield code="8">1053236</subfield></datafield>'
    )

    expected = [
        {
            'u': 'http://cds.cern.ch/record/1979225/files/1748-0221_10_01_C01003.pdf',
            'y': 'Published version from IOP, on CERN Document Server',
        },
    ]
    result = cds2hep_marc.do(create_record(snippet))

    assert expected == result['8564_']

    expected = [
        {
            'value': (
                'http://cds.cern.ch/record/1979225/files/1748-0221_10_01_C01003.pdf'
            ),
            'description': 'Published version from IOP, on CERN Document Server',
        },
    ]
    result = hep.do(create_record_from_dict(result))

    assert validate(result['urls'], subschema) is None
    assert expected == result['urls']


def test_urls_from_8564_u_y():
    schema = load_schema('hep')
    subschema = schema['properties']['urls']

    snippet = (  # cds.cern.ch/record/2159118
        '<datafield tag="856" ind1="4" ind2=" ">  <subfield'
        ' code="u">http://pos.sissa.it/archive/conferences/209/007/Charged2014_007.pdf</subfield>'
        '  <subfield code="y">Published version from PoS</subfield></datafield>'
    )

    expected = [
        {
            'u': 'http://pos.sissa.it/archive/conferences/209/007/Charged2014_007.pdf',
            'y': 'Published version from PoS',
        },
    ]
    result = cds2hep_marc.do(create_record(snippet))

    assert expected == result['8564_']

    expected = [
        {
            'value': (
                'http://pos.sissa.it/archive/conferences/209/007/Charged2014_007.pdf'
            ),
            'description': 'Published version from PoS',
        },
    ]
    result = hep.do(create_record_from_dict(result))

    assert validate(result['urls'], subschema) is None
    assert expected == result['urls']


def test_document_type_from_962__b_k_n():
    schema = load_schema('hep')
    subschema = schema['properties']['document_type']

    snippet = (  # cds.cern.ch/record/2275456
        '<datafield tag="962" ind1=" " ind2=" ">'
        '  <subfield code="b">1075481</subfield>'
        '  <subfield code="n">lathuile20080301</subfield>'
        '  <subfield code="k">79-84</subfield>'
        '</datafield>'
    )

    expected = [
        {'a': 'ConferencePaper'},
        {'a': 'HEP'},
        {'a': 'CORE'},
    ]
    result = cds2hep_marc.do(create_record(snippet))

    assert expected == result['980__']

    expected = ['conference paper']
    result = hep.do(create_record_from_dict(result))

    assert validate(result['document_type'], subschema) is None
    assert expected == result['document_type']


def test_document_type_from_multiple_980_a():
    schema = load_schema('hep')
    subschema = schema['properties']['document_type']

    snippet = (  # cds.cern.ch/record/1979225
        '<record>'
        '  <datafield tag="980" ind1=" " ind2=" ">'
        '    <subfield code="a">ARTICLE</subfield>'
        '  </datafield>'
        '  <datafield tag="980" ind1=" " ind2=" ">'
        '    <subfield code="a">ConferencePaper</subfield>'
        '  </datafield>'
        '</record>'
    )

    expected = [
        {'a': 'ConferencePaper'},
        {'a': 'HEP'},
        {'a': 'CORE'},
    ]
    result = cds2hep_marc.do(create_record(snippet))

    assert expected == result['980__']

    expected = ['conference paper']
    result = hep.do(create_record_from_dict(result))

    assert validate(result['document_type'], subschema) is None
    assert expected == result['document_type']
