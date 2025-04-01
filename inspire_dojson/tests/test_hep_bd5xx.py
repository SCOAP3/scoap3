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

from inspire_dojson.hep import hep, hep2marc


def test_public_notes_from_500__a_9():
    schema = load_schema('hep')
    subschema = schema['properties']['public_notes']

    snippet = (  # record/1450044
        '<datafield tag="500" ind1=" " ind2=" ">'
        '  <subfield code="9">arXiv</subfield>'
        '  <subfield code="a">5 pages</subfield>'
        '</datafield>'
    )

    expected = [
        {
            'source': 'arXiv',
            'value': '5 pages',
        },
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['public_notes'], subschema) is None
    assert expected == result['public_notes']

    expected = [
        {
            '9': 'arXiv',
            'a': '5 pages',
        },
    ]
    result = hep2marc.do(result)

    assert expected == result['500']


def test_public_notes_from_500__a_9_presented_on():
    schema = load_schema('hep')
    subschema = schema['properties']['public_notes']

    snippet = (  # record/1185462
        '<datafield tag="500" ind1=" " ind2=" ">  <subfield code="a">presented'
        ' on the 11th International Conference on Modification of Materials'
        ' with Particle Beams and Plasma Flows (Tomsk, Russia, 17-21 september'
        ' 2012)</subfield>  <subfield code="9">arXiv</subfield></datafield>'
    )

    expected = [
        {
            'source': 'arXiv',
            'value': (
                'presented on the 11th International Conference on Modification'
                ' of Materials with Particle Beams and Plasma Flows (Tomsk,'
                ' Russia, 17-21 september 2012)'
            ),
        },
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['public_notes'], subschema) is None
    assert expected == result['public_notes']

    expected = [
        {
            '9': 'arXiv',
            'a': (
                'presented on the 11th International Conference on Modification'
                ' of Materials with Particle Beams and Plasma Flows (Tomsk,'
                ' Russia, 17-21 september 2012)'
            ),
        },
    ]
    result = hep2marc.do(result)

    assert expected == result['500']


def test_public_notes_from_500__double_a_9():
    schema = load_schema('hep')
    subschema = schema['properties']['public_notes']

    snippet = (  # record/1380257
        '<datafield tag="500" ind1=" " ind2=" ">  <subfield'
        ' code="9">arXiv</subfield>  <subfield code="a">11 pages, 8 figures.'
        ' Submitted to MNRAS</subfield>  <subfield code="a">preliminary'
        ' entry</subfield></datafield>'
    )

    expected = [
        {
            'source': 'arXiv',
            'value': '11 pages, 8 figures. Submitted to MNRAS',
        },
        {
            'source': 'arXiv',
            'value': 'preliminary entry',
        },
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['public_notes'], subschema) is None
    assert expected == result['public_notes']

    expected = [
        {
            '9': 'arXiv',
            'a': '11 pages, 8 figures. Submitted to MNRAS',
        },
        {
            '9': 'arXiv',
            'a': 'preliminary entry',
        },
    ]
    result = hep2marc.do(result)

    assert expected == result['500']


def test_curated_and_public_notes_from_500__a_and_500__a_9():
    schema = load_schema('hep')
    curated_schema = schema['properties']['curated']
    public_notes_schema = schema['properties']['public_notes']

    snippet = (  # record/1450045
        '<record>'
        '  <datafield tag="500" ind1=" " ind2=" ">'
        '    <subfield code="a">*Brief entry*</subfield>'
        '  </datafield>'
        '  <datafield tag="500" ind1=" " ind2=" ">'
        '    <subfield code="a">11 pages, 5 figures</subfield>'
        '    <subfield code="9">arXiv</subfield>'
        '  </datafield>'
        '</record>'
    )

    expected_curated = False
    expected_public_notes = [
        {
            'source': 'arXiv',
            'value': '11 pages, 5 figures',
        },
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['curated'], curated_schema) is None
    assert expected_curated == result['curated']

    assert validate(result['public_notes'], public_notes_schema) is None
    assert expected_public_notes == result['public_notes']

    expected = [
        {
            'a': '* Brief entry *',
        },
        {
            '9': 'arXiv',
            'a': '11 pages, 5 figures',
        },
    ]
    result = hep2marc.do(result)

    assert expected == result['500']


def test_curated_from_500__a():
    schema = load_schema('hep')
    subschema = schema['properties']['curated']

    snippet = (  # record/1184775
        '<datafield tag="500" ind1=" " ind2=" ">'
        '  <subfield code="a">* Brief entry *</subfield>'
        '</datafield>'
    )

    expected = False
    result = hep.do(create_record(snippet))

    assert validate(result['curated'], subschema) is None
    assert expected == result['curated']

    expected = [
        {'a': '* Brief entry *'},
    ]
    result = hep2marc.do(result)

    assert expected == result['500']


def test_core_and_curated_and_public_notes_from_500__a_and_500__a_9_and_980__a():
    schema = load_schema('hep')
    core_schema = schema['properties']['core']
    curated_schema = schema['properties']['curated']
    public_notes_schema = schema['properties']['public_notes']

    snippet = (  # record/1217749
        '<record>'
        '  <datafield tag="500" ind1=" " ind2=" ">'
        '    <subfield code="a">* Temporary entry *</subfield>'
        '  </datafield>'
        '  <datafield tag="500" ind1=" " ind2=" ">'
        '    <subfield code="a">*Temporary entry*</subfield>'
        '  </datafield>'
        '  <datafield tag="500" ind1=" " ind2=" ">'
        '    <subfield code="a">5+3 pages, 3+2 figures</subfield>'
        '    <subfield code="9">arXiv</subfield>'
        '  </datafield>'
        '  <datafield tag="980" ind1=" " ind2=" ">'
        '    <subfield code="a">CORE</subfield>'
        '  </datafield>'
        '</record>'
    )

    expected_core = True
    expected_curated = False
    expected_public_notes = [
        {
            'source': 'arXiv',
            'value': '5+3 pages, 3+2 figures',
        },
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['core'], core_schema) is None
    assert expected_core == result['core']

    assert validate(result['curated'], curated_schema) is None
    assert expected_curated == result['curated']

    assert validate(result['public_notes'], public_notes_schema) is None
    assert expected_public_notes == result['public_notes']

    expected = [
        {
            'a': '* Temporary entry *',
        },
        {
            'a': '5+3 pages, 3+2 figures',
            '9': 'arXiv',
        },
    ]
    result = hep2marc.do(result)

    assert expected == result['500']


def test_thesis_info_defense_date_from_500__a():
    schema = load_schema('hep')
    subschema = schema['properties']['thesis_info']

    snippet = (  # record/1517362
        '<datafield tag="500" ind1=" " ind2=" ">'
        '  <subfield code="a">Presented on 2016-09-30</subfield>'
        '</datafield>'
    )

    expected = {'defense_date': '2016-09-30'}
    result = hep.do(create_record(snippet))

    assert validate(result['thesis_info'], subschema) is None
    assert expected == result['thesis_info']

    expected = [
        {'a': 'Presented on 2016-09-30'},
    ]
    result = hep2marc.do(result)

    assert expected == result['500']


def test_thesis_info_defense_date_from_500__a_incomplete_date():
    schema = load_schema('hep')
    subschema = schema['properties']['thesis_info']

    snippet = (  # record/1509061
        '<datafield tag="500" ind1=" " ind2=" ">'
        '  <subfield code="a">Presented on 2016</subfield>'
        '</datafield>'
    )

    expected = {'defense_date': '2016'}
    result = hep.do(create_record(snippet))

    assert validate(result['thesis_info'], subschema) is None
    assert expected == result['thesis_info']

    expected = [
        {'a': 'Presented on 2016'},
    ]
    result = hep2marc.do(result)

    assert expected == result['500']


def test_thesis_info_defense_date_from_500__a_incomplete_human_date():
    schema = load_schema('hep')
    subschema = schema['properties']['thesis_info']

    snippet = (  # record/887715
        '<datafield tag="500" ind1=" " ind2=" ">'
        '  <subfield code="a">Presented on Dec 1992</subfield>'
        '</datafield>'
    )

    expected = {'defense_date': '1992-12'}
    result = hep.do(create_record(snippet))

    assert validate(result['thesis_info'], subschema) is None
    assert expected == result['thesis_info']

    expected = [
        {'a': 'Presented on 1992-12'},
    ]
    result = hep2marc.do(result)

    assert expected == result['500']


def test_thesis_from_502__b_c_d_z():
    schema = load_schema('hep')
    subschema = schema['properties']['thesis_info']

    snippet = (  # record/897773
        '<datafield tag="502" ind1=" " ind2=" ">'
        '  <subfield code="b">PhD</subfield>'
        '  <subfield code="c">IIT, Roorkee</subfield>'
        '  <subfield code="d">2011</subfield>'
        '  <subfield code="z">909554</subfield>'
        '</datafield>'
    )

    expected = {
        'date': '2011',
        'degree_type': 'phd',
        'institutions': [
            {
                'curated_relation': True,
                'record': {
                    '$ref': 'http://localhost:5000/api/institutions/909554',
                },
                'name': 'IIT, Roorkee',
            },
        ],
    }
    result = hep.do(create_record(snippet))

    assert validate(result['thesis_info'], subschema) is None
    assert expected == result['thesis_info']

    expected = {
        'b': 'PhD',
        'c': [
            'IIT, Roorkee',
        ],
        'd': '2011',
    }
    result = hep2marc.do(result)

    assert expected == result['502']


def test_thesis_from_502_b_double_c_d_double_z():
    schema = load_schema('hep')
    subschema = schema['properties']['thesis_info']

    snippet = (  # record/1385648
        '<datafield tag="502" ind1=" " ind2=" ">'
        '  <subfield code="b">Thesis</subfield>'
        '  <subfield code="c">Nice U.</subfield>'
        '  <subfield code="c">Cote d\'Azur Observ., Nice</subfield>'
        '  <subfield code="d">2014</subfield>'
        '  <subfield code="z">903069</subfield>'
        '  <subfield code="z">904125</subfield>'
        '</datafield>'
    )

    expected = {
        'date': '2014',
        'degree_type': 'other',
        'institutions': [
            {
                'curated_relation': True,
                'name': 'Nice U.',
                'record': {
                    '$ref': 'http://localhost:5000/api/institutions/903069',
                },
            },
            {
                'curated_relation': True,
                'name': 'Cote d\'Azur Observ., Nice',
                'record': {
                    '$ref': 'http://localhost:5000/api/institutions/904125',
                },
            },
        ],
    }
    result = hep.do(create_record(snippet))

    assert validate(result['thesis_info'], subschema) is None
    assert expected == result['thesis_info']

    expected = {
        'b': 'Thesis',
        'c': [
            'Nice U.',
            'Cote d\'Azur Observ., Nice',
        ],
        'd': '2014',
    }
    result = hep2marc.do(result)

    assert expected == result['502']


def test_thesis_info_from_500__a_and_502__b_c_d():
    schema = load_schema('hep')
    subschema = schema['properties']['thesis_info']

    snippet = (  # record/1517362
        '<record>'
        '  <datafield tag="500" ind1=" " ind2=" ">'
        '    <subfield code="a">Presented on 2015-11-27</subfield>'
        '  </datafield>'
        '  <datafield tag="502" ind1=" " ind2=" ">'
        '    <subfield code="b">PhD</subfield>'
        '    <subfield code="c">Siegen U.</subfield>'
        '    <subfield code="d">2017</subfield>'
        '  </datafield>'
        '<record>'
    )

    expected = {
        'date': '2017',
        'defense_date': '2015-11-27',
        'degree_type': 'phd',
        'institutions': [
            {'name': 'Siegen U.'},
        ],
    }
    result = hep.do(create_record(snippet))

    assert validate(result['thesis_info'], subschema) is None
    assert expected == result['thesis_info']

    expected_500 = [
        {'a': 'Presented on 2015-11-27'},
    ]
    expected_502 = {
        'b': 'PhD',
        'c': [
            'Siegen U.',
        ],
        'd': '2017',
    }
    result = hep2marc.do(result)

    assert expected_500 == result['500']
    assert expected_502 == result['502']


def test_abstracts_from_520__a_9():
    schema = load_schema('hep')
    subschema = schema['properties']['abstracts']

    snippet = (  # record/1346798
        '<datafield tag="520" ind1=" " ind2=" ">  <subfield'
        ' code="9">Springer</subfield>  <subfield code="a">We study a notion of'
        ' non-commutative integration, in the spirit of modular spectral'
        ' triples, for the quantum group SU$_{q}$ (2). In particular we define'
        ' the non-commutative integral as the residue at the spectral dimension'
        ' of a zeta function, which is constructed using a Dirac operator and a'
        ' weight. We consider the Dirac operator introduced by Kaad and Senior'
        ' and a family of weights depending on two parameters, which are'
        ' related to the diagonal automorphisms of SU$_{q}$ (2). We show that,'
        ' after fixing one of the parameters, the non-commutative integral'
        ' coincides with the Haar state of SU$_{q}$ (2). Moreover we can impose'
        ' an additional condition on the zeta function, which also fixes the'
        ' second parameter. For this unique choice the spectral dimension'
        ' coincides with the classical dimension.</subfield></datafield>'
    )

    expected = [
        {
            'source': 'Springer',
            'value': (
                'We study a notion of non-commutative integration, in the'
                ' spirit of modular spectral triples, for the quantum group'
                ' SU$_{q}$ (2). In particular we define the non-commutative'
                ' integral as the residue at the spectral dimension of a zeta'
                ' function, which is constructed using a Dirac operator and a'
                ' weight. We consider the Dirac operator introduced by Kaad and'
                ' Senior and a family of weights depending on two parameters,'
                ' which are related to the diagonal automorphisms of SU$_{q}$'
                ' (2). We show that, after fixing one of the parameters, the'
                ' non-commutative integral coincides with the Haar state of'
                ' SU$_{q}$ (2). Moreover we can impose an additional condition'
                ' on the zeta function, which also fixes the second parameter.'
                ' For this unique choice the spectral dimension coincides with'
                ' the classical dimension.'
            ),
        },
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['abstracts'], subschema) is None
    assert expected == result['abstracts']

    expected = [
        {
            '9': 'Springer',
            'a': (
                'We study a notion of non-commutative integration, in the'
                ' spirit of modular spectral triples, for the quantum group'
                ' SU$_{q}$ (2). In particular we define the non-commutative'
                ' integral as the residue at the spectral dimension of a zeta'
                ' function, which is constructed using a Dirac operator and a'
                ' weight. We consider the Dirac operator introduced by Kaad and'
                ' Senior and a family of weights depending on two parameters,'
                ' which are related to the diagonal automorphisms of SU$_{q}$'
                ' (2). We show that, after fixing one of the parameters, the'
                ' non-commutative integral coincides with the Haar state of'
                ' SU$_{q}$ (2). Moreover we can impose an additional condition'
                ' on the zeta function, which also fixes the second parameter.'
                ' For this unique choice the spectral dimension coincides with'
                ' the classical dimension.'
            ),
        },
    ]
    result = hep2marc.do(result)

    assert expected == result['520']


def test_abstracts_from_520__double_a():
    schema = load_schema('hep')
    subschema = schema['properties']['abstracts']

    snippet = (  # record/1297699
        '<datafield tag="520" ind1=" " ind2=" ">  <subfield code="a">$D$ $K$'
        ' scattering and the $D_s$ spectrum from lattice QCD 520__</subfield> '
        ' <subfield code="a">We present results from Lattice QCD calculations'
        ' of the low-lying charmed-strange meson spectrum using two types of'
        ' Clover-Wilson lattices. In addition to quark-antiquark interpolating'
        ' fields we also consider meson-meson interpolators corresponding to'
        ' D-meson kaon scattering states. To calculate the all-to-all'
        ' propagation necessary for the backtracking loops we use the'
        ' (stochastic) distillation technique. For the charm quark we use the'
        ' Fermilab method. Results for the $J^P=0^+$ $D_{s0}^*(2317)$'
        ' charmed-strange meson are presented.</subfield></datafield>'
    )

    expected = [
        {'value': '$D$ $K$ scattering and the $D_s$ spectrum from lattice QCD 520__'},
        {
            'value': (
                'We present results from Lattice QCD calculations of the'
                ' low-lying charmed-strange meson spectrum using two types of'
                ' Clover-Wilson lattices. In addition to quark-antiquark'
                ' interpolating fields we also consider meson-meson'
                ' interpolators corresponding to D-meson kaon scattering'
                ' states. To calculate the all-to-all propagation necessary for'
                ' the backtracking loops we use the (stochastic) distillation'
                ' technique. For the charm quark we use the Fermilab method.'
                ' Results for the $J^P=0^+$ $D_{s0}^*(2317)$ charmed-strange'
                ' meson are presented.'
            )
        },
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['abstracts'], subschema) is None
    assert expected == result['abstracts']

    expected = [
        {'a': '$D$ $K$ scattering and the $D_s$ spectrum from lattice QCD 520__'},
        {
            'a': (
                'We present results from Lattice QCD calculations of the'
                ' low-lying charmed-strange meson spectrum using two types of'
                ' Clover-Wilson lattices. In addition to quark-antiquark'
                ' interpolating fields we also consider meson-meson'
                ' interpolators corresponding to D-meson kaon scattering'
                ' states. To calculate the all-to-all propagation necessary for'
                ' the backtracking loops we use the (stochastic) distillation'
                ' technique. For the charm quark we use the Fermilab method.'
                ' Results for the $J^P=0^+$ $D_{s0}^*(2317)$ charmed-strange'
                ' meson are presented.'
            )
        },
    ]
    result = hep2marc.do(result)

    assert expected == result['520']


def test_abstracts_from_520__h_9():
    snippet = (  # record/1079585
        '<datafield tag="520" ind1=" " ind2=" ">  <subfield'
        ' code="9">HEPDATA</subfield>  <subfield code="h">CERN-SPS.'
        ' Measurements of the spectra of positively charged kaons in'
        ' proton-carbon interactions at a beam momentum of 31 GeV/c. The'
        ' analysis is based on the full set of data collected in 2007 using a'
        ' 4% nuclear interaction length graphite target. Charged pion spectra'
        ' taken using the same data set are compared with the kaon'
        ' spectra.</subfield></datafield>'
    )

    result = hep.do(create_record(snippet))

    assert 'abstracts' not in result


def test_abstracts_from_double_520__a_9_reorders_fields():
    schema = load_schema('hep')
    subschema = schema['properties']['abstracts']

    snippet = (  # record/1634941
        '<record>  <datafield tag="520" ind1=" " ind2=" ">    <subfield'
        ' code="a">The origin of extragalactic magnetic fields is still poorly'
        ' understood. Based on a dedicated suite of cosmological'
        ' magneto-hydrodynamical simulations with the ENZO code we have'
        ' performed a survey of different models that may have caused'
        ' present-day magnetic fields in galaxies and galaxy clusters. The'
        ' outcomes of these models differ in cluster outskirts, filaments,'
        ' sheets and voids and we use these simulations to find observational'
        ' signatures of magnetogenesis. With these simulations, we predict the'
        ' signal of extragalactic magnetic fields in radio observations of'
        ' synchrotron emission from the cosmic web, in Faraday Rotation, in the'
        ' propagation of Ultra High Energy Cosmic Rays, in the polarized signal'
        ' from Fast Radio Bursts at cosmological distance and in spectra of'
        ' distant blazars. In general, primordial scenarios in which'
        ' present-day magnetic fields originate from the amplification of weak'
        ' (&lt;nG) uniform seed fields result more homogeneous and relatively'
        ' easier to observe magnetic fields than than astrophysical scenarios,'
        ' in which present-day fields are the product of feedback processes'
        ' triggered by stars and active galaxies. In the near future the best'
        ' evidence for the origin of cosmic magnetic fields will most likely'
        ' come from a combination of synchrotron emission and Faraday Rotation'
        ' observed at the periphery of large-scale structures.</subfield>   '
        ' <subfield code="9">arXiv</subfield>  </datafield>  <datafield'
        ' tag="520" ind1=" " ind2=" ">    <subfield code="a">The origin of'
        ' extragalactic magnetic fields is still poorly understood. Based on a'
        ' dedicated suite of cosmological magneto-hydrodynamical simulations'
        ' with the ENZO code we have performed a survey of different models'
        ' that may have caused present-day magnetic fields in galaxies and'
        ' galaxy clusters. The outcomes of these models differ in cluster'
        ' outskirts, filaments, sheets and voids and we use these simulations'
        ' to find observational signatures of magnetogenesis. With these'
        ' simulations, we predict the signal of extragalactic magnetic fields'
        ' in radio observations of synchrotron emission from the cosmic web, in'
        ' Faraday rotation, in the propagation of ultra high energy cosmic'
        ' rays, in the polarized signal from fast radio bursts at cosmological'
        ' distance and in spectra of distant blazars. In general, primordial'
        ' scenarios in which present-day magnetic fields originate from the'
        ' amplification of weak (⩽$\\rm nG$ ) uniform seed fields result in'
        ' more homogeneous and relatively easier to observe magnetic fields'
        ' than astrophysical scenarios, in which present-day fields are the'
        ' product of feedback processes triggered by stars and active galaxies.'
        ' In the near future the best evidence for the origin of cosmic'
        ' magnetic fields will most likely come from a combination of'
        ' synchrotron emission and Faraday rotation observed at the periphery'
        ' of large-scale structures.</subfield>    <subfield'
        ' code="9">IOP</subfield>  </datafield></record>'
    )

    expected = [
        {
            'source': 'IOP',
            'value': (
                u'The origin of extragalactic magnetic fields is still poorly'
                u' understood. Based on a dedicated suite of cosmological'
                u' magneto-hydrodynamical simulations with the ENZO code we'
                u' have performed a survey of different models that may have'
                u' caused present-day magnetic fields in galaxies and galaxy'
                u' clusters. The outcomes of these models differ in cluster'
                u' outskirts, filaments, sheets and voids and we use these'
                u' simulations to find observational signatures of'
                u' magnetogenesis. With these simulations, we predict the'
                u' signal of extragalactic magnetic fields in radio'
                u' observations of synchrotron emission from the cosmic web, in'
                u' Faraday rotation, in the propagation of ultra high energy'
                u' cosmic rays, in the polarized signal from fast radio bursts'
                u' at cosmological distance and in spectra of distant blazars.'
                u' In general, primordial scenarios in which present-day'
                u' magnetic fields originate from the amplification of weak'
                u' (⩽$\\rm nG$ ) uniform seed fields result in more homogeneous'
                u' and relatively easier to observe magnetic fields than'
                u' astrophysical scenarios, in which present-day fields are the'
                u' product of feedback processes triggered by stars and active'
                u' galaxies. In the near future the best evidence for the'
                u' origin of cosmic magnetic fields will most likely come from'
                u' a combination of synchrotron emission and Faraday rotation'
                u' observed at the periphery of large-scale structures.'
            ),
        },
        {
            'source': 'arXiv',
            'value': (
                'The origin of extragalactic magnetic fields is still poorly'
                ' understood. Based on a dedicated suite of cosmological'
                ' magneto-hydrodynamical simulations with the ENZO code we have'
                ' performed a survey of different models that may have caused'
                ' present-day magnetic fields in galaxies and galaxy clusters.'
                ' The outcomes of these models differ in cluster outskirts,'
                ' filaments, sheets and voids and we use these simulations to'
                ' find observational signatures of magnetogenesis. With these'
                ' simulations, we predict the signal of extragalactic magnetic'
                ' fields in radio observations of synchrotron emission from the'
                ' cosmic web, in Faraday Rotation, in the propagation of Ultra'
                ' High Energy Cosmic Rays, in the polarized signal from Fast'
                ' Radio Bursts at cosmological distance and in spectra of'
                ' distant blazars. In general, primordial scenarios in which'
                ' present-day magnetic fields originate from the amplification'
                ' of weak (<nG) uniform seed fields result more homogeneous and'
                ' relatively easier to observe magnetic fields than than'
                ' astrophysical scenarios, in which present-day fields are the'
                ' product of feedback processes triggered by stars and active'
                ' galaxies. In the near future the best evidence for the origin'
                ' of cosmic magnetic fields will most likely come from a'
                ' combination of synchrotron emission and Faraday Rotation'
                ' observed at the periphery of large-scale structures.'
            ),
        },
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['abstracts'], subschema) is None
    assert expected == result['abstracts']

    expected = [
        {
            '9': 'IOP',
            'a': (
                u'The origin of extragalactic magnetic fields is still poorly'
                u' understood. Based on a dedicated suite of cosmological'
                u' magneto-hydrodynamical simulations with the ENZO code we'
                u' have performed a survey of different models that may have'
                u' caused present-day magnetic fields in galaxies and galaxy'
                u' clusters. The outcomes of these models differ in cluster'
                u' outskirts, filaments, sheets and voids and we use these'
                u' simulations to find observational signatures of'
                u' magnetogenesis. With these simulations, we predict the'
                u' signal of extragalactic magnetic fields in radio'
                u' observations of synchrotron emission from the cosmic web, in'
                u' Faraday rotation, in the propagation of ultra high energy'
                u' cosmic rays, in the polarized signal from fast radio bursts'
                u' at cosmological distance and in spectra of distant blazars.'
                u' In general, primordial scenarios in which present-day'
                u' magnetic fields originate from the amplification of weak'
                u' (⩽$\\rm nG$ ) uniform seed fields result in more homogeneous'
                u' and relatively easier to observe magnetic fields than'
                u' astrophysical scenarios, in which present-day fields are the'
                u' product of feedback processes triggered by stars and active'
                u' galaxies. In the near future the best evidence for the'
                u' origin of cosmic magnetic fields will most likely come from'
                u' a combination of synchrotron emission and Faraday rotation'
                u' observed at the periphery of large-scale structures.'
            ),
        },
        {
            '9': 'arXiv',
            'a': (
                'The origin of extragalactic magnetic fields is still poorly'
                ' understood. Based on a dedicated suite of cosmological'
                ' magneto-hydrodynamical simulations with the ENZO code we have'
                ' performed a survey of different models that may have caused'
                ' present-day magnetic fields in galaxies and galaxy clusters.'
                ' The outcomes of these models differ in cluster outskirts,'
                ' filaments, sheets and voids and we use these simulations to'
                ' find observational signatures of magnetogenesis. With these'
                ' simulations, we predict the signal of extragalactic magnetic'
                ' fields in radio observations of synchrotron emission from the'
                ' cosmic web, in Faraday Rotation, in the propagation of Ultra'
                ' High Energy Cosmic Rays, in the polarized signal from Fast'
                ' Radio Bursts at cosmological distance and in spectra of'
                ' distant blazars. In general, primordial scenarios in which'
                ' present-day magnetic fields originate from the amplification'
                ' of weak (<nG) uniform seed fields result more homogeneous and'
                ' relatively easier to observe magnetic fields than than'
                ' astrophysical scenarios, in which present-day fields are the'
                ' product of feedback processes triggered by stars and active'
                ' galaxies. In the near future the best evidence for the origin'
                ' of cosmic magnetic fields will most likely come from a'
                ' combination of synchrotron emission and Faraday Rotation'
                ' observed at the periphery of large-scale structures.'
            ),
        },
    ]
    result = hep2marc.do(result)

    assert expected == result['520']


def test_funding_info_from_536__a_c_f_0():
    schema = load_schema('hep')
    subschema = schema['properties']['funding_info']

    snippet = (  # record/1508869
        '<datafield tag="536" ind1=" " ind2=" ">  <subfield'
        ' code="0">G:(EU-Grant)317089</subfield>  <subfield code="a">GATIS -'
        ' Gauge Theory as an Integrable System (317089)</subfield>  <subfield'
        ' code="c">317089</subfield>  <subfield'
        ' code="f">FP7-PEOPLE-2012-ITN</subfield></datafield>'
    )

    expected = [
        {
            'agency': 'GATIS - Gauge Theory as an Integrable System (317089)',
            'grant_number': '317089',
            'project_number': 'FP7-PEOPLE-2012-ITN',
        },
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['funding_info'], subschema) is None
    assert expected == result['funding_info']

    expected = [
        {
            'a': 'GATIS - Gauge Theory as an Integrable System (317089)',
            'c': '317089',
            'f': 'FP7-PEOPLE-2012-ITN',
        },
    ]
    result = hep2marc.do(result)

    assert expected == result['536']


def test_license_from_540__a_3():
    schema = load_schema('hep')
    subschema = schema['properties']['license']

    snippet = (  # record/120203
        '<datafield tag="540" ind1=" " ind2=" ">'
        '  <subfield code="3">Article</subfield>'
        '  <subfield code="a">OA</subfield>'
        '</datafield>'
    )

    expected = [
        {
            'license': 'OA',
            'material': 'publication',
        },
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['license'], subschema) is None
    assert expected == result['license']

    expected = [
        {
            '3': 'publication',
            'a': 'OA',
        },
    ]
    result = hep2marc.do(result)

    assert expected == result['540']


def test_license_from_540__a_u_3():
    schema = load_schema('hep')
    subschema = schema['properties']['license']

    snippet = (  # record/1184984
        '<datafield tag="540" ind1=" " ind2=" ">'
        '  <subfield code="3">Publication</subfield>'
        '  <subfield code="a">CC-BY-3.0</subfield>'
        '  <subfield'
        ' code="u">http://creativecommons.org/licenses/by/3.0/</subfield>'
        '</datafield>'
    )

    expected = [
        {
            'license': 'CC-BY-3.0',
            'material': 'publication',
            'url': 'http://creativecommons.org/licenses/by/3.0/',
        },
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['license'], subschema) is None
    assert expected == result['license']

    expected = [
        {
            '3': 'publication',
            'a': 'CC-BY-3.0',
            'u': 'http://creativecommons.org/licenses/by/3.0/',
        },
    ]
    result = hep2marc.do(result)

    assert expected == result['540']


def test_license_from_540__a_u_3_handles_preprint():
    schema = load_schema('hep')
    subschema = schema['properties']['license']

    snippet = (  # record/1682011
        '<datafield tag="540" ind1=" " ind2=" ">'
        '  <subfield code="3">preprint</subfield>'
        '  <subfield code="a">arXiv nonexclusive-distrib 1.0</subfield>'
        '  <subfield'
        ' code="u">http://arxiv.org/licenses/nonexclusive-distrib/1.0/</subfield>'
        '</datafield>'
    )

    expected = [
        {
            'license': 'arXiv nonexclusive-distrib 1.0',
            'material': 'preprint',
            'url': 'http://arxiv.org/licenses/nonexclusive-distrib/1.0/',
        },
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['license'], subschema) is None
    assert expected == result['license']

    expected = [
        {
            'a': 'arXiv nonexclusive-distrib 1.0',
            '3': 'preprint',
            'u': 'http://arxiv.org/licenses/nonexclusive-distrib/1.0/',
        },
    ]
    result = hep2marc.do(result)

    assert expected == result['540']


def test_license_from_540__double_a_u():
    schema = load_schema('hep')
    subschema = schema['properties']['license']

    snippet = (  # record/1414671
        '<datafield tag="540" ind1=" " ind2=" ">'
        '  <subfield code="a">Open Access</subfield>'
        '  <subfield code="a">CC-BY-3.0</subfield>'
        '  <subfield'
        ' code="u">http://creativecommons.org/licenses/by/3.0/</subfield>'
        '</datafield>'
    )

    expected = [
        {
            'license': 'CC-BY-3.0',
            'url': 'http://creativecommons.org/licenses/by/3.0/',
        },
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['license'], subschema) is None
    assert expected == result['license']

    expected = [
        {
            'a': 'CC-BY-3.0',
            'u': 'http://creativecommons.org/licenses/by/3.0/',
        },
    ]
    result = hep2marc.do(result)

    assert expected == result['540']


def test_copyright_from_542__d_e_g():
    schema = load_schema('hep')
    subschema = schema['properties']['copyright']

    snippet = (  # record/1511489
        '<datafield tag="542" ind1=" " ind2=" ">'
        '  <subfield code="d">American Physical Society</subfield>'
        '  <subfield code="g">2017</subfield>'
        '  <subfield code="e">Article</subfield>'
        '</datafield>'
    )

    expected = [
        {
            'holder': 'American Physical Society',
            'material': 'publication',
            'year': 2017,
        },
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['copyright'], subschema) is None
    assert expected == result['copyright']

    expected = [
        {
            'd': 'American Physical Society',
            'e': 'Article',
            'g': 2017,
        },
    ]
    result = hep2marc.do(result)

    assert expected == result['542']


def test_copyright_from_542__d_g_3():
    schema = load_schema('hep')
    subschema = schema['properties']['copyright']

    snippet = (  # record/1255327
        '<datafield tag="542" ind1=" " ind2=" ">'
        '  <subfield code="3">Article</subfield>'
        '  <subfield code="d">American Physical Society</subfield>'
        '  <subfield code="g">2014</subfield>'
        '</datafield>'
    )

    expected = [
        {
            'holder': 'American Physical Society',
            'material': 'publication',
            'year': 2014,
        },
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['copyright'], subschema) is None
    assert expected == result['copyright']

    expected = [
        {
            'd': 'American Physical Society',
            'e': 'Article',
            'g': 2014,
        },
    ]
    result = hep2marc.do(result)

    assert expected == result['542']


def test_copyright_from_542__d_g_3_with_weird_material():
    schema = load_schema('hep')
    subschema = schema['properties']['copyright']

    snippet = (  # record/773620
        '<datafield tag="542" ind1=" " ind2=" ">'
        '  <subfield code="3">Published thesis as a book</subfield>'
        '  <subfield code="d">Shaker Verlag</subfield>'
        '  <subfield code="g">2007</subfield>'
        '</datafield>'
    )

    expected = [
        {
            'holder': 'Shaker Verlag',
            'material': 'publication',
            'year': 2007,
        },
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['copyright'], subschema) is None
    assert expected == result['copyright']

    expected = [
        {
            'd': 'Shaker Verlag',
            'e': 'Article',
            'g': 2007,
        },
    ]
    result = hep2marc.do(result)

    assert expected == result['542']


def test_private_notes_from_595__a_9():
    schema = load_schema('hep')
    subschema = schema['properties']['_private_notes']

    snippet = (  # record/109310
        '<datafield tag="595" ind1=" " ind2=" ">'
        '  <subfield code="9">SPIRES-HIDDEN</subfield>'
        '  <subfield code="a">Title changed from ALLCAPS</subfield>'
        '</datafield>'
    )

    expected = [
        {
            'source': 'SPIRES-HIDDEN',
            'value': 'Title changed from ALLCAPS',
        },
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['_private_notes'], subschema) is None
    assert expected == result['_private_notes']

    expected = [
        {
            '9': 'SPIRES-HIDDEN',
            'a': 'Title changed from ALLCAPS',
        },
    ]
    result = hep2marc.do(result)

    assert expected == result['595']


def test_private_notes_from_595__double_a_9():
    schema = load_schema('hep')
    subschema = schema['properties']['_private_notes']

    snippet = (  # record/109310
        '<datafield tag="595" ind1=" " ind2=" ">  <subfield'
        ' code="9">SPIRES-HIDDEN</subfield>  <subfield code="a">TeXtitle from'
        ' script</subfield>  <subfield code="a">no affiliation (not clear pn'
        ' the fulltext)</subfield></datafield>'
    )

    expected = [
        {
            'source': 'SPIRES-HIDDEN',
            'value': 'TeXtitle from script',
        },
        {
            'source': 'SPIRES-HIDDEN',
            'value': 'no affiliation (not clear pn the fulltext)',
        },
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['_private_notes'], subschema) is None
    assert expected == result['_private_notes']

    expected = [
        {
            '9': 'SPIRES-HIDDEN',
            'a': 'TeXtitle from script',
        },
        {
            '9': 'SPIRES-HIDDEN',
            'a': 'no affiliation (not clear pn the fulltext)',
        },
    ]
    result = hep2marc.do(result)

    assert expected == result['595']


def test_private_notes_from_595__a_9_and_595__double_a_9():
    schema = load_schema('hep')
    subschema = schema['properties']['_private_notes']

    snippet = (  # record/109310
        '<record>  <datafield tag="595" ind1=" " ind2=" ">    <subfield'
        ' code="9">SPIRES-HIDDEN</subfield>    <subfield code="a">Title changed'
        ' from ALLCAPS</subfield>  </datafield>  <datafield tag="595" ind1=" "'
        ' ind2=" ">    <subfield code="9">SPIRES-HIDDEN</subfield>    <subfield'
        ' code="a">TeXtitle from script</subfield>    <subfield code="a">no'
        ' affiliation (not clear pn the fulltext)</subfield> '
        ' </datafield></record>'
    )

    expected = [
        {
            'source': 'SPIRES-HIDDEN',
            'value': 'Title changed from ALLCAPS',
        },
        {
            'source': 'SPIRES-HIDDEN',
            'value': 'TeXtitle from script',
        },
        {
            'source': 'SPIRES-HIDDEN',
            'value': 'no affiliation (not clear pn the fulltext)',
        },
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['_private_notes'], subschema) is None
    assert expected == result['_private_notes']

    expected = [
        {
            '9': 'SPIRES-HIDDEN',
            'a': 'Title changed from ALLCAPS',
        },
        {
            '9': 'SPIRES-HIDDEN',
            'a': 'TeXtitle from script',
        },
        {
            '9': 'SPIRES-HIDDEN',
            'a': 'no affiliation (not clear pn the fulltext)',
        },
    ]
    result = hep2marc.do(result)

    assert expected == result['595']


def test_private_notes_from_595_Ha():
    schema = load_schema('hep')
    subschema = schema['properties']['_private_notes']

    snippet = (  # record/1514389
        '<datafield tag="595" ind1=" " ind2="H">  <subfield'
        ' code="a">affiliations à corriger, voir avec Mathieu -'
        ' Dominique</subfield></datafield>'
    )

    expected = [
        {
            'source': 'HAL',
            'value': u'affiliations à corriger, voir avec Mathieu - Dominique',
        },
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['_private_notes'], subschema) is None
    assert expected == result['_private_notes']

    expected = [
        {'a': u'affiliations à corriger, voir avec Mathieu - Dominique'},
    ]
    result = hep2marc.do(result)

    assert expected == result['595_H']


def test_desy_bookkeeping_from_multiple_595_Da_d_s():
    schema = load_schema('hep')
    subschema = schema['properties']['_desy_bookkeeping']

    snippet = (  # record/1513161
        '<record>'
        '  <datafield tag="595" ind1=" " ind2="D">'
        '    <subfield code="a">8</subfield>'
        '    <subfield code="d">2017-02-17</subfield>'
        '    <subfield code="s">abs</subfield>'
        '  </datafield>'
        '  <datafield tag="595" ind1=" " ind2="D">'
        '    <subfield code="a">8</subfield>'
        '    <subfield code="d">2017-02-19</subfield>'
        '    <subfield code="s">printed</subfield>'
        '  </datafield>'
        '</record>'
    )

    expected = [
        {'expert': '8', 'date': '2017-02-17', 'status': 'abs'},
        {'expert': '8', 'date': '2017-02-19', 'status': 'printed'},
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['_desy_bookkeeping'], subschema) is None
    assert expected == result['_desy_bookkeeping']

    expected = [
        {'a': '8', 'd': '2017-02-17', 's': 'abs'},
        {'a': '8', 'd': '2017-02-19', 's': 'printed'},
    ]
    result = hep2marc.do(result)

    assert expected == result['595_D']


def test_desy_bookkeeping_from_595_D_double_a_d_s():
    schema = load_schema('hep')
    subschema = schema['properties']['_desy_bookkeeping']

    snippet = (  # record/558693
        '<datafield tag="595" ind1=" " ind2="D">'
        '  <subfield code="d">2016-07-23</subfield>'
        '  <subfield code="a">E</subfield>'
        '  <subfield code="s">final</subfield>'
        '  <subfield code="a">E</subfield>'
        '</datafield>'
    )

    expected = [
        {
            'expert': 'E',
            'date': '2016-07-23',
            'status': 'final',
        },
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['_desy_bookkeeping'], subschema) is None
    assert expected == result['_desy_bookkeeping']

    expected = [
        {
            'a': 'E',
            'd': '2016-07-23',
            's': 'final',
        },
    ]
    result = hep2marc.do(result)

    assert expected == result['595_D']


def test_export_to_from_595__c_cds():
    schema = load_schema('hep')
    subschema = schema['properties']['_export_to']

    snippet = (  # record/1513006
        '<datafield tag="595" ind1=" " ind2=" ">'
        '  <subfield code="c">CDS</subfield>'
        '</datafield>'
    )

    expected = {'CDS': True}
    result = hep.do(create_record(snippet))

    assert validate(result['_export_to'], subschema) is None
    assert expected == result['_export_to']

    expected = [{'c': 'CDS'}]
    result = hep2marc.do(result)

    assert expected == result['595']


def test_export_to_from_595__c_hal():
    schema = load_schema('hep')
    subschema = schema['properties']['_export_to']

    snippet = (  # record/1623281
        '<datafield tag="595" ind1=" " ind2=" ">'
        '  <subfield code="c">HAL</subfield>'
        '</datafield>'
    )

    expected = {'HAL': True}
    result = hep.do(create_record(snippet))

    assert validate(result['_export_to'], subschema) is None
    assert expected == result['_export_to']

    expected = [
        {'c': 'HAL'},
    ]
    result = hep2marc.do(result)

    assert expected == result['595']


def test_export_to_from_595__c_not_hal():
    schema = load_schema('hep')
    subschema = schema['properties']['_export_to']

    snippet = (  # record/1512891
        '<datafield tag="595" ind1=" " ind2=" ">'
        '  <subfield code="c">not HAL</subfield>'
        '</datafield>'
    )

    expected = {'HAL': False}
    result = hep.do(create_record(snippet))

    assert validate(result['_export_to'], subschema) is None
    assert expected == result['_export_to']

    expected = [{'c': 'not HAL'}]
    result = hep2marc.do(result)

    assert expected == result['595']


def test_export_to_from_595__double_c():
    schema = load_schema('hep')
    subschema = schema['properties']['_export_to']

    snippet = (  # record/1512843
        '<datafield tag="595" ind1=" " ind2=" ">'
        '  <subfield code="c">CDS</subfield>'
        '  <subfield code="c">not HAL</subfield>'
        '</datafield>'
    )

    expected = {
        'CDS': True,
        'HAL': False,
    }
    result = hep.do(create_record(snippet))

    assert validate(result['_export_to'], subschema) is None
    assert expected == result['_export_to']

    expected = [
        {'c': 'CDS'},
        {'c': 'not HAL'},
    ]
    result = hep2marc.do(result)

    assert expected == result['595']
