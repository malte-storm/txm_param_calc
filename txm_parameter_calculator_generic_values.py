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

# the source distance in m
SOURCE_DIST = 65

# the energy in keV
ENERGY = 12

# the relative energy bandwidth
BANDWIDTH = 1e-3

# the FZP outermost zone width dr in m
FZP_DR = 40e-9

# the FZP diameter D in m
FZP_D = 150e-6

# the detector magnification
M_DET = 1

# the detector pixelsize in m
DET_PIXSIZE = 6.5e-6

# the number of horizontal pixels in the detector
DET_NHOR = 2048

# the number of vertical pixels in the detector
DET_NVERT = 2048

# the sample to detector distance in m
DIST_SAMPLE_DET = 20

#the beamshaper diameter in m
BSC_D = 2.9e-3

# the diameter of the central stop in m
BSC_CS = 1.5e-3

# the field size of the illumination in m
BSC_FIELD = 60e-6
