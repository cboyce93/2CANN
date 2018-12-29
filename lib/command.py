#!/usr/bin/env python

class Command:
    
    def __init__(self):
        self.function = None
        # command options
        self.flag = []
        self.static = []
        self.iter = []
        
