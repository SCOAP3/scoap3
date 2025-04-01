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

"""DoJSON rules for journals."""

from __future__ import absolute_import, division, print_function

from dojson import utils
from idutils import normalize_issn
from inspire_utils.date import normalize_date
from inspire_utils.helpers import force_list, maybe_int

from inspire_dojson.journals.model import journals
from inspire_dojson.utils import get_record_ref


@journals.over('issns', '^022..')
@utils.for_each_value
def issns(self, key, value):
    def _get_issn(value):
        return normalize_issn(value.get('a'))

    def _get_medium(value):
        MEDIUM_MAP = {
            'Online (English)': 'online',
            'Online (Russian': 'online',
            'Online': 'online',
            'Print (Russian)': 'print',
            'Print': 'print',
            'e-only': 'online',
            'electronic': 'online',
            'online': 'online',
            'print': 'print',
            'printed': 'print',
        }

        return MEDIUM_MAP.get(value.get('b'))

    issn = _get_issn(value)
    medium = _get_medium(value)

    if issn:
        return {
            'medium': medium,
            'value': issn,
        }


@journals.over('journal_title', '^130..')
def journal_title(self, key, value):
    return {
        'title': value.get('a'),
        'subtitle': value.get('b'),
    }


@journals.over('related_records', '^530..')
@utils.for_each_value
def related_records(self, key, value):
    def _get_relation(value):
        RELATION_MAP = {
            'a': 'predecessor',
            'b': 'successor',
            'r': 'other',
        }

        return RELATION_MAP.get(value.get('w'))

    def _get_relation_freetext(value):
        return value.get('i')

    record = get_record_ref(maybe_int(value.get('0')), 'journals')
    relation = _get_relation(value)
    relation_freetext = _get_relation_freetext(value)

    if record and relation == 'other':
        return {
            'curated_relation': record is not None,
            'record': record,
            'relation_freetext': relation_freetext,
        }
    elif record and relation:
        return {
            'curated_relation': record is not None,
            'record': record,
            'relation': relation,
        }


@journals.over('license', '^540..')
def license(self, key, value):
    return {
        'license': value.get('a'),
        'url': value.get('u'),
    }


@journals.over('_harvesting_info', '^583..')
def _harvesting_info(self, key, value):
    return {
        'coverage': value.get('a'),
        'date_last_harvest': normalize_date(value.get('c')),
        'last_seen_item': value.get('3'),
        'method': value.get('i'),
    }


@journals.over('public_notes', '^640..')
@utils.for_each_value
def public_notes_640(self, key, value):
    public_note = value.get('a')

    if public_note:
        return {
            'source': value.get('9'),
            'value': public_note,
        }


@journals.over('publisher', '^643..')
@utils.for_each_value
def publisher(self, key, value):
    return value.get('b')


@journals.over('_private_notes', '^667..')
@utils.flatten
@utils.for_each_value
def _private_notes(self, key, value):
    """Populate the ``_private_notes`` key."""
    return [
        {
            'source': value.get('9'),
            'value': _private_note,
        }
        for _private_note in force_list(value.get('x'))
    ]


@journals.over('doi_prefixes', '^677..')
@utils.for_each_value
def doi_prefixes(self, key, value):
    return value.get('d')


@journals.over('public_notes', '^680..')
@utils.for_each_value
def public_notes_680(self, key, value):
    public_note = value.get('i')

    if public_note:
        return {
            'source': value.get('9'),
            'value': public_note,
        }


@journals.over('proceedings', '^690..')
def proceedings(self, key, value):
    """Populate the ``proceedings`` key.

    Also populates the ``refereed`` key through side effects.
    """
    proceedings = self.get('proceedings')
    refereed = self.get('refereed')

    if not proceedings:
        normalized_a_values = [el.upper() for el in force_list(value.get('a'))]
        if 'PROCEEDINGS' in normalized_a_values:
            proceedings = True

    if not refereed:
        normalized_a_values = [el.upper() for el in force_list(value.get('a'))]
        if 'PEER REVIEW' in normalized_a_values:
            refereed = True
        elif 'NON-PUBLISHED' in normalized_a_values:
            refereed = False

    self['refereed'] = refereed
    return proceedings


@journals.over('short_title', '^711..')
def short_title(self, key, value):
    """Populate the ``short_title`` key.

    Also populates the ``title_variants`` key through side effects.
    """
    short_title = value.get('a')
    title_variants = self.get('title_variants', [])

    if value.get('u'):
        short_title = value.get('u')
        title_variants.append(value.get('a'))

    self['title_variants'] = title_variants
    return short_title


@journals.over('title_variants', '^730..')
@utils.for_each_value
def title_variants(self, key, value):
    if value.get('b'):
        return

    return value.get('a')


@journals.over('deleted', '^980..')
def deleted(self, key, value):
    """Populate the ``deleted`` key.

    Also populates the ``book_series`` key through side effects.
    """
    deleted = self.get('deleted')
    book_series = self.get('book_series')

    if not deleted:
        normalized_a_values = [el.upper() for el in force_list(value.get('a'))]
        normalized_c_values = [el.upper() for el in force_list(value.get('c'))]
        if 'DELETED' in normalized_a_values or 'DELETED' in normalized_c_values:
            deleted = True

    if not book_series:
        normalized_a_values = [el.upper() for el in force_list(value.get('a'))]
        if 'BOOKSERIES' in normalized_a_values:
            book_series = True

    self['book_series'] = book_series
    return deleted
