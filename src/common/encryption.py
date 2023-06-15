"""
Script to use functions to encrypt and decrypt data
"""

from Crypto.Cipher import PKCS1_OAEP
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from pathlib import Path

from Crypto.Signature import pkcs1_15


def generate_keys():
    """
    Generates a pair of keys (public and private) using RSA algorithm
    :return: public and private keys
    """
    # check if file exists
    my_file = Path("../common/keys/rsa_private_key.pem")
    if my_file.is_file():
        print("Warning! - Keys already exists")
    else:
        print("Generating keys...")
        passphrase = input("Want to add a passphrase? (y/n): ")
        if passphrase == 'y':
            passphrase = input("Enter passphrase: ")
            key = RSA.generate(2048)
            encrypted_private_key = key.export_key(passphrase=passphrase, pkcs=8,
                                                   protection="scryptAndAES128-CBC")
            file_out = open("../common/keys/rsa_private_key.pem", "w+b")
            file_out.write(encrypted_private_key)
            file_out.close()

            public_key = key.publickey().export_key()
            file_out = open("../common/keys/rsa_public_key.pem", "w+b")
            file_out.write(public_key)
            file_out.close()

            print("Keys generated successfully")
        elif passphrase == 'n':
            key = RSA.generate(2048)
            private_key = key.export_key()

            file_out = open("../common/keys/rsa_private_key.pem", "w+b")
            file_out.write(private_key)
            file_out.close()

            public_key = key.publickey().export_key()
            file_out = open("../common/keys/rsa_public_key.pem", "w+b")
            file_out.write(public_key)
            file_out.close()

            print("Keys generated successfully")


def get_public_key():
    """
    Gets the public key from the server
    :return: public key
    """
    public_key = ""
    try:
        public_key = RSA.import_key(open("../common/keys/rsa_public_key.pem").read())
    except FileNotFoundError:
        print("Public key not found")
    return public_key


def get_private_key():
    """
    Gets the private key from the server
    :return: private key
    """
    private_key = ""
    try:
        private_key = RSA.import_key(open("../common/keys/rsa_private_key.pem").read())
    except FileNotFoundError:
        print("Private key not found")
    return private_key


def encrypt_message(message, public_key):
    """
    Encrypts a message using RSA algorithm
    :param message: message to encrypt (in bytes)
    :param public_key: public keys to encrypt the message
    :return: encrypted message
    """
    key = public_key
    cipher_rsa = PKCS1_OAEP.new(key)
    encrypted_message = cipher_rsa.encrypt(message)
    return encrypted_message


def decrypt_message(encrypted_message, private_key):
    """
    Decrypts a message using RSA algorithm
    :param encrypted_message: message to decrypt (in bytes)
    :param private_key: private keys to decrypt the message
    :return: decrypted message (in bytes)
    """
    key = private_key
    cipher_rsa = PKCS1_OAEP.new(key)
    decrypted_message = cipher_rsa.decrypt(encrypted_message)
    return decrypted_message


def sign_message(message, private_key) -> bytes:
    """
    Signs a message using RSA algorithm
    :param message: to sign
    :param private_key:
    :return signature:
    """
    h = SHA256.new(message)
    signature = pkcs1_15.new(private_key).sign(h)
    return signature


def verify_message(message, signature, public_key) -> bool:
    """
    Verifies a message using RSA algorithm
    :param message:
    :param signature:
    :param public_key:
    :return:
    """
    h = SHA256.new(message)
    try:
        pkcs1_15.new(public_key).verify(h, signature)
        return True
    except (ValueError, TypeError):
        return False
