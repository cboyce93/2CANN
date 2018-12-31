#!/usr/bin/env python

class Command:
    
    def __init__(self):
        
        # command function
        self.func = None        
        # command options
        self.flags = []
        self.statics = []   
        self.iters = []
        self.max_index = float(0)
        self.str = ""
  
    @property
    def function(self):
        return self.__function
    
    @function.setter
    def function(self, function):
        self.__function = function
        
    def get_max_index(self):
        """ return max index of module command so that adjustment does
            not allow the input of out-of-range indices"""
        if self.func is not None:
            return float(len(self.flags + self.statics + self.iters))
        else:
            return 0
