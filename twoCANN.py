#!/usr/bin/env python

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

from handlers import Handler

class twoCANN:  

    def __init__(self):
        self.builder = Gtk.Builder.new_from_file('2CANN.glade')
        self.builder.connect_signals(Handler(self.builder))
        self.window = self.builder.get_object('wrapper')
        self.window.show_all()

def main():
    Gtk.main()

if __name__ == "__main__":
    win = twoCANN()
    main()
