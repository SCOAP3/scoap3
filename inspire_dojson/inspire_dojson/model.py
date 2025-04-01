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

"""Filter-aware subclass of DoJSON's Overdo.

Allows for a list of filters to be passed during instantiation,
which are applied in succession to the result of the DoJSON rules.
"""

from __future__ import absolute_import, division, print_function

from functools import wraps

from dojson import Overdo
from dojson.errors import IgnoreKey
from six import raise_from

from inspire_dojson.errors import DoJsonError
from inspire_dojson.utils import dedupe_all_lists, strip_empty_values


class FilterOverdo(Overdo):
    def __init__(self, filters=None, *args, **kwargs):
        super(FilterOverdo, self).__init__(*args, **kwargs)
        self.filters = filters or []

    def do(self, blob, **kwargs):
        result = super(FilterOverdo, self).do(blob, **kwargs)

        for filter_ in self.filters:
            result = filter_(result, blob)

        return result

    def over(self, name, *source_tags):
        def decorator(creator):
            return super(FilterOverdo, self).over(name, *source_tags)(
                self._wrap_exception(creator, name)
            )

        return decorator

    @staticmethod
    def _wrap_exception(rule, name):
        @wraps(rule)
        def func(self, key, value):
            try:
                return rule(self, key, value)
            except Exception as exc:
                if type(exc) is IgnoreKey:
                    raise exc
                raise_from(
                    DoJsonError(
                        u'Error in rule "{name}" for field "{key}"'.format(
                            name=name, key=key
                        ),
                        exc.args,
                        value,
                    ),
                    exc,
                )

        return func


def add_schema(schema):
    def _add_schema(record, blob):
        record['$schema'] = schema
        return record

    return _add_schema


def add_collection(name):
    def _add_collection(record, blob):
        record['_collections'] = [name]
        return record

    return _add_collection


def clean_marc(record, blob):
    return strip_empty_values(record)


def clean_record(exclude_keys=()):
    def _clean_record(record, blob):
        return dedupe_all_lists(strip_empty_values(record), exclude_keys=exclude_keys)

    return _clean_record
