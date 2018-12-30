#!/usr/bin/env python

class Command:

    def build_command_str():
        cmd_str = ""
        cmd_str += self.func
        
        #for flag in self.flags:
            
    
    def get_command_iters():
        pass
        
    def __init__(self):
        
        # command function
        self.func = None
        self.func_iters = None
        
        # command options
        self.flags = []
        self.flag_iters = None

        self.statics = []
        self.static_iters = None
        
        self.iters = []
        self.iters_iters = None
    
    # getters and setters
    
    @property
    def function(self):
        return self.__function
    
    @function.setter
    def function(self, function):
        self.__function = function
