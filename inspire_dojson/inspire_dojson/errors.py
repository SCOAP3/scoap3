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

"""Custom errors for INSPIRE DoJSON."""

from __future__ import absolute_import, division, print_function

from six import python_2_unicode_compatible, text_type


@python_2_unicode_compatible
class DoJsonError(Exception):
    """Error during DoJSON processing."""

    def __str__(self):
        message = self.args[0]
        exc = u' '.join(text_type(arg) for arg in self.args[1])
        try:
            subfields = [(k, v) for (k, v) in self.args[2].items() if k != '__order__']
        except (
            AttributeError
        ):  # when not dealing with MARC, the value doesn't have to be a dict
            subfields = self.args[2]
        return u'{message}\n\n{exc}\n\nSubfields: {subfields}'.format(
            message=message, exc=exc, subfields=subfields
        )


class NotSupportedError(NotImplementedError):
    pass
