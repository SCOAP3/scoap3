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

"""INSPIRE DoJSON API."""

from __future__ import absolute_import, division, print_function

import os
import re
from itertools import chain

from dojson.contrib.marc21.utils import create_record
from inspire_utils.helpers import force_list
from inspire_utils.record import get_value
from lxml.builder import E
from lxml.etree import tostring
from six import iteritems, text_type, unichr
from six.moves import urllib

from inspire_dojson.cds import cds2hep_marc
from inspire_dojson.conferences import conferences
from inspire_dojson.data import data
from inspire_dojson.errors import NotSupportedError
from inspire_dojson.experiments import experiments
from inspire_dojson.hep import hep, hep2marc
from inspire_dojson.hepnames import hepnames, hepnames2marc
from inspire_dojson.institutions import institutions
from inspire_dojson.journals import journals
from inspire_dojson.utils import create_record_from_dict, force_single_element

try:
    unichr(0x100000)
    RE_INVALID_CHARS_FOR_XML = re.compile(
        u'[^\U00000009\U0000000A\U0000000D\U00000020-\U0000D7FF\U0000E000-\U0000FFFD\U00010000-\U0010FFFF]+'
    )
except ValueError:  # pragma: no cover
    RE_INVALID_CHARS_FOR_XML = re.compile(
        u'[^\U00000009\U0000000A\U0000000D\U00000020-\U0000D7FF\U0000E000-\U0000FFFD]+'
    )

RECORD = E.record
CONTROLFIELD = E.controlfield
DATAFIELD = E.datafield
SUBFIELD = E.subfield


def marcxml2record(marcxml):
    """Convert a MARCXML string to a JSON record.

    Tries to guess which set of rules to use by inspecting the contents
    of the ``980__a`` MARC field, but falls back to HEP in case nothing
    matches, because records belonging to special collections logically
    belong to the Literature collection but don't have ``980__a:HEP``.

    Args:
        marcxml(str): a string containing MARCXML.

    Returns:
        dict: a JSON record converted from the string.

    """
    marcjson = create_record(marcxml, keep_singletons=False)
    collections = _get_collections(marcjson)

    if 'conferences' in collections:
        return conferences.do(marcjson)
    elif 'data' in collections:
        return data.do(marcjson)
    elif 'experiment' in collections:
        return experiments.do(marcjson)
    elif 'hepnames' in collections:
        return hepnames.do(marcjson)
    elif 'institution' in collections:
        return institutions.do(marcjson)
    elif 'journals' in collections or 'journalsnew' in collections:
        return journals.do(marcjson)
    elif 'job' in collections or 'jobhidden' in collections:
        raise NotSupportedError("Jobs are not supported any more")
    return hep.do(marcjson)


def record2marcxml_etree(record):
    """Convert a JSON record to a MARCXML element tree."""
    schema_name = _get_schema_name(record)

    if schema_name == 'hep':
        marcjson = hep2marc.do(record)
    elif schema_name == 'authors':
        marcjson = hepnames2marc.do(record)
    else:
        raise NotSupportedError(
            u'JSON -> MARC rules missing for "{}"'.format(schema_name)
        )

    record = RECORD()

    for key, values in sorted(iteritems(marcjson)):
        tag, ind1, ind2 = _parse_key(key)
        if _is_controlfield(tag, ind1, ind2):
            value = force_single_element(values)
            if not isinstance(value, text_type):
                value = text_type(value)
            record.append(
                CONTROLFIELD(_strip_invalid_chars_for_xml(value), {'tag': tag})
            )
        else:
            for value in force_list(values):
                datafield = DATAFIELD({'tag': tag, 'ind1': ind1, 'ind2': ind2})
                for code, els in sorted(iteritems(value)):
                    for el in force_list(els):
                        if not isinstance(el, text_type):
                            el = text_type(el)
                        datafield.append(
                            SUBFIELD(_strip_invalid_chars_for_xml(el), {'code': code})
                        )
                record.append(datafield)

    return record


def record2marcxml(record):
    """Convert a JSON record to a MARCXML string.

    Deduces which set of rules to use by parsing the ``$schema`` key, as
    it unequivocally determines which kind of record we have.

    Args:
        record(dict): a JSON record.

    Returns:
        str: a MARCXML string converted from the record.

    """
    record_tree = record2marcxml_etree(record)
    return tostring(record_tree, encoding='utf8', pretty_print=True)


def cds_marcxml2record(marcxml):
    marcjson = create_record(marcxml, keep_singletons=False)

    return hep.do(create_record_from_dict(cds2hep_marc.do(marcjson)))


def _get_collections(marcjson):
    collections = chain.from_iterable(
        [force_list(el) for el in force_list(get_value(marcjson, '980__.a'))]
    )
    normalized_collections = [el.lower() for el in collections]

    return normalized_collections


def _get_schema_name(record):
    schema_url = record['$schema']
    parsed_url = urllib.parse.urlparse(schema_url)
    _, filename = os.path.split(parsed_url.path)
    schema_name, _ = os.path.splitext(filename)

    return schema_name


def _is_controlfield(tag, ind1, ind2):
    return tag.startswith('00')


def _parse_key(key):
    return key[:3], key[3:4] or ' ', key[4:5] or ' '


def _strip_invalid_chars_for_xml(s):
    return re.sub(RE_INVALID_CHARS_FOR_XML, '', s)
