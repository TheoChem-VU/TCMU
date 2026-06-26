'''
Module for working with very basic spread sheets.
The main motivation for the creation of this module is
that we cannot programmatically put molecular xyz-coordinates
or any multiline value inside of CSV files. This module
provides a very basic way of including any kind of value inside
a .xlsx file.
'''
from typing import List
import os
import openpyxl as xl


def append(file: str, values: List[str]):
    '''
    '''
    if not os.path.exists(file):
        wb = xl.Workbook()
        ws = wb.active
        row = ws.max_row
    else:
        wb = xl.load_workbook(file)
        ws = wb.active
        row = ws.max_row + 1

    for i, val in enumerate(values):
        ws.cell(row=row, column=i+1, value=val)

    wb.save(file)
