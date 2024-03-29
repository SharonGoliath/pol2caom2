# -*- coding: utf-8 -*-
# ***********************************************************************
# ******************  CANADIAN ASTRONOMY DATA CENTRE  *******************
# *************  CENTRE CANADIEN DE DONNÉES ASTRONOMIQUES  **************
#
#  (c) 2018.                            (c) 2018.
#  Government of Canada                 Gouvernement du Canada
#  National Research Council            Conseil national de recherches
#  Ottawa, Canada, K1A 0R6              Ottawa, Canada, K1A 0R6
#  All rights reserved                  Tous droits réservés
#
#  NRC disclaims any warranties,        Le CNRC dénie toute garantie
#  expressed, implied, or               énoncée, implicite ou légale,
#  statutory, of any kind with          de quelque nature que ce
#  respect to the software,             soit, concernant le logiciel,
#  including without limitation         y compris sans restriction
#  any warranty of merchantability      toute garantie de valeur
#  or fitness for a particular          marchande ou de pertinence
#  purpose. NRC shall not be            pour un usage particulier.
#  liable in any event for any          Le CNRC ne pourra en aucun cas
#  damages, whether direct or           être tenu responsable de tout
#  indirect, special or general,        dommage, direct ou indirect,
#  consequential or incidental,         particulier ou général,
#  arising from the use of the          accessoire ou fortuit, résultant
#  software.  Neither the name          de l'utilisation du logiciel. Ni
#  of the National Research             le nom du Conseil National de
#  Council of Canada nor the            Recherches du Canada ni les noms
#  names of its contributors may        de ses  participants ne peuvent
#  be used to endorse or promote        être utilisés pour approuver ou
#  products derived from this           promouvoir les produits dérivés
#  software without specific prior      de ce logiciel sans autorisation
#  written permission.                  préalable et particulière
#                                       par écrit.
#
#  This file is part of the             Ce fichier fait partie du projet
#  OpenCADC project.                    OpenCADC.
#
#  OpenCADC is free software:           OpenCADC est un logiciel libre ;
#  you can redistribute it and/or       vous pouvez le redistribuer ou le
#  modify it under the terms of         modifier suivant les termes de
#  the GNU Affero General Public        la “GNU Affero General Public
#  License as published by the          License” telle que publiée
#  Free Software Foundation,            par la Free Software Foundation
#  either version 3 of the              : soit la version 3 de cette
#  License, or (at your option)         licence, soit (à votre gré)
#  any later version.                   toute version ultérieure.
#
#  OpenCADC is distributed in the       OpenCADC est distribué
#  hope that it will be useful,         dans l’espoir qu’il vous
#  but WITHOUT ANY WARRANTY;            sera utile, mais SANS AUCUNE
#  without even the implied             GARANTIE : sans même la garantie
#  warranty of MERCHANTABILITY          implicite de COMMERCIALISABILITÉ
#  or FITNESS FOR A PARTICULAR          ni d’ADÉQUATION À UN OBJECTIF
#  PURPOSE.  See the GNU Affero         PARTICULIER. Consultez la Licence
#  General Public License for           Générale Publique GNU Affero
#  more details.                        pour plus de détails.
#
#  You should have received             Vous devriez avoir reçu une
#  a copy of the GNU Affero             copie de la Licence Générale
#  General Public License along         Publique GNU Affero avec
#  with OpenCADC.  If not, see          OpenCADC ; si ce n’est
#  <http://www.gnu.org/licenses/>.      pas le cas, consultez :
#                                       <http://www.gnu.org/licenses/>.
#
#  $Revision: 4 $
#
# ***********************************************************************
#

import importlib
import logging
import sys
import traceback

from math import sqrt

from caom2 import Observation, ProductType
from caom2utils import ObsBlueprint, get_gen_proc_arg_parser, gen_proc
from caom2pipe import StorageName
from caom2pipe import astro_composable as ac
from caom2pipe import execute_composable as ec
from caom2pipe import manage_composable as mc

from caom2 import Observation
from caom2utils import ObsBlueprint, get_gen_proc_arg_parser, gen_proc
from caom2pipe import manage_composable as mc
from caom2pipe import execute_composable as ec


__all__ = ['main_app', 'update', 'PolName', 'COLLECTION', 'APPLICATION']


APPLICATION = 'pol2caom2'
COLLECTION = 'ALMA'
POL_NAME_PATTERN = '*'


class PolName(ec.StorageName):
    """Naming rules:
    - support mixed-case file name storage, and mixed-case obs id values
    - support uncompressed files in storage
    """

    def __init__(self, obs_id=None, file_name=None, fname_on_disk=None):
        if obs_id is None:
            obs_id = PolName.get_obs_id_from_file_name(file_name)
        super(PolName, self).__init__(
            obs_id, COLLECTION, POL_NAME_PATTERN)
        self.file_name = file_name
        if file_name is None:
            self.file_id = None
        else:
            self.file_id = file_name.replace('.header', '')
        self.obs_id = obs_id
        if fname_on_disk is not None:
            self.fname_on_disk = fname_on_disk
            self.file_id = PolName.remove_extensions(fname_on_disk)

    @property
    def file_uri(self):
        """No .gz extension, unlike the default implementation."""
        return 'ad:{}/{}'.format(self.collection, self._get_file_id())

    @property
    def file_name(self):
        return self._file_name

    @file_name.setter
    def file_name(self, value):
        self._file_name = value

    def get_lineage(self, product_id):
        return '{}/{}'.format(product_id, self.file_uri)

    @property
    def product_id(self):
        return '{}.quicklook.v1'.format(self.obs_id)

    def _get_file_id(self):
        return self.file_id

    def is_valid(self):
        return True

    @staticmethod
    def get_obs_id_from_file_name(file_name):
        """The obs id is made of the VLASS epoch, tile name, and image centre
        from the file name.
        """
        obs_id = file_name
        return obs_id

    @staticmethod
    def remove_extensions(name):
        """How to get the file_id from a file_name."""
        return name.replace('.fits', '').replace('.header', '').replace('.jpg',
                                                                        '')


def accumulate_bp(bp, uri):
    """Configure the telescope-specific ObsBlueprint at the CAOM model 
    Observation level."""
    logging.debug('Begin accumulate_bp.')
    # bp.configure_position_axes((1, 2))
    # bp.configure_energy_axis(3)
    # bp.configure_polarization_axis(4)
    bp.configure_position_axes((5, 6))
    # bp.configure_energy_axis(3)
    bp.configure_polarization_axis(3)

    # obervation level
    bp.set('Observation.type', 'OBJECT')

    bp.clear('Observation.target.name')
    bp.set('Observation.target.type', 'field')
    bp.set('Observation.proposal.id', 'get_proposal_id(uri)')

    # plane level
    bp.set('Plane.calibrationLevel', '2')
    bp.set('Plane.dataProductType', 'image')

    bp.clear('Plane.provenance.name')
    bp.add_fits_attribute('Plane.provenance.name', 'ORIGIN')
    bp.clear('Plane.provenance.runID')
    bp.clear('Plane.provenance.lastExecuted')
    bp.add_fits_attribute('Plane.provenance.lastExecuted', 'DATE')

    bp.clear('Plane.metaRelease')
    bp.add_fits_attribute('Plane.metaRelease', 'DATE-OBS')
    bp.clear('Plane.dataRelease')
    bp.add_fits_attribute('Plane.dataRelease', 'DATE-OBS')

    # artifact level
    bp.clear('Artifact.productType')
    bp.set('Artifact.productType', 'get_product_type(uri)')

    # chunk level
    bp.clear('Chunk.position.axis.function.cd11')
    bp.clear('Chunk.position.axis.function.cd22')
    bp.add_fits_attribute('Chunk.position.axis.function.cd11', 'CDELT1')
    bp.set('Chunk.position.axis.function.cd12', 0.0)
    bp.set('Chunk.position.axis.function.cd21', 0.0)
    bp.add_fits_attribute('Chunk.position.axis.function.cd22', 'CDELT2')

    bp.set('Chunk.naxis', '6')
    logging.debug('Done accumulate_bp.')


def get_position_resolution(header):
    bmaj = header[0]['BMAJ']
    bmin = header[0]['BMIN']
    # From
    # https://open-confluence.nrao.edu/pages/viewpage.action?pageId=13697486
    # Clare Chandler via JJK - 21-08-18
    return 3600.0 * sqrt(bmaj*bmin)


def get_product_type(uri):
    if '.rms.' in uri:
        return ProductType.NOISE
    else:
        return ProductType.SCIENCE


def get_proposal_id(uri):
    file_name = ec.CaomName(uri).file_name
    return file_name[:8]


def get_time_refcoord_value(header):
    dateobs = header[0].get('DATE-OBS')
    if dateobs is not None:
        result = ac.get_datetime(dateobs)
        if result is not None:
            return result.mjd
        else:
            return None


def update(observation, **kwargs):
    """Called to fill multiple CAOM model elements and/or attributes, must
    have this signature for import_module loading and execution.

    :param observation A CAOM Observation model instance.
    :param **kwargs Everything else."""
    logging.debug('Begin update.')

    try:

        mc.check_param(observation, Observation)
        for plane in observation.planes:
            for artifact in observation.planes[plane].artifacts:
                for part in observation.planes[plane].artifacts[artifact].parts:
                    p = observation.planes[plane].artifacts[artifact].parts[part]
                    # for chunk in p.chunks:
                    #     if 'headers' in kwargs:
                    #         headers = kwargs['headers']
                    #         chunk.position.resolution = get_position_resolution(
                    #             headers)
                    #         # if chunk.energy is not None:
                    #             # A value of None per Chris, 2018-07-26
                    #             # Set the value to None here, because the
                    #             # blueprint is implemented to not set WCS
                    #             # information to None
                    #             # chunk.energy.restfrq = None
        logging.debug('Done update.')
        return observation
    except mc.CadcException as e:
        tb = traceback.format_exc()
        logging.debug(tb)
        logging.error(e)
        logging.error(
            'Terminating ingestion for {}'.format(observation.observation_id))
        return None


class PolCardinality(object):

    def __init__(self):
        self.collection = COLLECTION

    @staticmethod
    def build_blueprints(args):
        """This application relies on the caom2utils fits2caom2 ObsBlueprint
        definition for mapping FITS file values to CAOM model element
        attributes. This method builds the VLASS blueprint for a single
        artifact.

        The blueprint handles the mapping of values with cardinality of 1:1
        between the blueprint entries and the model attributes.

        :param args """
        module = importlib.import_module(__name__)
        blueprints = {}
        for ii in args.lineage:
            blueprint = ObsBlueprint(module=module)
            product_id, artifact_uri = mc.decompose_lineage(ii)
            accumulate_bp(blueprint, artifact_uri)
            blueprints[artifact_uri] = blueprint
        return blueprints

    def build_cardinality(self):
        pass  # TODO


def main_app():
    args = get_gen_proc_arg_parser().parse_args()
    try:
        pol = PolCardinality()
        blueprints = pol.build_blueprints(args)
        gen_proc(args, blueprints)
    except Exception as e:
        logging.error('Failed {} execution for {}.'.format(APPLICATION, args))
        tb = traceback.format_exc()
        logging.error(tb)
        sys.exit(-1)

    logging.debug('Done {} processing.'.format(APPLICATION))
