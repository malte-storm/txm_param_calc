BUTTON_STYLE = """
QPushButton{
    border: solid;
    border-bottom-color:#777777;
    border-bottom-width: 2px;
    border-right-color:#777777;
    border-right-width: 2px;
    border-top-color:#AAAAAA;
    border-top-width: 1px;
    border-left-color:#AAAAAA;
    border-left-width: 1px;
    border-radius: 3px;
    padding: 1px;
    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                               stop: 0 #fafafa, stop: 0.4 #f4f4f4,
                               stop: 0.5 #e7e7e7, stop: 1.0 #fafafa);
}
QPushButton:pressed{
    background:qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                               stop: 0 #dadada, stop: 0.4 #d4d4d4,
                               stop: 0.5 #c7c7c7, stop: 1.0 #dadada)
}
"""
SPIN_STYLE = """
QDoubleSpinBox{
    border: solid;
    border-bottom-color: #AAAAAA;
    border-bottom-width: 1px;
    border-right-color:#AAAAAA;
    border-right-width: 1px;
    border-top-color:#777777;
    border-top-width: 1px;
    border-left-color:#777777;
    border-left-width: 1px;
    border-radius: 3px;
    padding: 1px;
    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                stop: 0 #ECECEC, stop: 0.4 #ECECEC,
                                stop: 0.5 #DCDCDC, stop: 1.0 #ECECEC)
};
"""
TEXTBOX_STYLE = """
QLineEdit{
    border: solid;
    border-bottom-color: #AAAAAA;
    border-bottom-width: 1px;
    border-right-color:#AAAAAA;
    border-right-width: 1px;
    border-top-color:#777777;
    border-top-width: 1px;
    border-left-color:#777777;
    border-left-width: 1px;
    border-radius: 3px;
    padding: 1px;
    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                stop: 0 #ECECEC, stop: 0.4 #ECECEC,
                                stop: 0.5 #DCDCDC, stop: 1.0 #ECECEC)
};
"""

PLOT_TITLES = {
    'energy': 'Energy [keV]',
    'bandwidth':'Bandwidth',
    'FZP_dr':'FZP outer zone width [nm]',
    'FZP_D':'FZP diameter [um]',
    'M_det':'Detector magnification',
    'det_PixSize':'Detector pixel size [um]',
    'det_Nhor':'Detector number of pixels (hor.)',
    'det_Nvert':'Detector number of pixels (vert.)',
    'eff_pix':'Detector effective pixel size [nm]',
    'dist_sample_det':'Distance sample-detector [m]',
    'BSC_D': 'BSC diameter [mm]',
    'BSC_CS':'BSC central stop diameter [mm]',
    'BSC_field': 'BSC field size [um]'
}

PLOT_VAR_NAMES = {
    'None': None,
    'X-ray wavelength': 'wavelength',
    'FZP resolution':'FZP_resolution',
    'FZP object numerical aperture (NA)': 'FZP_objectNA',
    'FZP depth of focus':'FZP_DOF',
    'FZP number of zones':'FZP_Nzones',
    'Detector effective pixel size':'det_eff_pix',
    'Distance sample-detector':'dist_sample_det',
    'Distance sample-FZP':'dist_sample_FZP',
    'Effective pixel size':'det_eff_pix',
    'Geometric FOV (horizontal)': 'det_FOVhor',
    'Geometric FOV (vertical)':'det_FOVvert',
    'X-ray magnification':'M_xray',
    'Total magnification': 'M_total',
    'BSC central stop size':'BSC_CS',
    'BSC focal length': 'BSC_f',
    'BSC number of zones':'BSC_Nzones',
    'BSC effective FOV':'BSC_effFOV',
    'BSC free area': 'BSC_freeArea',
    'Distance BSC-sample':'dist_BSC_sample',
    'FZP theoretical FOV': 'FZP_FOV'
    }

PLOT_AXIS_LABELS = {
    'wavelength':'X-ray wavelength [A]',
    'FZP_resolution':'FZP resolution [nm]',
    'FZP_objectNA': 'FZP object numerical aperture (NA)',
    'FZP_DOF':'FZP depth of focus [um]',
    'FZP_Nzones':'FZP number of zones',
    'det_eff_pix':'Detector effective pixel size [nm]',
    'dist_sample_det':'Distance sample-detector [m]',
    'dist_sample_FZP':'Distance sample-FZP [mm]',
    'dist_BSC_sample':'Distance BSC-sample [m]',
    'det_FOVhor':'Geometric FOV (horizontal) [um]',
    'det_FOVvert':'Geometric FOV (vertical) [um]',
    'M_xray':'X-ray magnification',
    'M_total':'Total magnification',
    'BSC_CS':'Central stop size [mm]',
    'BSC_f':'BSC focal length [m]',
    'BSC_Nzones':'BSC number of zones',
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
    'det_eff_pix':1e9,
    'dist_sample_det':1,
    'dist_sample_FZP':1e3,
    'det_FOVhor':1e6,
    'det_FOVvert':1e6,
    'M_xray':1,
    'M_total':1,
    'BSC_CS':1e3,
    'BSC_f':1,
    'BSC_Nzones':1,
    'BSC_effFOV':1e6,
    'BSC_freeArea':100,
    'energy': 1,
    'bandwidth':1,
    'FZP_dr':1e9,
    'FZP_D':1e6,
    'M_det':1,
    'det_PixSize': 1e6,
    'det_Nhor':1,
    'det_Nvert': 1,
    'BSC_D':1e3,
    'BSC_CS': 1e3,
    'dist_BSC_sample': 1,
    'FZP_FOV':1e6
}

COLORS = ['#FFA500', '#1F45FC', '#4CC417', '#C11B17', '#4B0082',
          '#565051', '#43C6DB', '#43BFC7']
