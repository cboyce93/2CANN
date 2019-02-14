#!/usr/bin/env python

import re

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

def validate_loop(var, dir_exp):
    """ Return a tuple with bool and error message
    
    Valid directory selection contains
    -   ONE <v></v> open and closing local var tag
    """
    if not var.islower():
        return (False, "var - Only lowercase characters allowed.")
    for char in var:
        if char.isspace():
            return (False, "var - No whitespaces allowed.")
    if not var.isalpha():
        return (False, "var -No special characters allowed.")
    
    m = re.findall(r'(<v>%{.*?}</v>)', dir_exp)
    if len(m) == 0:
        return (False, "You must include one open and closing local var tag.")
    if len(m) > 1:
        return (False, "Only one open and closing local var tag allowed.")
    if len(m)==1:
        return (True, None)
    
