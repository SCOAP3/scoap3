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

"""DoJSON common rules."""

from __future__ import absolute_import, division, print_function

import re
from datetime import datetime

from dojson import utils
from flask import current_app
from inspire_schemas.api import load_schema
from inspire_schemas.utils import classify_field
from inspire_utils.date import PartialDate, earliest_date
from inspire_utils.helpers import force_list, maybe_int
from six.moves import urllib

from inspire_dojson.conferences.model import conferences
from inspire_dojson.data.model import data
from inspire_dojson.experiments.model import experiments
from inspire_dojson.hep.model import hep, hep2marc
from inspire_dojson.hepnames.model import hepnames, hepnames2marc
from inspire_dojson.institutions.model import institutions
from inspire_dojson.journals.model import journals
from inspire_dojson.utils import (
    force_single_element,
    get_recid_from_ref,
    get_record_ref,
)

IS_INTERNAL_UID = re.compile(r'^(inspire:uid:)?\d{5}$')
IS_ORCID = re.compile(r'^(orcid:)?\d{4}-\d{4}-\d{4}-\d{3}[0-9X]$')

WEBLINKS = {
    '00070': 'International Journal of Mathematics Server',
    '00108': 'J.Knot Theor.Ramifications',
    '00140': 'Heavy Ion Physics Server',
    '00145': 'Int. J. Math. Math. Sci. Server',
    '00154': 'J. Nonlin. Math. Phys. Server',
    '00181': 'Spektrum der Wissenschaft Server',
    '00182': 'SLAC Beam Line Server',
    '00201': 'ICFA Instrum.Bull. Server',
    '00203': 'Adv. Theor. Math. Phys. Server',
    '00211': 'KFZ Nachrichten Server',
    '00222': 'Living Reviews in Relativity Server',
    '00228': 'Nonlin. Phenom. Complex Syst. Server',
    '00238': 'Math. Phys. Anal. Geom. Server',
    '00256': 'Geometry and Topology Server',
    '00257': 'Electron.J.Diff.Eq. Server',
    '00264': 'Entropy Server',
    '00286': 'HEP Lib.Web. Server',
    '00327': 'World Sci.Lect.Notes Phys. Server',
    '00357': 'Cent. Eur. J. Phys. Server',
    '00372': 'Romanian Astronomical Journal Server',
    '00376': 'ICFA Server',
    '00411': 'Les Houches Lect. Notes Server',
    '00436': 'Int. J. Geom. Meth. Mod. Phys. Server',
    '00438': 'Phys.Part.Nucl.Lett. Server',
    '00462': 'Journal of Physics Conference Series Server',
    '00466': 'Prog.Phys. Server',
    '00480': 'SIGMA Server',
    '00484': 'Electron. J. Theor. Phys. Server',
    'AAEJA': 'Astronomy and Astrophysics Server',
    'AASRE': 'Astronomy and Astrophysics Review Server',
    'ADSABS': 'ADS Abstract Service',
    'ADSABS2': 'ADS Abstract Service',
    'AFLBD': 'Annales De La Fondation Louis De Broglie Server',
    'AHPAA': 'Ann. Henri Poincare Server',
    'AIPCONF': 'AIP Conference Server',
    'AJPIA': 'Am.J.Phys. Server',
    'ALETE': 'Astronomy Letters Server',
    'ANJOA': 'Astron.J. Server',
    'ANPYA': 'Annalen der Physik Server',
    'APCPC': 'AIP Conference Server',
    'APHYE': 'Astroparticle Physics Server',
    'APNYA': 'Ann. Phys. Server',
    'APPLA': 'Applied Physics Letter Server',
    'APPOA': 'Acta Physica Polonica Server',
    'APSSB': 'Astrophys. Space Sci. Server',
    'APSVC': 'Acta Physica Slovaca Server',
    'ARAAA': 'Annual Review of Astronomy and Astrophysics Server',
    'ARNUA': 'Annual Review of Nuclear and Particle Science',
    'ARTHF': 'Algebras and Representation Theory Server',
    'ARXERR': 'Erratum from arXiv.org server',
    'ASJOA': 'Astrophysical Journal Server',
    'ATLAS': 'ATLAS Notes from CERN server',
    'ATMP': 'ATMP Server',
    'ATPYA': 'Astrophysics Server',
    'ATROE': 'Astronomy Reports Server',
    'AUJPA': 'Austral.J.Phys. Server',
    'BABAR': 'Postscript from BABAR [BABAR Collaborators Only]',
    'BABARWEB': 'BaBar Publications Database',
    'BABARWEBP': 'BaBar Password Protected Publications Database',
    'BJPHE': 'Braz. J. Phys. Server',
    'BNL': 'Brookhaven Document Server',
    'BOOK-REVIEW': 'Review of this book',
    'BOOKCL': 'SLAC BOOKS Database',
    'BOOKREVIEW': 'Book review/article',
    'BOOKS': 'SLAC BOOKS Database',
    'BROOKHAVEN': 'Brookhaven Document Server',
    'C00-02-07': 'CHEP2000 Server',
    'C00-06-26.2': 'EPAC 2000 Server',
    'C00-09-14': 'QFTHEP00 Server',
    'C00-10-09.4': 'PCAPAC00 Server',
    'C01-01-20.1': 'Moriond Server',
    'C01-06-18.1': 'PAC01 Server',
    'C01-06-25.8': 'BeamBeam01 Server',
    'C01-07-26': 'MENU2001 Server',
    'C01-08-07': 'ICRC01 Server',
    'C01-08-20.1': 'FEL 2001 Server',
    'C01-09-06.1': 'QFTHEP01 Server',
    'C01-10-02.1': 'DESY Conference Server',
    'C02-03-18.1': 'Durham Conference Server',
    'C02-06-17.2': 'SUSY02 Server',
    'C02-09-22': 'Hadron Structure 2002 Server',
    'C02-10-15.1': 'Aguas de Lindoia 2002 Server',
    'C03-07-31': 'ICRC Server',
    'C04-04-14': 'DIS04 Server',
    'C04-04-19.4': 'ECLOUD04 Server',
    'C04-11-08.2': 'HHH-2004 Server',
    'C05-03-22': 'Phystat05 Conference Server',
    'C05-09-12': 'Phystat05 Conference Server',
    'C05-09-12.10': 'CERN Conference Server',
    'C05-10-17': 'ICATPP9 Conference Server',
    'C06-09-16.1': 'Yalta06 Conference Server',
    'C07-04-16': 'DIS2007 Conference Server',
    'C07-05-21.2': 'Blois07 Server',
    'C91-08-05': 'SLAC Summer Inst. 1991 Server',
    'C92-07-13.1': 'SLAC Summer Inst. 1992 Server',
    'C93-07-26': 'SLAC Summer Inst. 1993 Server',
    'C95-07-10.2': 'SLAC Summer Inst 1995 Server',
    'C95-10-29': 'ICALEPCS\'95 Server',
    'C97-09-04.1': 'QFTHEP\'97 Server',
    'C97-10-13': 'IWAA\'97 Server',
    'C98-06-22': 'EPAC98 Server',
    'C99-03-29': 'JACoW PAC99 Server',
    'C99-04-06': 'ANL Conference Server',
    'C99-04-12.3': 'LHC 99 JACoW Server',
    'C99-08-17': 'Conference Server',
    'C99-10-04': 'ICALEPCS99 Server',
    'CBPF': 'Rio de Janeiro, CBPF Server',
    'CDF93': 'CDF Document Server',
    'CDF94': 'CDF Document Server',
    'CDF95': 'CDF Document Server',
    'CDF96': 'CDF Document Server',
    'CDF97': 'CDF Document Server',
    'CDF98': 'CDF Document Server',
    'CDFCONF94': 'CDF Document Server',
    'CDFCONF95': 'CDF Document Server',
    'CDFCONF96': 'CDF Document Server',
    'CDFCONF97': 'CDF Document Server',
    'CDFCONF98': 'CDF Document Server',
    'CDS': 'CERN Document Server',
    'CDSWEB': 'CERN Library Record',
    'CECOA': 'CERN Courier Server',
    'CERN': 'CERN Document Server',
    'CERN-ATLAS': 'CERN ATLAS Server',
    'CERN-ATLAS-THESIS': 'ATLAS Thesis Server',
    'CERN9401': 'CERN Document Server',
    'CERN9402': 'CERN Document Server',
    'CERN9403': 'CERN Document Server',
    'CERN9404': 'CERN Document Server',
    'CERN9405': 'CERN Document Server',
    'CERN9406': 'CERN Document Server',
    'CERN9407': 'CERN Document Server',
    'CERN9408': 'CERN Document Server',
    'CERN9409': 'CERN Document Server',
    'CERN9410': 'CERN Document Server',
    'CERN9411': 'CERN Document Server',
    'CERN9412': 'CERN Document Server',
    'CERN9501': 'CERN Document Server',
    'CERN9502': 'CERN Document Server',
    'CERN9503': 'CERN Document Server',
    'CERN9504': 'CERN Document Server',
    'CERN9505': 'CERN Document Server',
    'CERN9506': 'CERN Document Server',
    'CERN9507': 'CERN Document Server',
    'CERN9508': 'CERN Document Server',
    'CERN9509': 'CERN Document Server',
    'CERN9510': 'CERN Document Server',
    'CERN9511': 'CERN Document Server',
    'CERN9512': 'CERN Document Server',
    'CERN9601': 'CERN Document Server',
    'CERN9602': 'CERN Document Server',
    'CERN9603': 'CERN Document Server',
    'CERN9604': 'CERN Document Server',
    'CERN9605': 'CERN Document Server',
    'CERN9606': 'CERN Document Server',
    'CERN9607': 'CERN Document Server',
    'CERN9608': 'CERN Document Server',
    'CERN9609': 'CERN Document Server',
    'CERN9610': 'CERN Document Server',
    'CERN9611': 'CERN Document Server',
    'CERN9612': 'CERN Document Server',
    'CERNAB': 'CERN AB Server',
    'CERNKEY': 'CERN Library Record',
    'CERNNO': 'CERN Library Record',
    'CERNREC': 'Cern Document Server',
    'CERNREP': 'CERN Server',
    'CERNSL': 'CERN SL Server',
    'CERNWEBCAST': 'CERN Web Lecture Archive',
    'CERNYEL': 'CERN Yellow Reports Server',
    'CERNYELLOW': 'CERN Yellow Reports Server',
    'CHACD': 'J. Korean Astron. Soc. Server',
    'CHAOE': 'Chaos Server',
    'CHEP97': 'Postscript from CHEP97 Server',
    'CHPHD': 'Chinese Phys. Server',
    'CITESEER': 'CiteSeer Server',
    'CJAAA': 'Chin. J. Astron. Astrophys. Server',
    'CJOPA': 'Chin.J.Phys. Server',
    'CJPHA': 'Canadian Journal of Physics Server',
    'CLNS93': 'Cornell Document Server',
    'CLNS94': 'Cornell Document Server',
    'CLNS95': 'Cornell Document Server',
    'CLNS96': 'Cornell Document Server',
    'CLNS97': 'Cornell Document Server',
    'CLNS98': 'Cornell Document Server',
    'CLNSCONF97': 'Cornell Document Server',
    'CLNSCONF98': 'Cornell Document Server',
    'CMMPE': 'Cambridge Monogr.Math.Phys. Server',
    'CMP': 'Commun. Math. Phys. Server',
    'CMPHF': 'Condensed Matter Phys. Server',
    'CNRS': 'CNRS Server',
    'COGPRINTS': 'Cogprints Server',
    'COLUMBIA-THESIS': 'Columbia U. Thesis Server',
    'CORNELL-LNS': 'Cornell U., LNS Server',
    'CPHCB': 'Comput. Phys. Commun. Server',
    'CPLEE': 'Chinese Physics Letters Server',
    'CQG': 'Class. Quant. Grav. server',
    'CQGRD': 'Class. Quantum Grav. Server',
    'CSENF': 'Comput. Sci. Engin. Server',
    'CT-THESIS': 'Caltech Thesis Server',
    'CTPHA': 'Contemp. Phys. Server',
    'CTPMD': 'Commun. Theor. Phys. Server',
    'CUP': 'Cambridge University Press Server',
    'CZYPA': 'Czech. J. Phys. Server',
    'D0': 'Postscript_Version from D0 Server',
    'DANKA': 'Doklady Physics Server',
    'DAPN': 'DAPNIA, Saclay Server',
    'DAPN-THESIS': 'DAPNIA, Saclay Thesis Server',
    'DARENET': 'DARENET Server',
    'DELPHITHESIS': 'DELPHI Thesis Server',
    'DESY': 'DESY Document Server',
    'DESY91': 'DESY Document Server',
    'DESY92': 'DESY Document Server',
    'DESY93': 'DESY Document Server',
    'DESY94': 'DESY Document Server',
    'DESY95': 'DESY Document Server',
    'DESY96': 'DESY Document Server',
    'DESYPROC': 'DESY Proceedings Server',
    'DGA': 'Diff. Geom. Appl. Document Server',
    'DMSEE': 'Turkish Journal of Math Server',
    'DOI': 'Journal Server',
    'DOPHF': 'Doklady Physics Server',
    'DSPACE': 'eCommons Digital Repository Server',
    'DUBNA': 'JINR DUBNA Preprint Server',
    'DUBNA2': 'JINR DUBNA Preprint Server',
    'DURHAM': 'HepData',
    'ECONF': 'Proceedings write-up on eConf',
    'ECONFPDF': 'pdf from eConf',
    'ECONFS': 'Slides on eConf',
    'EJP': 'Europ. J. Phys. server',
    'EJPHD': 'Eur. J. Phys. Server',
    'ELJOUR1': 'EIPL Particle Physics Server',
    'ELJOUR2': 'JHEP Server',
    'EPHJA-A': 'Euro.Phys.J.A Server',
    'EPHJA-B': 'Eur.Phys.J.B Server',
    'EPHJA-C': 'Eur.Phys.J.C Server',
    'EPHJA-D': 'Eur.Phys.J.D Server',
    'EPHJA-E': 'Eur.Phys.J.direct Server',
    'EPHJD': 'Eur.Phys.J.direct Server',
    'EPJA': 'Europ. Phys. Jour. A Server',
    'EPJB': 'Euro. Phys. Jour. B Server',
    'EPJC': 'Eur.Phys.J. C. Server',
    'EPJCD': 'Europ. Phys. Jour. direct C Server',
    'EPJD': 'Euro. Phys. Jour. D Server',
    'EPL': 'Europhys. Lett. Server',
    'EPN': 'Europhys. News Server',
    'EUCLID': 'Project Euclid Server',
    'EUPNA': 'Europhysics News Server',
    'EXASE': 'Experimental Astronomy Server',
    'FBOOKS': 'Fermilab BOOKS Database',
    'FBS': 'Few Body Sys. Server',
    'FERMILAB': 'Fermilab Library Server (fulltext available)',
    'FERMILABAPNOTE': 'Fermilab Library Server (fulltext available)',
    'FERMILABBACHELORS': 'Fermilab Library Server (fulltext available)',
    'FERMILABBEAMDOC': 'Fermilab Beam Docs Server',
    'FERMILABCONF': 'Fermilab Library Server (fulltext available)',
    'FERMILABDESIGN': 'Fermilab Library Server (fulltext available)',
    'FERMILABEN': 'Fermilab Library Server (fulltext available)',
    'FERMILABEXP': 'Fermilab Library Server (fulltext available)',
    'FERMILABFN': 'Fermilab Library Server (fulltext available)',
    'FERMILABLOI': 'Fermilab Library Server',
    'FERMILABLU': 'Fermilab Library Server (fulltext available)',
    'FERMILABMASTERS': 'Fermilab Library Server (fulltext unavailable)',
    'FERMILABMASTERSF': 'Fermilab Library Server (fulltext available)',
    'FERMILABMINERVA': 'MINERvA Document Server',
    'FERMILABMISC': 'Fermilab Library Server (fulltext available)',
    'FERMILABNAL': 'Fermilab Library Server (fulltext available)',
    'FERMILABOTHER': 'Fermilab Library Server',
    'FERMILABPROPOSAL': 'Fermilab Library Server (fulltext available)',
    'FERMILABPUB': 'Fermilab Library Server (fulltext available)',
    'FERMILABR': 'Fermilab Library Server (fulltext available)',
    'FERMILABRESEARCH': 'Fermilab Library Server (fulltext available)',
    'FERMILABSDC': 'Fermilab Library Server',
    'FERMILABTEST': 'Fermilab Library Server (fulltext available)',
    'FERMILABTHESIS': 'Fermilab Library Server (fulltext unavailable)',
    'FERMILABTHESISF': 'Fermilab Library Server (fulltext available)',
    'FERMILABTM': 'Fermilab Library Server (fulltext available)',
    'FERMILABTODAY': 'Fermilab Today Result of the Week',
    'FERMILABUPC': 'Fermilab Library Server (fulltext available)',
    'FERMILABVLHCPUB': 'Fermilab Library Server (fulltext available)',
    'FERMILABWORKBOOK': 'Fermilab Library Server',
    'FIZIKAB': 'Fizika B Server',
    'FNDPA': 'Found.Phys. Server',
    'FOCUS': 'Physical Review Focus',
    'FPLEE': 'Found. Phys. Lett. Server',
    'FPYKA': 'Fortschr. Phys. Server',
    'FZKAA-B': 'Fizika B Server',
    'FZKAAB': 'Fizika B Server',
    'GRGVA': 'Gen.Rel.Grav. Server',
    'HEPLW': 'HEP Lib.Webzine Server',
    'HEPPDF': 'PDF Server',
    'HLTPA': 'Health Physics Server',
    'HSERVER': 'HTML_Version from a server',
    'HTTP://POS.SISSA.IT/ARCHIVE/CONFERENCES/045/026/LHC07_026.PDF': (
        'HTTP://WWW-BD.FNAL.GOV/ICFABD/NEWSLETTER45.PDF'
    ),
    'ICTP': 'ICTP Trieste Preprint Server',
    'ICTP-LNS': 'ICTP Lecture Notes Server',
    'IEEE': 'IEEExplore Server',
    'IHEP': 'IHEP Document Server',
    'IJMPA': 'Int. J. Mod. Phys. Server',
    'IJMPB': 'Int. J. Mod. Phys. Server',
    'IJMPC': 'Int. J. Mod. Phys. Server',
    'IJMPD': 'Int. J. Mod. Phys. Server',
    'IJMPE': 'Int. J. Mod. Phys. Server',
    'IJTPB': 'Int. J. Theor. Phys. Server',
    'IMPAE': 'Int.J.Mod.Phys.A Server',
    'IMPAE-A': 'Int.J.Mod.Phys.A Server',
    'IMPAE-B': 'Int.J.Mod.Phys.B Server',
    'IMPAE-C': 'Int.J.Mod.Phys.C Server',
    'IMPAE-D': 'Int.J.Mod.Phys.D Server',
    'IMPAE-E': 'Int.J.Mod.Phys.E Server',
    'IN2P3': 'HAL in2p3 Server',
    'INDICO': 'CERN Indico Server',
    'INETA': 'Instruments and Experimental Techniques Server',
    'INTERACTIONS': 'Interactions.org article',
    'IOPLETT': 'IOP Phys.Express Lett. Server',
    'IRNPE': 'Int.Rev.Nucl.Phys. Server',
    'JACOW': 'Full-text at JACoW Server',
    'JACOWS': 'Slides on JACoW Server',
    'JAUMA': 'J.Austral.Math.Soc. Server',
    'JCAPA': 'JCAP Electronic Journal Server',
    'JCTPA': 'J. Comput. Phys. Server',
    'JDGEA': 'J. Diff. Geom. Server',
    'JETP': 'J. Exp. Theor. Phys. Server',
    'JETPL': 'J. Exp. Theor. Phys. Lett. Server',
    'JGP': 'J. Geom. Phys. Document Server',
    'JGPHE': 'Journal of Geometry and Physics Server',
    'JHEP': 'JHEP Electronic Journal Server',
    'JHEPA': 'JHEP Electronic Journal Server',
    'JHEPA-CONF': 'JHEP Conference PDF Server',
    'JHEPOA': 'JHEP Electronic Journal Server',
    'JINST': 'JINST Electronic Journal Server',
    'JKPSD': 'J. Korean Phys. Soc. Server',
    'JLAB': 'JLab Document Server',
    'JMAPA': 'J.Math.Phys. Server',
    'JMP': 'J. Math. Phys. server',
    'JPA': 'J. Phys. A server',
    'JPAGB': 'J. Phys. A Server',
    'JPCBA': 'J. Phys. C Server',
    'JPG': 'J. Phys. G server',
    'JPHGB': 'J. Phys. G Server',
    'JSTAT': 'Journal of Statistical Mechanics Server',
    'JSTOR': 'JSTOR Server',
    'JSYRE': 'J. Synchrotron Radiat. Server',
    'JTPHE': 'J.Exp.Theor.Phys. Server',
    'JTPLA': 'J.Exp.Theor.Phys.Lett. Server',
    'JUPSA': 'Journal of the Physical Society of Japan Server',
    'JVSTA': 'J. Vac. Sci. Technol. Server',
    'JVSTA-A': 'J. Vac. Sci. Technol. A server',
    'JVSTA-B': 'J. Vac. Sci. Technol. B server',
    'JVSTB': 'J. Vac. Sci. Technol. Server',
    'KEKSCAN': 'KEK scanned document',
    'LANL': 'Los Alamos Server',
    'LCLSP': 'LCLS Papers Server',
    'LCLST': 'LCLS Tech Notes Server',
    'LCNOTES': 'DESY LC Notes Server',
    'LINAC2000': 'Linac2000 Econf Server',
    'LMPHD': 'Lett. Math. Phys Server',
    'LNPHA': 'Springer Lecture Notes of Physics Server',
    'MPEJ': 'Mathematical Physics Electronic Journal Server',
    'MPHYA': 'Med.Phys. Server',
    'MPLAE-A': 'Mod.Phys.Lett.A Server',
    'MPLAE-B': 'Mod.Phys.Lett.B Server',
    'MSNET': 'Mathematical Reviews',
    'MSTCE': 'Meas. Sci. Technol. Server',
    'MTF': 'Fermilab MTF Notes Server',
    'MUNI': 'Munich U. Server',
    'NATUA': 'Nature Server',
    'NCA': 'Il Nuovo Cimento Server',
    'NCB': 'Il Nuovo Cimento Server',
    'NCC': 'Il Nuovo Cimento Server',
    'NCD': 'Il Nuovo Cimento Server',
    'NDLTD': 'Networked Digital Library Server',
    'NEWAS': 'New Astronomy Server',
    'NEWAST': 'New Astronomy Server',
    'NFKAF': 'FZK Nachr. Server',
    'NIMA': 'Nucl. Instrum. Methods A Document Server',
    'NIMB': 'Nucl. Instrum. Methods B Document Server',
    'NJOPF': 'New Journal of Physics Server',
    'NOAND': 'Nonlinear Analysis Server',
    'NOBEL': 'Nobel Foundation Server',
    'NOTES': 'Notes or further material',
    'NOVO': 'Novosibirsk, IYF Server',
    'NPA2': 'Nucl. Phys. A Document Server',
    'NPB2': 'Nucl. Phys. B Document Server',
    'NPBPS': 'Nuclear Physics Electronic',
    'NPBPS2': 'Nuclear Physics B - Proceedings Supplements',
    'NPE': 'Nuclear Physics Electronic Announcements',
    'NSENA': 'Nucl.Sci.Eng. Server',
    'NUCIA': 'Nuovo Cim. PDF Server',
    'NUCLPHYS': 'Nuclear Physics Server',
    'NUIMA-A': 'Nuclear Physics Electronic',
    'NUIMA-B': 'Nuclear Physics Electronic',
    'NUMDAM': 'NUMDAM Server',
    'NUMI-PUBLIC': 'NuMI Server',
    'NUMI-RESTRICTED': 'NuMI Restricted Server',
    'NUPHA-A': 'Nuclear Physics Electronic',
    'NUPHA-B': 'Nuclear Physics Electronic',
    'NUPHZ': 'Nuclear Physics Electronic',
    'NUPHZ-TOC': 'Nuclear Physics Electronic',
    'NWSCA': 'New Scientist Server',
    'OLAL': 'Orsay, LAL Server',
    'OSTI': 'OSTI Information Bridge Server',
    'OUP': 'Oxford University Press Server',
    'PANUE': 'Phys.At.Nucl. Server',
    'PANUEO': 'Phys.At.Nucl. Server',
    'PARTICLEZ': 'particlez.org Server',
    'PDG': 'Particle Data Group (PDG) Server',
    'PDG-RPP': 'Review of Particle Properties full record',
    'PDG2002PDF': 'PDF from PDG site',
    'PDG2002PS': 'Postscript from PDG Site',
    'PDG2004PDF': 'PDF from PDG site',
    'PDG2004PS': 'PS from PDG site',
    'PDG98': 'PDG-RPP Server',
    'PDG98R': 'PDG Server',
    'PDGJOURNAL': 'Review of Particle Properties full record',
    'PDGLIV': 'pdgLive (measurements quoted by PDG)',
    'PHLTA-A': 'Phys. Lett. A Server',
    'PHLTA-B': 'Nuclear Physics Electronic',
    'PHMBA': 'Phys. Med. Biol. Server',
    'PHPEF': 'Physics in Perspective Server',
    'PHRVA': 'Phys.Rev. Server',
    'PHRVA-A': 'Phys. Rev. A Server',
    'PHRVA-B': 'Phys. Rev. B Server',
    'PHRVA-C': 'Phys. Rev. C Server',
    'PHRVA-D': 'Phys. Rev. D Server',
    'PHRVA-E': 'Phys. Rev. E Server',
    'PHRVA-FOCUS': 'Physical Review Focus',
    'PHSTB': 'Physica Scripta Server',
    'PHTOA': 'Physics Today Server',
    'PHUSE': 'Physics uspekhii Server',
    'PHUZA': 'Physik in unserer Zeit Server',
    'PHWOE': 'Physics World Server',
    'PHYSA': 'Physica A Document Server',
    'PHYSA-A': 'Physica A Server',
    'PHYSA-D': 'Physica D Server',
    'PHYSD': 'Physica A Document Server',
    'PHYSICSWEB': 'Physicsweb.org article',
    'PHYSICSWORLD': 'physicsworld.com article',
    'PHYSORG': 'PhysOrg.com article',
    'PHYSREV': 'Physical Review Server',
    'PNASA': 'Proc.Nat.Acad.Sci. Server',
    'POS': 'Proceedings of Science Server',
    'PPN': 'Phys. Part. Nucl. Server',
    'PPNP': 'Prog. Part. Nucl. Phys. Document Server',
    'PPNPD': 'Prog. Part. Nucl. Phys. server',
    'PPNUE': 'Phys.Part.Nucl. Server',
    'PPNUE-S': 'Phys. Part. Nucl. Server',
    'PPNUE1': 'Phys. Part. Nucl. (AIP) Server',
    'PPNUES': 'Phys. Part. Nucl. Suppl. Server',
    'PR': 'Physics Reports Document Server',
    'PRAMC': 'Pramana Server',
    'PRAMCARC': 'Pramana Archive Server',
    'PRC': 'Phys. Rev. C Server',
    'PRD': 'Phys. Rev. D Server',
    'PRDOLA': 'Phys. Rev. Online Archive',
    'PRE': 'Phys. Rev. E Server',
    'PRL': 'Phys. Rev. Lett. Server',
    'PRLTA': 'Phys. Rev. Lett. Server',
    'PRPLC': 'Physics Reports Server',
    'PRSLA': 'Proceedings of the Royal Society Server',
    'PRSTA': 'Phys.Rev.ST Accel.Beams Server',
    'PTPKA': 'Prog.Theor.Phys. Server',
    'PTRSA': 'Phil.Trans.Roy.Soc.Lond. Server',
    'PUBMED': 'PUBMED Server',
    'RCCHB': 'La Recherche Server',
    'RESOF': 'Resonance Journal of Science Education Server',
    'RINGBERG': 'Ringberg Conference Server',
    'RJMPE': 'Russ. J. Math. Phys. Server',
    'RMEAE': 'Radiation Measurements Server',
    'RMHPB': 'Reports on Mathematical Physics Server',
    'RMP': 'Rev. Mod. Phys. Server',
    'RMPHA': 'Rev. Mod. Phys. Server',
    'RMPHE': 'Reviews in Mathematical Physics Server',
    'RMXFA': 'Rev. Mex. Fis. Server',
    'RORPE': 'Rom. Rep. Phys. Server',
    'RPDOD': 'Radiation Protection Dosimetry Server',
    'RPPHA': 'Rep. Prog. Phys. Server',
    'RRPQA': 'Rom. J. Phys. Server',
    'RSI': 'Rev.Sci.Instrum. Server',
    'RSINA': 'Rev. Sci. Instrum. Server',
    'SACLAY': 'Saclay Document Server',
    'SALAM': 'ICTP Preprint Archive',
    'SCAMA': 'Scientific American Server',
    'SCIDIR': 'Science Direct',
    'SCIEA': 'Science Server',
    'SCIENCEBLOG': 'Science Blog article',
    'SCIENCEDAILY': 'Science Daily Article',
    'SERVER': 'Electronic Version from a server',
    'SERVER2': 'Electronic Version from another server',
    'SLAC': 'SLAC Document Server',
    'SLACBOOK': 'SLAC Book Catalog Record',
    'SLACPUB': 'SLAC Document Server',
    'SLACREPT': 'SLAC Document Server',
    'SLACTN': 'SLAC Document Server',
    'SLACTODAY': 'SLAC Today article',
    'SOPJA': 'Russ.Phys.J. Server',
    'SPACE': 'SPACE.com Article',
    'SPIE': 'SPIE Server',
    'SPRINGER': 'Springer Books Server',
    'SPTPA': 'Tech. Phys. Server',
    'SSC': 'HEPNET Document Server',
    'SSI91': 'SLAC Document Server',
    'SSI92': 'SLAC Document Server',
    'SSI93': 'SLAC Document Server',
    'SSI94': 'SLAC Document Server',
    'SSI96': 'SLAC Document Server',
    'SSI97': 'SLAC Document Server',
    'SSI98': 'SLAC Document Server',
    'TECHPHYS': 'Tech. Phys. Server',
    'TECHPHYSL': 'Tech. Phys. Lett. Server',
    'TJPHE': 'Turkish Journal of Physics Server',
    'TMFZA': 'Teor.Mat.Fiz. Server',
    'TMPHA': 'Theor.Math.Phys. Server',
    'TORONTO-A': 'Toronto U. Astron. Thesis Server',
    'TP': 'Tech. Phys. Server',
    'UCOL': 'University Coll. London Server',
    'UMI': 'UMI Thesis Server',
    'VAC': 'Vacuum Document Server',
    'VACUA': 'Vacuum Server',
    'VIDEO': 'Watch the video of the talk',
    'WORLDSCI': 'World Scientific Books Server',
    'ZBLATT': 'Zentralblatt MATH Server',
    'ZFDOF': 'Journal of Physical Studies Server',
    'ZNTFA': 'Z. Naturforsch. Server',
    'ZPA': 'Z. Phys. A Server',
    'ZPC': 'Z. Phys. C Server',
}


def control_number(endpoint):
    """Populate the ``control_number`` key.

    Also populates the ``self`` key through side effects.
    """

    def _control_number(self, key, value):
        self['self'] = get_record_ref(int(value), endpoint)
        return int(value)

    return _control_number


conferences.over('control_number', '^001')(control_number('conferences'))
data.over('control_number', '^001')(control_number('data'))
experiments.over('control_number', '^001')(control_number('experiments'))
hep.over('control_number', '^001')(control_number('literature'))
hepnames.over('control_number', '^001')(control_number('authors'))
institutions.over('control_number', '^001')(control_number('institutions'))
journals.over('control_number', '^001')(control_number('journals'))


@hep2marc.over('001', '^control_number$')
@hepnames2marc.over('001', '^control_number$')
def control_number2marc(self, key, value):
    return value


@conferences.over('legacy_version', '^005')
@data.over('legacy_version', '^005')
@experiments.over('legacy_version', '^005')
@hep.over('legacy_version', '^005')
@hepnames.over('legacy_version', '^005')
@institutions.over('legacy_version', '^005')
@journals.over('legacy_version', '^005')
def legacy_version(self, key, value):
    return value


@hep2marc.over('005', '^legacy_version$')
@hepnames2marc.over('005', '^legacy_version$')
def legacy_version2marc(self, key, value):
    return value


@hep.over('acquisition_source', '^541..')
@hepnames.over('acquisition_source', '^541..')
def acquisition_source(self, key, value):
    """Populate the ``acquisition_source`` key."""

    def _get_datetime(value):
        d_value = force_single_element(value.get('d', ''))
        if d_value:
            try:
                date = PartialDate.loads(d_value)
            except ValueError:
                return d_value
            else:
                datetime_ = datetime(year=date.year, month=date.month, day=date.day)
                return datetime_.isoformat()

    internal_uid, orcid, source = None, None, None

    a_values = force_list(value.get('a'))
    for a_value in a_values:
        if IS_INTERNAL_UID.match(a_value):
            internal_uid = (
                int(a_value[12:])
                if a_value.startswith('inspire:uid:')
                else int(a_value)
            )
        elif IS_ORCID.match(a_value):
            orcid = a_value[6:] if a_value.startswith('orcid:') else a_value
        else:
            source = a_value

    c_value = force_single_element(value.get('c', ''))
    normalized_c_value = c_value.lower()

    if normalized_c_value == 'batchupload':
        method = 'batchuploader'
    elif normalized_c_value == 'submission':
        method = 'submitter'
    else:
        method = normalized_c_value

    return {
        'datetime': _get_datetime(value),
        'email': value.get('b'),
        'internal_uid': internal_uid,
        'method': method,
        'orcid': orcid,
        'source': source,
        'submission_number': value.get('e'),
    }


@hep2marc.over('541', '^acquisition_source$')
@hepnames2marc.over('541', '^acquisition_source$')
def acquisition_source2marc(self, key, value):
    orcid = value.get('orcid')
    source = value.get('source')

    a_value = 'orcid:' + orcid if orcid else source

    method = value.get('method')

    if method == 'batchuploader':
        c_value = 'batchupload'
    elif method == 'submitter':
        c_value = 'submission'
    else:
        c_value = method

    return {
        'a': a_value,
        'b': value.get('email'),
        'c': c_value,
        'd': value.get('datetime'),
        'e': value.get('submission_number'),
    }


@conferences.over('public_notes', '^500..')
@experiments.over('public_notes', '^500..')
@hepnames.over('public_notes', '^500..')
@institutions.over('public_notes', '^500..')
@journals.over('public_notes', '^500..')
@utils.flatten
@utils.for_each_value
def public_notes_500(self, key, value):
    """Populate the ``public_notes`` key."""
    return [
        {
            'source': value.get('9'),
            'value': public_note,
        }
        for public_note in force_list(value.get('a'))
    ]


@hep2marc.over('500', '^public_notes$')
@hepnames2marc.over('500', '^public_notes$')
@utils.for_each_value
def public_notes2marc(self, key, value):
    return {
        '9': value.get('source'),
        'a': value.get('value'),
    }


@conferences.over('_private_notes', '^595..')
@experiments.over('_private_notes', '^595..')
@hepnames.over('_private_notes', '^595..')
@institutions.over('_private_notes', '^595..')
@journals.over('_private_notes', '^595..')
@utils.flatten
@utils.for_each_value
def _private_notes_595(self, key, value):
    """Populate the ``_private_notes`` key."""
    return [
        {
            'source': value.get('9'),
            'value': _private_note,
        }
        for _private_note in force_list(value.get('a'))
    ]


@hep2marc.over('595', '^_private_notes$')
@hepnames2marc.over('595', '^_private_notes$')
@utils.for_each_value
def _private_notes2marc(self, key, value):
    return {
        '9': value.get('source'),
        'a': value.get('value'),
    }


@conferences.over('inspire_categories', '^65017')
@experiments.over('inspire_categories', '^65017')
@hep.over('inspire_categories', '^65017')
@institutions.over('inspire_categories', '^65017')
@journals.over('inspire_categories', '^65017')
def inspire_categories(self, key, value):
    schema = load_schema('elements/inspire_field')
    valid_sources = schema['properties']['source']['enum']

    inspire_categories = self.get('inspire_categories', [])

    scheme = force_single_element(value.get('2'))
    if scheme == 'arXiv':  # XXX: we skip arXiv categories here because
        return inspire_categories  # we're going to add them later in a filter.

    source = force_single_element(value.get('9', '')).lower()
    if source not in valid_sources:
        if source == 'automatically added based on dcc, ppf, dk':
            source = 'curator'
        elif source == 'submitter':
            source = 'user'
        else:
            source = None

    terms = force_list(value.get('a'))
    for _term in terms:
        term = classify_field(_term)
        if term:
            inspire_categories.append(
                {
                    'term': term,
                    'source': source,
                }
            )

    return inspire_categories


@hep2marc.over('65017', '^inspire_categories$')
@utils.for_each_value
def inspire_categories2marc(self, key, value):
    return {
        '2': 'INSPIRE',
        '9': value.get('source'),
        'a': value.get('term'),
    }


@conferences.over('_private_notes', '^667..')
@experiments.over('_private_notes', '^667..')
@hep.over('_private_notes', '^667..')
@institutions.over('_private_notes', '^667..')
@utils.for_each_value
def _private_notes_667(self, key, value):
    return {
        'source': value.get('9'),
        'value': value.get('a'),
    }


@conferences.over('public_notes', '^680..')
@experiments.over('public_notes', '^680..')
@institutions.over('public_notes', '^680..')
@journals.over('public_notes', '^680..')
@utils.for_each_value
def public_notes_680(self, key, value):
    return {
        'source': value.get('9'),
        'value': value.get('i'),
    }


@conferences.over('urls', '^8564.')
@experiments.over('urls', '^8564.')
@hep.over('urls', '^8564.')
@institutions.over('urls', '^8564.')
@journals.over('urls', '^8564.')
def urls(self, key, value):
    def _is_internal_url(url):
        base = urllib.parse.urlparse(current_app.config['LEGACY_BASE_URL'])
        base_netloc = base.netloc or base.path
        base_domain = '.'.join(base_netloc.split('.')[-2:])
        parsed_url = urllib.parse.urlparse(url)
        url_netloc = parsed_url.netloc or parsed_url.path

        return base_domain in url_netloc

    urls = self.get('urls', [])

    description = force_single_element(value.get('y'))
    description = WEBLINKS.get(description, description)
    for url in force_list(value.get('u')):
        if not _is_internal_url(url):
            urls.append(
                {
                    'description': description,
                    'value': url,
                }
            )

    return urls


@hep2marc.over('8564', '^urls$')
@hepnames2marc.over('8564', '^urls$')
@utils.for_each_value
def urls2marc(self, key, value):
    return {
        'u': value.get('value'),
        'y': value.get('description'),
    }


@conferences.over('legacy_creation_date', '^961..')
@experiments.over('legacy_creation_date', '^961..')
@hep.over('legacy_creation_date', '^961..')
@hepnames.over('legacy_creation_date', '^961..')
@institutions.over('legacy_creation_date', '^961..')
@journals.over('legacy_creation_date', '^961..')
def legacy_creation_date(self, key, value):
    if 'legacy_creation_date' in self and self['legacy_creation_date']:
        return self['legacy_creation_date']

    x_values = force_list(value.get('x'))
    if x_values:
        return earliest_date(x_values)


@hep2marc.over('961', '^legacy_creation_date$')
@hepnames2marc.over('961', '^legacy_creation_date$')
def legacy_creation_date2marc(self, key, value):
    return {'x': value}


def external_system_identifiers(endpoint):
    """Populate the ``external_system_identifiers`` key.

    Also populates the ``new_record`` key through side effects.
    """

    @utils.flatten
    @utils.for_each_value
    def _external_system_identifiers(self, key, value):
        new_recid = maybe_int(value.get('d'))
        if new_recid:
            self['new_record'] = get_record_ref(new_recid, endpoint)

        return [
            {
                'schema': 'SPIRES',
                'value': ext_sys_id,
            }
            for ext_sys_id in force_list(value.get('a'))
        ]

    return _external_system_identifiers


conferences.over('external_system_identifiers', '^970..')(
    external_system_identifiers('conferences')
)
experiments.over('external_system_identifiers', '^970..')(
    external_system_identifiers('experiments')
)
hep.over('external_system_identifiers', '^970..')(
    external_system_identifiers('literature')
)
institutions.over('external_system_identifiers', '^970..')(
    external_system_identifiers('institutions')
)
journals.over('external_system_identifiers', '^970..')(
    external_system_identifiers('journals')
)


@hep2marc.over('970', '^new_record$')
@hepnames2marc.over('970', '^new_record$')
def new_record2marc(self, key, value):
    return {'d': get_recid_from_ref(value)}


@data.over('deleted', '^980..')
def deleted(self, key, value):
    return value.get('c', '').upper() == 'DELETED'


def deleted_records(endpoint):
    """Populate the ``deleted_records`` key."""

    @utils.for_each_value
    def _deleted_records(self, key, value):
        deleted_recid = maybe_int(value.get('a'))
        if deleted_recid:
            return get_record_ref(deleted_recid, endpoint)

    return _deleted_records


conferences.over('deleted_records', '^981..')(deleted_records('conferences'))
data.over('deleted_records', '^981..')(deleted_records('data'))
experiments.over('deleted_records', '^981..')(deleted_records('experiments'))
hep.over('deleted_records', '^981..')(deleted_records('literature'))
hepnames.over('deleted_records', '^981..')(deleted_records('authors'))
institutions.over('deleted_records', '^981..')(deleted_records('institutions'))
journals.over('deleted_records', '^981..')(deleted_records('journals'))


@hep2marc.over('981', 'deleted_records')
@hepnames2marc.over('981', 'deleted_records')
@utils.for_each_value
def deleted_records2marc(self, key, value):
    return {'a': get_recid_from_ref(value)}
