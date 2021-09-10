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
Module with the utility functions for the txm_calc GUI.
"""

__author__      = "Malte Storm"
__copyright__   = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "1.0.0"
__maintainer__ = "Malte Storm"
__status__ = "Alpha"
__all__ = ['stringFill']

import numpy as np


def stringFill(_string, _len, fill_front=False, fill_dots=True):
    """
    Fill a string up to a specific length with filling characters.

    If a string is longer than the defined length, it will be cropped.

    Examples
    --------
        1. stringFill('test 123', 12)
            -->  'test 123 ...'
        2. stringFill('test 123', 12, fill_front = True)
            --> '... test 123'

    Parameters
    ----------
    _string : str
        The string to be processed.

    _len : int
        The length of the return string.

    fill_front : bool, optional
        Keyword to select whether the input should be padded
        in front or at the back. The default is False.

    fill_dots : bool, optional
        Keyword to select whether the string should be padded
        with dots. If False, spaces are used instead. The default is True.

    Returns
    -------
    str
        The padded string.
    """
    tmp = len(_string)
    if tmp < _len:
        if fill_dots:
            if fill_front:
                return (_len - tmp - 1) * '.' + ' ' + _string
            return _string + ' ' + (_len - tmp - 1) * '.'
        if fill_front:
            return (_len - tmp) * ' ' + _string
        return _string + (_len - tmp) * ' '
    return _string[:_len]


def get_array_from_str(string):
    """
    Get an array from a string expression.

    This function parses a string expression and returns an array.

    Valid inputs are single numbers (integer, float), lists and tuples
    and numpy expressions np.r_, np.arange, and np.linspace

    Parameters
    ----------
    string : str
        The input to be parsed.

    Returns
    -------
    np.ndarray
        The output array.
    """
    # Parse lists and tuples:
    if string[0] in ['(', '['] and string[-1] in [']', ')']:
        return np.asarray([float(item)
                           for item in string[1:-1].split(',')])
    # Parse numpy arrays
    if string[:3] == 'np.':
        string = string[3:]
    if string[:6] == 'numpy.':
        string = string[6:]
    if string[:3] == 'r_[':
        return np.asarray([float(item) for item
                           in string[3:-1].strip('[]()').split(',')])
    if string[:6] == 'arange':
        _items = string[6:].strip('()').split(',')
        if len(_items) == 2:
            return np.arange(float(_items[0]), float(_items[1]))
        if len(_items) == 3:
            return np.arange(float(_items[0]), float(_items[1]),
                             float(_items[2]))
    if string[:8] == 'linspace':
        _items = string[6:].strip('()').split(',')
        if len(_items) == 2:
            return np.linspace(float(_items[0]), float(_items[1]))
        if len(_items) == 3:
            return np.linspace(float(_items[0]), float(_items[1]),
                             float(_items[2]))
    return np.asarray(float(string))
