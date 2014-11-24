__author__ = 'scott'
import tempfile
import os
from backend.habbo import Habbo


class Exec:
    @staticmethod
    def process(hotel):
        operating_dir = os.path.dirname(os.path.abspath(__file__))
        email = 'clientparse@xksc.org'
        password = 'passw0rd'
        replacement_key = operating_dir + '/../common/security/replacement.pem'
        tools_dir = operating_dir + '/../tools'
        temp_dir = tempfile.mkdtemp('_habbo')
        clients_dir = operating_dir + '/../clients/'

        session = Habbo(email,
                        password,
                        hotel,
                        replacement_key,
                        tools_dir,
                        temp_dir,
                        clients_dir)

        session.login()
        session.parse_client()
        session.download_swf()
        session.disassemble_swf()
        session.crack_bytecode()
        session.get_original_key()
        session.replace_key()
        session.reassemble_swf()
        session.store_results()
        return session.return_results()