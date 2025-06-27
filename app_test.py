import csv
import os

import pytest

from main import (get_column_types, get_path_to_csv_file, get_where_params, 
                  get_aggregate_params, get_order_by_params, 
                  read_lines_of_file, get_list_where, aggregate_list_objs, 
                  get_list_order_by, main)


def create_dir_or_file(
    path, 
    directory_name: str | None = None, 
    file_name: str | None = None
) -> list:
    '''Create a directory or file and return the list of absolute paths.'''
    result = []

    if directory_name:
        d = path / directory_name
        d.mkdir()
        result.append(d)

    if file_name:
        f = path / file_name
        f.touch()
        result.append(f)

    return result


def test_get_path_to_csv_file_1(tmp_path):
    listdir = create_dir_or_file(
        path=tmp_path, 
        file_name='file.csv'
    )
    path = None
    assert get_path_to_csv_file(path, listdir) == tmp_path / 'file.csv'


def test_get_path_to_csv_file_2(tmp_path):
    listdir = create_dir_or_file(
        path=tmp_path, 
        directory_name='directory.csv'
    )
    path = None

    with pytest.raises(SystemExit) as e:
        get_path_to_csv_file(path, listdir)

    assert e.value.code == 'Error: file not found'


def test_get_path_to_csv_file_3(tmp_path):
    listdir = create_dir_or_file(path=tmp_path)
    path = None

    with pytest.raises(SystemExit) as e:
        get_path_to_csv_file(path, listdir)

    assert e.value.code == 'Error: file not found'


def test_get_path_to_csv_file_4(tmp_path):
    listdir = create_dir_or_file(
        path=tmp_path,
        file_name='file.txt',
    )
    path = tmp_path / 'file.txt'

    with pytest.raises(SystemExit) as e:
        get_path_to_csv_file(path, listdir)

    assert e.value.code == 'Error: incorrect file extension'


def test_get_path_to_csv_file_5(tmp_path):
    listdir = create_dir_or_file(
        path=tmp_path
    )
    path = tmp_path / 'file.txt'

    with pytest.raises(SystemExit) as e:
        get_path_to_csv_file(path, listdir)

    assert e.value.code == 'Error: file not found'


def test_get_path_to_csv_file_6(tmp_path):
    listdir = create_dir_or_file(
        path=tmp_path
    )
    path = tmp_path / 'file.csv'

    with pytest.raises(SystemExit) as e:
        get_path_to_csv_file(path, listdir)

    assert e.value.code == 'Error: file not found'


def test_get_path_to_csv_file_7(tmp_path):
    listdir = create_dir_or_file(
        path=tmp_path,
        file_name='file.csv'
    )
    path = tmp_path / 'file.csv'
    assert get_path_to_csv_file(path, listdir) == tmp_path / 'file.csv'


def test_get_path_to_csv_file_8(tmp_path):
    listdir = create_dir_or_file(
        path=tmp_path,
        directory_name='directory.csv'
    )
    path = tmp_path / 'directory.csv'

    with pytest.raises(SystemExit) as e:
        get_path_to_csv_file(path, listdir)

    assert e.value.code == 'Error: file not found'


@pytest.mark.parametrize('data_to_csv, expected_result', [
    (
        [['name', 'year', 'age', 'website'], 
         ['alex', '1985', '40.5', '55.com']], 
        {'name': str, 'year': int, 'age': float, 'website': str}
    ),
])
def test_get_column_types(tmp_path, data_to_csv, expected_result):
    listdir = create_dir_or_file(
        path=tmp_path, 
        file_name='file.csv'
    )
    path = tmp_path / listdir[0]
    
    with open(path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(data_to_csv)

    assert get_column_types(path) == expected_result


@pytest.mark.parametrize('params, expected_result', [
    ('name=alex', {'column': 'name', 'operator': '=', 'value': 'alex'}),
    ('year<10',   {'column': 'year', 'operator': '<', 'value': 10}),
    ('age>30.1',  {'column': 'age', 'operator': '>', 'value': 30.1}),
    (
        'name=galaxy z flip 5',  
        {'column': 'name', 'operator': '=', 'value': 'galaxy z flip 5'}
    ),
    (None, None),
])
def test_get_where_params(params, expected_result):
    column_types = {'name': str, 'year': int, 'age': float}
    assert get_where_params(column_types, params) == expected_result


def test_long_column_and_value_in_get_where_params():
    params = 'name lastname middlename=john carter bob'
    column_types = {'name lastname middlename': str}
    expected_result = {
            'column': 'name lastname middlename', 
            'operator': '=', 
            'value': 'john carter bob'
        }
    assert get_where_params(column_types, params) == expected_result


@pytest.mark.parametrize('params, expected_result', [
    ('namealex',     'Error: incorrect format of the "--where" argument'),
    ('name==alex',   'Error: incorrect format of the "--where" argument'),
    ('name<=alex',   'Error: incorrect format of the "--where" argument'),
    ('=alex',        'Error: incorrect format of the "--where" argument'),
    ('name=',        'Error: incorrect format of the "--where" argument'),

    ('height=180',   'Error: invalid column in the "--where" argument'),
    ('year=no_int',  'Error: invalid value in the "--where" argument'),
    ('age=no_float', 'Error: invalid value in the "--where" argument'),
])
def test_exception_get_where_params(params, expected_result):
    column_types = {'name': str, 'year': int, 'age': float}

    with pytest.raises(SystemExit) as e:
        get_where_params(column_types, params)

    assert e.value.code == expected_result


@pytest.mark.parametrize('params, expected_result', [
    ('year=avg',  {'column': 'year', 'operator': '=', 'value': 'avg'}),
    ('age=avg',   {'column': 'age', 'operator': '=', 'value': 'avg'}),
    (None, None),
])
def test_get_aggregate_params(params, expected_result):
    column_types = {'name': str, 'year': int, 'age': float}
    assert get_aggregate_params(column_types, params) == expected_result


@pytest.mark.parametrize('params, expected_result', [
    ('yearavg',    'Error: incorrect format of the "--aggregate" argument'),
    ('year==avg',  'Error: incorrect format of the "--aggregate" argument'),
    ('year<=avg',  'Error: incorrect format of the "--aggregate" argument'),
    ('=avg',       'Error: incorrect format of the "--aggregate" argument'),
    ('year=',      'Error: incorrect format of the "--aggregate" argument'),

    ('height=avg', 'Error: invalid column in the "--aggregate" argument'),
    ('name=avg',   'Error: invalid column type in the "--aggregate" argument'),
    ('year=fff',   'Error: invalid value in the "--aggregate" argument'),
])
def test_exception_get_aggregate_params(params, expected_result):
    column_types = {'name': str, 'year': int, 'age': float}

    with pytest.raises(SystemExit) as e:
        get_aggregate_params(column_types, params)

    assert e.value.code == expected_result


@pytest.mark.parametrize('params, expected_result',[
    ('name=asc',  {'column': 'name', 'operator': '=', 'value': 'asc'}),
    (None, None),
])
def test_get_order_by_params(params, expected_result):
    column_types = {'name': str, 'year': int, 'age': float}
    assert get_order_by_params(column_types, params) == expected_result


@pytest.mark.parametrize('params, expected_result', [
    ('nameasc',    'Error: incorrect format of the "--order_by" argument'),
    ('name==asc',  'Error: incorrect format of the "--order_by" argument'),
    ('name<=asc',  'Error: incorrect format of the "--order_by" argument'),
    ('=asc',       'Error: incorrect format of the "--order_by" argument'),
    ('name=',      'Error: incorrect format of the "--order_by" argument'),

    ('height=asc', 'Error: invalid column in the "--order-by" argument'),
    ('name=fff',   'Error: invalid value in the "--order-by" argument'),
])
def test_exception_get_order_by_params(params, expected_result):
    column_types = {'name': str, 'year': int, 'age': float}

    with pytest.raises(SystemExit) as e:
        get_order_by_params(column_types, params)

    assert e.value.code == expected_result


@pytest.mark.parametrize('data_to_csv, column_types, expected_result', [
    (
        [['name', 'year', 'age', 'website'], 
         ['alex', '1985', '40.5', '55.com']],
        {'name': str, 'year': int, 'age': float, 'website': str}, 
        [{'name': 'alex', 'year': 1985, 'age': 40.5, 'website': '55.com'}]
    ),
])
def test_read_lines_of_file(
    tmp_path, 
    data_to_csv, 
    column_types, 
    expected_result
):
    listdir = create_dir_or_file(
        path=tmp_path,
        file_name='file.csv'
    )
    path = tmp_path / listdir[0]

    with open(path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(data_to_csv)

    assert read_lines_of_file(path, column_types) == expected_result


@pytest.mark.parametrize('params, expected_result', [
    # operator "="
    (
        {'column': 'name', 'operator': '=', 'value': 'alex'},
        [{'name': 'alex', 'year': 1985, 'age': 40.5}]
    ),
    (
        {'column': 'name', 'operator': '=', 'value': 'mark'},
        [{'name': 'mark', 'year': 1990, 'age': 35.0}]
    ),
    (
        {'column': 'year', 'operator': '=', 'value': 1985},
        [{'name': 'alex', 'year': 1985, 'age': 40.5}]
    ),
    (
        {'column': 'year', 'operator': '=', 'value': 1990},
        [{'name': 'mark', 'year': 1990, 'age': 35.0}]
    ),
    (
        {'column': 'age', 'operator': '=', 'value': 40.5},
        [{'name': 'alex', 'year': 1985, 'age': 40.5}]
    ),
    (
        {'column': 'age', 'operator': '=', 'value': 35.0},
        [{'name': 'mark', 'year': 1990, 'age': 35.0}]
    ),
    # operator "<"
    (
        {'column': 'name', 'operator': '<', 'value': 'alex'},
        []
    ),
    (
        {'column': 'name', 'operator': '<', 'value': 'mark'},
        [{'name': 'alex', 'year': 1985, 'age': 40.5}]
    ),
    (
        {'column': 'year', 'operator': '<', 'value': 1985},
        []
    ),
    (
        {'column': 'year', 'operator': '<', 'value': 1990},
        [{'name': 'alex', 'year': 1985, 'age': 40.5}]
    ),
    (
        {'column': 'age', 'operator': '<', 'value': 40.5},
        [{'name': 'mark', 'year': 1990, 'age': 35.0}]
    ),
    (
        {'column': 'age', 'operator': '<', 'value': 35.0},
        []
    ),
    # operator ">"
    (
        {'column': 'name', 'operator': '>', 'value': 'alex'},
        [{'name': 'mark', 'year': 1990, 'age': 35.0}]
    ),
    (
        {'column': 'name', 'operator': '>', 'value': 'mark'},
        []
    ),
    (
        {'column': 'year', 'operator': '>', 'value': 1985},
        [{'name': 'mark', 'year': 1990, 'age': 35.0}]
    ),
    (
        {'column': 'year', 'operator': '>', 'value': 1990},
        []
    ),
    (
        {'column': 'age', 'operator': '>', 'value': 40.5},
        []
    ),
    (
        {'column': 'age', 'operator': '>', 'value': 35.0},
        [{'name': 'alex', 'year': 1985, 'age': 40.5}]
    ),
])
def test_get_list_where(params, expected_result):
    list_objs = [
        {'name': 'alex', 'year': 1985, 'age': 40.5},
        {'name': 'mark', 'year': 1990, 'age': 35.0},
    ]
    assert get_list_where(list_objs, params) == expected_result


@pytest.mark.parametrize('params, expected_result', [
    # value "avg"
    (
        {'column': 'year', 'operator': '=', 'value': 'avg'},
        [('avg',), (1987.5,)]
    ),
    (
        {'column': 'age', 'operator': '=', 'value': 'avg'},
        [('avg',), (37.75,)]
    ),
    # value "min"
    (
        {'column': 'year', 'operator': '=', 'value': 'min'},
        [('min',), (1985,)]
    ),
    (
        {'column': 'age', 'operator': '=', 'value': 'min'},
        [('min',), (35.0,)]
    ),
    # value "max"
    (
        {'column': 'year', 'operator': '=', 'value': 'max'},
        [('max',), (1990,)]
    ),
    (
        {'column': 'age', 'operator': '=', 'value': 'max'},
        [('max',), (40.5,)]
    ),
])
def test_aggregate_list_objs(params, expected_result):
    list_objs = [
        {'name': 'alex', 'year': 1985, 'age': 40.5},
        {'name': 'mark', 'year': 1990, 'age': 35.0},
    ]
    assert aggregate_list_objs(list_objs, params) == expected_result


@pytest.mark.parametrize('list_objs, params, expected_result', [
    (   
        [],
        {'column': 'year', 'operator': '=', 'value': 'avg'},
        [('avg',), ('Error: There are no objects for aggregation',)]
    ),
    (
        [{'name': 'Nick', 'year': 0, 'age': 2025.0},],
        {'column': 'year', 'operator': '=', 'value': 'avg'},
        [('avg',), (0,)]
    ),
])
def test_exception_aggregate_list_objs(list_objs, params, expected_result):
    assert aggregate_list_objs(list_objs, params) == expected_result


@pytest.mark.parametrize('params, expected_result', [
    # value "asc"
    (
        {'column': 'name', 'operator': '=', 'value': 'asc'},
        [
            {'name': 'alex', 'year': 1985, 'age': 40.5},
            {'name': 'cole', 'year': 2000, 'age': 25.0},
            {'name': 'mark', 'year': 1990, 'age': 35.0},
        ]
    ),
    (
        {'column': 'year', 'operator': '=', 'value': 'asc'},
        [
            {'name': 'alex', 'year': 1985, 'age': 40.5},
            {'name': 'mark', 'year': 1990, 'age': 35.0},
            {'name': 'cole', 'year': 2000, 'age': 25.0},
        ]
    ),
    (
        {'column': 'age', 'operator': '=', 'value': 'asc'},
        [
            {'name': 'cole', 'year': 2000, 'age': 25.0},
            {'name': 'mark', 'year': 1990, 'age': 35.0},
            {'name': 'alex', 'year': 1985, 'age': 40.5},
        ]
    ),
    # value "desc"
    (
        {'column': 'name', 'operator': '=', 'value': 'desc'},
        [
            {'name': 'mark', 'year': 1990, 'age': 35.0},
            {'name': 'cole', 'year': 2000, 'age': 25.0},
            {'name': 'alex', 'year': 1985, 'age': 40.5},
        ]
    ),
    (
        {'column': 'year', 'operator': '=', 'value': 'desc'},
        [
            {'name': 'cole', 'year': 2000, 'age': 25.0},
            {'name': 'mark', 'year': 1990, 'age': 35.0},
            {'name': 'alex', 'year': 1985, 'age': 40.5},
        ]
    ),
    (
        {'column': 'age', 'operator': '=', 'value': 'desc'},
        [
            {'name': 'alex', 'year': 1985, 'age': 40.5},
            {'name': 'mark', 'year': 1990, 'age': 35.0},
            {'name': 'cole', 'year': 2000, 'age': 25.0},
        ]
    ),
])
def test_get_list_order_by(params, expected_result):
    list_objs = [
        {'name': 'alex', 'year': 1985, 'age': 40.5},
        {'name': 'mark', 'year': 1990, 'age': 35.0},
        {'name': 'cole', 'year': 2000, 'age': 25.0},
    ]
    assert get_list_order_by(list_objs, params) == expected_result


@pytest.mark.parametrize(
    'where_params, aggregate_params, order_by_params, expected_result', [
    (
        None, 
        None, 
        None, 
        [
            {'name': 'mark', 'year': 1990, 'age': 35.0},
            {'name': 'alex', 'year': 1985, 'age': 40.5},
            {'name': 'cole', 'year': 2000, 'age': 25.0},
        ]
    ),
    (
        {'column': 'name', 'operator': '>', 'value': 'alex'},
        None, 
        None,
        [
            {'name': 'mark', 'year': 1990, 'age': 35.0},
            {'name': 'cole', 'year': 2000, 'age': 25.0},
        ]
    ),
    (
        None,
        None, 
        {'column': 'name', 'operator': '=', 'value': 'desc'}, 
        [
            {'name': 'mark', 'year': 1990, 'age': 35.0},
            {'name': 'cole', 'year': 2000, 'age': 25.0},
            {'name': 'alex', 'year': 1985, 'age': 40.5},
        ]
    ),
])
def test_main(
    where_params,
    aggregate_params,
    order_by_params,
    expected_result
):
    data = [
        {'name': 'mark', 'year': 1990, 'age': 35.0},
        {'name': 'alex', 'year': 1985, 'age': 40.5},
        {'name': 'cole', 'year': 2000, 'age': 25.0},
    ]

    assert main(
        list_objs=data, 
        where_params=where_params,
        aggregate_params=aggregate_params,
        order_by_params=order_by_params
    ) == expected_result


@pytest.mark.parametrize(
    'where_params, aggregate_params, order_by_params, expected_result', [
    (
        None,
        {'column': 'year', 'operator': '=', 'value': 'avg'}, 
        {'column': 'name', 'operator': '=', 'value': 'asc'}, 
        'Error: the "--order-by" argument is not accepted together ' 
        'with the "--aggregate" argument'
    ),
    (
        None,
        {'column': 'age', 'operator': '=', 'value': 'avg'},
        None,
        0
    ),
])
def test_exception_main(
    where_params,
    aggregate_params,
    order_by_params,
    expected_result
):
    data = [
        {'name': 'mark', 'year': 1990, 'age': 35.0},
        {'name': 'alex', 'year': 1985, 'age': 40.5},
        {'name': 'cole', 'year': 2000, 'age': 25.0},
    ]

    with pytest.raises(SystemExit) as e:
        main(
            list_objs=data, 
            where_params=where_params,
            aggregate_params=aggregate_params,
            order_by_params=order_by_params
        )
    assert e.value.code == expected_result
