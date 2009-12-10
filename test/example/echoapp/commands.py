# -*- coding: utf-8 -*-

from djboss.commands import *
import sys


@command
@argument('-n', '--no-newline', action='store_true',
          help="Don't print a newline afterwards.")
@argument('words', nargs='*')
def echo(args):
    """Echo the arguments back to the console."""
    
    string = ' '.join(args.words)
    if args.no_newline:
        sys.stdout.write(string)
    else:
        print string


@command
def hello(args):
    """Print a cliche to the console."""
    
    print "Hello, World!"
