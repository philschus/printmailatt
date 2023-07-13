#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan 25 13:43:20 2022
@author: philip
"""

import secrets
from base64 import urlsafe_b64encode as b64e, urlsafe_b64decode as b64d

from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

backend = default_backend()
iterations = 100_000

def _derive_key(password: bytes, salt: bytes, iterations: int = iterations) -> bytes:
    """Derive a secret key from a given password and salt"""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(), length=32, salt=salt,
        iterations=iterations, backend=backend)
    return b64e(kdf.derive(password))

def password_encrypt(message: bytes, password: str, iterations: int = iterations) -> bytes:
    salt = secrets.token_bytes(16)
    key = _derive_key(password.encode(), salt, iterations)
    return b64e(
        b'%b%b%b' % (
            salt,
            iterations.to_bytes(4, 'big'),
            b64d(Fernet(key).encrypt(message)),
        )
    )

def password_decrypt(token: bytes, password: str) -> bytes:
    decoded = b64d(token)
    salt, iter, token = decoded[:16], decoded[16:20], b64e(decoded[20:])
    iterations = int.from_bytes(iter, 'big')
    key = _derive_key(password.encode(), salt, iterations)
    return Fernet(key).decrypt(token)

def get_mackey(verbose: bool) -> str:
    
    import os
    
    mycmdiprouter = 'ip r | grep default | grep -o -P "(?<=via )(\S*)(?=\s)"' 
    mycmdnetdev   = 'ip r | grep default | grep -o -P "(?<=dev )(\S*)(?=\s)"'
    
    stRouterIP   = os.popen(mycmdiprouter).read().rstrip("\n")
    stNetDevice  = os.popen(mycmdnetdev).read().rstrip("\n")
    
    mycmd1 = r'ip addr show ' + stNetDevice + ' | grep ether | grep -o -E "([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})" | head -1'
    mycmd2 = r'arp -n | grep ' + stRouterIP + ' | grep -o -E "([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})"' 
    
    mac_local  = os.popen(mycmd1).read().rstrip("\n")
    mac_router = os.popen(mycmd2).read().rstrip("\n")
    
    mac_key    = mac_local + ":" + mac_router
    
    if verbose:
        print('Router IP address:   ' + stRouterIP)
        print('Network device name: ' + stNetDevice)
    
    return mac_key
