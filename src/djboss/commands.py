# -*- coding: utf-8 -*-

from djboss.parser import SUBPARSERS


__all__ = ['Command', 'command', 'argument']


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
        elif hasattr(self.function, '__doc__'):
            # Just the first line of the docstring.
            return self.function.__doc__.splitlines()[0]
    help = property(help)
    
    def description(self):
        if hasattr(self.function, 'djboss_description'):
            return self.function.djboss_description
        elif hasattr(self.function, '__doc__'):
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


@command(add_help=False, prefix_chars='')
@argument('args', nargs='*')
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
