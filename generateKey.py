#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan 25 13:44:38 2022

@author: philip
"""

import getpass
import macpassencrypt

mac_key = macpassencrypt.get_mackey(True)

stMessage   = getpass.getpass('Enter IMAP password to be encrypted: ')

mykey   = macpassencrypt.password_encrypt(stMessage.encode(), mac_key)

print('\nCopy the following key to your cfg-file:\n')
print(mykey.decode())
print('\n')
