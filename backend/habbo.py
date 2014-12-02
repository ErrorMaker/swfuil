__author__ = 'Scott Stamp <scott@hypermine.com>'
import base64
import glob
from urllib import request
import requests
import re
import shutil
from Crypto.PublicKey import RSA

from common.cd import cd
from common.db import *
from backend.rabcdasm import RABCDasm


class Habbo:
    """Logic for handling login, SWF manipulation, etc..."""
    ipCookiePattern = re.compile("\'(YPF.*)', '(.*)', 10\);")
    playerIdPattern = re.compile('/identity/useOrCreateAvatar/([0-9]*)')
    swfNamePattern = re.compile('//(.*)/gordon/(.*)/Habbo\.swf')
    buildVersionPattern = re.compile('<meta name="build" content="(.*)" />')
    encryptedKeyPattern = re.compile('dummy_field" caption="(.*)" visible')
    byteCodePattern = re.compile("\s*code\s*pushfalse\s*pushtrue")

    session = requests.session()

    buildVersion = None
    swfURL = None
    swfName = None
    rabc = None
    origKeyfile = None
    origKeytext = None
    origKey = None
    origXML = None
    complete = False

    def __init__(self, email, password, hotel, private_key, tools_path, temp_path, gordon_path):
        self.email = email

        self.loginCredentials = {
            'credentials.username': email,
            'credentials.password': password
        }

        self.hotel = hotel or 'com'
        self.urls = {
            'home': 'https://www.habbo.{0}'.format(hotel),
            'login': 'https://www.habbo.{0}/account/submit'.format(hotel),
            'forward': 'http://www.habbo.{0}/identity/useOrCreateAvatar'.format(hotel),
            'client': 'http://www.habbo.{0}/client'.format(hotel)
        }

        self.toolsPath = tools_path
        self.tempPath = temp_path
        self.gordonPath = gordon_path

        f = open(private_key, encoding='latin-1')
        self.newKeyRSA = RSA.importKey(f.read()) or RSA.generate()
        self.newKey = {'n': hex(self.newKeyRSA.n)[2:],
                       'e': hex(self.newKeyRSA.e)[2:],
                       'd': hex(self.newKeyRSA.d)[2:]}

        self.newKeytext = self.encrypt_key(self.newKey['n'],
                                           self.newKey['e'])

    def set_ip_cookie(self):
        """Fetch IP cookie (not implemented on all hotels"""
        home = self.session.get(self.urls['home']).text
        if 'YPF' in home:
            ip_cookie = re.search(self.ipCookiePattern, home)
            ip_cookie = {ip_cookie.group(1): ip_cookie.group(2)}
            requests.utils.add_dict_to_cookiejar(self.session.cookies, ip_cookie)

    def login(self):
        """Login with specified credentials"""
        self.set_ip_cookie()
        redirection = self.session.post(self.urls['login'], data=self.loginCredentials)
        try:
            player_id = re.search(self.playerIdPattern, redirection.text).group(1)
            self.session.get(self.urls['forward'] + '/' + player_id + '?next=')
        except:
            # Session is already active
            pass

    def parse_client(self):
        """Parse client from current session"""
        client = self.session.get(self.urls['client']).text
        swf = re.search(self.swfNamePattern, client)
        self.buildVersion = re.search(self.buildVersionPattern, client).group(1)
        self.swfURL = 'http:' + swf.group(0)
        self.swfName = swf.group(2)

    def download_swf(self):
        """Download SWF with current session"""
        with cd(self.tempPath):
            request.urlretrieve(self.swfURL, self.swfName + '.swf')

    def disassemble_swf(self):
        """Disassemble SWF"""
        with cd(self.tempPath):
            self.rabc = RABCDasm(self.toolsPath, self.tempPath, self.swfName, True)
            self.rabc.abcexport()
            self.rabc.swfbinexport()
            self.rabc.rabcdasm()

    def reassemble_swf(self):
        """Reassemble SWF ... this whole thing would be pretty useless otherwise"""
        self.rabc.swfbinreplace(self.origKeyfile.split('-')[-1].split('.')[0], self.origKeyfile)
        self.rabc.rabcasm('0')
        self.rabc.abcreplace('0')

    def crack_bytecode(self):
        """Let's really fuck up their day, shall we?"""
        with cd('{0}/{1}-0'.format(self.tempPath, self.swfName)):
            for file in glob.glob('**/*.class.asasm'):
                with open(file, 'r+') as f:
                    content = f.read()
                    content = re.sub(self.byteCodePattern,
                                     "\r\n    code\r\n     pushtrue\r\n     returnvalue",
                                     content)
                    f.seek(0)
                    f.write(content)
                    f.truncate()
                    f.close()

    @staticmethod
    def decrypt_key(key):
        """Decrypt original public key"""
        try:
            key = base64.b64decode(key).decode()

            mod_len = ord(key[0])
            exp_len = ord(key[mod_len + 1])

            mod = key[1:mod_len + 1]
            exp = key[mod_len + 2:mod_len + exp_len + 2]

            return {'n': mod, 'e': exp}

        except:
            return "not a valid original key"

    @staticmethod
    def encrypt_key(n, e):
        """Encrypt replacement public key"""
        return base64.b64encode(''.join([chr(len(n)), n, chr(len(e)), e]).encode()).decode()

    def get_original_key(self):
        """Extract original public key from binary resources"""
        with cd(self.tempPath):
            for file in glob.glob('*.bin'):
                with open(file, 'r', encoding='latin-1') as f:
                    contents = f.read()
                if 'dummy_field' in contents:
                    self.origKeyfile = file
                    self.origXML = contents
                else:
                    os.remove(file)

            encrypted_key = re.search(self.encryptedKeyPattern, self.origXML).group(1)

        self.origKeytext = encrypted_key
        self.origKey = self.decrypt_key(encrypted_key)

    def replace_key(self):
        """Replace keys in original binary"""
        with cd(self.tempPath):
            with open(self.origKeyfile, 'r+', encoding='latin-1') as f:
                contents = f.read()
                contents = contents.replace(self.origKeytext,
                                            self.newKeytext)
                f.seek(0)
                f.write(contents)
                f.truncate()
                f.close()

    def return_results(self):
        """Return a report of the above processes"""
        return self.__dict__

    def store_results(self):
        DatabaseHelper.insert_value(self)

        client_path = os.path.join(self.gordonPath, self.swfName)

        if not os.path.exists(client_path):
            os.makedirs(client_path)

        shutil.copyfile(os.path.join(self.tempPath, self.swfName + '.swf'),
                        os.path.join(client_path, 'Habbo.swf'))

        print(', '.join(glob.glob('gordon/**/*')))

        shutil.rmtree(self.tempPath)