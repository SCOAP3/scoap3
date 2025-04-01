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
from inspire_dojson.hep import hep, hep2marc
from inspire_dojson.hepnames import hepnames, hepnames2marc


def test_acquisition_source_from_541__a_c():
    schema = load_schema('hep')
    subschema = schema['properties']['acquisition_source']

    snippet = (  # record/1487640
        '<datafield tag="541" ind1=" " ind2=" ">'
        '  <subfield code="a">IOP</subfield>'
        '  <subfield code="c">batchupload</subfield>'
        '</datafield>'
    )

    expected = {
        'source': 'IOP',
        'method': 'batchuploader',
    }
    result = hep.do(create_record(snippet))

    assert validate(result['acquisition_source'], subschema) is None
    assert expected == result['acquisition_source']

    expected = {
        'a': 'IOP',
        'c': 'batchupload',
    }
    result = hep2marc.do(result)

    assert expected == result['541']


def test_acquisition_source_from_541__double_a_b_c_e():
    schema = load_schema('hep')
    subschema = schema['properties']['acquisition_source']

    snippet = (  # record/1416571
        '<datafield tag="541" ind1=" " ind2=" ">'
        '  <subfield code="a">inspire:uid:52524</subfield>'
        '  <subfield code="a">orcid:0000-0002-1048-661X</subfield>'
        '  <subfield code="b">oliver.schlotterer@web.de</subfield>'
        '  <subfield code="c">submission</subfield>'
        '  <subfield code="e">504296</subfield>'
        '</datafield>'
    )

    expected = {
        'email': 'oliver.schlotterer@web.de',
        'internal_uid': 52524,
        'method': 'submitter',
        'orcid': '0000-0002-1048-661X',
        'submission_number': '504296',
    }
    result = hep.do(create_record(snippet))  # no roundtrip

    assert validate(result['acquisition_source'], subschema) is None
    assert expected == result['acquisition_source']

    expected = {
        'a': 'orcid:0000-0002-1048-661X',
        'b': 'oliver.schlotterer@web.de',
        'c': 'submission',
        'e': '504296',
    }
    result = hep2marc.do(result)

    assert expected == result['541']


def test_acquisition_source_from_541__a_b_c_d_e_converts_dates_to_datetimes():
    schema = load_schema('authors')
    subschema = schema['properties']['acquisition_source']

    snippet = (  # record/982806
        '<datafield tag="541" ind1=" " ind2=" ">'
        '  <subfield code="a">inspire:uid:51852</subfield>'
        '  <subfield code="b">jmyang@itp.ac.cn</subfield>'
        '  <subfield code="c">submission</subfield>'
        '  <subfield code="d">2016-05-24</subfield>'
        '  <subfield code="e">805819</subfield>'
        '</datafield>'
    )

    expected = {
        'datetime': '2016-05-24T00:00:00',
        'email': 'jmyang@itp.ac.cn',
        'internal_uid': 51852,
        'method': 'submitter',
        'submission_number': '805819',
    }
    result = hepnames.do(create_record(snippet))

    assert validate(result['acquisition_source'], subschema) is None
    assert expected == result['acquisition_source']

    expected = {
        'b': 'jmyang@itp.ac.cn',
        'c': 'submission',
        'd': '2016-05-24T00:00:00',
        'e': '805819',
    }
    result = hepnames2marc.do(result)

    assert expected == result['541']


def test_acquisition_source_from_541__a_b_c_d_e_handles_datetime():
    schema = load_schema('hep')
    subschema = schema['properties']['acquisition_source']

    snippet = (  # record/1644748
        '<datafield tag="541" ind1=" " ind2=" ">'
        '  <subfield code="a">orcid:0000-0002-7307-0726</subfield>'
        '  <subfield code="b">ratra@phys.ksu.edu</subfield>'
        '  <subfield code="c">submission</subfield>'
        '  <subfield code="d">2017-12-23T18:39:38.751244</subfield>'
        '  <subfield code="e">832953</subfield>'
        '</datafield>'
    )

    expected = {
        'datetime': '2017-12-23T18:39:38.751244',
        'email': 'ratra@phys.ksu.edu',
        'method': 'submitter',
        'orcid': '0000-0002-7307-0726',
        'submission_number': '832953',
    }
    result = hep.do(create_record(snippet))

    assert validate(result['acquisition_source'], subschema) is None
    assert expected == result['acquisition_source']

    expected = {
        'a': 'orcid:0000-0002-7307-0726',
        'b': 'ratra@phys.ksu.edu',
        'c': 'submission',
        'd': '2017-12-23T18:39:38.751244',
        'e': '832953',
    }
    result = hep2marc.do(result)

    assert expected == result['541']


def test_self_from_001():
    schema = load_schema('hep')
    subschema = schema['properties']['self']

    snippet = '<controlfield tag="001">1508668</controlfield>'  # record/1508668

    expected = {'$ref': 'http://localhost:5000/api/literature/1508668'}
    result = hep.do(create_record(snippet))

    assert validate(result['self'], subschema) is None
    assert expected == result['self']


def test_control_number_from_001():
    schema = load_schema('hep')
    subschema = schema['properties']['control_number']

    snippet = '<controlfield tag="001">1508668</controlfield>'  # record/1508668

    expected = 1508668
    result = hep.do(create_record(snippet))

    assert validate(result['control_number'], subschema) is None
    assert expected == result['control_number']

    expected = 1508668
    result = hep2marc.do(result)

    assert expected == result['001']


def test_legacy_creation_date_from_961__x_and_961__c():
    schema = load_schema('hep')
    subschema = schema['properties']['legacy_creation_date']

    snippet = (  # record/1124236
        '<record>'
        '  <datafield tag="961" ind1=" " ind2=" ">'
        '    <subfield code="x">2012-07-30</subfield>'
        '  </datafield>'
        '  <datafield tag="961" ind1=" " ind2=" ">'
        '    <subfield code="c">2012-11-20</subfield>'
        '  </datafield>'
        '</record>'
    )

    expected = '2012-07-30'
    result = hep.do(create_record(snippet))

    assert validate(result['legacy_creation_date'], subschema) is None
    assert expected == result['legacy_creation_date']

    expected = {'x': '2012-07-30'}
    result = hep2marc.do(result)

    assert expected == result['961']


def test_legacy_creation_date_from_961__c_and_961__x():
    schema = load_schema('hep')
    subschema = schema['properties']['legacy_creation_date']

    snippet = (  # synthetic data
        '<record>'
        '  <datafield tag="961" ind1=" " ind2=" ">'
        '    <subfield code="c">2012-11-20</subfield>'
        '  </datafield>'
        '  <datafield tag="961" ind1=" " ind2=" ">'
        '    <subfield code="x">2012-07-30</subfield>'
        '  </datafield>'
        '</record>'
    )

    expected = '2012-07-30'
    result = hep.do(create_record(snippet))

    assert validate(result['legacy_creation_date'], subschema) is None
    assert expected == result['legacy_creation_date']

    expected = {'x': '2012-07-30'}
    result = hep2marc.do(result)

    assert expected == result['961']


def test_legacy_creation_date_from_961__c_does_not_raise():
    snippet = (  # record/1501611
        '<datafield tag="961" ind1=" " ind2=" ">'
        '  <subfield code="c">2009-07-12</subfield>'
        '</datafield>'
    )

    assert 'legacy_creation_date' not in hep.do(create_record(snippet))


def test_legacy_creation_date_from_961__double_x_does_not_raise():
    schema = load_schema('authors')
    subschema = schema['properties']['legacy_creation_date']

    snippet = (  # record/982164
        '<datafield tag="961" ind1=" " ind2=" ">'
        '  <subfield code="x">2006-04-21</subfield>'
        '  <subfield code="x">1996-09-01</subfield>'
        '</datafield>'
    )

    expected = '1996-09-01'
    result = hepnames.do(create_record(snippet))

    assert validate(result['legacy_creation_date'], subschema) is None
    assert expected == result['legacy_creation_date']

    expected = {'x': '1996-09-01'}
    result = hepnames2marc.do(result)

    assert expected == result['961']


def test_external_system_identifiers_from_970__a():
    schema = load_schema('hep')
    subschema = schema['properties']['external_system_identifiers']

    snippet = (  # record/1297176
        '<datafield tag="970" ind1=" " ind2=" ">'
        '  <subfield code="a">SPIRES-10325093</subfield>'
        '</datafield>'
    )

    expected = [
        {
            'schema': 'SPIRES',
            'value': 'SPIRES-10325093',
        },
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['external_system_identifiers'], subschema) is None
    assert expected == result['external_system_identifiers']

    expected = [
        {'a': 'SPIRES-10325093'},
    ]
    result = hep2marc.do(result)

    assert expected == result['970']


def test_external_system_identifiers_from_970__double_a():
    schema = load_schema('hep')
    subschema = schema['properties']['external_system_identifiers']

    snippet = (  # record/1217763
        '<datafield tag="970" ind1=" " ind2=" ">'
        '  <subfield code="a">SPIRES-9663061</subfield>'
        '  <subfield code="a">SPIRES-9949933</subfield>'
        '</datafield>'
    )

    expected = [
        {
            'schema': 'SPIRES',
            'value': 'SPIRES-9663061',
        },
        {
            'schema': 'SPIRES',
            'value': 'SPIRES-9949933',
        },
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['external_system_identifiers'], subschema) is None
    assert expected == result['external_system_identifiers']

    expected = [
        {'a': 'SPIRES-9663061'},
        {'a': 'SPIRES-9949933'},
    ]
    result = hep2marc.do(result)

    assert expected == result['970']


def test_external_system_identifiers_from_970__a_conferences():
    schema = load_schema('conferences')
    subschema = schema['properties']['external_system_identifiers']

    snippet = (  # record/972464
        '<datafield tag="970" ind1=" " ind2=" ">'
        '  <subfield code="a">CONF-461733</subfield>'
        '</datafield>'
    )

    expected = [
        {
            'schema': 'SPIRES',
            'value': 'CONF-461733',
        },
    ]
    result = conferences.do(create_record(snippet))

    assert validate(result['external_system_identifiers'], subschema) is None
    assert expected == result['external_system_identifiers']


def test_new_record_from_970__d():
    schema = load_schema('hep')
    subschema = schema['properties']['new_record']

    snippet = (  # record/37545
        '<datafield tag="970" ind1=" " ind2=" ">'
        '  <subfield code="d">361769</subfield>'
        '</datafield>'
    )

    expected = {'$ref': 'http://localhost:5000/api/literature/361769'}
    result = hep.do(create_record(snippet))

    assert validate(result['new_record'], subschema) is None
    assert expected == result['new_record']

    expected = {'d': 361769}
    result = hep2marc.do(result)

    assert expected == result['970']


def test_deleted_records_from_981__a():
    schema = load_schema('hep')
    subschema = schema['properties']['deleted_records']

    snippet = (  # record/1508886
        '<datafield tag="981" ind1=" " ind2=" ">'
        '  <subfield code="a">1508668</subfield>'
        '</datafield>'
    )

    expected = [{'$ref': 'http://localhost:5000/api/literature/1508668'}]
    result = hep.do(create_record(snippet))

    assert validate(result['deleted_records'], subschema) is None
    assert expected == result['deleted_records']

    expected = [
        {'a': 1508668},
    ]
    result = hep2marc.do(result)

    assert expected == result['981']


def test_inspire_categories_from_65017a_2():
    schema = load_schema('hep')
    subschema = schema['properties']['inspire_categories']

    snippet = (  # record/1426196
        '<datafield tag="650" ind1="1" ind2="7">'
        '  <subfield code="2">Inspire</subfield>'
        '  <subfield code="a">Experiment-HEP</subfield>'
        '</datafield>'
    )

    expected = [
        {
            'term': 'Experiment-HEP',
        },
    ]
    result = hep.do(create_record(snippet))  # no roundtrip

    assert validate(result['inspire_categories'], subschema) is None
    assert expected == result['inspire_categories']

    expected = [
        {
            '2': 'INSPIRE',
            'a': 'Experiment-HEP',
        },
    ]
    result = hep2marc.do(result)

    assert expected == result['65017']


def test_inspire_categories_from_65017a_2_9_discards_conference():
    schema = load_schema('hep')
    subschema = schema['properties']['inspire_categories']

    snippet = (  # record/1479228
        '<datafield tag="650" ind1="1" ind2="7">'
        '  <subfield code="2">INSPIRE</subfield>'
        '  <subfield code="9">conference</subfield>'
        '  <subfield code="a">Accelerators</subfield>'
        '</datafield>'
    )

    expected = [
        {
            'term': 'Accelerators',
        },
    ]
    result = hep.do(create_record(snippet))  # no roundtrip

    assert validate(result['inspire_categories'], subschema) is None
    assert expected == result['inspire_categories']

    expected = [
        {
            '2': 'INSPIRE',
            'a': 'Accelerators',
        },
    ]
    result = hep2marc.do(result)

    assert expected == result['65017']


def test_inspire_categories_from_65017a_2_9_converts_automatically_added():
    schema = load_schema('hep')
    subschema = schema['properties']['inspire_categories']

    snippet = (  # record/669400
        '<datafield tag="650" ind1="1" ind2="7">  <subfield'
        ' code="2">INSPIRE</subfield>  <subfield'
        ' code="a">Instrumentation</subfield>  <subfield code="9">automatically'
        ' added based on DCC, PPF, DK</subfield></datafield>'
    )

    expected = [
        {
            'source': 'curator',
            'term': 'Instrumentation',
        },
    ]
    result = hep.do(create_record(snippet))  # no roundtrip

    assert validate(result['inspire_categories'], subschema) is None
    assert expected == result['inspire_categories']

    expected = [
        {
            '2': 'INSPIRE',
            '9': 'curator',
            'a': 'Instrumentation',
        },
    ]
    result = hep2marc.do(result)

    assert expected == result['65017']


def test_inspire_categories_from_65017a_2_9_converts_submitter():
    schema = load_schema('hep')
    subschema = schema['properties']['inspire_categories']

    snippet = (  # record/1511089
        '<datafield tag="650" ind1="1" ind2="7">'
        '  <subfield code="a">Math and Math Physics</subfield>'
        '  <subfield code="9">submitter</subfield>'
        '  <subfield code="2">INSPIRE</subfield>'
        '</datafield>'
    )

    expected = [
        {
            'source': 'user',
            'term': 'Math and Math Physics',
        },
    ]
    result = hep.do(create_record(snippet))  # no roundtrip

    assert validate(result['inspire_categories'], subschema) is None
    assert expected == result['inspire_categories']

    expected = [
        {'2': 'INSPIRE', '9': 'user', 'a': 'Math and Math Physics'},
    ]
    result = hep2marc.do(result)

    assert expected == result['65017']


def test_inspire_categories_from_65017a_2_discards_arxiv():
    snippet = (  # record/1511862
        '<datafield tag="650" ind1="1" ind2="7">'
        '  <subfield code="a">math-ph</subfield>'
        '  <subfield code="2">arXiv</subfield>'
        '</datafield>'
    )

    result = hep.do(create_record(snippet))

    assert 'inspire_categories' not in result


def test_urls_from_8564_u_y():
    schema = load_schema('hep')
    subschema = schema['properties']['urls']

    snippet = (  # record/1405358
        '<datafield tag="856" ind1="4" ind2=" ">'
        '  <subfield code="u">http://www-lib.kek.jp/ar/ar.html</subfield>'
        '  <subfield code="y">KEK</subfield>'
        '</datafield>'
    )

    expected = [
        {
            'description': 'KEK',
            'value': 'http://www-lib.kek.jp/ar/ar.html',
        },
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['urls'], subschema) is None
    assert expected == result['urls']

    expected = [
        {
            'u': 'http://www-lib.kek.jp/ar/ar.html',
            'y': 'KEK',
        },
    ]
    result = hep2marc.do(result)

    assert expected == result['8564']


def test_urls_from_8564_ignores_internal_links():
    snippet = (  # record/1610503
        '<datafield tag="856" ind1="4" ind2=" ">'
        '  <subfield code="s">1506142</subfield>'
        '  <subfield'
        ' code="u">http://inspirehep.net/record/1610503/files/arXiv:1707.05770.pdf</subfield>'
        '</datafield>'
    )

    result = hep.do(create_record(snippet))

    assert 'urls' not in result


def test_urls_from_8564_ignores_internal_links_with_subdomain():
    snippet = (  # record/1610503
        '<datafield tag="856" ind1="4" ind2=" ">'
        '  <subfield code="s">1506142</subfield>'
        '  <subfield'
        ' code="u">http://old.inspirehep.net/record/1610503/files/arXiv:1707.05770.pdf</subfield>'
        '</datafield>'
    )

    result = hep.do(create_record(snippet))

    assert 'urls' not in result


def test_urls_from_8564_ignores_internal_links_https():
    snippet = (  # record/1508036
        '<datafield tag="856" ind1="4" ind2=" ">  <subfield code="s">2392681</subfield>'
        '  <subfield'
        ' code="u">https://inspirehep.net/record/1508108/files/fermilab-pub-16-617-cms.pdf</subfield>'
        '  <subfield code="y">Fulltext</subfield></datafield>'
    )

    result = hep.do(create_record(snippet))

    assert 'urls' not in result


def test_urls_from_8564_s_u_ignores_s():
    schema = load_schema('hep')
    subschema = schema['properties']['urls']

    snippet = (  # record/1511347
        '<datafield tag="856" ind1="4" ind2=" ">'
        '  <subfield code="s">443981</subfield>'
        '  <subfield'
        ' code="u">http://localhost:5000/record/1511347/files/HIG-16-034-pas.pdf</subfield>'
        '</datafield>'
    )

    expected = [
        {'value': 'http://localhost:5000/record/1511347/files/HIG-16-034-pas.pdf'},
    ]
    result = hep.do(create_record(snippet))  # no roundtrip

    assert validate(result['urls'], subschema) is None
    assert expected == result['urls']

    expected = [
        {'u': 'http://localhost:5000/record/1511347/files/HIG-16-034-pas.pdf'},
    ]
    result = hep2marc.do(result)

    assert expected == result['8564']


def test_urls_from_8564_u_w_y_ignores_w_and_translates_weblinks():
    schema = load_schema('hep')
    subschema = schema['properties']['urls']

    snippet = (  # record/1120360
        '<datafield tag="856" ind1="4" ind2=" ">'
        '  <subfield code="w">12-316</subfield>'
        '  <subfield code="y">FERMILABPUB</subfield>'
        '  <subfield'
        ' code="u">http://lss.fnal.gov/cgi-bin/find_paper.pl?pub-12-316</subfield>'
        '</datafield>'
    )

    expected = [
        {
            'description': 'Fermilab Library Server (fulltext available)',
            'value': 'http://lss.fnal.gov/cgi-bin/find_paper.pl?pub-12-316',
        },
    ]
    result = hep.do(create_record(snippet))  # no roundtrip

    assert validate(result['urls'], subschema) is None
    assert expected == result['urls']

    expected = [
        {
            'u': 'http://lss.fnal.gov/cgi-bin/find_paper.pl?pub-12-316',
            'y': 'Fermilab Library Server (fulltext available)',
        },
    ]
    result = hep2marc.do(result)

    assert expected == result['8564']


def test_urls_from_8564_u_w_y_ignores_w_and_translates_weblinks_with_apostrophes():
    schema = load_schema('hep')
    subschema = schema['properties']['urls']

    snippet = (  # record/417789
        '<datafield tag="856" ind1="4" ind2=" ">'
        '  <subfield code="w">Abstracts_2/Stanek.html</subfield>'
        '  <subfield code="y">C95-10-29</subfield>'
        '  <subfield'
        ' code="u">http://www-bd.fnal.gov/icalepcs/abstracts/Abstracts_2/Stanek.html</subfield>'
        '</datafield>'
    )

    expected = [
        {
            'description': 'ICALEPCS\'95 Server',
            'value': (
                'http://www-bd.fnal.gov/icalepcs/abstracts/Abstracts_2/Stanek.html'
            ),
        },
    ]
    result = hep.do(create_record(snippet))  # no roundtrip

    assert validate(result['urls'], subschema) is None
    assert expected == result['urls']

    expected = [
        {
            'u': 'http://www-bd.fnal.gov/icalepcs/abstracts/Abstracts_2/Stanek.html',
            'y': 'ICALEPCS\'95 Server',
        },
    ]
    result = hep2marc.do(result)

    assert expected == result['8564']


def test_urls_from_8564_u_double_y_selects_the_first_y():
    schema = load_schema('hep')
    subschema = schema['properties']['urls']

    snippet = (  # record/1312672
        '<datafield tag="856" ind1="4" ind2=" ">  <subfield'
        ' code="u">http://link.springer.com/journal/10909/176/5/page/1</subfield>'
        '  <subfield code="y">Part II</subfield>  <subfield'
        ' code="y">Springer</subfield></datafield>'
    )

    expected = [
        {
            'description': 'Part II',
            'value': 'http://link.springer.com/journal/10909/176/5/page/1',
        },
    ]
    result = hep.do(create_record(snippet))  # no roundtrip

    assert validate(result['urls'], subschema) is None
    assert expected == result['urls']

    expected = [
        {
            'u': 'http://link.springer.com/journal/10909/176/5/page/1',
            'y': 'Part II',
        },
    ]
    result = hep2marc.do(result)

    assert expected == result['8564']


def test_private_notes_from_595__9():
    snippet = (  # record/1005469
        '<datafield tag="595" ind1=" " ind2=" ">'
        '  <subfield code="9">SPIRES-HIDDEN</subfield>'
        '</datafield>'
    )

    assert '_private_notes' not in hepnames.do(create_record(snippet))


def test_legacy_version_from_005():
    schema = load_schema('hep')
    subschema = schema['properties']['legacy_version']

    snippet = (  # record/1694560
        '<controlfield tag="005">20180919130452.0</controlfield>'
    )

    expected = '20180919130452.0'
    result = hep.do(create_record(snippet))

    assert validate(result['legacy_version'], subschema) is None
    assert expected == result['legacy_version']

    expected = '20180919130452.0'
    result = hep2marc.do(result)

    assert expected == result['005']
