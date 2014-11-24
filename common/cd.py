__author__ = 'Scott Stamp <scott@hypermine.com>'
import os


class cd:
    """Context manager for changing the current working directory"""

    def __init__(self, newpath):
        self.newPath = newpath

    def __enter__(self):
        self.savedPath = os.getcwd()
        os.chdir(self.newPath)

    def __exit__(self, etype, value, traceback):
        os.chdir(self.savedPath)
