
# file openpyxl/tests/test_dump.py

# Copyright (c) 2010 openpyxl
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
# @license: http://www.opensource.org/licenses/mit-license.php
# @author: Eric Gazoni

# Python stdlib imports
from datetime import time, datetime

# 3rd party imports
from nose.tools import eq_

from openpyxl.workbook import Workbook
from openpyxl.writer import dump_worksheet
from openpyxl.cell import get_column_letter

from openpyxl.reader.excel import load_workbook

from openpyxl.writer.strings import StringTableBuilder

from tempfile import NamedTemporaryFile
import os
import os.path as osp
import shutil

def _get_test_filename():

    test_file = NamedTemporaryFile(prefix='openpyxl.', suffix='.xlsx', delete=False)
    test_file.close()
    return test_file.name

def test_dump_sheet():

    test_filename = _get_test_filename()

    wb = Workbook(optimized_write=True)

    ws = wb.create_sheet()

    letters = [get_column_letter(x + 1) for x in xrange(20)]

    expected_rows = []

    for row in xrange(20):

        expected_rows.append(['%s%d' % (letter, row + 1) for letter in letters])

    for row in xrange(20):

        expected_rows.append([(row + 1) for letter in letters])

    for row in xrange(10):

        expected_rows.append([datetime(2010, ((x % 12) + 1), row + 1) for x in range(len(letters))])

    for row in xrange(20):

        expected_rows.append(['=%s%d' % (letter, row + 1) for letter in letters])

    for row in expected_rows:

        ws.append(row)

    wb.save(test_filename)

    wb2 = load_workbook(test_filename, True)

    ws = wb2.worksheets[0]


    for ex_row, ws_row in zip(expected_rows[:-20], ws.iter_rows()):

        for ex_cell, ws_cell in zip(ex_row, ws_row):

            eq_(ex_cell, ws_cell.internal_value)

    os.remove(test_filename)


def test_table_builder():

    sb = StringTableBuilder()

    result = {'a':0, 'b':1, 'c':2, 'd':3}

    for letter in sorted(result.keys()):

        for x in range(5):

            sb.add(letter)

    table = dict(sb.get_table())

    for key, idx in result.iteritems():
        eq_(idx, table[key])

def test_open_too_many_files():

    test_filename = _get_test_filename()

    wb = Workbook(optimized_write=True)

    for i in range(200): # over 200 worksheets should raise an OSError ('too many open files') 

        wb.create_sheet()

    wb.save(test_filename)

    os.remove(test_filename)

def test_create_temp_file():

    f = dump_worksheet.create_temporary_file()

    if not osp.isfile(f):
        raise Exception("The file %s does not exist" % f)

def test_get_temp_file():

    FILES = []

    for i in range(dump_worksheet.DESCRIPTORS_CACHE_SIZE * 2):

        filename = dump_worksheet.create_temporary_file(suffix=str(i))
        fobj = dump_worksheet.get_temporary_file(filename)

        FILES.append(filename)

    eq_(len(dump_worksheet.DESCRIPTORS_CACHE), dump_worksheet.DESCRIPTORS_CACHE_SIZE)

    filename = FILES[0]

    assert filename  not in dump_worksheet.DESCRIPTORS_CACHE, "The cache contains a value that should have been evicted"

    fobj = dump_worksheet.get_temporary_file(filename)

    assert filename  in dump_worksheet.DESCRIPTORS_CACHE, "The cache does not contain a value that should have been loaded"

    # clean this mess a bit
    for fobj in dump_worksheet.DESCRIPTORS_CACHE.values():
        fobj.close()

    for filename in FILES:
        os.remove(filename)
