#!/usr/bin/env python3

class Project:
    
    def __init__(self, name):
        self.name = name
        self.filename = None
        self.vars = [["${ROOT}", "YA"]]
        self.working_directory = None
