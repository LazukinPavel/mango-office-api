
import hashlib


def encrypt_string(string):
    hash_string = hashlib.sha256(string.encode()).hexdigest()
    return hash_string

