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


@command
@argument('app', type=APP_LABEL)
def app_path(args):
    """Print a path to the specified app."""
    
    import os.path as p
    
    path, base = p.split(p.splitext(args.app.__file__)[0])
    if base == '__init__':
        print p.join(path, '')
    else:
        if p.splitext(args.app.__file__[-4:])[1] in ('.pyc', '.pyo'):
            print args.app.__file__[:-1]
        else:
            print args.app.__file__
