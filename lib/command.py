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
  
    @property
    def function(self):
        return self.__function
    
    @function.setter
    def function(self, function):
        self.__function = function
        
    def get_max_index(self):
        if self.func is not None:
            return float(len(self.flags + self.statics + self.iters))
        else:
            return 0
