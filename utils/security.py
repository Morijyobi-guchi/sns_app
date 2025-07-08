# utils/security.py
import hashlib
import os
import secrets

def generate_salt():
    return secrets.token_hex(16)

def hash_password(password, salt):
    return hashlib.pbkdf2_hmac(
        'sha256', 
        password.encode('utf-8'), 
        salt.encode('utf-8'), 
        100000
    ).hex()

def verify_password(stored_password, provided_password, salt):
    return stored_password == hash_password(provided_password, salt)