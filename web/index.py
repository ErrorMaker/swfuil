__author__ = 'scott'
import tempfile
import os
from backend.habbo import Habbo


class Exec:
    Session = None
    OperatingDir = os.path.dirname(os.path.abspath(__file__))
    Email = 'clientparse@xksc.org'
    Password = 'passw0rd'
    Hotel = 'com'
    # Do we need to be concerned about path traversal?
    ReplacementKey = OperatingDir + '/../common/security/replacement.pem'
    ToolsDir = OperatingDir + '/../tools'
    TempDir = tempfile.mkdtemp('_habbo')

    def __init__(self):
        self.Session = Habbo(self.Email,
                             self.Password,
                             self.Hotel,
                             self.ReplacementKey,
                             self.ToolsDir,
                             self.TempDir)

        print(self.__dict__['Session'].__dict__)

    def login(self):
        self.Session.login()
        self.Session.parse_client()

    def get_original_key(self):
        return self.Session.__dict__['origKey']['n']