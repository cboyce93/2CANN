#!/usr/bin/env python3

import pickle

def open_project(filename):
    try:
        fo = open(filename, 'rb')
        return pickle.load(fo)
    except pickle.UnpicklingError:
        pass
