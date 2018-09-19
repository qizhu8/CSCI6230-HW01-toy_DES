# -*- coding: utf-8 -*-
#!/usr/bin/env python3

import numpy as np
import sys
if sys.version_info[0] < 3:
    raise Exception("Must be using Python 3")

class DES(object):
    """docstring for DES."""

    def __init__(self):
        super(DES, self).__init__()
        self.tab_text_init_P = None # table of initial permutation
        self.tab_text_inv_P = None  # table of inverse permutation
        self.rounds = None          # rounds

        # parameters for the F function
        self.tab_F_E = None         # table of the expansion block of the F function
        self.tab_F_S = None         # tables of the S box (table_idx, row, col) of the F function
        self.tab_F_P = None         # table of the permutation block of the F function

        # generate keys
        self.tab_key_init_P = None  # initial permutation table to generate keys
        self.tab_key_sub_P = None   # permutation table for sub sequences to generate keys
        self.keys = None            # set of keys

    def set_rounds(self, rounds):
        if rounds >= 1:
            self.rounds = rounds
        else:
            print("rounds should be a positive integer")
            return


    # initial permutation
    def set_init_P_table(self, table):
        # set initial permutation table
        self.tab_text_init_P = table

    def print_init_P_table(self):
        if self.tab_text_init_P is not None:
            print("Initial Permutation table looks like:")
            print(self.tab_text_init_P)
        else:
            print("Please specify the Initial Permutation table by using set_init_P_table()")

    # inverse permutation
    def set_inv_P_table(self, table):
        # set initial permutation table
        self.tab_text_inv_P = table

    def print_inv_P_table(self):
        if self.tab_text_inv_P is not None:
            print("Initial Permutation table looks like:")
            print(self.tab_text_inv_P)
        else:
            print("Please specify the Initial Permutation table by using set_inv_P_table()")

    # F function
    ## expansion block of the F function
    def set_F_E_table(self, table):
        # set the expansion table
        self.tab_F_E = np.asarray(table)

    def print_F_E_table(self):
        # print the expansion table
        if self.tab_F_E is not None:
            print("Expansion table of the F function looks like:")
            print(self.tab_F_E)
        else:
            print("Please specify the Expansion table of the F function using set_F_E_table()")

    #$ substitution block of the F function
    def set_F_SBoxs_tables(self, tables):
        # this function is used to set all the tables of the S boxs using a 3-d array
        self.tab_F_S = np.asarray(tables)

    def print_F_SBoxs_tables(self):
        # print the SBox's tables
        if self.tab_F_S is not None:
            for idx in range(len(self.tab_F_S)):
                print("Substitution table %d of the F function looks like:" % idx)
                print(self.tab_F_S[idx])
        else:
            print("Please specify the S tables of the F function using set_F_SBoxs_tables()")

    def F_SBox(self, inputs):
        # do S substitution
        output = []
        for idx, item in enumerate(inputs):
            # need to be changed if the table is not 2x2
            col = item[1] * 2 + item[2]
            row = item[0] * 2 + item[3]
            rst = self.tab_F_S[idx][row, col]
            # print("row, col (%d, %d) item %d" % (row, col, rst))
            rst = list(np.binary_repr(rst, width=2))
            output.append([int(i) for i in rst])
        return np.array(output)

    #$ permutation block of the F function
    def set_F_P_table(self, table):
        # set the permutation table
        self.tab_F_P = np.asarray(table)

    def print_F_P_table(self):
        # print the permutation table of the F function
        if self.tab_F_P is not None:
            print("Table of the permutation block of the F function looks like:")
            print(self.tab_F_P)
        else:
            print("Please specify the P table of the F function using set_F_P_table()")

    def print_F_tables(self):
        # print all the tables of the F function
        self.print_F_E_table()
        self.print_F_SBoxs_tables()
        self.print_F_P_table()

    def F_func(self, input, key):
        input_E = self.permutation(input, self.tab_F_E)
        input_E_key = self.XOR(input_E, key)
        input_E_key_halves = self.split_to_halves(input_E_key)
        input_E_key_halves_S = self.F_SBox(input_E_key_halves)
        input_E_key_halves_S_P = self.permutation(np.concatenate(input_E_key_halves_S, axis=0), self.tab_F_P)
        return input_E_key_halves_S_P

    ## generate keys
    def set_key_init_P_table(self, table):
        # set the initial permutation table to generate keys
        self.tab_key_init_P = table

    def print_key_init_P_table(self):
        # print the initial permutation table to generate keys
        if self.tab_key_init_P is not None:
            print("Table of the initial permutation block to generate sequences:")
            print(self.tab_key_init_P)
        else:
            print("Please specify the initial permutation table to generate keys by using set_key_init_P_table()")

    ## key generation block
    def set_key_sub_P_table(self, table):
        # set the permutation table for sub sequences to generate keys
        self.tab_key_sub_P = table

    def print_key_sub_P_table(self):
        # print the permutation table for sub sequences to generate keys
        if self.tab_key_sub_P is not None:
            print("Table of the permutation block to generate keys from sequences:")
            print(self.tab_key_sub_P)
        else:
            print("Please specify the table of the permutation block to generate keys from sequences by using set_key_sub_P_table()")

    def gen_keys(self, init_key):
        # generate keys from the input sequence with certain rounds

        # sanitary check
        if self.rounds is None:
            print("Please specify the rounds number by set_rounds()")
            return

        keys = []
        input_P10 = self.permutation(init_key, self.tab_key_init_P)
        input_P10_halves = self.split_to_halves(input_P10)
        input_P10_halves_shift = self.left_shift(input_P10_halves)
        input_P8 = input_P10_halves_shift
        for key_idx in range(self.rounds):
            key = self.permutation(np.concatenate(input_P8, axis=0), self.tab_key_sub_P)
            keys.append(key)
            input_P8 = self.left_shift(input_P8)
        self.keys = np.asarray(keys)
        return self.keys

    ## basic options
    def permutation(self, input, table):
        # permutate input sequences based on the table
        output_idx = np.asarray(table, dtype=int).ravel() # reshape to 1d
        output = np.asarray([input[i] for i in output_idx])
        return output


    def left_shift(self, input):
        # cyclicly shift input sequence to the left
        if len(input.shape) == 1:
            output = np.roll(input, -1)
        else:
            output = np.roll(input, -1, axis=1)
        return output

    def XOR(self, input1, input2):
        # doing XOR on input1 and input2
        if input1.shape != input2.shape:
            print("Input1 and input2 are not of the same shape")
            return
        output = np.logical_xor(input1, input2)
        return output

    def byte_to_bin(self, bytes):
        # convert bytes (or char) to bool list
        if len(bytes) == 1:
            if not isinstance(bytes[0], int):
                bytes = ord(bytes)
            return [int(item) > 0 for item in np.binary_repr(bytes, width=8)]
        bin_list = []
        if isinstance(bytes[0], int):
            ord_flag = False
        else:
            ord_flag = True
        for byte in bytes:
            if ord_flag:
                byte = ord(byte)
            bin_list.append([int(item) > 0 for item in np.binary_repr(byte, width=8)])
        return bin_list

    def bin_to_byte(self, bins):
        if len(bins[0]) == 1:
            return int("".join([str(item+0) for item in bins]), 2)
        return [chr(int("".join([str(item+0) for item in rst]), 2)) for rst in bins]

    def split_to_halves(self, input):
        # split input sequence to two subsequences of same length
        input_len = len(input)
        if input_len % 2 != 0:
            print("input sequence is of length %d which is not an even number" % input_len)
            return

        output = np.array([input[:input_len//2], input[input_len//2:]])
        return output

    def encrypt_one_byte(self, plaintext, init_key, keys=None):
        # main block to encrypt plain text
        if keys is None:
            keys = self.gen_keys(init_key)
        plaintext_initP = self.permutation(plaintext, self.tab_text_init_P)
        plaintext_initP_halves = self.split_to_halves(plaintext_initP)
        L0, R0 = plaintext_initP_halves[0], plaintext_initP_halves[1]
        for round_idx in range(self.rounds):
            R1 = self.XOR(L0, self.F_func(R0, keys[round_idx]))
            L1 = R0
            R0, L0 = R1, L1
        L0, R0 = R0, L0
        cipher = self.permutation(np.concatenate([L0, R0], axis=0), self.tab_text_inv_P)
        return cipher, keys

    def decrypt_one_byte(self, cipher, init_key, keys=None):
        # main block to decrypt cipher text
        if keys is None:
            keys = self.gen_keys(init_key)
        cipher_initP = self.permutation(cipher, self.tab_text_init_P)
        cipher_initP_halves = self.split_to_halves(cipher_initP)
        L0, R0 = cipher_initP_halves[0], cipher_initP_halves[1]
        for round_idx in range(self.rounds):
            R1 = self.XOR(L0, self.F_func(R0, keys[-round_idx-1]))
            L1 = R0
            R0, L0 = R1, L1
        L0, R0 = R0, L0
        plaintext = self.permutation(np.concatenate([L0, R0], axis=0), self.tab_text_inv_P)
        return plaintext, keys

    def encrypt(self, text_str, init_key):
        keys = None
        cipher_list = []
        for text_byte in self.byte_to_bin(text_str):
            cipher_byte, keys = self.encrypt_one_byte(text_byte, init_key, keys)
            cipher_list.append(cipher_byte)
        cipher_str = "".join(self.bin_to_byte(cipher_list))
        return cipher_str

    def decrypt(self, cipher_str, init_key):
        keys = None
        text_list = []
        for cipher_byte in self.byte_to_bin(cipher_str):
            text_byte, keys = self.decrypt_one_byte(cipher_byte, init_key, keys)
            text_list.append(text_byte)
        text_str = "".join(self.bin_to_byte(text_list))
        return text_str
