__author__ = 'Scott Stamp <scott@hypermine.com>'
from common.cd import cd
from subprocess import Popen


class RABCDasm:
    """Wrapper for RABCDasm tools"""

    def __init__(self, toolsdir, tempdir, swfname, debug=False):
        self.toolsDir = toolsdir
        self.tempDir = tempdir
        self.swfName = swfname
        self.debug = debug

    def abcexport(self):
        with cd(self.tempDir):
            p = ([self.toolsDir + '/abcexport', self.swfName + '.swf'])
            Popen(p).wait()
            if self.debug:
                print(p)
                print('--------------------')

    def abcreplace(self, index):
        with cd(self.tempDir):
            p = ([self.toolsDir + '/abcreplace',
                  self.swfName + '.swf',
                  index,
                  '{0}-{1}/{0}-{1}.main.abc'.format(self.swfName, index)])
            Popen(p).wait()
            if self.debug:
                print(p)
                print('--------------------')

    def swfbinexport(self):
        with cd(self.tempDir):
            p = ([self.toolsDir + '/swfbinexport', self.swfName + '.swf'])
            Popen(p).wait()
            if self.debug:
                print(p)
                print('--------------------')

    def swfbinreplace(self, index, binfile):
        with cd(self.tempDir):
            p = ([self.toolsDir + '/swfbinreplace', self.swfName + '.swf', index, binfile])
            Popen(p).wait()
            if self.debug:
                print(p)
                print('--------------------')

    def rabcdasm(self):
        with cd(self.tempDir):
            p = ([self.toolsDir + '/rabcdasm',
                  '{0}-0.abc'.format(self.swfName)])
            Popen(p).wait()
            if self.debug:
                print(p)
                print('--------------------')

    def rabcasm(self, index):
        with cd(self.tempDir):
            p = ([self.toolsDir + '/rabcasm',
                  '{0}-{1}/{0}-{1}.main.asasm'.format(self.swfName, index)])
            Popen(p).wait()
            if self.debug:
                print(p)
                print('--------------------')
