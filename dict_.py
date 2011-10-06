""" Dictionary helper functions.
"""

import collections


def safe_update(d, u, allow_false=False, **kwargs):
    """ Function to recursively update a dictionary, overwriting only if key 
        values have a higher precedence (depending on whether value is 'True' 
        and whether we 'allow_false' updates. Will never update with a value 
        of 'None'
    """
    # process u
    if hasattr(u, 'iteritems'):
        t = u.iteritems()
    else:
        t = u
    for k, v in t:
        if v and isinstance(v, dict):
            if isinstance(d.get(k), dict):
                safe_update(d[k], v, allow_false=allow_false)
            else:
                d[k] = v
        elif ((allow_false and v != None) or v or 
                (v != None and not d.get(k))):
            d[k] = v
    # process kwargs
    for k, v in kwargs.iteritems():
        if v and isinstance(v, dict):
            if isinstance(d.get(k), dict):
                safe_update(d[k], v, allow_false=allow_false)
            else:
                d[k] = v
        elif ((allow_false and v != None) or v or 
                (v != None and not d.get(k))):
            d[k] = v

def strip(d):
    """ Function to recursively remove 'None' values from a dictionary.
    """
    for k, v in d.items():
        if isinstance(v, dict):
            strip(d[k])
        elif v == None:
            del d[k]

def split(d):
    """ Function separate a dict's values that are dicts themselves. Removes 
        empty values.
    """
    g = {}
    for k, v in d.items():
        if isinstance(v, dict):
            t = d.pop(k)
            strip_dict(t)
            if t:
                g[k] = t
        elif v == None:
            del d[k]
    return d, g

def insert(parent, child, *args):
    """ Recursively inserts an element into a dictionary hierachy.
        Called as insert(dict, key_1, key_2, ..., key_n, val)
    """
    if len(args) > 1:
        if not isinstance(parent.get(child), dict):
            parent[child] = {}
        insert(parent[child], *args)
    else:
        parent[child] = args[0]

def group(l, attrs=('name')):
    """ Group list into dict hierachy based on attrs iterable.
    """
    grouped = {}
    for i in l:
        child = [eval('.'.join(('i', attr))) for attr in attrs]
        child.append(i)
        insert(grouped, *child)
    return grouped

def remove_children(group, test):
    """ Function to remove elements from dict hierachy using test function.
    """
    for child in group:
        if isinstance(child, dict):
            remove_children(child, cmp)
        else:
            if test(child):
                del child

def flatten(d):
    """ Function to flatten dict hierachy.
    """
    l = []
    for i in d.itervalues():
        if isinstance(i, dict):
            l.extend(flatten(i))
        else:
            l.append(i)
    return l

