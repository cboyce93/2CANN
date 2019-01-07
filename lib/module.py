#!/usr/bin/env python

from lib.command import Command
import pickle

class Module:

    def save(self, root_dir):
        # create file object
        try:
            self.set_filepath(root_dir)
            fo = open(self.fp , 'wb')
            pickle.dump(self, fo, protocol=pickle.DEFAULT_PROTOCOL)
        except pickle.PicklingError:
            pass

    def set_filepath(self, root):
        self.fp = root + self.name + ".mod"
    
    def __init__(self):
        self.category = None
        self.name = None
        self.author = None
        self.desc = None
        self.url = None
        self.command = Command()
    
    # getters and setters
    
    @property
    def category(self):
        return self.__category
    
    @category.setter
    def category(self, category):
        self.__category = category
    
    @property
    def name(self):
        return self.__name
    
    @name.setter
    def name(self, name):
        self.__name = name
    
    @property
    def author(self):
        return self.__author
    
    @author.setter
    def author(self, author):
        self.__author = author
    
    @property
    def desc(self):
        return self.__desc
    
    @desc.setter
    def desc(self, desc):
        self.__desc = desc
        
    @property
    def url(self):
        return self.__url
    
    @url.setter
    def url(self, url):
        self.__url = url
        
