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

import pytest
from dojson.contrib.marc21.utils import create_record
from flask import current_app
from inspire_schemas.api import load_schema, validate
from mock import patch

from inspire_dojson.hep import hep, hep2marc


@pytest.fixture()
def _legacy_afs_service_config():
    config = {'LABS_AFS_HTTP_SERVICE': 'http://legacy-afs-web'}
    with patch.dict(current_app.config, config):
        yield


@pytest.mark.usefixtures("_legacy_afs_service_config")
def test_documents_from_FFT():
    schema = load_schema('hep')
    subschema = schema['properties']['documents']

    snippet = (  # record/1628455
        '<datafield tag="FFT" ind1=" " ind2=" ">  <subfield'
        ' code="a">/opt/cds-invenio/var/data/files/g151/3037619/content.pdf;1'
        '</subfield>'
        '  <subfield code="d"/>  <subfield code="f">.pdf</subfield>  <subfield'
        ' code="n">arXiv:1710.01187</subfield>  <subfield code="r"/>  <subfield'
        ' code="s">2017-10-04 09:42:00</subfield>  <subfield code="t">Main</subfield> '
        ' <subfield code="v">1</subfield>  <subfield code="z"/></datafield>'
    )

    expected = [
        {
            'key': 'arXiv:1710.01187.pdf',
            'url': 'http://legacy-afs-web/var/data/files/g151/3037619/content.pdf%3B1',
        },
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['documents'], subschema) is None
    assert expected == result['documents']
    assert 'figures' not in result


@pytest.mark.usefixtures("_legacy_afs_service_config")
def test_documents_from_FFT_special_cases_arxiv_properly():
    schema = load_schema('hep')
    subschema = schema['properties']['documents']

    snippet = (  # record/1628455
        '<datafield tag="FFT" ind1=" " ind2=" ">  <subfield'
        ' code="a">/opt/cds-invenio/var/data/files/g151/3037619/content.pdf;2'
        '</subfield>'
        '  <subfield code="d"/>  <subfield code="f">.pdf</subfield>  <subfield'
        ' code="n">arXiv:1710.01187</subfield>  <subfield code="r"/>  <subfield'
        ' code="s">2017-12-06 03:34:26</subfield>  <subfield code="t">arXiv</subfield> '
        ' <subfield code="v">2</subfield>  <subfield code="z"/></datafield>'
    )

    expected = [
        {
            'key': 'arXiv:1710.01187.pdf',
            'url': 'http://legacy-afs-web/var/data/files/g151/3037619/content.pdf%3B2',
            'source': 'arxiv',
            'hidden': True,
        },
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['documents'], subschema) is None
    assert expected == result['documents']
    assert 'figures' not in result


@pytest.mark.usefixtures("_legacy_afs_service_config")
def test_documents_are_unique_from_FFT():
    schema = load_schema('hep')
    subschema = schema['properties']['documents']

    snippet = (  # record/1628455
        '<record>  <datafield tag="FFT" ind1=" " ind2=" ">    <subfield'
        ' code="a">/opt/cds-invenio/var/data/files/g151/3037619/content.pdf;1'
        '</subfield>'
        '    <subfield code="d"/>    <subfield code="f">.pdf</subfield>    <subfield'
        ' code="n">arXiv:1710.01187</subfield>    <subfield code="r"/>    <subfield'
        ' code="s">2017-10-04 09:42:00</subfield>    <subfield code="t">Main</subfield>'
        '    <subfield code="v">1</subfield>    <subfield code="z"/>  </datafield> '
        ' <datafield tag="FFT" ind1=" " ind2=" ">    <subfield'
        ' code="a">/opt/cds-invenio/var/data/files/g151/3037619/content.pdf;1'
        '</subfield>'
        '    <subfield code="d"/>    <subfield code="f">.pdf</subfield>    <subfield'
        ' code="n">arXiv:1710.01187</subfield>    <subfield code="r"/>    <subfield'
        ' code="s">2017-10-04 09:42:00</subfield>    <subfield code="t">Main</subfield>'
        '    <subfield code="v">1</subfield>    <subfield code="z"/> '
        ' </datafield></record>'
    )

    expected = [
        {
            'key': 'arXiv:1710.01187.pdf',
            'url': 'http://legacy-afs-web/var/data/files/g151/3037619/content.pdf%3B1',
        },
        {
            'key': '1_arXiv:1710.01187.pdf',
            'url': 'http://legacy-afs-web/var/data/files/g151/3037619/content.pdf%3B1',
        },
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['documents'], subschema) is None
    assert expected == result['documents']
    assert 'figures' not in result


@pytest.mark.usefixtures("_legacy_afs_service_config")
def test_figures_from_FFT():
    schema = load_schema('hep')
    subschema = schema['properties']['figures']

    snippet = (  # record/1628455
        '<datafield tag="FFT" ind1=" " ind2=" ">  <subfield'
        ' code="a">/opt/cds-invenio/var/data/files/g151/3037399/content.png;1'
        '</subfield>'
        '  <subfield code="d">00009 Co-simulation results, at'
        ' $50~\\mathrm{ms}$...</subfield>  <subfield code="f">.png</subfield> '
        ' <subfield code="n">FIG10</subfield>  <subfield code="r"/>  <subfield'
        ' code="s">2017-10-04 07:54:54</subfield>  <subfield code="t">Main</subfield> '
        ' <subfield code="v">1</subfield>  <subfield code="z"/></datafield>'
    )

    expected = [
        {
            'key': 'FIG10.png',
            'caption': 'Co-simulation results, at $50~\\mathrm{ms}$...',
            'url': 'http://legacy-afs-web/var/data/files/g151/3037399/content.png%3B1',
            'source': 'arxiv',
        },
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['figures'], subschema) is None
    assert expected == result['figures']
    assert 'documents' not in result


@pytest.mark.usefixtures("_legacy_afs_service_config")
def test_figures_order_from_FFT():
    schema = load_schema('hep')
    subschema = schema['properties']['figures']

    snippet = (  # record/1628455
        '<record>  <datafield tag="FFT" ind1=" " ind2=" ">    <subfield'
        ' code="a">/opt/cds-invenio/var/data/files/g151/3037400/content.png;1'
        '</subfield>'
        '    <subfield code="d">00010 Co-simulation results, at'
        ' $50~\\mathrm{ms}$...</subfield>    <subfield code="f">.png</subfield>   '
        ' <subfield code="n">FIG11</subfield>    <subfield code="r"/>    <subfield'
        ' code="s">2017-10-04 07:54:54</subfield>    <subfield code="t">Main</subfield>'
        '    <subfield code="v">1</subfield>    <subfield code="z"/>  </datafield> '
        ' <datafield tag="FFT" ind1=" " ind2=" ">    <subfield'
        ' code="a">/opt/cds-invenio/var/data/files/g151/3037399/content.png;1'
        '</subfield>'
        '    <subfield code="d">00009 Co-simulation results, at'
        ' $50~\\mathrm{ms}$...</subfield>    <subfield code="f">.png</subfield>   '
        ' <subfield code="n">FIG10</subfield>    <subfield code="r"/>    <subfield'
        ' code="s">2017-10-04 07:54:54</subfield>    <subfield code="t">Main</subfield>'
        '    <subfield code="v">1</subfield>    <subfield code="z"/>  </datafield> '
        ' <datafield tag="FFT" ind1=" " ind2=" ">    <subfield'
        ' code="a">/opt/cds-invenio/var/data/files/g151/3037401/content.png;1'
        '</subfield>'
        '    <subfield code="d">00011 Co-simulation results, at'
        ' $50~\\mathrm{ms}$...</subfield>    <subfield code="f">.png</subfield>   '
        ' <subfield code="n">FIG12</subfield>    <subfield code="r"/>    <subfield'
        ' code="s">2017-10-04 07:54:54</subfield>    <subfield code="t">Main</subfield>'
        '    <subfield code="v">1</subfield>    <subfield code="z"/> '
        ' </datafield></record>'
    )

    expected = [
        {
            'key': 'FIG10.png',
            'caption': 'Co-simulation results, at $50~\\mathrm{ms}$...',
            'url': 'http://legacy-afs-web/var/data/files/g151/3037399/content.png%3B1',
            'source': 'arxiv',
        },
        {
            'key': 'FIG11.png',
            'caption': 'Co-simulation results, at $50~\\mathrm{ms}$...',
            'url': 'http://legacy-afs-web/var/data/files/g151/3037400/content.png%3B1',
            'source': 'arxiv',
        },
        {
            'key': 'FIG12.png',
            'caption': 'Co-simulation results, at $50~\\mathrm{ms}$...',
            'url': 'http://legacy-afs-web/var/data/files/g151/3037401/content.png%3B1',
            'source': 'arxiv',
        },
    ]
    result = hep.do(create_record(snippet))
    assert validate(result['figures'], subschema) is None
    assert expected == result['figures']
    assert 'documents' not in result


def test_documents_from_FFT_ignores_context():
    snippet = (  # record/1610503
        '<datafield tag="FFT" ind1=" " ind2=" ">  <subfield'
        ' code="a">/opt/cds-invenio/var/data/files/g148/2964970/content.png;context;1'
        '</subfield>'
        '  <subfield code="d"/>  <subfield code="f">.png;context</subfield>  <subfield'
        ' code="n">TNR</subfield>  <subfield code="r"/>  <subfield code="s">2017-07-19'
        ' 09:29:27</subfield>  <subfield code="t">Main</subfield>  <subfield'
        ' code="v">1</subfield><subfield code="z"/>  <subfield'
        ' code="o">HIDDEN</subfield></datafield>'
    )

    result = hep.do(create_record(snippet))

    assert 'documents' not in result
    assert 'figures' not in result


def test_documents_from_FFT_does_not_require_s():
    schema = load_schema('hep')
    subschema = schema['properties']['documents']

    snippet = (  # DESY harvest
        '<datafield tag="FFT" ind1=" " ind2=" ">  <subfield'
        ' code="a">http://www.mdpi.com/2218-1997/3/1/24/pdf</subfield> '
        ' <subfield code="d">Fulltext</subfield>  <subfield'
        ' code="t">INSPIRE-PUBLIC</subfield></datafield>'
    )

    expected = [
        {
            'key': 'document',
            'fulltext': True,
            'url': 'http://www.mdpi.com/2218-1997/3/1/24/pdf',
        }
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['documents'], subschema) is None
    assert expected == result['documents']
    assert 'figures' not in result

    expected = [
        {
            'a': 'http://www.mdpi.com/2218-1997/3/1/24/pdf',
            'd': 'Fulltext',
            't': 'INSPIRE-PUBLIC',
            'n': 'document',
        },
    ]
    result = hep2marc.do(result)

    assert expected == result['FFT']


def test_fft_from_FFT_percent_percent():
    snippet = (  # record/1094156
        '<datafield tag="FFT" ind1="%" ind2="%">  <subfield'
        ' code="a">/opt/cds-invenio/var/tmp-shared/apsharvest_unzip_5dGfY5/'
        ' articlebag-10-1103-PhysRevD-87-083514-apsxml/data/PhysRevD.87.083514/'
        'fulltext.xml</subfield>'
        '  <subfield code="o">HIDDEN</subfield>  <subfield'
        ' code="t">APS</subfield></datafield>'
    )

    result = hep.do(create_record(snippet))
    assert 'documents' not in result
    assert 'figures' not in result


def test_documents_to_FFT():
    schema = load_schema('hep')
    subschema = schema['properties']['documents']

    snippet = {
        'documents': [
            {
                'key': 'some_document.pdf',
                'description': 'Thesis fulltext',
                'hidden': True,
                'fulltext': True,
                'material': 'publication',
                'url': '/api/files/1234-1234-1234-1234/some_document.pdf',
                'original_url': 'http://example.com/some_document.pdf',
                'source': 'submitter',
            }
        ]
    }  # synthetic data

    expected = [
        {
            'a': (
                'http://localhost:5000/api/files/1234-1234-1234-1234/some_document.pdf'
            ),
            'd': 'Thesis fulltext',
            'f': '.pdf',
            't': 'INSPIRE-PUBLIC',
            'o': 'HIDDEN',
            'n': 'some_document',
        }
    ]

    assert validate(snippet['documents'], subschema) is None

    result = hep2marc.do(snippet)

    assert expected == result['FFT']


@pytest.mark.usefixtures("_legacy_afs_service_config")
def test_documents_to_FFT_converts_afs_urls_to_path():
    schema = load_schema('hep')
    subschema = schema['properties']['documents']

    snippet = {
        'documents': [
            {
                'key': 'some_document.pdf',
                'description': 'Thesis fulltext',
                'hidden': True,
                'fulltext': True,
                'url': 'http://legacy-afs-web/var/files/some_document.pdf%3B1',
                'original_url': 'http://example.com/some_document.pdf',
            }
        ]
    }  # synthetic data

    expected = [
        {
            'a': 'file:///afs/cern.ch/project/inspire/PROD/var/files/some_document.pdf%3B1',
            'd': 'Thesis fulltext',
            't': 'INSPIRE-PUBLIC',
            'f': '.pdf',
            'o': 'HIDDEN',
            'n': 'some_document',
        }
    ]

    assert validate(snippet['documents'], subschema) is None

    result = hep2marc.do(snippet)
    assert expected == result['FFT']


def test_documents_to_FFT_special_cases_arxiv_properly():
    schema = load_schema('hep')
    subschema = schema['properties']['documents']

    snippet = {
        "documents": [
            {
                'fulltext': True,
                'hidden': True,
                'key': '1712.04934.pdf',
                'material': 'preprint',
                'original_url': 'http://export.arxiv.org/pdf/1712.04934',
                'source': 'arxiv',
                'url': '/api/files/d82dc015-83ea-4d83-820b-adb7ce1e42d0/1712.04934.pdf',
            }
        ],
    }  # holdingpen/820589

    expected = [
        {
            'a': 'http://localhost:5000/api/files/d82dc015-83ea-4d83-820b-adb7ce1e42d0/1712.04934.pdf',
            'd': 'Fulltext',
            't': 'arXiv',
            'f': '.pdf',
            'n': '1712.04934',
        }
    ]

    assert validate(snippet['documents'], subschema) is None

    result = hep2marc.do(snippet)

    assert expected == result['FFT']


def test_documents_to_FFT_uses_filename():
    schema = load_schema('hep')
    subschema = schema['properties']['documents']

    snippet = {
        'documents': [
            {
                "description": "Article from SCOAP3",
                "filename": "scoap3-fulltext.pdf",
                "key": "136472d8763496230daa8b6b72fb219a",
                "original_url": (
                    "http://legacy-afs-web/var/data/files/g206/4135590/content.pdf%3B1"
                ),
                "source": "SCOAP3",
                "url": "https://s3.cern.ch/inspire-prod-files-1/136472d8763496230daa8b6b72fb219a",
            }
        ]
    }  # literature/1789709

    expected = [
        {
            'a': 'https://s3.cern.ch/inspire-prod-files-1/136472d8763496230daa8b6b72fb219a',
            'd': 'Article from SCOAP3',
            't': 'SCOAP3',
            'n': 'scoap3-fulltext',
            'f': '.pdf',
        }
    ]

    assert validate(snippet['documents'], subschema) is None

    result = hep2marc.do(snippet)

    assert expected == result['FFT']


def test_documents_to_FFT_uses_material_as_filename_fallback():
    schema = load_schema('hep')
    subschema = schema['properties']['documents']

    snippet = {
        "documents": [
            {
                "key": "8f09853e5bc12d6d077ba0833e97626e",
                "url": "https://inspirehep.net/files/8f09853e5bc12d6d077ba0833e97626e",
                "source": "Springer",
                "fulltext": True,
                "filename": "document",
                "material": "addendum",
            },
            {
                "key": "35715635c16bc869b4995e150b140bf8",
                "url": "https://inspirehep.net/files/35715635c16bc869b4995e150b140bf8",
                "hidden": True,
                "source": "arxiv",
                "filename": "2103.11769.pdf",
                "fulltext": True,
                "material": "preprint",
                "original_url": "http://export.arxiv.org/pdf/2103.11769",
            },
            {
                "key": "277ff3946ce757cba86a4ab4ebb95287",
                "url": "https://inspirehep.net/files/277ff3946ce757cba86a4ab4ebb95287",
                "filename": "document",
                "fulltext": True,
                "material": "publication",
            },
        ],
    }  # literature/1852846

    expected = [
        {
            "a": "https://inspirehep.net/files/8f09853e5bc12d6d077ba0833e97626e",
            "d": "Fulltext",
            "n": "addendum",
            "t": "Springer",
        },
        {
            "a": "https://inspirehep.net/files/35715635c16bc869b4995e150b140bf8",
            "d": "Fulltext",
            "n": "2103.11769",
            "t": "arXiv",
            "f": ".pdf",
        },
        {
            "a": "https://inspirehep.net/files/277ff3946ce757cba86a4ab4ebb95287",
            "d": "Fulltext",
            "n": "document",
            "t": "INSPIRE-PUBLIC",
        },
    ]

    assert validate(snippet['documents'], subschema) is None

    result = hep2marc.do(snippet)

    assert expected == result['FFT']


def test_figures_to_FFT():
    schema = load_schema('hep')
    subschema = schema['properties']['figures']

    snippet = {
        'figures': [
            {
                'key': 'some_figure.png',
                'caption': 'This figure illustrates something',
                'material': 'preprint',
                'url': '/api/files/1234-1234-1234-1234/some_figure.png',
                'source': 'arxiv',
            }
        ]
    }  # synthetic data

    expected = [
        {
            'a': 'http://localhost:5000/api/files/1234-1234-1234-1234/some_figure.png',
            'd': '00000 This figure illustrates something',
            't': 'Plot',
            'n': 'some_figure',
            'f': '.png',
        }
    ]

    assert validate(snippet['figures'], subschema) is None

    result = hep2marc.do(snippet)

    assert expected == result['FFT']


@pytest.mark.usefixtures("_legacy_afs_service_config")
def test_figures_to_FFT_converts_afs_urls_to_paths():
    schema = load_schema('hep')
    subschema = schema['properties']['figures']

    snippet = {
        'figures': [
            {
                'key': 'some_figure.png',
                'caption': 'This figure illustrates something',
                'url': 'http://legacy-afs-web/var/files/some_figure.png%3B1',
                'original_url': 'http://example.com/some_figure.png%3B1',
            }
        ]
    }  # synthetic data

    expected = [
        {
            'a': (
                'file:///afs/cern.ch/project/inspire/PROD/var/files/some_figure.png%3B1'
            ),
            'd': '00000 This figure illustrates something',
            't': 'Plot',
            'n': 'some_figure',
            'f': '.png',
        }
    ]

    assert validate(snippet['figures'], subschema) is None

    result = hep2marc.do(snippet)
    assert expected == result['FFT']


def test_figures_to_FFT_uses_filename():
    schema = load_schema('hep')
    subschema = schema['properties']['figures']

    snippet = {
        'figures': [
            {
                "caption": (
                    "(Color online) (a) Comparison between the function"
                    " $f_\\Gamma(Q\\xi)$ (\\ref{eq:fgamma}) and the Kawasaki"
                    " function defined in footnote \\ref{footnote:kawasaki}."
                    " Large-$Q$ modes relax faster with $f_\\Gamma$ than with"
                    " $K$. (b) Illustration of the contribution $\\Delta s_Q$"
                    " to the entropy density by a single slow mode with wave"
                    " number $Q$ ($x{\\,\\equiv\\,}\\phi_Q/\\bar\\phi_Q$)."
                    " $\\Delta s_Q$ is negative whether $\\phi_Q$ is below or"
                    " above its equilibrium value ({\\it cf.}"
                    " Eq.~(\\ref{eq:deltas}) below)."
                ),
                "filename": "plot_functions.png",
                "key": "b43cbd4ccd7cceb3a30d2b80894101d1",
                "source": "arxiv",
                "url": "https://s3.cern.ch/inspire-prod-files-b/b43cbd4ccd7cceb3a30d2b80894101d1",
            }
        ]
    }  # literature/1789762

    expected = [
        {
            'a': 'https://s3.cern.ch/inspire-prod-files-b/b43cbd4ccd7cceb3a30d2b80894101d1',
            'd': (
                '00000 (Color online) (a) Comparison between the function'
                ' $f_\\Gamma(Q\\xi)$ (\\ref{eq:fgamma}) and the Kawasaki'
                ' function defined in footnote \\ref{footnote:kawasaki}.'
                ' Large-$Q$ modes relax faster with $f_\\Gamma$ than with $K$.'
                ' (b) Illustration of the contribution $\\Delta s_Q$ to the'
                ' entropy density by a single slow mode with wave number $Q$'
                ' ($x{\\,\\equiv\\,}\\phi_Q/\\bar\\phi_Q$). $\\Delta s_Q$ is'
                ' negative whether $\\phi_Q$ is below or above its equilibrium'
                ' value ({\\it cf.} Eq.~(\\ref{eq:deltas}) below).'
            ),
            't': 'Plot',
            'n': 'plot_functions',
            'f': '.png',
        }
    ]

    assert validate(snippet['figures'], subschema) is None

    result = hep2marc.do(snippet)

    assert expected == result['FFT']


@pytest.mark.usefixtures("_legacy_afs_service_config")
def test_figures_from_FFT_generates_valid_uri():
    schema = load_schema('hep')
    subschema = schema['properties']['figures']

    snippet = (  # record/1245001
        '<datafield tag="FFT" ind1=" " ind2=" ">  <subfield'
        ' code="a">/opt/cds-invenio/var/data/files/g83/1678426/FKLP'
        ' new_VF.png;1</subfield>  <subfield code="d">00000 Inflationary'
        ' potential ${g^{2}\\vp^{2}\\over 2} (1-a\\vp+b\\vp^{2})^2$ '
        ' (\\ref{three}), for $a = 0.1$, $b = 0.0035$. The field is shown in'
        ' Planck units, the potential $V$ is shown in units $g^{2}$. In'
        ' realistic models of that type, $g \\sim 10^{-5} - 10^{-6}$ in Planck'
        ' units, depending on details of the theory, so the height of the'
        ' potential in this figure is about $10^{-10}$ in Planck'
        ' units.</subfield>  <subfield code="f">.png</subfield>  <subfield'
        ' code="n">FKLP new_VF</subfield>  <subfield code="r"></subfield> '
        ' <subfield code="s">2013-10-22 05:04:33</subfield>  <subfield'
        ' code="t">Plot</subfield>  <subfield code="v">1</subfield>  <subfield'
        ' code="z"></subfield></datafield>'
    )

    expected = [
        {
            'key': 'FKLP new_VF.png',
            'caption': (
                'Inflationary potential ${g^{2}\\vp^{2}\\over 2}'
                ' (1-a\\vp+b\\vp^{2})^2$  (\\ref{three}), for $a = 0.1$, $b ='
                ' 0.0035$. The field is shown in Planck units, the potential'
                ' $V$ is shown in units $g^{2}$. In realistic models of that'
                ' type, $g \\sim 10^{-5} - 10^{-6}$ in Planck units, depending'
                ' on details of the theory, so the height of the potential in'
                ' this figure is about $10^{-10}$ in Planck units.'
            ),
            'url': (
                'http://legacy-afs-web/var/data/files/g83/1678426/FKLP%20new_VF.png%3B1'
            ),
            'source': 'arxiv',
        }
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['figures'], subschema) is None
    assert expected == result['figures']

    expected = [
        {
            'a': 'file:///afs/cern.ch/project/inspire/PROD/var/data/files/g83/1678426/FKLP%20new_VF.png%3B1',
            'd': (
                '00000 Inflationary potential ${g^{2}\\vp^{2}\\over 2}'
                ' (1-a\\vp+b\\vp^{2})^2$  (\\ref{three}), for $a = 0.1$, $b ='
                ' 0.0035$. The field is shown in Planck units, the potential'
                ' $V$ is shown in units $g^{2}$. In realistic models of that'
                ' type, $g \\sim 10^{-5} - 10^{-6}$ in Planck units, depending'
                ' on details of the theory, so the height of the potential in'
                ' this figure is about $10^{-10}$ in Planck units.'
            ),
            't': 'Plot',
            'n': 'FKLP new_VF',
            'f': '.png',
        }
    ]
    result = hep2marc.do(result)

    assert expected == result['FFT']


@pytest.mark.usefixtures("_legacy_afs_service_config")
def test_figures_and_documents_from_FFT_without_d_subfield():
    schema = load_schema('hep')
    figures_subschema = schema['properties']['figures']
    documents_subschema = schema['properties']['documents']

    snippet = (  # record/1628455
        '<record>  <datafield tag="FFT" ind1=" " ind2=" ">    <subfield'
        ' code="a">/opt/cds-invenio/var/data/files/g151/3037399/content.png;1'
        '</subfield>'
        '    <subfield code="f">.png</subfield>    <subfield code="n">FIG10</subfield> '
        '   <subfield code="r"/>    <subfield code="s">2017-10-04 07:54:54</subfield>  '
        '  <subfield code="t">Main</subfield>    <subfield code="v">1</subfield>  '
        ' <subfield code="z"/>  </datafield>  <datafield tag="FFT" ind1=" " ind2=" ">  '
        '  <subfield'
        ' code="a">/opt/cds-invenio/var/data/files/g151/3037619/content.pdf;1'
        '</subfield>'
        '    <subfield code="f">.pdf</subfield>    <subfield'
        ' code="n">arXiv:1710.01187</subfield>    <subfield code="r"/>    <subfield'
        ' code="s">2017-10-04 09:42:00</subfield>    <subfield code="t">Main</subfield>'
        '    <subfield code="v">1</subfield>    <subfield code="z"/> '
        ' </datafield></record>'
    )

    expected_figures = [
        {
            'key': 'FIG10.png',
            'url': 'http://legacy-afs-web/var/data/files/g151/3037399/content.png%3B1',
            'source': 'arxiv',
        },
    ]

    expected_documents = [
        {
            'key': 'arXiv:1710.01187.pdf',
            'url': 'http://legacy-afs-web/var/data/files/g151/3037619/content.pdf%3B1',
        },
    ]

    result = hep.do(create_record(snippet))

    assert validate(result['figures'], figures_subschema) is None
    assert validate(result['documents'], documents_subschema) is None
    assert 'documents' in result
    assert 'figures' in result

    assert expected_figures == result['figures']
    assert expected_documents == result['documents']


@pytest.mark.usefixtures("_legacy_afs_service_config")
def test_figures_from_FFT_with_composite_file_extension():
    schema = load_schema('hep')
    subschema = schema['properties']['figures']

    snippet = (  # record/852500
        '<datafield tag="FFT" ind1=" " ind2=" ">  <subfield'
        ' code="a">/opt/cds-invenio/var/data/files/g22/457549/266.stripe82.jpg.png;1'
        '</subfield>'
        '  <subfield code="d">00011 Examples of relaxed early-types (top three rows)'
        ' and galaxies classified as late-type (bottom three rows). We show both the'
        ' multi-colour standard-depth image (left-hand column) and itsdeeper Stripe82'
        ' counterpart (right-hand column).</subfield>  <subfield'
        ' code="f">.jpg.png</subfield>  <subfield code="n">266.stripe82</subfield> '
        ' <subfield code="r"></subfield>  <subfield code="s">2010-10-09'
        ' 23:23:31</subfield>  <subfield code="t">Plot</subfield>  <subfield'
        ' code="v">1</subfield>  <subfield code="z"></subfield></datafield>'
    )

    expected = [
        {
            'caption': (
                'Examples of relaxed early-types (top three rows) and galaxies'
                ' classified as late-type (bottom three rows). We show both the'
                ' multi-colour standard-depth image (left-hand column) and itsdeeper'
                ' Stripe82 counterpart (right-hand column).'
            ),
            'key': '266.stripe82.jpg.png',
            'url': 'http://legacy-afs-web/var/data/files/g22/457549/266.stripe82.jpg.png%3B1',
            'source': 'arxiv',
        },
    ]

    result = hep.do(create_record(snippet))

    assert validate(result['figures'], subschema) is None
    assert expected == result['figures']


def test_figures2marc_handles_unicode():
    schema = load_schema('hep')
    subschema = schema['properties']['figures']

    record = {
        'figures': [
            {
                'caption': (
                    u'Hard gaps. (a) Differential conductance $G_S$ of an'
                    u' epitaxial nanowire device as a function of backgate'
                    u' voltage $V_{BG}$ and source\u00d0drain voltage $V_{SD}$.'
                    u' Increasing $V_{BG}$, the conductance increases from the'
                    u' tunneling to the Andreev regime (orange and blue plots'
                    u' in the bottom). Adapted from Ref. \\cite{Chang2015}. (b)'
                    u' Subgap conductance $G_s$ as a function of the normal'
                    u' (above-gap) conductance $G_n$. Red curve is the theory'
                    u' prediction for a single channel NS contact, Eq.'
                    u' (\\ref{NS-Andreev}). Inset shows different $dI/dV$ taken'
                    u' at different values of $G_n$. Adapted from Ref.'
                    u' \\cite{Zhang2016}.'
                ),
                'key': 'Fig21.png',
                'label': 'fig:21',
                'material': 'preprint',
                'source': 'arxiv',
                'url': '/api/files/feb489f4-7e13-4ca4-b51c-2c8c2242d596/Fig21.png',
            },
        ],
    }  # holdingpen/772341
    assert validate(record['figures'], subschema) is None

    expected = [
        {
            'a': 'http://localhost:5000/api/files/feb489f4-7e13-4ca4-b51c-2c8c2242d596/Fig21.png',
            'd': (
                u'00000 Hard gaps. (a) Differential conductance $G_S$ of an'
                u' epitaxial nanowire device as a function of backgate voltage'
                u' $V_{BG}$ and source\xd0drain voltage $V_{SD}$. Increasing'
                u' $V_{BG}$, the conductance increases from the tunneling to'
                u' the Andreev regime (orange and blue plots in the bottom).'
                u' Adapted from Ref. \\cite{Chang2015}. (b) Subgap conductance'
                u' $G_s$ as a function of the normal (above-gap) conductance'
                u' $G_n$. Red curve is the theory prediction for a single'
                u' channel NS contact, Eq. (\\ref{NS-Andreev}). Inset shows'
                u' different $dI/dV$ taken at different values of $G_n$.'
                u' Adapted from Ref. \\cite{Zhang2016}.'
            ),
            't': 'Plot',
            'n': 'Fig21',
            'f': '.png',
        },
    ]
    result = hep2marc.do(record)

    assert expected == result['FFT']


def test_documents_from_FFT_without_t_subfield():
    schema = load_schema('hep')
    subschema = schema['properties']['documents']

    snippet = (
        "<datafield tag='FFT' ind1=' ' ind2=' '>  <subfield"
        " code='a'>http://scoap3.iop.org/article/doi/10.1088/1674-1137/43/1/013104?format=pdf</subfield>"
        "  <subfield code='f'>.pdf</subfield>  <subfield"
        " code='n'>fulltext</subfield></datafield>"
    )

    expected = [
        {
            'url': 'http://scoap3.iop.org/article/doi/10.1088/1674-1137/43/1/013104?format=pdf',
            'key': 'fulltext.pdf',
        }
    ]
    result = hep.do(create_record(snippet))
    assert validate(result['documents'], subschema) is None
    assert expected == result['documents']
    assert 'figures' not in result
