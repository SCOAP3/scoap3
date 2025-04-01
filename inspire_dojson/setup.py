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

"""INSPIRE-specific rules to transform from MARCXML to JSON and back."""

from __future__ import absolute_import, division, print_function

from setuptools import find_packages, setup

URL = "https://github.com/inspirehep/inspire-dojson"

with open("README.rst") as f:
    readme = f.read()


install_requires = [
    "Flask>=0.12.3",
    "IDUtils~=1.0,>=1.0.1",
    "dojson~=1.0,>=1.3.1",
    "inspire-schemas",
    "inspire-utils~=3.0,>=3.0.0",
    "isbnid_fork~=0.0,>=0.5.2",
    "langdetect~=1.0,>=1.0.7",
    "pycountry~=17.0,>=17.5.4",
    "MarkupSafe>=1.1.1",
    "urllib3~=1.25.0",
]

docs_require = []

tests_require = [
    "flake8-future-import~=0.0,>=0.4.3",
    "mock~=2.0,>=2.0.0",
    "pytest~=4.0,>=4.6",
    "pytest-cov~=2.0,>=2.6.1",
]

dev_require = [
    "pre-commit==3.5.0",
]

extras_require = {
    "docs": docs_require,
    "tests": tests_require,
    "dev": dev_require,
}

extras_require["all"] = []
for _name, reqs in extras_require.items():
    extras_require["all"].extend(reqs)

packages = find_packages(exclude=["docs"])

setup(
    name="inspire-dojson",
    url=URL,
    license="GPLv3",
    author="CERN",
    author_email="admin@inspirehep.net",
    packages=packages,
    include_package_data=True,
    zip_safe=False,
    platforms="any",
    description=__doc__,
    long_description=readme,
    install_requires=install_requires,
    tests_require=tests_require,
    extras_require=extras_require,
    version="63.2.27",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
