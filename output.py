#!/usr/bin/env python
""" Wrappers to nicely output data in different formats.
"""

import sys
#import os
import logging
#import csv

from wrappers import s, header_join, ls, retry_open
import unicode_csv as csv


def repr2Dof2D(table, row_headers=None, column_headers=None, sep=None,
               minor_sep=None, header_sep=None):
    """Gives a string representation of a 2D array of 2D arrays."""
    # Some pretty defaults
    if header_sep is None:
        header_sep = ('\t|| ', '\n========\n') if sep is None else sep
    if minor_sep is None:
        minor_sep = (', ', '\n') if sep is None else sep
    if sep is None:
        sep = ('\t| ', '\n--------\n')
    # Main body.
    if column_headers:          # Add the top row
        if row_headers and len(column_headers) == len(table[0]):
            # Add the blank square in the top left
            rows = [header_join([''] + column_headers, header_sep[0], sep[0])]
        else:
            rows = [header_join(column_headers, header_sep[0], sep[0])]
    else:
        rows = []
    for i, row in enumerate(table):
        cell_rows = []  # Initiate list with rows of each cell concat'ed.
        for cell in row:
            for ii, cell_row in enumerate(cell):
                if len(cell_rows) <= ii:        # if first column, initiate row
                    if row_headers:
                        # Add the header or a blank filler.
                        cell_rows.append([row_headers[i]] if ii == 0 else [''])
                    else:
                        cell_rows.append([])
                cell_rows[ii].append(minor_sep[0].join(s(cell_row)))
        rows.append(minor_sep[1].join([header_join(r, header_sep[0], sep[0])
                                        for r in cell_rows]))
    return header_join(rows, header_sep[1], sep[1])


def latex2Dof2D(table, row_headers=None, column_headers=None, sep=None,
                minor_sep=None, header_sep=None):
    """Wrapper around repr2Dof2D() for LaTeX tabular environments."""
    # Some pretty defaults (requires booktabs package.
    cols = table.shape[1]
    inner_cols = table[0, 0].shape[1]
    if header_sep is None:
        if sep is None:
            header_sep = ('\t& ', '\t\\\\ \\hline\\hline\n')
        else:
            header_sep = sep
    if minor_sep is None:
        minor_sep = ('\t& ', '\t\\\\\n') if sep is None else sep
    if sep is None:
        sep = ('\t& ', '\t\\\\ \\hline\n')
    # Make LaTeX tabular header.
    header = '\\begin{tabular}{'
    if row_headers:
        header += 'l||'
    header += '|'.join([' '.join(['r'] * inner_cols)] * cols)
    header += '}\n'
    # Make headers span correct number of cells.
    r_h = map(lambda r: '\\multirow{%s}{*}{%s}' % (table[0, 0].shape[0], r),
              row_headers)
    c_h = map(lambda c: '\\multicolumn{%s}{|c}{%s}' % (table[0, 0].shape[1],
                                                       c),
              column_headers)
    str_repr = repr2Dof2D(table, r_h, c_h, sep, minor_sep, header_sep)
    footer = '\t\\\\\n\\end{tabular}'
    return '\n'.join((header, str_repr, footer))


def booktabs2Dof2D(table, row_headers=None, column_headers=None, sep=None,
                   minor_sep=None, header_sep=None):
    """Wrapper around repr2Dof2D() for LaTeX booktabs tabular environments."""
    # Some pretty defaults (requires booktabs package.
    cols = table.shape[1]
    inner_cols = table[0, 0].shape[1]
    if header_sep is None:
        if sep is None:
            if column_headers:      # Need a pretty header split.
                # Add the blank square in the top left
                inc = (2 if row_headers and len(column_headers) == cols else 1)
                mid = ' '.join(['\\cmidrule(lr){%s-%s}' %
                                    (i, i + inner_cols - 1)
                                    for i in range(inc, cols * inner_cols + 1,
                                                   inner_cols)])
            else:
                mid = '\\midrule'
            header_sep = ('\t& ', ''.join(('\t\\\\ ', mid, '\n')))
        else:
            header_sep = sep
    if minor_sep is None:
        minor_sep = ('\t& ', '\t\\\\\n') if sep is None else sep
    if sep is None:
        sep = ('\t& ', '\t\\\\ \\addlinespace\n')
    # Make LaTeX tabular header.
    header = '\\begin{tabular}{'
    if row_headers:
        header += 'l '
    header += ' '.join([' '.join(['r'] * inner_cols)] * cols)
    header += '}\n\\toprule'
    # Make headers span correct number of cells.
    r_h = map(lambda r: '\\multirow{%s}{*}{%s}' % (table[0, 0].shape[0], r),
              row_headers)
    c_h = map(lambda c: '\\multicolumn{%s}{c}{%s}' % (table[0, 0].shape[1], c),
              column_headers)
    str_repr = repr2Dof2D(table, r_h, c_h, sep, minor_sep, header_sep)
    footer = '\t\\\\ \\bottomrule\n\\end{tabular}'
    return '\n'.join((header, str_repr, footer))


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


try:
    import xlwt

    class OutputXl(OutputBase):
        pass
except ImportError:
    pass


try:
    from htmlgen import HTMLgen

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

        def close(self, fl=None, *args, **kwargs):
            if fl == None:
                fl = self.file
            fl.write(str(self.html))
            super(self.__class__, self).close(fl, *args, **kwargs)
except ImportError:
    pass


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


if __name__ == '__main__':
    sys.stderr.write('\n'.join((__doc__, 'import only.', '')))
    sys.exit(1)
