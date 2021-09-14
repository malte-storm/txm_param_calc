# This file is part of txm_calc.

# txm_calc is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# txm_calc is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with txm_calc. If not, see <http://www.gnu.org/licenses/>.

"""
Module with required constants and styles which are used in the TXM param
calculator.
"""

__author__      = "Malte Storm"
__copyright__   = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "1.0.0"
__maintainer__ = "Malte Storm"
__status__ = "Alpha"
__all__ = []


PLOT_TITLES = {
    'energy': 'Energy [keV]',
    'bandwidth':'Bandwidth',
    'FZP_dr':'FZP outer zone width [nm]',
    'FZP_D':'FZP diameter [um]',
    'M_det':'Detector magnification',
    'det_PixSize':'Detector generic pixel size [um]',
    'det_Nhor':'Detector number of pixels (hor.)',
    'det_Nvert':'Detector number of pixels (vert.)',
    'eff_pix':'Detector effective pixel size [nm]',
    'dist_sample_det':'Distance sample-detector [m]',
    'BSC_D': 'BSC diameter [mm]',
    'BSC_CS':'BSC central stop diameter [mm]',
    'BSC_field': 'BSC field size [um]',
}

PLOT_VAR_NAMES = {
    'None': None,
    'X-ray wavelength': 'wavelength',
    'FZP resolution':'FZP_resolution',
    'FZP object numerical aperture (NA)': 'FZP_objectNA',
    'FZP depth of focus':'FZP_DOF',
    'FZP number of zones':'FZP_Nzones',
    'Detector effective pixel size':'det_eff_pix',
    'Detector generic pixel size': 'det_PixSize',
    'Distance sample-detector':'dist_sample_det',
    'Distance sample-FZP':'dist_sample_FZP',
    'Effective pixel size':'eff_pix',
    'Geometric FOV (horizontal)': 'det_FOVhor',
    'Geometric FOV (vertical)':'det_FOVvert',
    'X-ray magnification':'M_xray',
    'Total magnification': 'M_total',
    'BSC central stop size':'BSC_CS',
    'BSC focal length': 'BSC_f',
    'BSC effective FOV':'BSC_effFOV',
    'BSC free area': 'BSC_freeArea',
    'BSC field size': 'BSC_field',
    'Distance BSC-sample':'dist_BSC_sample',
    'FZP theoretical FOV': 'FZP_FOV'
    }

PLOT_AXIS_LABELS = {
    'wavelength':'X-ray wavelength [A]',
    'FZP_resolution':'FZP resolution [nm]',
    'FZP_objectNA': 'FZP object numerical aperture (NA)',
    'FZP_DOF':'FZP depth of focus [um]',
    'FZP_Nzones':'FZP number of zones',
    'eff_pix':'Detector effective pixel size [nm]',
    'dist_sample_det':'Distance sample-detector [m]',
    'dist_sample_FZP':'Distance sample-FZP [mm]',
    'dist_BSC_sample':'Distance BSC-sample [m]',
    'det_FOVhor':'Geometric FOV (horizontal) [um]',
    'det_FOVvert':'Geometric FOV (vertical) [um]',
    'det_PixSize': 'Detector generic pixel size [um]',
    'M_xray':'X-ray magnification',
    'M_total':'Total magnification',
    'BSC_CS':'Central stop size [mm]',
    'BSC_f':'BSC focal length [m]',
    'BSC_effFOV':'BSC effective FOV [um]',
    'BSC_freeArea':'BSC free area [%]',
    'FZP_FOV':'FZP theoretical FOV'
    }

SCALING_FACTOR = {
    'wavelength':1e10,
    'FZP_resolution':1e9,
    'FZP_objectNA': 1,
    'FZP_DOF':1e6,
    'FZP_Nzones':1,
    'FZP_f': 1e3,
    'eff_pix':1e9,
    'dist_sample_det':1,
    'dist_sample_FZP':1e3,
    'det_FOVhor':1e6,
    'det_FOVvert':1e6,
    'det_PixSize': 1e6,
    'M_xray': 1,
    'M_total': 1,
    'BSC_CS': 1e3,
    'BSC_f': 1,
    'BSC_effFOV': 1e6,
    'BSC_freeArea': 100,
    'BSC_field': 1e6,
    'BSC_D': 1e3,
    'dist_BSC_sample': 1,
    'energy': 1,
    'bandwidth':1,
    'FZP_dr':1e9,
    'FZP_D':1e6,
    'FZP_angularFOV': 1e3,
    'FZP_FOV': 1e6,
    'M_det':1,
    'det_PixSize': 1e6,
    'det_Nhor':1,
    'det_Nvert': 1,
    'FZP_FOV':1e6,
    'total_eff': 100
}

COLORS = ['#FFA500', '#1F45FC', '#4CC417', '#C11B17', '#4B0082',
          '#565051', '#43C6DB', '#43BFC7']

SOURCE_DIST = 65

GENERIC_PARAMS = {
    'energy': 12,
    'bandwidth': 1e-3,
    'FZP_dr': 50e-9,
    'FZP_D': 150e-6,

    'M_det': 1,
    'det_PixSize': 6.5e-6,
    'det_Nhor': 2048,
    'det_Nvert': 2048,
    'eff_pix': 50e-9,
    'dist_sample_det': 8.3,

    'BSC_D': 2.9e-3,
    'BSC_CS': 1.5e-3,
    'BSC_dr': 50e-9,
    'BSC_field': 60e-6,
}
