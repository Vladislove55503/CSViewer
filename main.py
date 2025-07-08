import csv
import os
from operator import itemgetter
import re
import sys
from typing import List

import argparse
from tabulate import tabulate


def get_args():
    '''Return the arguments from the command line.'''
    parser = argparse.ArgumentParser(
        description='Getting arguments from the command line'
    )
    parser.add_argument(
        '-f',
        '--file',
        type=str,
        help='The path to the file'
    )
    parser.add_argument(
        '-w',
        '--where',
        type=str,
        help='Filtering parameter in the "column=value" format'
    )
    parser.add_argument(
        '-a',
        '--aggregate',
        type=str,
        help='Aggregation parameter in the "column=value" format'
    )
    parser.add_argument(
        '-ob',
        '--order-by',
        type=str,
        help='Sorting parameter in the "column=value" format'
    )
    args = parser.parse_args()
    return args


def get_path_to_csv_file(
    path: str | None,
    listdir: list = os.listdir()
) -> str:
    '''Return the path to the csv file, or terminate the program.'''
    if path == None:
        for path_in_dir in listdir:
            root, ext = os.path.splitext(path_in_dir)
            if ext == '.csv' and os.path.isfile(path_in_dir):
                return path_in_dir

        sys.exit('Error: file not found')

    elif os.path.isfile(path):
        root, ext = os.path.splitext(path)
        if ext == '.csv':
            return path

        sys.exit('Error: incorrect file extension')

    else:
        sys.exit('Error: file not found')


def get_column_types(path: str) -> dict:
    '''Return the dictionary of columns and their types.'''
    with open(path) as file:
        reader = csv.reader(file)
        headers = next(reader)
        row_values = next(reader)

    for i in range(len(row_values)):
        if row_values[i].isdigit():
            row_values[i] = int
            continue
        try:
            float(row_values[i])
            row_values[i] = float
        except ValueError:
            row_values[i] = str

    column_types = dict(zip(headers, row_values))
    return column_types


def get_where_params(column_types: dict, params: str) -> dict | None:
    '''Return the dictionary with the filtering parameters.'''
    if params == None:
        return None

    try:
        pat = re.compile(
            r'(?P<column>(\w+\s?)+)'
            r'(?P<operator>=|<|>)'
            r'(?P<value>(-?\d+.?\d+)|(\w+\s?)+)'
        )
        match = pat.search(params)
        where_params = match.groupdict()
    except:
        sys.exit('Error: incorrect format of the "--where" argument')

    if where_params['column'] not in column_types:
        sys.exit('Error: invalid column in the "--where" argument')

    if column_types[where_params['column']] == int:
        try:
            where_params['value'] = int(float(where_params['value']))
        except:
            sys.exit('Error: invalid value in the "--where" argument')

    if column_types[where_params['column']] == float:
        try:
            where_params['value'] = float(where_params['value'])
        except:
            sys.exit('Error: invalid value in the "--where" argument')

    return where_params


def get_aggregate_params(column_types: dict, params: str) -> dict | None:
    '''Return the dictionary with the aggregation parameters.'''
    allowed_values = ['avg', 'min', 'max']

    if params == None:
        return None

    try:
        pat = re.compile(
            r'(?P<column>(\w+\s?)+)(?P<operator>=)(?P<value>\w+)'
        )
        match = pat.search(params)
        aggregate_params = match.groupdict()
    except:
        sys.exit('Error: incorrect format of the "--aggregate" argument')

    if aggregate_params['column'] not in column_types:
        sys.exit('Error: invalid column in the "--aggregate" argument')

    if column_types[aggregate_params['column']] == str:
        sys.exit('Error: invalid column type in the "--aggregate" argument')

    if aggregate_params['value'] not in allowed_values:
        sys.exit('Error: invalid value in the "--aggregate" argument')

    return aggregate_params


def get_order_by_params(column_types: dict, params: str) -> dict | None:
    '''Return the dictionary with the sorting parameters.'''
    allowed_values = ['asc', 'desc']

    if params == None:
        return None

    try:
        pat = re.compile(
            r'(?P<column>(\w+\s?)+)(?P<operator>=)(?P<value>\w+)'
        )
        match = pat.search(params)
        order_by_params = match.groupdict()
    except:
        sys.exit('Error: incorrect format of the "--order_by" argument')

    if order_by_params['column'] not in column_types:
        sys.exit('Error: invalid column in the "--order-by" argument')

    if order_by_params['value'] not in allowed_values:
        sys.exit('Error: invalid value in the "--order-by" argument')

    return order_by_params


def read_lines_of_file(path: str, column_types: dict) -> List[dict]:
    '''Read the file and return the list of dictionaries with string data.'''
    with open(path) as file:
        list_objs = []
        headers = column_types.keys()
        reader = csv.DictReader(file)

        for row in reader:
            for header in headers:
                if column_types[header] == int:
                    row[header] = int(row[header])
                elif column_types[header] == float:
                    row[header] = float(row[header])

            list_objs.append(row)

        return list_objs


def get_list_where(list_objs: List[dict], params: dict) -> List[dict]:
    '''Change the list according to the "--where" condition.'''
    if params['operator'] == '=':
        list_objs = [
            obj for obj in list_objs
            if obj[params['column']] == params['value']
        ]

    elif params['operator'] == '<':
        list_objs = [
            obj for obj in list_objs
            if obj[params['column']] < params['value']
        ]

    elif params['operator'] == '>':
        list_objs = [
            obj for obj in list_objs
            if obj[params['column']] > params['value']
        ]

    return list_objs


def aggregate_list_objs(list_objs: List[dict], params: dict) -> List[tuple]:
    '''Aggregate the list according to the "--aggregate" condition.'''
    if len(list_objs) == 0:
        return [
            (params['value'],),
            ('Error: There are no objects for aggregation',)
        ]

    if params['value'] == 'avg':
        total_amount = 0

        for obj in list_objs:
            total_amount += obj[params['column']]

        try:
            result = total_amount / len(list_objs)
        except ZeroDivisionError:
            result = 0

    elif params['value'] == 'min':
        result = float('inf')

        for obj in list_objs:
            result = min(result, obj[params['column']])

    elif params['value'] == 'max':
        result = float('-inf')

        for obj in list_objs:
            result = max(result, obj[params['column']])

    aggregated_data = [(params['value'],), (result,)]
    return aggregated_data


def get_list_order_by(list_objs: List[dict], params: dict) -> List[dict]:
    '''Sort the list by the "--order-by" condition.'''
    if params['value'] == 'asc':
        sorted_list = sorted(list_objs, key=itemgetter(params['column']))

    elif params['value'] == 'desc':
        sorted_list = sorted(
            list_objs,
            key=itemgetter(params['column']),
            reverse=True
        )

    return sorted_list


def main(
    list_objs: List[dict],
    where_params: dict | None,
    aggregate_params: dict | None,
    order_by_params: dict | None
) -> List[dict]:
    '''Edit the list and output the resulting table.'''
    if order_by_params and aggregate_params:
        sys.exit('Error: the "--order-by" argument is not accepted together '
                 'with the "--aggregate" argument')

    if where_params:
        list_objs = get_list_where(list_objs=list_objs, params=where_params)

    if aggregate_params:
        aggregated_data = aggregate_list_objs(
            list_objs=list_objs,
            params=aggregate_params
        )
        print(tabulate(aggregated_data, headers='firstrow', tablefmt='grid'))
        sys.exit(0)

    if order_by_params:
        list_objs = get_list_order_by(
            list_objs=list_objs,
            params=order_by_params
        )

    print(tabulate(list_objs, headers='keys', tablefmt='grid'))
    return list_objs


if __name__ == '__main__':
    args = get_args()

    path_to_csv_file = get_path_to_csv_file(path=args.file)
    column_types = get_column_types(path_to_csv_file)

    where_params = get_where_params(
        column_types=column_types,
        params=args.where
    )
    aggregate_params = get_aggregate_params(
        column_types=column_types,
        params=args.aggregate
    )
    order_by_params = get_order_by_params(
        column_types=column_types,
        params=args.order_by
    )

    list_objs_of_file = read_lines_of_file(
        path=path_to_csv_file,
        column_types=column_types
    )

    main(
        list_objs=list_objs_of_file,
        where_params=where_params,
        aggregate_params=aggregate_params,
        order_by_params=order_by_params
    )
