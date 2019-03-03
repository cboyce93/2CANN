#!/usr/bin/env python

import re
import requests

def validate_module(m):
    """ Return a tuple with bool and error message """
    error_message = ""
    if not re.match("^[A-Za-z0-9]*$", m.name):
        error_messge += "- Name cannot have spaces or special characters"
    #if m.uri != "":
    #    if requests.get(m.uri).status_code == 200:
    #        error_messge += "- Invalid Url"
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

def validate_modules_exist(m):
    """ Returns True if number of modules is greater than 0
    Input: self.modules
    """
    if len(m) == 0:
        return False
    else:
        return True
def validate_module_selected(m):
    """Returns True if module is selected
        input: self.module
    """
    if m == None:
        return False
    else:
        return True
