""" Wrappers to nicely output data in different formats
"""

import sys
import os
import logging
#import csv

from htmlgen import HTMLgen
import xlwt

from wrappers import retry_open, ls
import unicode_csv as csv


class OutputBase(object):
    def __init__(self, name=__name__, *args, **kwargs):
        self.log = logging.getLogger(__name__)
        self.name = name

    def open(self, fl=None, *args, **kwargs):
        if hasattr(self, 'file') and not self.file.closed:
            self.close()
        if fl == None:
            fl = self.file_name
        self.file = retry_open(fl, *args, **kwargs)
        self.file_name = fl
        self.log.debug("Opened {0} for writing.".format(fl))
        return self.file
    
    def write(self, message):
        print(message)

    def close(self, fl=None, *args, **kwargs):
        if fl == None:
            fl = self.file
        fl.close(*args, **kwargs)
        self.log.debug("{0} closed.".format(fl.name))

    #def __del__(self):
        #if not self.file.closed:
            #self.close()

class OutputCsv(OutputBase):
    def __init__(self, *args, **kwargs):
        super(self.__class__, self).__init__(*args, **kwargs)
        if '.csv' in self.name:
            self.file_name = self.name
            self.name = self.name.partition('.csv')[0]
        else:
            self.file_name = '.'.join((self.name, 'csv'))
        self.open(mode='wb')
    
    def open(self, *args, **kwargs):
        super(self.__class__, self).open(*args, **kwargs)
        self.csv = csv.writer(self.file, lineterminator='\n')
        return self.file
    
    def writerow(self, row):
        if self.file.tell() == 0:
            if hasattr(row, '_fields'):
                self.csv.writerow(row._fields)
        self.csv.writerow(row)

class OutputXl(OutputBase):
    pass

class OutputHtml(OutputBase):
    def __init__(self, *args, **kwargs):
        super(self.__class__, self).__init__(*args, **kwargs)
        if '.htm' in self.name:
            self.file_name = self.name
            self.name = self.name.partition('.htm')[0]
        else:
            self.file_name = '.'.join((self.name, 'html'))
        self.open(mode='wb')
        
    def open(self, title=None, *args, **kwargs):
        super(self.__class__, self).open(*args, **kwargs)
        if title == None:
            title = self.name
        self.html = HTMLgen.SimpleDocument(title=title)
        self.table = HTMLgen.Table(tabletitle=title)
        self.table.body = []
        self.html.append(self.table)
        return self.file
        
    def writerow(self, row):
        if not self.table.heading:
            if hasattr(row, '_fields'):
                self.table.heading = row._fields
        self.table.body.append(list(row))
        
    def close(self, fl= None, *args, **kwargs):
        if fl == None:
            fl = self.file
        fl.write(str(self.html))
        super(self.__class__, self).close(fl, *args, **kwargs)


def table(rows, name='output', types=('csv',)):
    log = logging.getLogger(__name__.title())
    log.info("Attempting to write list to file type(s): " + ls(types))
    op_names = [''.join(('Output', t.title())) for t in types]
    env = globals()
    outputs = [env[op_n](name) for op_n in op_names if op_n in env]
    log.debug("Found valid output types: " + ls(outputs))
    for row in rows:
        [output.writerow(row) for output in outputs]
    [output.close() for output in outputs]

