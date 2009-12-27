# -*- coding: utf-8 -*-

import functools
import sys

from djboss.parser import SUBPARSERS


__all__ = ['Command', 'command', 'argument', 'APP_LABEL']


class Command(object):
    
    """Wrapper to manage creation and population of sub-parsers on functions."""
    
    def __init__(self, function, **kwargs):
        self.function = function
        self.parser = self._make_parser(**kwargs)
        self._init_arguments()
    
    add_argument = property(lambda self: self.parser.add_argument)
    
    def __call__(self, args):
        return self.function(args)
    
    def name(self):
        """The name of this command."""
        
        if hasattr(self.function, 'djboss_name'):
            return self.function.djboss_name
        else:
            return self.function.__name__.replace('_', '-')
    name = property(name)
    
    def help(self):
        if hasattr(self.function, 'djboss_help'):
            return self.function.djboss_help
        elif getattr(self.function, '__doc__', None):
            # Just the first line of the docstring.
            return self.function.__doc__.splitlines()[0]
    help = property(help)
    
    def description(self):
        if hasattr(self.function, 'djboss_description'):
            return self.function.djboss_description
        elif getattr(self.function, '__doc__', None):
            return self.function.__doc__
    description = property(description)
    
    def _make_parser(self, **kwargs):
        """Create and register a subparser for this command."""
        
        kwargs.setdefault('help', self.help)
        kwargs.setdefault('description', self.description)
        return SUBPARSERS.add_parser(self.name, **kwargs)
    
    def _init_arguments(self):
        """Initialize the subparser with arguments stored on the function."""
        
        if hasattr(self.function, 'djboss_arguments'):
            while self.function.djboss_arguments:
                args, kwargs = self.function.djboss_arguments.pop()
                self.add_argument(*args, **kwargs)


def APP_LABEL(label=None, **kwargs):
    
    """
    argparse type to resolve arguments to Django apps.
    
    Example Usage:
    
        *   `@argument('app', type=APP_LABEL)`
        *   `@argument('app', type=APP_LABEL(empty=False))`
        *   `APP_LABEL('auth')` => `<module 'django.contrib.auth' ...>`
    """
    
    from django.db import models
    from django.conf import settings
    from django.utils.importlib import import_module
    
    if label is None:
        return functools.partial(APP_LABEL, **kwargs)
    
    # `get_app('auth')` will return the `django.contrib.auth.models` module.
    models_module = models.get_app(label, emptyOK=kwargs.get('empty', True))
    if models_module is None:
        for installed_app in settings.INSTALLED_APPS:
            # 'app' should resolve to 'path.to.app'.
            if installed_app.split('.')[-1] == label:
                return import_module(installed_app)
    else:
        # 'path.to.app.models' => 'path.to.app'
        return import_module(models_module.__name__.rsplit('.', 1)[0])


def command(*args, **kwargs):
    """Decorator to declare that a function is a command."""
    
    def decorator(function):
        return Command(function, **kwargs)
    
    if args:
        return decorator(*args)
    return decorator


def argument(*args, **kwargs):
    """Decorator to add an argument to a command."""
    
    def decorator(function):
        if isinstance(function, Command):
            func = function.function
        else:
            func = function
        
        if not hasattr(func, 'djboss_arguments'):
            func.djboss_arguments = []
        func.djboss_arguments.append((args, kwargs))
        
        return function
    return decorator


def manage(args):
    """Run native Django management commands under djboss."""
    
    from django.core import management as mgmt
    
    OldOptionParser = mgmt.LaxOptionParser
    class LaxOptionParser(mgmt.LaxOptionParser):
        def __init__(self, *args, **kwargs):
            kwargs['prog'] = 'djboss manage'
            OldOptionParser.__init__(self, *args, **kwargs)
    mgmt.LaxOptionParser = LaxOptionParser
    
    utility = mgmt.ManagementUtility(['djboss manage'] + args.args)
    utility.prog_name = 'djboss manage'
    utility.execute()

# `prefix_chars=''` will stop argparse from interpreting the management
# sub-command options as options on this command.
manage = Command(manage, add_help=False, prefix_chars='')
manage.add_argument('args', nargs='*')
