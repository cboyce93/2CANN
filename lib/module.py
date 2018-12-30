#!/usr/bin/env python

from lib.command import Command

class Module:

    def save(self):
        # write to db
        pass

    def __init__(self):
        self.category = None
        self.name = None
        self.author = None
        self.desc = None
        self.url = None
        self.command = None
    
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
        