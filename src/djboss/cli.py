# -*- coding: utf-8 -*-

import logging
import os
import sys
import textwrap

from django.utils.importlib import import_module

from djboss.commands import Command


class SettingsImportError(ImportError):
    pass


def get_settings():
    sys.path.append(os.getcwd())
    if 'DJANGO_SETTINGS_MODULE' in os.environ:
        try:
            return import_module(os.environ['DJANGO_SETTINGS_MODULE'])
        except ImportError, exc:
            raise SettingsImportError(textwrap.dedent("""\
                There was an error importing the module specified by the
                DJANGO_SETTINGS_MODULE environment variable. Make sure that it
                refers to a valid and importable Python module."""), exc)
    
    try:
        import settings
    except ImportError, exc:
        raise SettingsImportError(textwrap.dedent("""\
            Couldn't import a settings module. Make sure that a `settings.py`
            file exists in the current directory, and that it can be imported,
            or that the DJANGO_SETTINGS_MODULE environment variable points
            to a valid and importable Python module."""), exc)
    return settings


def find_commands(app):
    """Return a dict of `command_name: command_obj` for the given app."""
    
    commands = {}
    app_module = import_module(app) # Fail loudly if an app doesn't exist.
    try:
        commands_module = import_module(app + '.commands')
    except ImportError:
        pass
    else:
        for command in vars(commands_module).itervalues():
            if isinstance(command, Command):
                commands[command.name] = command
    return commands


def find_all_commands(apps):
    """Return a dict of `command_name: command_obj` for all the given apps."""
    
    commands = {}
    commands.update(find_commands('djboss'))
    for app in apps:
        commands.update(find_commands(app))
    return commands


def main():
    try:
        settings = get_settings()
    except SettingsImportError, exc:
        print >> sys.stderr, exc.args[0]
        print >> sys.stderr
        print >> sys.stderr, "The original exception was:"
        print >> sys.stderr, '\t' + str(exc.args[1])
        sys.exit(1)
    
    commands = find_all_commands(settings.INSTALLED_APPS)
    
    from djboss.parser import PARSER
    
    PARSER.set_defaults(settings=settings)
    args = PARSER.parse_args()
    logging.root.setLevel(getattr(logging, args.log_level))
    
    # Call the command.
    commands[args.command](args)


if __name__ == '__main__':
    main()
