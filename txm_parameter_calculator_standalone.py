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
import tempfile
import shutil
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
utils = importlib.util.module_from_spec(spec)
spec.loader.exec_module(utils)


spec = importlib.util.spec_from_file_location(
    'txm_parameter_calculator_generic_values',
    os.path.join(os.path.dirname(__file__),
                 'txm_parameter_calculator_generic_values.py'))
generics = importlib.util.module_from_spec(spec)
spec.loader.exec_module(generics)


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
        self.zip_basedir = ''
        self.zip_filename = None

        self.__init_figures()
        self.__init_optics_parameters()
        self.__init_slot_connections()
        self.__init_widget_visibilities()

    def __init_figures(self):
        """
        Initialize the figures and required attributes.
        """
        self.figure1 = plt.figure(1, figsize=(11, 8), dpi=80)
        self.figure1Canvas = FigureCanvas(self.figure1)
        self.figure1Canvas.setParent(self)
        self.figure1Canvas.setGeometry(410, 200, self.widgetX - 410 - 10,
                                       self.widgetY - 200 - 10)
        self.f1ax1 = self.figure1.add_axes([0.085, 0.1, 0.84, 0.87])
        self.f1ax2 = self.f1ax1.twinx()
        self.plot1_type = 'linear'
        self.plot2_type = 'linear'
        self.plot1ylow = 0
        self.plot1yhigh = 1
        self.plot2ylow = 0
        self.plot2yhigh = 1
        self.plot1var = None
        self.plot2var = None
        self.plot1_autoscale = True
        self.plot2_autoscale = True
        self.axContentPlot1 = False
        self.axContentPlot2 = False
        self.f2plotContent = False
        self.activeVar = None
        self.figureExists = False
        self.ignoreUpdate = False

        self.figure2 = plt.figure(2, figsize=(6, 4), dpi=80)
        self.figure2Canvas = FigureCanvas(self.figure2)
        self.figure2Canvas.setParent(self)
        self.figure2Canvas.setGeometry(890, 10, self.widgetX - 890 - 10,
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
        for _att in ['energy', 'bandwidth', 'FZP_dr', 'FZP_D', 'M_det',
                     'det_PixSize', 'det_Nhor', 'det_Nvert', 'dist_sample_det',
                     'BSC_D', 'BSC_CS', 'BSC_field']:
            _val = generics.__getattribute__(_att.upper())
            setattr(self, _att, np.asarray(_val))
            self._update_edit_value(_att, _val)

        self.det_useEffPix = False
        self.BSC_useFullDet = False

    def _update_edit_value(self, att, value):
        """
        Update an input edit with a new value.

        Parameters
        ----------
        att : str
            The attribute name.
        value : object
            Any object which has a string representation.
        """
        _edit = getattr(self, f'edit_{att}')
        _edit.setText(str(value * CONST.SCALING_FACTOR[att]))

    def __init_slot_connections(self):
        """
        Connect all slots and signals.
        """
        self.edit_energy.editingFinished.connect(partial(
            self.update_attribute, 'energy', self._updateParameters1))

        self.edit_bandwidth.editingFinished.connect(partial(
            self.update_attribute, 'bandwidth',
            self._updateParameters1))

        self.edit_FZP_dr.editingFinished.connect(partial(
            self.update_attribute, 'FZP_dr', self._updateParameters1))
        self.edit_FZP_D.editingFinished.connect(partial(
            self.update_attribute, 'FZP_D', self._updateParameters1))
        self.edit_M_det.editingFinished.connect(partial(
            self.update_attribute, 'M_det', self._updateParameters2))
        self.edit_det_PixSize.editingFinished.connect(partial(
            self.update_attribute, 'det_PixSize',
            self._updateParameters2))
        self.edit_det_Nhor.editingFinished.connect(partial(
            self.update_attribute, 'det_Nhor', self._updateParameters2))
        self.edit_det_Nvert.editingFinished.connect(partial(
            self.update_attribute, 'det_Nvert',
            self._updateParameters2))

        self.comboBox_ParametersDet.currentIndexChanged.connect(
            self.selectParametersDet)

        self.edit_dist_sample_det.editingFinished.connect(partial(
            self.update_attribute, 'dist_sample_det',
            self._updateParameters2))
        self.edit_eff_pix.editingFinished.connect(partial(
            self.update_attribute, 'eff_pix', self._updateParameters2))
        self.edit_BSC_D.editingFinished.connect(partial(
            self.update_attribute, 'BSC_D', self._updateParameters3))

        self.comboBox_ParametersCS.currentIndexChanged.connect(
            self.selectParametersCS)
        self.edit_BSC_CS.editingFinished.connect(partial(
            self.update_attribute, 'BSC_CS', self._updateParameters3))
        self.edit_BSC_field.editingFinished.connect(partial(
            self.update_attribute, 'BSC_field',
            self._updateParameters3))

        self.but_SaveData.clicked.connect(self.writeData)
        self._updateParameters1()

        # plotting parameters:
        self.edit_plot1low.valueChanged.connect(partial(
            self.change_plot_limit, 1, 'low'))
        self.edit_plot1high.valueChanged.connect(partial(
            self.change_plot_limit, 1, 'high'))
        self.comboBox_plot1_type.currentIndexChanged.connect(partial(
            self.change_plot_type, 1))
        self.comboBox_plot1_autoscale.currentIndexChanged.connect(
            partial(self.change_plot_autoscale, 1))
        self.comboBox_plot1_variable.currentIndexChanged.connect(
            partial(self.change_plot_variable, 1))

        self.edit_plot2low.valueChanged.connect(partial(
            self.change_plot_limit, 2, 'low'))
        self.edit_plot2high.valueChanged.connect(partial(
            self.change_plot_limit, 2, 'high'))
        self.comboBox_plot2_variable.currentIndexChanged.connect(
            partial(self.change_plot_variable, 2))
        self.comboBox_plot2_type.currentIndexChanged.connect(partial(
            self.change_plot_type, 2))
        self.comboBox_plot2_autoscale.currentIndexChanged.connect(
            partial(self.change_plot_autoscale, 2))

    def __init_widget_visibilities(self):
        """
        Initialize styles and layout and set widget properties.
        """
        for item in [self.label_input_dist_sample_det,
                     self.edit_dist_sample_det, self.label_eff_pix,
                     self.label_name_eff_pix]:
            item.setVisible(True)
        for item in [self.label_input_eff_pix, self.edit_eff_pix,
                     self.label_name_dist_sample_det,
                     self.label_dist_sample_det]:
            item.setVisible(False)
        self.edit_dist_sample_det.setText(str(self.dist_sample_det))

        self.edit_BSC_CS.setVisible(True)
        self.label_BSC_CS.setVisible(False)
        self.refresh_plots()
        self.show()

    def _update_label_value(self, name):
        """
        Updathe the label with the name with the current value
        (or values for arrays).

        Parameters
        ----------
        name : str
            The variable name.
        """
        _vals = getattr(self, name) * CONST.SCALING_FACTOR[name]
        if _vals.size == 1:
            _text = str(np.round(_vals, 4))
        else:
            _text = self.__get_range_string_from_array(_vals)
        _label = getattr(self, f'label_{name}')
        _label.setText(_text)

    @staticmethod
    def __get_range_string_from_array(arr):
        """
        Get a short string which describes the value range of an array.

        Parameters
        ----------
        arr : np.ndarray
            The input array

        Returns
        -------
        str :
            The formatted string with the array range.
        """
        _low = np.round(arr[0], 4)
        _high = np.round(arr[-1], 4)
        _text = str(f'{_low} [...] {_high}')
        return _text

    def update_attribute(self, att_name, call_update):
        """
        Generic method to update a parameter.

        This method will read the QLineEdit and parse the value to an array.
        The required update function is called to have all derived values
        up to date with the new input.

        Parameters
        ----------
        att_name : str
            The name of the attribute to update.
        call_update : method
            The name of the update method to calculate all derived values.
        """
        _edit = getattr(self, f'edit_{att_name}')
        if self.activeVar == att_name:
            self.activeVar = None
        try:
            _tmpval = utils.get_array_from_str(_edit.text())
        except Exception as e:
            QtWidgets.QMessageBox.critical(
                self, 'Error',
                ('Could not parse input on attribute '
                 f'"{CONST.PLOT_TITLES[att_name]}" value or multiple '
                 f'input parameter arrays selected:\n{e}'),
                buttons=QtWidgets.QMessageBox.Ok)
            return
        if _tmpval.size > 1:
            _text = '[' + ', '.join([str(val) for val in _tmpval]) + ']'
        else:
            _text = str(_tmpval)
        _edit.setText(_text)
        setattr(self, att_name, _tmpval / CONST.SCALING_FACTOR[att_name])
        if _tmpval.size > 1:
            self.activeVar = att_name
        call_update()

    def _updateParameters1(self):
        """
        Update all parameters from group 1 (FZP parameters).
        """
        self.wavelength = 12.398e-10 / self.energy
        self.FZP_resolution = np.maximum(
            1.22 * self.FZP_dr,
            0.61 * (self.FZP_D * self.FZP_dr * self.bandwidth)**0.5)
        self.FZP_objectNA = np.asarray(self.wavelength / (2 * self.FZP_dr))
        self.FZP_DOF = np.asarray(2 * self.FZP_dr ** 2 / self.wavelength)
        self.FZP_Nzones = np.asarray(self.FZP_D / (4 * self.FZP_dr))
        self.FZP_f = np.asarray(self.FZP_D * self.FZP_dr / self.wavelength)

        for _name in ['wavelength', 'FZP_resolution', 'FZP_objectNA',
                      'FZP_DOF', 'FZP_Nzones', 'FZP_f']:
            self._update_label_value(_name)
        self._updateParameters2()

    def _updateParameters2(self):
        """
        Update all parameters from group 1 (Experimental layout / detector).
        """
        if self.det_useEffPix:
            self.M_total = np.asarray(self.det_PixSize / self.eff_pix)
            self.M_xray = np.asarray(self.M_total / self.M_det)
            self.dist_sample_FZP = np.asarray(
                self.FZP_f * (1.0 + self.M_xray) / self.M_xray)
            self.dist_FZP_det = np.asarray(self.FZP_f * (1.0 + self.M_xray))
            self.dist_sample_det = np.asarray(self.dist_FZP_det
                                              + self.dist_sample_FZP)
        else:  # i.e. use distance sample-det
            self.dist_sample_FZP = utils.calc_working_dists(
                self.dist_sample_det, self.FZP_f)[0]
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
                 / (self.dist_FZP_det + self.M_xray ** 2
                    * self.dist_sample_FZP)
                 + 1) ** 2 - 2)
        self.FZP_FOV = self.FZP_angularFOV * 2 * self.dist_sample_FZP

        for _name in ['det_FOVhor', 'det_FOVvert', 'dist_sample_det',
                      'eff_pix', 'M_xray', 'M_total', 'dist_sample_FZP',
                      'FZP_angularFOV', 'FZP_FOV']:
            self._update_label_value(_name)
        self._updateParameters3()

    def _updateParameters3(self):
        """
        Update all parameters from group 1 (beamshaper / illumination).
        """
        self.BSC_f = np.asarray(self.BSC_D * self.FZP_dr / self.wavelength)

        self.dist_BSC_sample = utils.calc_working_dists(CONST.SOURCE_DIST,
                                                        self.BSC_f)[0]
        self.dist_source_BSC = CONST.SOURCE_DIST - self.dist_BSC_sample
        if self.BSC_useFullDet:
            self.BSC_CShor = np.asarray(
                self.det_PixSize * self.det_Nhor * self.dist_BSC_sample
                / self.dist_sample_det / self.M_det)
            self.BSC_CSvert = np.asarray(
                self.det_PixSize * self.det_Nvert * self.dist_BSC_sample
                / self.dist_sample_det / self.M_det)
            self.BSC_CS = np.where(
                self.BSC_CShor >= self.BSC_CSvert, self.BSC_CShor,
                self.BSC_CSvert)
        self.BSC_effFOV = (self.BSC_CS / self.dist_BSC_sample
                           * self.dist_sample_det / self.M_xray)
        _tmpval = 1 - self.BSC_CS ** 2 / (np.pi * (self.BSC_D / 2) ** 2)
        self.BSC_freeArea = np.where(_tmpval > 0, _tmpval, 0)
        tmp_hor = np.minimum(self.det_FOVhor, self.BSC_effFOV)
        eff_hor = np.where(
            tmp_hor < self.BSC_field, tmp_hor / self.BSC_field, 1)
        tmp_ver = np.minimum(self.det_FOVvert, self.BSC_effFOV)
        eff_vert = np.where(
            tmp_ver < self.BSC_field, tmp_ver / self.BSC_field, 1)

        self.total_eff =  eff_hor * eff_vert * self.BSC_freeArea

        for _name in ['BSC_CS', 'BSC_f', 'BSC_effFOV',
                      'BSC_freeArea', 'dist_BSC_sample', 'total_eff']:
            self._update_label_value(_name)

        if tmp_hor.size == 1:
            _text = (f'{tmp_hor*1e6:.1f} um \u2259 '
                     f'{int(tmp_hor/self.eff_pix)} px')
        else:
            _text = self.__get_range_string_from_array(tmp_hor * 1e6)
        self.label_FOV_hor.setText(_text)
        if tmp_ver.size == 1:
            _text = (f'{tmp_ver*1e6:.1f} um \u2259 '
                     f'{int(tmp_ver/self.eff_pix)} px')
        else:
            _text = self.__get_range_string_from_array(tmp_ver * 1e6)
        self.label_FOV_vert.setText(_text)

        self.check_NFZP = (
            np.where((self.FZP_Nzones > 100), True, False)
            * np.where((self.FZP_Nzones < 1 / self.bandwidth), True, False))
        self.check_DOF = np.where(self.FZP_DOF >= self.BSC_effFOV, True,
                                     False)
        self.refresh_plots()

    def selectParametersDet(self):
        tmp = str(self.comboBox_ParametersDet.currentText())
        if tmp == 'Set detector effective pixel size':
            self.det_useEffPix = True
            self.edit_eff_pix.setText(str(self.eff_pix * 1e9))
        else:
            self.det_useEffPix = False
            self.edit_dist_sample_det.setText(str(self.dist_sample_det))
        for item in [self.label_input_dist_sample_det,
                     self.edit_dist_sample_det, self.label_eff_pix,
                     self.label_name_eff_pix]:
            item.setVisible(not self.det_useEffPix)
        for item in [self.label_input_eff_pix, self.edit_eff_pix,
                     self.label_name_dist_sample_det,
                     self.label_dist_sample_det]:
            item.setVisible(self.det_useEffPix)
        self._updateParameters2()

    def selectParametersCS(self):
        tmp = str(self.comboBox_ParametersCS.currentText())
        if tmp == 'Use full detector FOV':
            self.BSC_useFullDet = True
        else:
            self.BSC_useFullDet = False
        self.edit_BSC_CS.setVisible(not self.BSC_useFullDet)
        self.label_BSC_CS.setVisible(self.BSC_useFullDet)
        self._updateParameters2()

    def change_plot_type(self, index):
        _box = getattr(self, f'comboBox_plot{index}_type')
        _text = _box.currentText()
        setattr(self, f'plot{index}_type', _text)
        self.refresh_plots()

    def change_plot_autoscale(self, index):
        _box = getattr(self, f'comboBox_plot{index}_autoscale')
        _txt = _box.currentText()
        _val = True if _txt == 'True' else False
        setattr(self, f'plot{index}_autoscale', _val)
        self.refresh_plots()

    def change_plot_limit(self, index, limit):
        _low_edit = getattr(self, f'edit_plot{index}low')
        _high_edit = getattr(self, f'edit_plot{index}high')
        _low = _low_edit.value()
        _high = _high_edit.value()
        if _low >= _high:
            if limit == 'low':
                _high = _low + 1
            elif limit == 'high':
                _low = _high - 1
        setattr(self, f'plot{index}ylow', _low)
        setattr(self, f'plot{index}yhigh', _high)
        if not self.ignoreUpdate:
            self.refresh_plots()

    def change_plot_variable(self, index):
        _box = getattr(self, f'comboBox_plot{index}_variable')
        _txt = _box.currentText()
        _var = CONST.PLOT_VAR_NAMES[_txt]
        setattr(self, f'plot{index}var', _var)
        self.refresh_plots()

    def refresh_plots(self):
        self.__clear_plot()
        if self.activeVar == None or getattr(self, self.activeVar).size == 1:
            return

        self.plotTitle = CONST.PLOT_TITLES[self.activeVar]
        self.plotx = (getattr(self, self.activeVar)
                      * CONST.SCALING_FACTOR[self.activeVar])

        if self.plot1var is not None:
            self.__plot_variable(1, CONST.COLORS[3])
        if self.plot2var is not None:
            self.__plot_variable(2, CONST.COLORS[1])
        self.__plot_checks()
        self.figure1Canvas.draw()
        self.figure2Canvas.draw()

    def __clear_plot(self):
        """
        Remove any existing items from the plot.
        """
        if self.figureExists:
            self.figure2ax.cla()
        if self.axContentPlot1:
            self.f1ax1.cla()
            self.axContentPlot1 = False
        if self.axContentPlot2:
            self.f1ax2.cla()
            self.axContentPlot2 = False

    def __plot_variable(self, index, color):
        """
        Plot a figure for the specified variable

        Parameters
        ----------
        index : int
            The variable index. Can be 1 or 2.
        color : str
            A RGB color code for the line.
        """
        _ax = getattr(self, f'f1ax{index}')
        _plotvar = getattr(self, f'plot{index}var')
        _tmpval = getattr(self, _plotvar) * CONST.SCALING_FACTOR[_plotvar]
        if _tmpval.size == 1:
            _tmpval = np.array([_tmpval] * self.plotx.size)
        if getattr(self, f'plot{index}_type') == 'logarithmic':
            _ax.set_yscale('log')
            _plotfunc = _ax.semilogy
        else: # linear plot
            _ax.set_yscale('linear')
            _plotfunc = _ax.plot
        _plotfunc(self.plotx, _tmpval, color=color,
                  linewidth=1.5, markeredgewidth=0, markersize=4, marker='o')
        _ax.set_ylabel(CONST.PLOT_AXIS_LABELS[self.plot1var], color=color)
        _ax.set_xlabel(self.plotTitle)
        setattr(self, f'axContentPlot{index}', True)
        if getattr(self, f'plot{index}_autoscale'):
            ylow, yhigh = np.amin(_tmpval), np.amax(_tmpval)
            ylow = min(0.995 * ylow, 1.01 * ylow)
            yhigh = max(0.995 * yhigh, 1.01 * yhigh)
            _ax.set_ylim([ylow, yhigh])
            self.ignoreUpdate = True
            _edit_low = getattr(self, f'edit_plot{index}low')
            _edit_low.setValue(ylow)
            _edit_high = getattr(self, f'edit_plot{index}high')
            _edit_high.setValue(yhigh)
            self.ignoreUpdate = False
        else:
            _ax.set_ylim([getattr(self, f'plot{index}ylow'),
                          getattr(self, f'plot{index}yhigh')])
        _ax.set_xlim([self.plotx[0], self.plotx[-1]])

    def __plot_checks(self):
        """
        Plot the bandwidth and depth of focus checks.
        """
        if self.check_NFZP.size == 1:
            self.check_NFZP = np.array([self.check_NFZP] * self.plotx.size)
        if self.check_DOF.size == 1:
            self.check_DOF = np.array([self.check_DOF] * self.plotx.size)
        self.figure2ax.plot(
            self.plotx, self.check_NFZP + 0.05, color=CONST.COLORS[3],
            linewidth=1.5, markeredgewidth=0, markersize=4, marker='o')
        self.figure2ax.plot(
            self.plotx, self.check_DOF, color=CONST.COLORS[1], linewidth=1.5,
            markeredgewidth=0, markersize=4, marker='o')
        self.figure2ax.set_ylim(-0.5, 1.8)
        self.figure2ax.set_xlim([self.plotx[0], self.plotx[-1]])
        self.figure2ax.set_yticks([0, 1])
        self.figure2ax.set_yticklabels(['warning', 'OK'])
        self.figure2ax.set_xlabel(self.plotTitle)
        if not self.figureExists:
            self.figure2.text(0.15, 0.79, 'Number of FZP zones',
                              color=CONST.COLORS[3])
            self.figure2.text(0.65, 0.79, 'Depth of field',
                              color=CONST.COLORS[1])
            self.figureExists = True

    def writeData(self):
        """
        Write data to txt files and plots and zip everything into a single
        zip file.
        """
        if not self.__check_for_active_var():
            return
        self.__query_zip_filename()
        if not self.zip_file_ok:
            return
        self.tmpdir = tempfile.mkdtemp()
        try:
            self.__create_figures_and_data_for_zip()
            self.__create_file_with_input_parameters()
            self.__write_zo_zip()
        except:
            raise
        finally:
            shutil.rmtree(self.tmpdir)

    def __check_for_active_var(self):
        """
        Check that an active var has been set and its size is larger than 1.

        Returns
        -------
        bool :
            Result of the check.
        """
        if self.activeVar is None or getattr(self, self.activeVar).size == 1:
            QtWidgets.QMessageBox.warning(
                self, 'Warning',
                'Saving of plots requires focus on one input variable with '
                'more than one entries. Aborting ...',
                buttons=QtWidgets.QMessageBox.Ok)
            return False
        return True

    def __query_zip_filename(self):
        """
        Query the user for a zip filename and check if the file can be opened.
        """
        self.zip_file_ok = False
        self.zip_fname = QtWidgets.QFileDialog.getSaveFileName(
            self, 'Name of archive filename', '', "Zip files (*.zip)")[0]
        self.zip_basedir = os.path.dirname(self.zip_fname)
        self.zip_filename = os.path.basename(self.zip_fname)
        if self.zip_fname not in ['', None]:
            try:
                with zipfile.ZipFile(self.zip_fname, 'w') as zobject:
                    self.zip_file_ok = True
            except:
                QtWidgets.QMessageBox.critical(
                    self, 'Error',
                    (f'The selected file:\n\t{self.zip_fname}\nis '
                     'write-protected and cannot be opened. Aborting ...'),
                    buttons=QtWidgets.QMessageBox.Ok)

    def __create_figures_and_data_for_zip(self):
        """
        Create all figures for export.
        """
        _plotx = (getattr(self, self.activeVar)
                  * CONST.SCALING_FACTOR[self.activeVar])
        for item in CONST.PLOT_AXIS_LABELS.keys():
            _val = getattr(self, item) * CONST.SCALING_FACTOR[item]
            if _val.size == 1:
                _val = np.array([_val] * _plotx.size)
            self.f3ax.cla()
            self.f3ax.plot(_plotx, _val, color=CONST.COLORS[3],
                           linewidth=1.5, markeredgewidth=0, markersize=4,
                           marker='o')
            self.f3ax.set_ylabel(CONST.PLOT_AXIS_LABELS[item],
                                 color=CONST.COLORS[3])
            self.f3ax.set_xlabel(CONST.PLOT_TITLES[self.activeVar])
            ylow = np.amin(_val)
            yhigh = np.amax(_val)
            ylow = min(0.995 * ylow, 1.01 * ylow)
            yhigh = max(0.995 * yhigh, 1.01 * yhigh)
            self.f3ax.set_ylim([ylow, yhigh])
            self.f3ax.grid(True)
            self.figure3.savefig(
                self.tmpdir + os.sep + item + f'_vs_{self.activeVar}.png')
            np.savetxt(
                self.tmpdir + os.sep + item + f'_vs_{self.activeVar}.txt',
                np.asarray([_plotx, _val]).T,
                header=f'Column 0: {self.activeVar}\nColumn 1: {item}')

    def __create_file_with_input_parameters(self):
        """
        Create a text file which includes all the input parameters for
        reference.
        """
        _txt_parameters = ''
        for item in CONST.PLOT_TITLES.keys():
            # writeItem = True
            if ((item == 'dist_sample_det' and self.det_useEffPix)
                    or (item == 'eff_pix' and not self.det_useEffPix)
                    or (item == 'BSC_CS' and self.BSC_useFullDet)
                    or item == 'BSC_field'):
                continue
            _txt_parameters += (
                utils.stringFill(CONST.PLOT_TITLES[item] + ':', 40) + ' '
                + str(getattr(self, item) * CONST.SCALING_FACTOR[item]) + '\n')
        with open(self.tmpdir + os.sep + '_Input_Parameters.txt', 'w') as f:
            f.write(_txt_parameters)

    def __write_zo_zip(self):
        """
        Write all the stored text files and images to the zip file.
        """
        with zipfile.ZipFile(self.zip_fname, 'w') as zobject:
            for item in CONST.PLOT_AXIS_LABELS.keys():
                zobject.write(
                    self.tmpdir + os.sep + item + f'_vs_{self.activeVar}.png',
                    item + f'_vs_{self.activeVar}.png')
                zobject.write(
                    self.tmpdir + os.sep + item + f'_vs_{self.activeVar}.txt',
                    item + f'_vs_{self.activeVar}.txt')
            zobject.write(self.tmpdir + os.sep + '_Input_Parameters.txt',
                        '_Input_Parameters.txt')

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
