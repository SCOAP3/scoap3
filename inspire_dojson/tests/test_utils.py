# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2014-2019 CERN.
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
from flask import current_app
from mock import patch

from inspire_dojson.utils import (
    absolute_url,
    afs_url,
    afs_url_to_path,
    dedupe_all_lists,
    force_single_element,
    get_recid_from_ref,
    get_record_ref,
    normalize_date_aggressively,
    normalize_rank,
    strip_empty_values,
)


def test_normalize_rank_returns_none_on_falsy_value():
    assert normalize_rank('') is None


def test_normalize_rank_returns_uppercase_value_if_found_in_rank_types():
    expected = 'STAFF'
    result = normalize_rank('staff')

    assert expected == result


def test_normalize_rank_ignores_periods_in_value():
    expected = 'PHD'
    result = normalize_rank('Ph.D.')

    assert expected == result


def test_normalize_rank_allows_alternative_names():
    expected = 'VISITOR'
    result = normalize_rank('VISITING SCIENTIST')

    assert expected == result


def test_normalize_rank_allows_abbreviations():
    expected = 'POSTDOC'
    result = normalize_rank('PD')

    assert expected == result


def test_normalize_rank_falls_back_on_other():
    expected = 'OTHER'
    result = normalize_rank('FOO')

    assert expected == result


def test_force_single_element_returns_first_element_on_a_list():
    expected = 'foo'
    result = force_single_element(['foo', 'bar', 'baz'])

    assert expected == result


def test_force_single_element_returns_element_when_not_a_list():
    expected = 'foo'
    result = force_single_element('foo')

    assert expected == result


def test_force_single_element_returns_none_on_empty_list():
    assert force_single_element([]) is None


def test_absolute_url_with_undef_server_name():
    config = {'SERVER_NAME': None}

    with patch.dict(current_app.config, config):
        expected = 'http://inspirehep.net/foo'
        result = absolute_url('foo')

        assert expected == result


def test_absolute_url_with_server_name_localhost():
    config = {'SERVER_NAME': 'localhost:5000'}

    with patch.dict(current_app.config, config):
        expected = 'http://localhost:5000/foo'
        result = absolute_url('foo')

        assert expected == result


def test_absolute_url_with_http_server_name():
    config = {'SERVER_NAME': 'http://example.com'}

    with patch.dict(current_app.config, config):
        expected = 'http://example.com/foo'
        result = absolute_url('foo')

        assert expected == result


def test_absolute_url_with_https_server_name():
    config = {'SERVER_NAME': 'https://example.com'}

    with patch.dict(current_app.config, config):
        expected = 'https://example.com/foo'
        result = absolute_url('foo')

        assert expected == result


def test_absolute_url_with_https_preferred_scheme():
    config = {'PREFERRED_URL_SCHEME': 'https'}

    with patch.dict(current_app.config, config):
        expected = 'https://localhost:5000/foo'
        result = absolute_url('foo')

        assert expected == result


def test_afs_url_ignores_non_afs_path():
    expected = 'http://example.com/file.pdf'
    result = afs_url('http://example.com/file.pdf')

    assert expected == result


def test_afs_url_converts_afs_path():
    expected = 'file:///afs/cern.ch/project/inspire/PROD/var/file.txt'
    result = afs_url('/opt/cds-invenio/var/file.txt')

    assert expected == result


def test_afs_url_converts_new_afs_path():
    expected = 'file:///afs/cern.ch/project/inspire/PROD/var/data/files/g220/4413039/content.xml'
    result = afs_url(
        '/opt/venvs/inspire-legacy/var/data/files/g220/4413039/content.xml'
    )

    assert expected == result


def test_afs_url_encodes_characters():
    expected = 'file:///afs/cern.ch/project/inspire/PROD/var/file%20with%20spaces.txt'
    result = afs_url('/opt/cds-invenio/var/file with spaces.txt')

    assert expected == result


def test_afs_url_handles_none():
    expected = None
    result = afs_url(None)

    assert expected == result


def test_afs_url_with_custom_afs_path():
    config = {'LEGACY_AFS_PATH': '/custom/path/'}

    with patch.dict(current_app.config, config):
        expected = 'file:///custom/path/var/file.txt'
        result = afs_url('/opt/cds-invenio/var/file.txt')

        assert expected == result


def test_afs_url_handles_unicode():
    expected = u'file:///afs/cern.ch/project/inspire/PROD/var/data/files/g70/1407585/%E7%89%A9%E7%90%86%E7%A7%91%E5%AD%A6%E4%B8%8E%E6%8A%80%E6%9C%AF%E5%AD%A6%E9%99%A2-%E6%9D%8E%E5%A8%9C-200650218-%E5%AD%A6%E4%BD%8D%E7%BA%A7....pdf%3B1'
    result = afs_url(
        u'/opt/cds-invenio/var/data/files/g70/1407585/物理科学与技术学院-李娜-200650218-学位级....pdf;1'
    )

    assert expected == result


def test_afs_url_with_afs_service_enabled_and_encodes_characters():
    config = {'LABS_AFS_HTTP_SERVICE': 'http://jessicajones.com/nested/nested'}

    with patch.dict(current_app.config, config):
        expected = 'http://jessicajones.com/nested/nested/var/file%20with%20spaces.txt'
        result = afs_url('/opt/cds-invenio/var/file with spaces.txt')

        assert expected == result


def test_afs_url_with_afs_service_enabled_converts_afs_path():
    config = {'LABS_AFS_HTTP_SERVICE': 'http://jessicajones.com/nested/nested'}

    with patch.dict(current_app.config, config):
        expected = 'http://jessicajones.com/nested/nested/var/file.txt'
        result = afs_url('/opt/cds-invenio/var/file.txt')

        assert expected == result


def test_afs_url_with_afs_service_enabled_with_trailing_slash_converts_afs_path():
    config = {'LABS_AFS_HTTP_SERVICE': 'http://jessicajones.com/nested/nested/'}

    with patch.dict(current_app.config, config):
        expected = 'http://jessicajones.com/nested/nested/var/file.txt'
        result = afs_url('/opt/cds-invenio/var/file.txt')

        assert expected == result


def test_afs_url_to_path_handles_none():
    expected = None
    result = afs_url_to_path(None)

    assert expected == result


def test_afs_url_returns_non_afs_urls_unchanged():
    expected = "http://example.com"
    result = afs_url_to_path("http://example.com")

    assert expected == result


def test_afs_url_converts_afs_url_to_path():
    config = {
        'LABS_AFS_HTTP_SERVICE': 'http://jessicajones.com/nested/nested',
    }

    expected = "file:///afs/cern.ch/project/inspire/PROD/var/file.txt"
    with patch.dict(current_app.config, config):
        result = afs_url_to_path("http://jessicajones.com/nested/nested/var/file.txt")

    assert expected == result


def test_afs_url_handles_custom_afs_path():
    config = {
        'LABS_AFS_HTTP_SERVICE': 'http://jessicajones.com/nested/nested',
        'LEGACY_AFS_PATH': '/foo/bar',
    }

    expected = "file:///foo/bar/var/file.txt"
    with patch.dict(current_app.config, config):
        result = afs_url_to_path("http://jessicajones.com/nested/nested/var/file.txt")

    assert expected == result


def test_get_record_ref_with_empty_server_name():
    config = {'SERVER_NAME': None}

    with patch.dict(current_app.config, config):
        expected = 'http://inspirehep.net/api/endpoint/123'
        result = get_record_ref(123, 'endpoint')

        assert expected == result['$ref']


def test_get_record_ref_with_server_name_localhost():
    config = {'SERVER_NAME': 'localhost:5000'}

    with patch.dict(current_app.config, config):
        expected = 'http://localhost:5000/api/endpoint/123'
        result = get_record_ref(123, 'endpoint')

        assert expected == result['$ref']


def test_get_record_ref_with_http_server_name():
    config = {'SERVER_NAME': 'http://example.com'}

    with patch.dict(current_app.config, config):
        expected = 'http://example.com/api/endpoint/123'
        result = get_record_ref(123, 'endpoint')

        assert expected == result['$ref']


def test_get_record_ref_with_https_server_name():
    config = {'SERVER_NAME': 'https://example.com'}

    with patch.dict(current_app.config, config):
        expected = 'https://example.com/api/endpoint/123'
        result = get_record_ref(123, 'endpoint')

        assert expected == result['$ref']


def test_get_record_ref_without_recid_returns_none():
    assert get_record_ref(None, 'endpoint') is None


def test_get_record_ref_without_endpoint_defaults_to_record():
    config = {'SERVER_NAME': None}

    with patch.dict(current_app.config, config):
        expected = 'http://inspirehep.net/api/record/123'
        result = get_record_ref(123)

        assert expected == result['$ref']


def test_get_recid_from_ref_returns_none_on_none():
    assert get_recid_from_ref(None) is None


def test_get_recid_from_ref_returns_none_on_simple_strings():
    assert get_recid_from_ref('a_string') is None


def test_get_recid_from_ref_returns_none_on_empty_object():
    assert get_recid_from_ref({}) is None


def test_get_recid_from_ref_returns_none_on_object_with_wrong_key():
    assert get_recid_from_ref({'bad_key': 'some_val'}) is None


def test_get_recid_from_ref_returns_none_on_ref_a_simple_string():
    assert get_recid_from_ref({'$ref': 'a_string'}) is None


def test_get_recid_from_ref_returns_none_on_ref_malformed():
    assert get_recid_from_ref({'$ref': 'http://bad_url'}) is None


def test_dedupe_all_lists():
    obj = {
        'l0': list(range(10)) + list(range(10)),
        'o1': [{'foo': 'bar'}] * 10,
        'o2': [{'foo': [1, 2]}, {'foo': [1, 1, 2]}] * 10,
    }

    expected = {
        'l0': list(range(10)),
        'o1': [{'foo': 'bar'}],
        'o2': [{'foo': [1, 2]}],
    }

    assert dedupe_all_lists(obj) == expected


def test_strip_empty_values():
    obj = {
        '_foo': (),
        'foo': (1, 2, 3),
        '_bar': [],
        'bar': [1, 2, 3],
        '_baz': set(),
        'baz': set([1, 2, 3]),
        'qux': True,
        'quux': False,
        'plugh': 0,
    }

    expected = {
        'foo': (1, 2, 3),
        'bar': [1, 2, 3],
        'baz': set([1, 2, 3]),
        'qux': True,
        'quux': False,
        'plugh': 0,
    }
    result = strip_empty_values(obj)

    assert expected == result


def test_strip_empty_values_returns_none_on_none():
    assert strip_empty_values(None) is None


def test_normalize_date_aggressively_accepts_correct_date():
    assert normalize_date_aggressively('2015-02-24') == '2015-02-24'


def test_normalize_date_aggressively_strips_wrong_day():
    assert normalize_date_aggressively('2015-02-31') == '2015-02'


def test_normalize_date_aggressively_strips_wrong_month():
    assert normalize_date_aggressively('2015-20-24') == '2015'


def test_normalize_date_aggressively_raises_on_wrong_format():
    with pytest.raises(ValueError, match='Unknown string format: 2014=12'):
        normalize_date_aggressively('2014=12-01')


def test_normalize_date_aggressively_ignores_fake_dates():
    assert normalize_date_aggressively('0000') is None
