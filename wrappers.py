""" wrappers/__init__.py
    Useful Wrapper variables, functions, or classes.

    @author: TjlHope
"""

import sys
import time
import codecs
import re

import urllib2
import logging

log = logging.getLogger(__name__)

def timestamp():
    """ Nice timestamp format.
    """
    return time.strftime("%Y-%m-%d %H:%M:%S")

delchars = ''.join(c for c in map(chr, xrange(256)) if not c.isalnum())
def key(k, *args):
    """ Strips spacing chars to give a nice dict key str. Any extra arguments 
        given are also removed from the string
    """
    k = str(k).lower()
    for arg in args:
        k = k.replace(arg, '')
    return k.translate(None, delchars)

def ls(iterable):
    """ Nicely display an iterable as a string, in brackets only if there are 
        multiple values.
    """
    iter_strs = [str(i) for i in iterable]
    string = iter_strs[0] if len(iter_strs) is 1 else "', '".join(iter_strs)
    return string.join(("'", "'"))

def unkey(k, key_type=None, sep=' ', case='lower', keywords=[]):
    """ Attempts to reconstruct a str that has been 'key()'ed.
    """
    # Populate keywords to split on
    keywords += [__package__.__name__, 'name', 'type', 'str']
    # if we can use preset defaults
    if key_type == 'sentence':
        sep = ' '
        case = 'capitalize'
    elif key_type == 'header':
        sep = '-'
        case = 'title'
        keywords += ['accept', 'url', 'agent']
    # Insert 'sep' between 'keywords'
    for kw in keywords:
        k.replace(kw, sep + kw + sep)
    # return it with 'case' case
    return getattr(k, case)()

def display_TraceBack(logger=logging.getLogger('TB'), level='error'):
    """ Allow the logging of a Traceback to a file.
    """
    # Get exec stack
    (exc_type, exc_val, exc_tb) = sys.exc_info()
    # Get 'logger's logging function 'level'
    log = getattr(logger, level)
    log("Caught an {0} exception at {1}.".format(exc_type, timestamp()))
    log("Error - {0}".format(exc_val))
    log("Call traceback")
    # Iterate over tb
    while exc_tb:
        function_name = exc_tb.tb_frame.f_code.co_name
        file_name = exc_tb.tb_frame.f_code.co_filename
        line_no = exc_tb.tb_lineno
        log(filename+" - \'"+function_name+"\' - "+str(line_no))
        exc_tb = exc_tb.tb_next

def retry_open(fl, *args, **kwargs):
    """ Allows you to retry opening the file if theres an IOError so that 2 
        hour processing run isn't wasted.
    """
    while True:
        try:
            return codecs.open(fl, *args, **kwargs)
        except IOError as ex:
            sys.stdout.write("{0} when opening {1}\n".format(ex, fl))
            sys.stdout.write("<Enter> to retry, s to skip: ")
            if 's' not in sys.stdin.readline().lower().strip():
                continue

def retry_urlopen(url, attempts=50, *args, **kwargs):
    """ Keep retrying the connection in-case the network's down.
    """
    for attempt in range(attempts):
        try:
            return urllib2.urlopen(url, *args, **kwargs)
        except urllib2.URLError as ex:
            log.error("Caught {0} in GetPage, retry number {1}.".format(ex, attempt))
            if "590" in str(ex):
                log.error("Getting new cookie")
                GetCookie()
            continue
            
    log.error("Retried {0} times with no valid response.".format(attempts))
    raise urllib2.URLError("Open retried {0} times!".format(attempts))
            
html_tag_re = re.compile('<.*?>')
def strip_html(data):
    return html_tag_re.sub('', data)

if __name__ == '__main__':
    sys.stderr.write("This module is to be imported, do not use directly.")
    sys.exit(1)
