#!/usr/bin/env python
""" Wrappers to easily import data from different formats.
"""

import sys
import logging
from collections import namedtuple, OrderedDict

try:
    import unicode_csv as csv
except ImportError:
    import csv


log = logging.getLogger(__name__)


def csv2list(fl, fieldnames=None, return_type=None, **kwargs):
    """ Reads a csv file, using the first line as column headings if none are
        supplied, returns rows as a list.

        Results are returned as a list of rows, each row either being an
        instance of the type returned by the constractor passed as
        'return_type', of a namedtuple that is generated from the file name and
        header. If a fieldnames iterable is supplied, as would be to a

        DictReader, this is used instead of the first row for headings.
        Extra kwargs are passed directly to the csv.reader, including an
        optional 'encoding' if the unicode_csv is in use.
    """
    log.info("Parsing '{0}'.".format(fl))
    with open(fl, 'rb') as csv_file:
        log.debug("Getting sample to test for dialect.")
        sample = ''.join([csv_file.readline() for i in range(5)])
        csv_file.seek(0)
        if 'dialect' not in kwargs:
            log.debug("Sniff dialect.")
            sniffer = csv.Sniffer()
            kwargs['dialect'] = sniffer.sniff(sample)
        log.debug("Initiate reader.")
        reader = csv.reader(csv_file, **kwargs)
        if not return_type:
            log.debug("Attempting to generate return tuple")
            if sniffer.has_header(sample):
                if fieldnames:
                    log.debug(' '.join(("Fieldnames defined in function call,",
                                        "discarding unneded header row.")))
                    reader.next()
                else:
                    fieldnames = reader.next()
            if fieldnames:
                name = fl.split('.', 1)[0]
                return_type = namedtuple(name, fieldnames)
            else:
                log.debug(' '.join(("Could not generate a namedtuple,",
                                    "falling back to a standardtuple.")))
                return_type = tuple
        log.debug("Parsing '{0}' into '{1}'s.".format(fl, return_type))
        rows = [return_type(row) for row in reader]
        log.debug("Parsed {0} rows".format(len(rows)))
    return rows


# Function template definitions for csv2dict row adding.
_new_template = """
def _new(v):
    return {0}
"""
_new_dict = {'always': '[v]',
             'only': 'v',
             'overwrite': 'v',
             'never': 'v',
             'raise': 'v'
            }
_add_template = """
def _add(ov, v):
    {0}
"""
_add_dict = {'always': 'return ov + [v]',
             'only': 'return (ov + [v]) if isinstance(ov, list) else [ov, v]',
             'overwrite': 'return v',
             'never': 'return ov',
             'raise': 'raise TypeError("Cannot assign multiple values")'
            }


def csv2dict(fl, fieldnames=None, row_headers=False, list_values='raise',
             return_type=None, **kwargs):
    """ Reads a csv file, using the first line as column headings if none are
        supplied, and the first column as rows headers.

        The row headers act as keys to the OrderedDict that is returned. Each
        entry in the dict is either an instance of the type returned by the
        constractor passed as 'return_type', of a namedtuple that is generated
        from the file name and header. If a fieldnames iterable is supplied, as
        would be to a DictReader, this is used instead of the first row for
        headings.

        The 'list_values' arg defines whether to make dict values a list of the
        respective rows with the same first column:
            'always'    always use lists
            'only'      only use lists when there are multiple entries
            'overwrite' overwrite old values with newer ones
            'never'     never use lists, discarding later values
            'raise'     raise a TypeError if there are multiple values.

        Extra kwargs are passed directly to the csv.reader, including an
        optional 'encoding' if the unicode_csv is in use.
    """
    # Create function definitions for different versions of 'list_values'
    try:
        exec _new_template.format(_new_dict[list_values])
        #def _new(v): return v
        exec _add_template.format(_add_dict[list_values])
        #def _add(ov, v): raise TypeError("Cannot assign multiple values")
    except KeyError:
        raise ValueError("Invalid value for 'list_values': '{0}'."
                            .format(list_values))
    # Initiate dictionary
    rows = OrderedDict()
    log.info("Parsing '{0}'.".format(fl))
    with open(fl, 'rb') as csv_file:
        log.debug("Getting sample to test for dialect.")
        sample = ''.join([csv_file.readline() for i in range(5)])
        csv_file.seek(0)
        if 'dialect' not in kwargs:
            log.debug("Sniff dialect.")
            sniffer = csv.Sniffer()
            kwargs['dialect'] = sniffer.sniff(sample)
        log.debug("Initiate reader.")
        reader = csv.reader(csv_file, **kwargs)
        if not return_type:
            log.debug("Attempting to generate return tuple")
            if sniffer.has_header(sample):
                if fieldnames:
                    log.debug(' '.join(("Fieldnames defined in function call,",
                                        "discarding unneded header row.")))
                    reader.next()
                else:
                    fieldnames = reader.next()
            if fieldnames:
                first_row = reader.next()
                if len(fieldnames) >= len(first_row) and first_row[0]:
                    name, fieldnames = fieldnames[0], fieldnames[1:]
                else:
                    name = fl.split('.', 1)[0]
                return_type = namedtuple(name.capitalize(), fieldnames)
                rows[first_row[0]] = _new(return_type(*first_row[1:]))
            else:
                log.debug(' '.join(("Could not generate a namedtuple,",
                                    "falling back to a standard tuple.")))
                return_type = tuple
        log.debug("Parsing '{0}' into '{1}'s.".format(fl, return_type))
        for row in reader:
            if row[0] in rows:
                rows[row[0]] = _add(rows[row[0]], return_type(*row[1:]))
            else:
                rows[row[0]] = _new(return_type(*row[1:]))
        log.debug("Parsed {0} rows".format(len(rows)))
    return rows

if __name__ == '__main__':
    sys.stderr.write('\n'.join((__doc__, 'import only.', '')))
    sys.exit(0)
