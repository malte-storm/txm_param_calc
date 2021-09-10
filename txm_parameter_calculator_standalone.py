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
Module with the txm_calc GUI which can be used to calculate parameters
for X-ray microscope optics setups.
"""

__author__      = "Malte Storm"
__copyright__   = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "1.0.0"
__maintainer__ = "Malte Storm"
__status__ = "Alpha"
__all__ = ['txm_calc']

import sys
import os
import zipfile
import importlib
from functools import partial

import numpy as np
from PyQt5 import uic as QtUic
from PyQt5 import QtGui, QtWidgets
from PyQt5 import QtCore
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

plt.rcParams['font.size'] = 15


spec = importlib.util.spec_from_file_location(
    'txm_parameter_calculator_constants',
    os.path.join(os.path.dirname(__file__),
                 'txm_parameter_calculator_constants.py'))
CONST = importlib.util.module_from_spec(spec)
spec.loader.exec_module(CONST)


spec = importlib.util.spec_from_file_location(
    'txm_parameter_calculator_utils',
    os.path.join(os.path.dirname(__file__),
                 'txm_parameter_calculator_utils.py'))
UTILS = importlib.util.module_from_spec(spec)
spec.loader.exec_module(UTILS)



class cTXMCalculator(QtWidgets.QMainWindow):
    def __init__(self, parent, name='TXM parameter calculator',
                 screensize = [1920, 1200]):
        super(cTXMCalculator, self).__init__()
        workDir = os.path.dirname(__file__)
        QtUic.loadUi(f'{workDir}/txm_parameter_calculator_layout.ui', self)
        self.setWindowIcon(
            QtGui.QIcon(f'{workDir}/txm_parameter_calculator_icon.png'))

        self.setWindowTitle(name)
        self.widgetX = 1790
        self.widgetY = 1080
        self.setGeometry(10, 30, self.widgetX, self.widgetY)
        self.setWindowFlags(QtCore.Qt.WindowCloseButtonHint
                            | QtCore.Qt.WindowMinimizeButtonHint)
        self.setFixedSize(self.widgetX, self.widgetY)
        self.main = parent
        self.zip_basedir = None
        self.zip_filename = None

        self.__init_figures()
        self.__init_optics_parameters()
        self.__init_slot_connections()
        self.__init_styles_and_layout()

    def __init_figures(self):
        """
        Initialize the figures and required attributes.
        """
        self.figure1 = plt.figure(1, figsize=(11, 8), dpi=80)
        self.figure1Canvas = FigureCanvas(self.figure1)
        self.figure1Canvas.setParent(self)
        self.figure1Canvas.setGeometry(480, 200, self.widgetX - 480 - 10,
                                       self.widgetY - 200 - 10)
        self.f1ax1 = self.figure1.add_axes([0.085, 0.1, 0.84, 0.87])
        self.f1ax2 = self.f1ax1.twinx()
        self.plot1Type = 'linear'
        self.plot2Type = 'linear'
        self.plot1ylow = 0
        self.plot1yhigh = 1
        self.plot2ylow = 0
        self.plot2yhigh = 1
        self.plot1var = None
        self.plot2var = None
        self.plot1Autoscale = True
        self.plot2Autoscale = True
        self.ax1plotContent = False
        self.ax2plotContent = False
        self.f2plotContent = False
        self.activeVar = None
        self.figureExists = False
        self.ignoreUpdate = False

        self.figure2 = plt.figure(2, figsize=(6, 4), dpi=80)
        self.figure2Canvas = FigureCanvas(self.figure2)
        self.figure2Canvas.setParent(self)
        self.figure2Canvas.setGeometry(920, 10, self.widgetX - 920 - 10,
                                       200 - 10)
        self.figure2ax = self.figure2.add_axes([0.085, 0.34, 0.84, 0.6])

        self.figure3 = plt.figure(3, figsize=(12, 10))
        self.f3ax = self.figure3.add_axes([0.1, 0.15, 0.84, 0.8])
        self.f3content = False
        self.f3ax.cla()

    def __init_optics_parameters(self):
        """
        Initialize the required attributes for the optical calculations.
        """
        # parameters 1 (beamline and FZP)
        self.energy = np.asarray(12)
        self.bandwidth = np.asarray(1e-3)
        self.FZP_dr = np.asarray(50e-9)
        self.FZP_D = np.asarray(150e-6)

        # parameters 2 (detector)
        self.M_det = np.asarray(1)
        self.det_PixSize = np.asarray(6.5e-6)
        self.det_Nhor = np.asarray(2048)
        self.det_Nvert = np.asarray(2048)
        self.det_useEffPix = False
        self.eff_pix = np.asarray(50e-9)
        self.dist_sample_det = np.asarray(8.3)

        # parameters 3 (beamshaper)
        self.BSC_D = np.asarray(2.9e-3)
        self.BSC_CS = np.asarray(1.5e-3)
        self.BSC_dr = np.asarray(50e-9)
        self.BSC_field = np.asarray(60e-6)
        self.BSC_useFullDet = False

    def __init_slot_connections(self):
        """
        Connect all slots and signals.
        """
        self.but_SetEnergy.clicked.connect(partial(
            self.clickButtonSetAttribute, 'energy', self._updateParameters1))
        self.edit_energy.returnPressed.connect(partial(
            self.clickButtonSetAttribute, 'energy', self._updateParameters1))

        self.but_SetBandwidth.clicked.connect(partial(
            self.clickButtonSetAttribute, 'bandwidth',
            self._updateParameters1))
        self.edit_bandwidth.returnPressed.connect(partial(
            self.clickButtonSetAttribute, 'bandwidth',
            self._updateParameters1))

        self.but_SetFZP_dr.clicked.connect(partial(
            self.clickButtonSetAttribute, 'FZP_dr', self._updateParameters1))
        self.edit_FZP_dr.returnPressed.connect(partial(
            self.clickButtonSetAttribute, 'FZP_dr', self._updateParameters1))

        self.but_SetFZP_D.clicked.connect(partial(
            self.clickButtonSetAttribute, 'FZP_D', self._updateParameters1))
        self.edit_FZP_D.returnPressed.connect(partial(
            self.clickButtonSetAttribute, 'FZP_D', self._updateParameters1))

        self.but_SetM_det.clicked.connect(partial(
            self.clickButtonSetAttribute, 'M_det', self._updateParameters2))
        self.edit_M_det.returnPressed.connect(partial(
            self.clickButtonSetAttribute, 'M_det', self._updateParameters2))

        self.but_SetPixSize.clicked.connect(partial(
            self.clickButtonSetAttribute, 'eff_pix', self._updateParameters2))
        self.edit_det_PixSize.returnPressed.connect(partial(
            self.clickButtonSetAttribute, 'eff_pix', self._updateParameters2))

        self.but_SetDet_Nhor.clicked.connect(partial(
            self.clickButtonSetAttribute, 'det_Nhor', self._updateParameters2))
        self.edit_det_Nhor.returnPressed.connect(partial(
            self.clickButtonSetAttribute, 'det_Nhor', self._updateParameters2))

        self.but_SetDet_Nvert.clicked.connect(partial(
            self.clickButtonSetAttribute, 'det_Nvert',
            self._updateParameters2))
        self.edit_det_Nvert.returnPressed.connect(partial(
            self.clickButtonSetAttribute, 'det_Nvert',
            self._updateParameters2))

        self.comboBox_ParametersDet.currentIndexChanged.connect(
            self.selectParametersDet)

        self.but_SetDistSampleDet.clicked.connect(partial(
            self.clickButtonSetAttribute, 'dist_sample_det',
            self._updateParameters2))
        self.edit_dist_sample_det.returnPressed.connect(partial(
            self.clickButtonSetAttribute, 'dist_sample_det',
            self._updateParameters2))

        self.but_SetEffPix.clicked.connect(partial(
            self.clickButtonSetAttribute, 'eff_pix', self._updateParameters2))
        self.edit_eff_pix.returnPressed.connect(partial(
            self.clickButtonSetAttribute, 'eff_pix', self._updateParameters2))

        self.but_SetBSC_D.clicked.connect(partial(
            self.clickButtonSetAttribute, 'BSC_D', self._updateParameters3))
        self.edit_BSC_D.returnPressed.connect(partial(
            self.clickButtonSetAttribute, 'BSC_D', self._updateParameters3))

        self.comboBox_ParametersCS.currentIndexChanged.connect(
            self.selectParametersCS)

        self.but_SetBSC_CS.clicked.connect(partial(
            self.clickButtonSetAttribute, 'BSC_CS', self._updateParameters3))
        self.edit_BSC_CS.returnPressed.connect(partial(
            self.clickButtonSetAttribute, 'BSC_CS', self._updateParameters3))

        self.but_SetBSC_field.clicked.connect(partial(
            self.clickButtonSetAttribute, 'BSC_field',
            self._updateParameters3))
        self.edit_BSC_field.returnPressed.connect(partial(
            self.clickButtonSetAttribute, 'BSC_field',
            self._updateParameters3))

        self.but_SaveData.clicked.connect(self.writeData)
        self._updateParameters1()

        # plotting parameters:
        self.edit_plot1Low.valueChanged.connect(self.changePlot1LimitLow)
        self.edit_plot1High.valueChanged.connect(self.changePlot1LimitHigh)
        self.edit_plot2Low.valueChanged.connect(self.changePlot2LimitLow)
        self.edit_plot2High.valueChanged.connect(self.changePlot2LimitHigh)
        self.comboBox_plot1.currentIndexChanged.connect(self.changePlot1Type)
        self.comboBox_plot1_autoscale.currentIndexChanged.connect(
            self.changePlot1Autoscale)
        self.comboBox_plot1_variable.currentIndexChanged.connect(
            self.changePlot1Variable)
        self.comboBox_plot2_variable.currentIndexChanged.connect(
            self.changePlot2Variable)
        self.comboBox_plot2.currentIndexChanged.connect(self.changePlot2Type)
        self.comboBox_plot2_autoscale.currentIndexChanged.connect(
            self.changePlot2Autoscale)

    def __init_styles_and_layout(self):
        """
        Initialize styles and layout and set widget properties.
        """
        self.button_style = CONST.BUTTON_STYLE
        self.spin_style = CONST.SPIN_STYLE
        self.textbox_style = CONST.TEXTBOX_STYLE
        self.palette_red = QtGui.QPalette()
        self.palette_red.setColor(QtGui.QPalette.Foreground, QtCore.Qt.red)

        self.palette_green = QtGui.QPalette()
        self.palette_green.setColor(QtGui.QPalette.Foreground, QtCore.Qt.green)

        self.palette_blk = QtGui.QPalette()
        self.palette_blk.setColor(QtGui.QPalette.Foreground, QtCore.Qt.black)

        self.palette_blue = QtGui.QPalette()
        self.palette_blue.setColor(QtGui.QPalette.Foreground, QtCore.Qt.blue)

        for item in [self.label_21, self.edit_dist_sample_det,
                     self.but_SetDistSampleDet, self.label_54, self.label_104]:
            item.setVisible(False)
        for item in [self.label_20, self.edit_eff_pix, self.but_SetEffPix,
                     self.label_53, self.label_103]:
            item.setVisible(True)
        for item in [self.edit_BSC_CS, self.but_SetBSC_CS]:
            item.setVisible(False)

        self.stdfont = QtGui.QFont()
        self.stdfont.setFamily("Arial")
        self.stdfont.setPointSize(11)

        self.stdfontsmall = QtGui.QFont()
        self.stdfontsmall.setFamily("Arial")
        self.stdfontsmall.setPointSize(8)

        self.stdfontbold = QtGui.QFont()
        self.stdfontbold.setFamily("Arial")
        self.stdfontbold.setPointSize(11)
        self.stdfontbold.setBold(True)
        self.stdfontbold.setWeight(75)

        tmp = str(self.comboBox_ParametersDet.currentText())
        if tmp == 'Set detector effective pixel size':
            self.det_useEffPix = True
            for item in [self.label_21, self.edit_dist_sample_det,
                         self.but_SetDistSampleDet, self.label_54,
                         self.label_104]:
                item.setVisible(False)
            for item in [self.label_20, self.edit_eff_pix, self.but_SetEffPix,
                         self.label_53, self.label_103]:
                item.setVisible(True)
            self.edit_eff_pix.setText(str(self.eff_pix * 1e9))
        if tmp == 'Set target distance sample-det':
            self.det_useEffPix = False
            for item in [self.label_21, self.edit_dist_sample_det,
                         self.but_SetDistSampleDet, self.label_54,
                         self.label_104]:
                item.setVisible(True)
            for item in [self.label_20, self.edit_eff_pix, self.but_SetEffPix,
                         self.label_53, self.label_103]:
                item.setVisible(False)
                self.edit_dist_sample_det.setText(str(self.dist_sample_det))

        tmp = str(self.comboBox_ParametersCS.currentText())
        if tmp == 'Use full detector FOV':
            self.BSC_useFullDet = True
            for item in [self.edit_BSC_CS, self.but_SetBSC_CS]:
                item.setVisible(False)
            self.label_200.setVisible(True)
        if tmp == 'Select central stop size':
            self.BSC_useFullDet = False
            for item in [self.edit_BSC_CS, self.but_SetBSC_CS]:
                item.setVisible(True)
            self.label_200.setVisible(False)
        self.RefreshPlot()
        self.show()

    def _updateParameters1(self):
        self.wavelength = np.asarray(12.398 / self.energy * 1e-10)
        self.FZP_resolution = np.asarray(1.22 * self.FZP_dr)
        self.FZP_objectNA = np.asarray(self.wavelength / (2 * self.FZP_dr))
        self.FZP_DOF = np.asarray(2 * self.FZP_dr ** 2 / self.wavelength)
        self.FZP_Nzones = np.asarray(self.FZP_D / (4 * self.FZP_dr))
        self.FZP_f = np.asarray(self.FZP_D * self.FZP_dr / self.wavelength)

        self.label_1.setText(str(self.wavelength * 1e10))
        self.label_2.setText(str(self.FZP_resolution * 1e9))
        self.label_3.setText(str(self.FZP_objectNA))
        self.label_4.setText(str(self.FZP_DOF * 1e6))
        self.label_5.setText(str(self.FZP_Nzones))
        self.label_6.setText(str(self.FZP_f * 1e3))
        self._updateParameters2()

    def _updateParameters2(self):
        if self.det_useEffPix:
            self.M_total = np.asarray(self.det_PixSize / self.eff_pix)
            self.M_xray = np.asarray(self.M_total / self.M_det)
            self.dist_sample_FZP = np.asarray(
                self.FZP_f * (1.0 + self.M_xray) / self.M_xray
        )
            self.dist_FZP_det = np.asarray(self.FZP_f * (1.0 + self.M_xray))
            self.dist_sample_det = np.asarray(self.dist_FZP_det
                                                 + self.dist_sample_FZP)
        else:  # i.e. use distance sample-det
            self.dist_sample_FZP = np.asarray(
                self.dist_sample_det / 2
                - (self.dist_sample_det ** 2 / 4
                   - self.dist_sample_det * self.FZP_f) ** 0.5
           )
            self.dist_FZP_det = np.asarray(self.dist_sample_det
                                              - self.dist_sample_FZP)
            self.M_xray = np.asarray(self.dist_FZP_det
                                        / self.dist_sample_FZP)
            self.M_total = np.asarray(self.M_xray * self.M_det)
            self.eff_pix = np.asarray(self.det_PixSize / self.M_total)

        self.det_FOVhor = np.asarray(self.eff_pix * self.det_Nhor)
        self.det_FOVvert = np.asarray(self.eff_pix * self.det_Nvert)
        self.FZP_imageNA = self.FZP_D / 2 / self.dist_FZP_det
        self.FZP_angularFOV = (
            2 * (self.wavelength / (5 * self.FZP_imageNA ** 2)
            / (self.dist_FZP_det + self.M_xray ** 2 * self.dist_sample_FZP)
            + 1) ** 2 - 2
        )
        self.FZP_FOV = self.FZP_angularFOV * 2 * self.dist_sample_FZP

        self.label_101.setText(str(self.det_FOVhor * 1e6))
        self.label_102.setText(str(self.det_FOVvert * 1e6))
        self.label_103.setText(str(self.dist_sample_det))
        self.label_104.setText(str(self.eff_pix * 1e9))
        self.label_105.setText(str(self.M_xray))
        self.label_106.setText(str(self.M_total))
        self.label_107.setText(str(self.dist_sample_FZP * 1e3))
        self.label_108.setText(str(self.FZP_angularFOV * 1e3))
        self.label_109.setText(str(self.FZP_FOV * 1e6))
        self._updateParameters3()

    def _updateParameters3(self):
        self.BSC_f = np.asarray(self.BSC_D * self.FZP_dr / self.wavelength)
        self.dist_BSC_sample = np.asarray(
            240. / 2 - (240. ** 2 / 4 - 240. * self.BSC_f) ** 0.5
        )
        self.dist_source_BSC = np.asarray(240. - self.dist_BSC_sample)
        self.BSC_Nzones = self.BSC_D / (4 * self.BSC_dr)
        if self.BSC_useFullDet:
            self.BSC_CShor = np.asarray(
                self.det_PixSize * self.det_Nhor * self.dist_BSC_sample
                / self.dist_sample_det / self.M_det
            )
            self.BSC_CSvert = np.asarray(
                self.det_PixSize * self.det_Nvert * self.dist_BSC_sample
                / self.dist_sample_det / self.M_det
            )
            self.BSC_CS = np.where(
                self.BSC_CShor >= self.BSC_CSvert, self.BSC_CShor,
                self.BSC_CSvert
            )
        self.BSC_effFOV = (self.BSC_CS / self.dist_BSC_sample
                           * self.dist_sample_det / self.M_xray)
        self.tmpval = 1 - self.BSC_CS ** 2 / (np.pi * (self.BSC_D / 2) ** 2)
        self.BSC_freeArea = np.where(self.tmpval > 0, self.tmpval, 0)

        tmp_hor = np.amin(
            np.concatenate([[self.det_FOVhor], [self.BSC_effFOV]]), axis=0)
        eff_hor = np.where(
            tmp_hor < self.BSC_field, tmp_hor / self.BSC_field, 1)
        tmp_vert = np.amin(
            np.concatenate([[self.det_FOVhor], [self.BSC_effFOV]]), axis=0)
        eff_vert = np.where(
            tmp_vert < self.BSC_field, tmp_vert / self.BSC_field, 1)

        self.total_eff =  eff_hor * eff_vert * self.BSC_freeArea
        self.label_200.setText(str(self.BSC_CS * 1e3))
        self.label_201.setText(str(self.BSC_f))
        self.label_203.setText(str(self.BSC_effFOV * 1e6))
        self.label_204.setText(str(self.BSC_freeArea * 100))
        self.label_205.setText(str(self.dist_BSC_sample))

        self.label_202.setText(str(np.round(self.total_eff*100, 1)))

        if tmp_hor.size == 1:
            self.label_206.setText('%.1f um \u2259 %i px'
                                   %(tmp_hor*1e6, tmp_hor/self.eff_pix))
            self.label_207.setText('%.1f um \u2259 %i px'
                                   %(tmp_vert*1e6, tmp_vert/self.eff_pix))
        else:
            self.label_206.setText(str(np.round(tmp_hor*1e6, 1)))
            self.label_207.setText(str(np.round(tmp_vert*1e6, 1)))

        self.check_NFZP = (
            np.where((self.FZP_Nzones > 100), True, False)
            * np.where((self.FZP_Nzones < 1 / self.bandwidth), True, False))
        self.check_DOF = np.where(self.FZP_DOF >= self.BSC_effFOV, True,
                                     False)
        self.check_NBSC = np.where(self.BSC_Nzones < 1 / self.bandwidth,
                                      True, False)
        self.RefreshPlot()

    def selectParametersDet(self):
        tmp = str(self.comboBox_ParametersDet.currentText())
        if tmp == 'Set detector effective pixel size':
            self.det_useEffPix = True
            for item in [self.label_21, self.edit_dist_sample_det,
                         self.but_SetDistSampleDet, self.label_54,
                         self.label_104]:
                item.setVisible(False)
            for item in [self.label_20, self.edit_eff_pix, self.but_SetEffPix,
                         self.label_53, self.label_103]:
                item.setVisible(True)
            self.edit_eff_pix.setText(str(self.eff_pix * 1e9))
        if tmp == 'Set target distance sample-det':
            self.det_useEffPix = False
            for item in [self.label_21, self.edit_dist_sample_det,
                         self.but_SetDistSampleDet, self.label_54,
                         self.label_104]:
                item.setVisible(True)
            for item in [self.label_20, self.edit_eff_pix, self.but_SetEffPix,
                         self.label_53, self.label_103]:
                item.setVisible(False)
                self.edit_dist_sample_det.setText(str(self.dist_sample_det))
        self._updateParameters2()

    def selectParametersCS(self):
        tmp = str(self.comboBox_ParametersCS.currentText())
        if tmp == 'Use full detector FOV':
            self.BSC_useFullDet = True
            for item in [self.edit_BSC_CS, self.but_SetBSC_CS]:
                item.setVisible(False)
            self.label_200.setVisible(True)
        if tmp == 'Select central stop size':
            self.BSC_useFullDet = False
            for item in [self.edit_BSC_CS, self.but_SetBSC_CS]:
                item.setVisible(True)
            self.label_200.setVisible(False)
        self._updateParameters2()

    def clickButtonSetAttribute(self, att_name, call_update):
        _edit = getattr(self, f'edit_{att_name}')
        if self.activeVar == att_name:
            self.activeVar = None
        try:
            _tmpval = UTILS.get_array_from_str(_edit.text())
        except Exception as e:
            QtWidgets.QMessageBox.critical(
                self, 'Error',
                ('Could not parse input on attribute '
                 f'"{CONST.PLOT_TITLES[att_name]}" value or multiple '
                 f'input parameter arrays selected:\n{e}'),
                buttons=QtWidgets.QMessageBox.Ok)
            return
        _edit.setText(str(_tmpval))
        setattr(self, att_name, _tmpval / CONST.SCALING_FACTOR[att_name])
        if _tmpval.size > 1:
            self.activeVar = att_name
        call_update()

    def changePlot1Type(self):
        self.plot1Type = str(self.comboBox_plot1.currentText())
        self.RefreshPlot()

    def changePlot2Type(self):
        self.plot2Type = str(self.comboBox_plot2.currentText())
        self.RefreshPlot()

    def changePlot1Autoscale(self):
        _txt = self.comboBox_plot1_autoscale.currentText()
        self.plot1Autoscale = True if _txt == 'True' else False
        self.RefreshPlot()

    def changePlot2Autoscale(self):
        _txt = self.comboBox_plot2_autoscale.currentText()
        self.plot2Autoscale = True if _txt == 'True' else False
        self.RefreshPlot()

    def changePlot1LimitLow(self):
        self.plot1ylow = self.edit_plot1Low.value()
        if self.plot1ylow >= self.plot1yhigh:
            self.plot1ylow = self.plot1yhigh - 1
        if not self.ignoreUpdate:
            self.RefreshPlot()

    def changePlot1LimitHigh(self):
        self.plot1yhigh = self.edit_plot1High.value()
        if self.plot1ylow >= self.plot1yhigh:
            self.plot1yhigh = self.plot1ylow + 1
        if not self.ignoreUpdate:
            self.RefreshPlot()

    def changePlot2LimitLow(self):
        self.plot2ylow = self.edit_plot2Low.value()
        if self.plot2ylow >= self.plot2yhigh:
            self.plot2ylow = self.plot2yhigh - 1
        if not self.ignoreUpdate:
            self.RefreshPlot()

    def changePlot2LimitHigh(self):
        self.plot2yhigh = self.edit_plot2High.value()
        if self.plot2ylow >= self.plot2yhigh:
            self.plot2yhigh = self.plot2ylow + 1
        if not self.ignoreUpdate:
            self.RefreshPlot()

    def changePlot1Variable(self):
        self.plot1var = CONST.PLOT_VAR_NAMES[
            str(self.comboBox_plot1_variable.currentText())]
        self.RefreshPlot()

    def changePlot2Variable(self):
        self.plot2var = CONST.PLOT_VAR_NAMES[
            str(self.comboBox_plot2_variable.currentText())]
        self.RefreshPlot()

    def RefreshPlot(self):
        if self.figureExists:
            self.figure2ax.lines.pop(0)
            self.figure2ax.lines.pop(0)
            self.figure2ax.lines.pop(0)
        if self.ax1plotContent:
            self.f1ax1.cla()
            self.ax1plotContent = False
        if self.ax2plotContent:
            self.f1ax2.cla()
            self.ax2plotContent = False
        if self.activeVar == None or getattr(self, self.activeVar).size == 1:
            return

        self.plotTitle = CONST.PLOT_TITLES[self.activeVar]
        self.plotx = (getattr(self, self.activeVar)
                      * CONST.SCALING_FACTOR[self.activeVar])

        if self.plot1var is not None:
            self.tmpval = (getattr(self, self.plot1var)
                           * CONST.SCALING_FACTOR[self.plot1var])
            if self.tmpval.size == 1:
                self.tmpval = np.array([self.tmpval] * self.plotx.size)
            if self.plot1Type == 'logarithmic':
                self.f1ax1.set_yscale('log')
                self.f1ax1.semilogy(
                    self.plotx, self.tmpval, color=CONST.COLORS[3],
                    linewidth=1.5, markeredgewidth=0, markersize=4, marker='o')
            elif self.plot1Type == 'linear':
                self.f1ax1.set_yscale('linear')
                self.f1ax1.plot(
                    self.plotx, self.tmpval, color=CONST.COLORS[3],
                    linewidth=1.5, markeredgewidth=0, markersize=4, marker='o')
            self.f1ax1.set_ylabel(CONST.PLOT_AXIS_LABELS[self.plot1var],
                                  color=CONST.COLORS[3])
            self.ax1plotContent = True
            self.f1ax1.set_xlabel(self.plotTitle)
            if self.plot1Autoscale:
                ylow, yhigh = np.amin(self.tmpval), np.amax(self.tmpval)
                ylow = min(0.995 * ylow, 1.01 * ylow)
                yhigh = max(0.995 * yhigh, 1.01 * yhigh)
                self.f1ax1.set_ylim([ylow, yhigh])
                self.ignoreUpdate = True
                self.edit_plot1Low.setValue(ylow)
                self.edit_plot1High.setValue(yhigh)
                self.edit_plot1Low.setValue(ylow)
                self.edit_plot1High.setValue(yhigh)
                self.ignoreUpdate = False
            else:
                self.f1ax1.set_ylim([self.plot1ylow, self.plot1yhigh])
            self.f1ax1.set_xlim([self.plotx[0], self.plotx[-1]])
        if self.plot2var != None:
            self.tmpval = (getattr(self, self.plot2var)
                           * CONST.SCALING_FACTOR[self.plot2var])
            if self.tmpval.size == 1:
                self.tmpval = np.array([self.tmpval] * self.plotx.size)
            if self.plot2Type == 'logarithmic':
                self.f1ax2.set_yscale('log')
                self.f1ax2.semilogy(
                    self.plotx, self.tmpval, color=CONST.COLORS[1],
                    linewidth=1.5, markeredgewidth=0, markersize=4, marker='o')
            elif self.plot2Type == 'linear':
                self.f1ax2.set_yscale('linear')
                self.f1ax2.plot(
                    self.plotx, self.tmpval, color=CONST.COLORS[1],
                    linewidth=1.5, markeredgewidth=0, markersize=4, marker='o')
            self.f1ax2.set_ylabel(CONST.PLOT_AXIS_LABELS[self.plot2var],
                                  color=CONST.COLORS[1])
            self.f1ax1.set_xlabel(self.plotTitle)
            self.ax2plotContent = True
            if self.plot2Autoscale:
                ylow, yhigh = np.amin(self.tmpval), np.amax(self.tmpval)
                ylow = min(0.99 * ylow, 1.005 * ylow)
                yhigh = max(0.99 * yhigh, 1.005 * yhigh)
                self.f1ax2.set_ylim([ylow, yhigh])
                self.ignoreUpdate = True
                self.edit_plot2Low.setValue(ylow)
                self.edit_plot2High.setValue(yhigh)
                self.edit_plot2Low.setValue(ylow)
                self.edit_plot2High.setValue(yhigh)
                self.ignoreUpdate = False
            if not self.plot2Autoscale:
                self.f1ax2.set_ylim([self.plot2ylow, self.plot2yhigh])
            self.f1ax2.set_xlim([self.plotx[0], self.plotx[-1]])

        if not self.plot2Autoscale:
            self.f1ax2.set_ylim([self.plot2ylow, self.plot2yhigh])

        if self.check_NFZP.size == 1:
            self.check_NFZP = np.array([self.check_NFZP] * self.plotx.size)
        if self.check_DOF.size == 1:
            self.check_DOF = np.array([self.check_DOF] * self.plotx.size)
        if self.check_NBSC.size == 1:
            self.check_NBSC = np.array([self.check_NBSC] * self.plotx.size)
        self.figure2ax.plot(
            self.plotx, self.check_NFZP + 0.05, color=CONST.COLORS[3],
            linewidth=1.5, markeredgewidth=0, markersize=4, marker='o'
        )
        self.figure2ax.plot(
            self.plotx, self.check_DOF, color=CONST.COLORS[1], linewidth=1.5,
            markeredgewidth=0, markersize=4, marker='o')
        self.figure2ax.plot(
            self.plotx, self.check_NBSC - 0.05, color=CONST.COLORS[2],
            linewidth=1.5, markeredgewidth=0, markersize=4, marker='o')
        self.figure2ax.set_ylim(-0.5, 1.8)
        self.figure2ax.set_xlim([self.plotx[0], self.plotx[-1]])
        self.figure2ax.set_yticks([0, 1])
        self.figure2ax.set_yticklabels(['warning', 'OK'])
        self.figure2ax.set_xlabel(self.plotTitle)
        if not self.figureExists:
            self.figure2.text(0.15, 0.79, 'Number of FZP zones',
                              color=CONST.COLORS[3])
            self.figure2.text(0.425, 0.79, 'Depth of field',
                              color=CONST.COLORS[1])
            self.figure2.text(0.65, 0.79, 'Number of BSC zones',
                              color=CONST.COLORS[2])
            self.figureExists = True
        self.figure1Canvas.draw()
        self.figure2Canvas.draw()

    def writeData(self):
        if self.zip_basedir == None:
            self.zip_fname = QtWidgets.QFileDialog.getSaveFileName(
                self, 'Name of logfile', '', "Zip files (*.zip)")[0]
        elif self.zip_basedir != None:
            self.zip_fname = QtWidgets.QFileDialog.getSaveFileName(
                self, 'Name of logfile', self.zip_basedir, "Zip files (*.zip)"
            )[0]
        self.zip_basedir = os.path.dirname(self.zip_fname)
        self.zip_filename = os.path.basename(self.zip_fname)
        if self.zip_fname not in ['', None]:
            try:
                with zipfile.ZipFile(self.zip_fname, 'w') as zobject:
                    self.zip_fobject = True
            except:
                self.zip_fobject = None
                QtWidgets.QMessageBox.critical(
                    self, 'Error',
                    ('The selected file:\n\t%s\nis ' % (self.zip_fname)
                     + 'write-protected and cannot be opened.'),
                    buttons=QtWidgets.QMessageBox.Ok)
                return
            if self.activeVar == None:
                return

            if getattr(self, self.activeVar).size > 1:
                self.plotx = (getattr(self, self.activeVar)
                              * CONST.SCALING_FACTOR[self.activeVar])
                for item in CONST.PLOT_AXIS_LABELS.keys():
                    self.plotTitle = CONST.PLOT_TITLES[self.activeVar]
                    self.tmpval = (getattr(self, item)
                                   * CONST.SCALING_FACTOR[item])
                    if self.tmpval.size == 1:
                        self.tmpval = np.array(
                            [self.tmpval] * self.plotx.size)

                    self.f3ax.plot(
                        self.plotx, self.tmpval, color=CONST.COLORS[3],
                        linewidth=1.5, markeredgewidth=0, markersize=4,
                        marker='o')
                    self.f3ax.set_ylabel(CONST.PLOT_AXIS_LABELS[item],
                                         color=CONST.COLORS[3])
                    self.f3ax.set_xlabel(self.plotTitle)
                    ylow = np.amin(self.tmpval)
                    yhigh = np.amax(self.tmpval)
                    ylow = min(0.995 * ylow, 1.01 * ylow)
                    yhigh = max(0.995 * yhigh, 1.01 * yhigh)
                    self.f3ax.set_ylim([ylow, yhigh])
                    self.f3ax.grid(True)
                    self.figure3.savefig(
                        self.zip_basedir + os.sep + item
                        + '_vs_%s.png' % self.activeVar
                    )
                    np.savetxt(
                        self.zip_basedir + os.sep + item
                        + '_vs_%s.txt' % self.activeVar,
                        np.asarray([self.plotx, self.tmpval])
                    )
            self.txt_parameters = ''
            for item in CONST.PLOT_TITLES.keys():
                writeItem = True
                if item == 'dist_sample_det' and self.det_useEffPix:
                    writeItem = False
                if item == 'det_eff_pix' and not self.det_useEffPix:
                    writeItem = False
                if item == 'BSC_CS' and self.BSC_useFullDet:
                    writeItem = False
                if item == 'BSC_field':
                    writeItem = False
                if writeItem:
                    self.txt_parameters += (
                        UTILS.stringFill(CONST.PLOT_TITLES[item] + ':', 40)
                        + ' '
                        + str(self.__dict__[item]
                              * CONST.SCALING_FACTOR[item]) + '\n'
                    )
            with open(self.zip_basedir + os.sep + '_Input_Parameters.txt',
                      'w') as f:
                f.write(self.txt_parameters)
            try:
                with zipfile.ZipFile(self.zip_fname, 'w') as zobject:
                    for item in CONST.PLOT_AXIS_LABELS.keys():
                        zobject.write(
                            self.zip_basedir + os.sep + item
                            + '_vs_%s.png' % self.activeVar,
                            item + '_vs_%s.png' % self.activeVar
                        )
                        zobject.write(
                            self.zip_basedir + os.sep + item
                            + '_vs_%s.txt' % self.activeVar,
                            item + '_vs_%s.txt' % self.activeVar
                        )
                        os.remove(
                            self.zip_basedir + os.sep + item
                            + '_vs_%s.txt' % self.activeVar
                        )
                        os.remove(
                            self.zip_basedir + os.sep + item
                            + '_vs_%s.png' % self.activeVar
                        )
                    zobject.write(
                        self.zip_basedir + os.sep + '_Input_Parameters.txt',
                        '_Input_Parameters.txt'
                    )
                    os.remove(
                        self.zip_basedir + os.sep + '_Input_Parameters.txt'
                    )
            except:
                self.zip_fobject = None
                QtWidgets.QMessageBox.critical(
                    self, 'Error',
                    "Error writing zip file\n\t%s." % (self.zip_fname),
                    buttons=QtWidgets.QMessageBox.Ok
                )

    def closeEvent(self, event, reply=None):
        """Safety check for closing of window."""
        if reply == None:
            reply = QtWidgets.QMessageBox.question(
                self, 'Message', "Are you sure to quit?",
                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                QtWidgets.QMessageBox.No
            )
        if reply == QtWidgets.QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()


def txm_calc(parent=None, name='TXM parameter calculator'):
    app = QtWidgets.QApplication(sys.argv)
    screensize = app.desktop().screenGeometry()
    gui = cTXMCalculator((), name=name, screensize = [screensize.width(),
                                                      screensize.height()])
    if sys.platform == 'win32' or sys.platform == 'win64':
        sys.exit(app.exec_())
    else:
        app.exec_()


if __name__ == '__main__':
    txm_calc()
