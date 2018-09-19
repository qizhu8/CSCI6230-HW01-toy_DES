# -*- coding: utf-8 -*-
#!/usr/bin/env python3

import numpy as np
from DES import DES

import socket
import os
import sys
import hashlib # check the md5 of the received file
if sys.version_info[0] < 3:
    raise Exception("Must be using Python 3")
# initial permutation table
tab_init_P = np.array([2, 6, 3, 1, 4, 8, 5, 7]) - 1
# Inverse initial permutation table
tab_inv_P = np.array([4, 1, 3, 5, 7, 2, 8, 6]) - 1

## F function
# expansion table of the F function
tab_F_E = np.array([[4, 1, 2, 3], [2, 3, 4, 1]]) - 1
# substitution tables of the F function's
tab_F_S_0 = np.array([[1, 0, 3, 2], [3, 2, 1, 0], [0, 2, 1, 3], [3, 1, 3, 2]])
tab_F_S_1 = np.array([[0, 1, 2, 3], [2, 0, 1, 3], [3, 0, 1, 0], [2, 1, 0, 3]])
# permutation table of the F function
tab_F_P = np.array([2, 4, 3, 1])- 1

# permutation table for key generation block
tab_key_P10 = np.array([3, 5, 2, 7, 4, 10, 1, 9, 8, 6]) - 1
tab_key_P8 = np.array([6, 3, 7, 4, 8, 5, 10, 9]) - 1


# test input
init_key_10bits = np.array([0, 1, 1, 0, 1, 0, 1, 0, 1, 1], dtype=bool)
rounds=2

des = DES()
des.set_rounds(rounds)
des.set_init_P_table(tab_init_P)
des.set_inv_P_table(tab_inv_P)
des.set_F_E_table(tab_F_E)
des.set_F_SBoxs_tables(np.array([tab_F_S_0, tab_F_S_1]))
des.set_F_P_table(tab_F_P)
des.set_key_init_P_table(tab_key_P10)
des.set_key_sub_P_table(tab_key_P8)

# socket communication
host = 'localhost'
port = 9999
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind((host, port))
sock.listen(1)
conn, addr = sock.accept()
print("connected")
rec = conn.recv(32)
cipher = rec
while rec:
    rec = conn.recv(32)
    cipher += rec
cipher = cipher.decode()
plaintext_rec = des.decrypt(cipher, init_key_10bits)

with open('rx_file.txt', 'wb') as f:
    f.write(plaintext_rec.encode())
sock.close()

received_file_md5 = hashlib.md5(open('rx_file.txt','rb').read()).hexdigest()
print("The md5 of the received file is:", received_file_md5)
