# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2014-2017 CERN.
#
# INSPIRE is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
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
from flask import Flask
from langdetect import DetectorFactory

CONFIG = {
    'SERVER_NAME': 'localhost:5000',
    'LEGACY_BASE_URL': 'http://inspirehep.net',
}


@pytest.fixture(autouse=True, scope='session')
def app():
    app = Flask(__name__)
    app.config.update(CONFIG)
    with app.app_context():
        yield app


@pytest.fixture()
def _stable_langdetect(app):
    """Ensure that ``langdetect`` always returns the same thing.

    See: https://github.com/Mimino666/langdetect#basic-usage.
    """
    seed = DetectorFactory.seed
    DetectorFactory.seed = 0

    yield

    DetectorFactory.seed = seed
