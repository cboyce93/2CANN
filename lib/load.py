#!/usr/bin/env python3

import pickle

def load_module(filename):
        try:
            fo = open(filename, 'rb')
            return pickle.load(fo)
        except pickle.UnpicklingError:
            pass
