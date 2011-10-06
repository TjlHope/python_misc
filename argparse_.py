""" Action Classes and Parser wrappers for the argparse module.
"""

import argparse
import logging


class LogLevel(argparse.Action):
    """ Action class for argparse to set/change the log level.
    """
    def __call__(self, parser, namespace, values=None, option_string=None):
        if isinstance(option_string, basestring):
            # get increment
            if '-q' in option_string:
                inc = 10
            elif '-v' in option_string:
                inc = -10
            else:
                return
            # Get level
            try:
                level = getattr(namespace, self.dest) + inc
            except TypeError:
                # Use default base level
                try:
                    level = getattr(logging, self.default) + inc
                except TypeError:
                    level = logging.getLogger().level + inc
            # Set level
            setattr(namespace, self.dest, level if level else 1)

class GetPass(argparse.Action):
    """ Action class for argparse to read a password from the commandline.
    """
    def __call__(self, parser, namespace, values=None, option_string=None):
        import getpass
        setattr(namespace, self.dest, getpass.getpass())

class ArgumentParser(argparse.ArgumentParser):
    """ Class that adds log_level parsing by default.
    """
    def __init__(self, *args, **kwargs):
        super(ArgumentParser, self).__init__(*args, **kwargs)
        self.add_argument('-v', '--verbose', nargs=0, dest='log_level', 
                action=LogLevel, help="Louder execution [repeatable].")
        self.add_argument('-q', '--quiet', nargs=0, dest='log_level', 
                action=LogLevel, help="Quieter execution [repeatable].")

class AuthArgumentParser(ArgumentParser):
    """ Class that adds username and password parsing by default.
    """
    def __init__(self, *args, **kwargs):
        super(AuthArgumentParser, self).__init__(*args, **kwargs)
        self.add_argument('-u', '--user', '--username',
                help="Username for authentication.")
        self.add_argument('-p', '--passwd', '--password',
                help="Password for authentication.")
        self.add_argument('-a', '--askpass', nargs=0, dest='passwd', 
                action=GetPass, help="Prompt for password.")

