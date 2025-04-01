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

"""DoJSON utils."""

from __future__ import absolute_import, division, print_function

import os
import re

from dojson.utils import GroupableOrderedDict
from flask import current_app
from inspire_utils.date import normalize_date
from inspire_utils.dedupers import dedupe_list, dedupe_list_of_dicts
from inspire_utils.helpers import force_list, maybe_int
from isbn import ISBN
from six import binary_type, iteritems, text_type
from six.moves import urllib

DEFAULT_AFS_PATH = '/afs/cern.ch/project/inspire/PROD'


def normalize_isbn(isbn):
    """Normalize an ISBN in order to be schema-compliant."""
    try:
        return str(ISBN(isbn))
    except Exception:
        return isbn


def normalize_rank(rank):
    """Normalize a rank in order to be schema-compliant."""
    normalized_ranks = {
        'BA': 'UNDERGRADUATE',
        'BACHELOR': 'UNDERGRADUATE',
        'BS': 'UNDERGRADUATE',
        'BSC': 'UNDERGRADUATE',
        'JUNIOR': 'JUNIOR',
        'MAS': 'MASTER',
        'MASTER': 'MASTER',
        'MS': 'MASTER',
        'MSC': 'MASTER',
        'PD': 'POSTDOC',
        'PHD': 'PHD',
        'POSTDOC': 'POSTDOC',
        'SENIOR': 'SENIOR',
        'STAFF': 'STAFF',
        'STUDENT': 'PHD',
        'UG': 'UNDERGRADUATE',
        'UNDERGRADUATE': 'UNDERGRADUATE',
        'VISITING SCIENTIST': 'VISITOR',
        'VISITOR': 'VISITOR',
    }
    if not rank:
        return None
    rank = rank.upper().replace('.', '')
    return normalized_ranks.get(rank, 'OTHER')


def force_single_element(obj):
    """Force an object to a list and return the first element."""
    lst = force_list(obj)
    if lst:
        return lst[0]
    return None


def get_recid_from_ref(ref_obj):
    """Retrieve recid from jsonref reference object.

    If no recid can be parsed, returns None.
    """
    if not isinstance(ref_obj, dict):
        return None
    url = ref_obj.get('$ref', '')
    return maybe_int(url.split('/')[-1])


def absolute_url(relative_url):
    """Returns an absolute URL from a URL relative to the server root.

    The base URL is taken from the Flask app config if present, otherwise it
    falls back to ``http://inspirehep.net``.
    """
    default_server = 'http://inspirehep.net'
    server = current_app.config['SERVER_NAME'] or default_server
    scheme = current_app.config['PREFERRED_URL_SCHEME']
    if not re.match('^https?://', server):
        server = u'{scheme}://{server}'.format(scheme=scheme, server=server)
    return urllib.parse.urljoin(server, relative_url)


def afs_url(file_path):
    """Convert a file path to a URL pointing to its path on AFS.

    If ``file_path`` doesn't start with ``/opt/cds-invenio/``, and hence is not on
    AFS, it returns it unchanged.

    The base AFS path is taken from the Flask app config if present, otherwise
    it falls back to ``/afs/cern.ch/project/inspire/PROD``.
    """
    afs_path = current_app.config.get('LEGACY_AFS_PATH', DEFAULT_AFS_PATH)
    afs_service = current_app.config.get('LABS_AFS_HTTP_SERVICE')

    if file_path is None:
        return None
    process_path = False

    if file_path.startswith('/opt/cds-invenio/'):
        process_path = True
        file_path = os.path.relpath(file_path, '/opt/cds-invenio/')
    elif file_path.startswith('/opt/venvs/inspire-legacy/'):
        process_path = True
        file_path = os.path.relpath(file_path, '/opt/venvs/inspire-legacy/')

    if process_path:
        if afs_service:
            return os.path.join(
                afs_service,
                urllib.request.pathname2url(file_path.encode('utf-8')),
            )
        file_path = os.path.join(afs_path, file_path)
        return urllib.parse.urljoin(
            'file://', urllib.request.pathname2url(file_path.encode('utf-8'))
        )

    return file_path


def afs_url_to_path(url):
    """Convert a AFS URL to its corresponding path on AFS.

    If ``url`` doesn't start with the AFS HTTP service and hence is not on
    AFS, it returns it unchanged.

    The base AFS path is taken from the Flask app config if present, otherwise
    it falls back to ``/afs/cern.ch/project/inspire/PROD``.
    """
    afs_path = current_app.config.get('LEGACY_AFS_PATH', DEFAULT_AFS_PATH)
    afs_service = current_app.config.get('LABS_AFS_HTTP_SERVICE')

    if url is None:
        return None

    if not afs_service or not url.startswith(afs_service):
        return url

    path = url[len(afs_service) :].lstrip('/')
    return urllib.parse.urljoin('file://', os.path.join(afs_path, path))


def get_record_ref(recid, endpoint='record'):
    """Create record jsonref reference object from recid.

    None recids will return a None object.
    Valid recids will return an object in the form of: {'$ref': url_for_record}
    """
    if recid is None:
        return None
    return {'$ref': absolute_url(u'/api/{}/{}'.format(endpoint, recid))}


def strip_empty_values(obj):
    """Recursively strips empty values."""
    if isinstance(obj, dict):
        new_obj = {}
        for key, val in obj.items():
            new_val = strip_empty_values(val)
            if new_val is not None:
                new_obj[key] = new_val
        return new_obj or None
    elif isinstance(obj, (list, tuple, set)):
        new_obj = []
        for val in obj:
            new_val = strip_empty_values(val)
            if new_val is not None:
                new_obj.append(new_val)
        return type(obj)(new_obj) or None
    elif obj or obj is False or obj == 0:
        return obj
    else:
        return None


def dedupe_all_lists(obj, exclude_keys=()):
    """Recursively remove duplucates from all lists.

    Args:
        obj: collection to deduplicate
        exclude_keys (Container[str]): key names to ignore for deduplication
    """
    squared_dedupe_len = 10
    if isinstance(obj, dict):
        new_obj = {}
        for key, value in obj.items():
            if key in exclude_keys:
                new_obj[key] = value
            else:
                new_obj[key] = dedupe_all_lists(value)
        return new_obj
    elif isinstance(obj, (list, tuple, set)):
        new_elements = [dedupe_all_lists(v) for v in obj]
        if len(new_elements) < squared_dedupe_len:
            new_obj = dedupe_list(new_elements)
        else:
            new_obj = dedupe_list_of_dicts(new_elements)
        return type(obj)(new_obj)
    else:
        return obj


def normalize_date_aggressively(date):
    """Normalize date, stripping date parts until a valid date is obtained."""

    def _strip_last_part(date):
        parts = date.split('-')
        return '-'.join(parts[:-1])

    fake_dates = {'0000', '9999'}
    if date in fake_dates:
        return None
    try:
        return normalize_date(date)
    except (IndexError, TypeError, ValueError):
        if '-' not in date:
            raise
        else:
            new_date = _strip_last_part(date)
            return normalize_date_aggressively(new_date)


def create_record_from_dict(dictionary):
    """Create an input record for dojson from a dict."""
    return GroupableOrderedDict(iteritems(dictionary))


def quote_url(unquoted):
    if isinstance(unquoted, text_type):
        unquoted = unquoted.encode('utf-8')
    return urllib.parse.quote(unquoted)


def unquote_url(quoted):
    unquoted = urllib.parse.unquote(quoted)
    if isinstance(unquoted, binary_type):
        unquoted = unquoted.decode('utf-8')
    return unquoted
