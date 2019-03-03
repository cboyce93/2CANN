#!/usr/bin/env python

class Variable:

    def __init__(self):
        self.name = None
        self.val = None

    def __ne__(self,o):
        if self.name != o.val:
            return True
        if self.val != o.val:
            return True
        else:
            return False 
