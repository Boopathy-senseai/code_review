from datetime import timedelta, datetime
from cryptography.fernet import Fernet
import dateutil
from dateutil import parser
import sys, os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class Helper:
    def checkDatetimeExpiry(datetime_p, upto, type):
        if sys.version_info[0] >= 3.9:
            user_datetime = datetime.fromisoformat(datetime_p)
        else:
            user_datetime = dateutil.parser.isoparse(datetime_p)

        present = datetime.now()
        if type == "h":
            user_datetime = user_datetime + timedelta(hours=upto)
            if present > user_datetime:
                return True
            else:
                return False

        elif type == "m":
            user_datetime = user_datetime + timedelta(minutes=upto)
            if present > user_datetime:
                return True
            else:
                return False

    def check_valid_url(url):
        return True


class EncryptDecrypt:
    def generate_key():
        """
        Generates a key and save it into a file
        """
        key = Fernet.generate_key()
        with open(BASE_DIR + "/secret.key", "wb") as key_file:
            key_file.write(key)

    def load_key():
        """
        Load the previously generated key
        """
        return open(BASE_DIR + "/secret.key", "rb").read()

    def encrypt_message(message):
        """
        Encrypts a message
        """
        key = EncryptDecrypt.load_key()
        encoded_message = message.encode()
        f = Fernet(key)
        return f.encrypt(encoded_message)

    def decrypt_message(encrypted_message):
        """
        Decrypts an encrypted message
        """
        key = EncryptDecrypt.load_key()
        f = Fernet(key)
        return f.decrypt(encrypted_message)
