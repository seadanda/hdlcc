# This file is part of HDL Code Checker.
#
# Copyright (c) 2016 Andre Souto
#
# HDL Code Checker is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# HDL Code Checker is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with HDL Code Checker.  If not, see <http://www.gnu.org/licenses/>.

# pylint: disable=function-redefined, missing-docstring, protected-access

import os
import os.path as p
import logging
from multiprocessing import Queue

import hdlcc

_logger = logging.getLogger(__name__)

class StandaloneProjectBuilder(hdlcc.HdlCodeCheckerBase):
    "Class for testing HdlCodeCheckerBase"
    _msg_queue = Queue()
    _ui_handler = logging.getLogger('UI')
    def __init__(self, project_file=None):
        super(StandaloneProjectBuilder, self).__init__(project_file)

    def _handleUiInfo(self, message):
        self._msg_queue.put(('info', message))
        self._ui_handler.info(message)

    def _handleUiWarning(self, message):
        self._msg_queue.put(('warning', message))
        self._ui_handler.warning(message)

    def _handleUiError(self, message):
        self._msg_queue.put(('error', message))
        self._ui_handler.error(message)

class SourceMock(object):
    def __init__(self, library, design_units, dependencies=None, filename=None):
        if filename is not None:
            self.filename = filename
        else:
            self.filename = library + '_' + design_units[0]['name'] + '.vhd'

        self.filetype = hdlcc.utils.getFileType(self.filename)
        self.abspath = p.abspath(self.filename)
        self.flags = []

        self.library = library
        self._design_units = design_units
        if dependencies is not None:
            self._dependencies = dependencies
        else:
            self._dependencies = []

        self._createMockFile()

    def _createMockFile(self):
        with open(self.filename, 'w') as fd:
            libs = hdlcc.utils.removeDuplicates(
                [x['library'] for x in self._dependencies])

            for lib in libs:
                fd.write("library {0};\n".format(lib))

            for dependency in self._dependencies:
                fd.write("use {0}.{1};\n".format(dependency['library'],
                                                 dependency['unit']))

            for design_unit in self._design_units:
                fd.write("{0} is {1} end {0} {1};\n".
                         format(design_unit['type'],
                                design_unit['name']))

    def __del__(self):
        if p.exists(self.filename):
            os.remove(self.filename)

    def getmtime(self):
        return p.getmtime(self.filename)

    def __str__(self):
        return "[%s] %s" % (self.library, self.filename)

    def getDesignUnits(self):
        return self._design_units

    def getDependencies(self):
        return self._dependencies

    #  def getLibraries(self):
    #      return []

    #  def getSourceContent(self):
    #      return ''

class MSimMock(hdlcc.builders.base_builder.BaseBuilder):  # pylint: disable=abstract-method
    _logger = logging.getLogger('MSimMock')
    builder_name = 'msim_mock'
    file_types = ('vhdl', )
    def __init__(self, target_folder):
        self._target_folder = target_folder
        if not p.exists(self._target_folder):
            os.mkdir(self._target_folder)

        super(MSimMock, self).__init__(target_folder)

    def _makeRecords(self, _): # pragma: no cover
        return []

    def _shouldIgnoreLine(self, line): # pragma: no cover
        return True

    def _checkEnvironment(self):
        return

    @staticmethod
    def isAvailable():
        return True

    def _buildSource(self, source, flags=None): # pragma: no cover
        return [], []

    def _createLibrary(self, source): # pragma: no cover
        pass

    def getBuiltinLibraries(self): # pragma: no cover
        return []


class FailingBuilder(MSimMock):  # pylint: disable=abstract-method
    _logger = logging.getLogger("FailingBuilder")
    builder_name = 'FailingBuilder'
    def _checkEnvironment(self):
        raise hdlcc.exceptions.SanityCheckError(
            self.builder_name, "Fake error")

