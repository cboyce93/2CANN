#!/usr/bin/env python

def validate_module(m):
    """ Return a tuple with bool and error message """
    error_message = ""
    if '' in {m.category, m.name, m.author, m.desc, m.url}:
        error_message += "- An entry has not been modified from its original state.\n"
    if False in {m.category.isalpha(), m.name.isalpha(), m.author.isalpha()}:
        error_message += "- Category, Name &amp; Author may not contain numbers or special characters.\n"
    if m.command is None:
        error_message += "- Module has yet to be assigned a command.\n"
    if error_message is not "":
        return (False, error_message)
    else:
        return (True, None)
        
    
