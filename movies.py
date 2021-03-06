"""MovieLens Dataset exploration using python

This script allows user to get information about films.

This file can also be imported as a module and contains the following
functions:

    * read_csv - Read data from CSV file and return it as a list
    * print_data_csv - Print data in csv format
    * get_columns - Get column names of data
    * get_shape - Get number of rows and columns of data
    * data_info - Print data summary info
    * get_sorted_data - Get sorted data by column and order
    * get_groupped_data - Group data by column and apply aggregation function
    * get_groupped_data_from_file - Returns froupped data from file
    * merged_data - Merge Join two sorted datasets (tables) into one on unique key
    * get_factorized_data - Factorize column of data which contains multiple categorical data by splitting it on list of categories
    * get_categories_of_column - Get list of unique categories of non-atomic column which contains multiple categorical values splitted by delimiter
    * get_data_with_splitted_col - Split column of data and create new column by regular expression
    * filtered_data_col_contains - Filter data in condition if column contains substring
    * filtered_data_col_in_range - Filter data by slicing integer column
    * stacked_data - Return vertically stacked data
    * sliced_data - Dataset safe slicing method
    * get_arguments - Construct the argument parser and get the arguments
    * main - the main function of the script
"""


# import the necessary packages
import csv
import re
import time
import argparse
import logging as log
from itertools import groupby
from statistics import mean


DATA_FOLDER_PATH = 'data/ml-latest-small/'


def read_csv(file_path: str, delimiter: str = ',', columns: list = None, encoding: str = 'ascii') -> list:
    """Read data from CSV file and return it as a list

    Parameters
    ----------
    file_path : str
        File name of csv file
    delimiter : str, optional
        Delimiter of csv file, by default ','
    columns : list, optional
        Columns to read from file, by default None
    encoding : str, optional
        File encoding method, by default 'ascii'

    Returns
    -------
    list
        Data from file stored in list of dicts with column names as a keys
    """
    data = []
    try:
        with open(file_path, newline='') as csvfile:
            reader = csv.DictReader(csvfile, delimiter=delimiter)
            if columns:
                for row in reader:
                    data_row = {col: row.get(col) for col in columns}
                    data.append(data_row)
            else:
                data = [row for row in reader]
    except Exception as e:
        log.exception(e)

    return data


def get_groupped_data_from_file(file_path: str, group_by: str, agg_col: str, delimiter: str = ',') -> list:
    """Returns groupped data with two columns from file. Optimized algorithm 
    of reading and groupping with mean operations.

    Parameters
    ----------
    file_path : str
        File name to read
    group_by : str
        Group by column name
    agg_col : str
        Aggregation column name
    delimiter : str, optional
        Delimiter of csv file, by default ','

    Returns
    -------
    list
        Data stored in list of dicts
    """
    data = []
    try:
        with open(file_path, newline='') as csvfile:
            reader = csv.DictReader(csvfile, delimiter=delimiter)

            group_vals = {}
            for row in reader:
                gr_val = row.get(group_by)
                agg_val = float(row.get(agg_col))

                if gr_val in group_vals.keys():
                    group_vals[gr_val] += [agg_val]
                else:
                    group_vals[gr_val] = [agg_val]

            for k, v in group_vals.items():
                data.append({group_by: k, agg_col: round(sum(v)/len(v), 4)})
    except Exception as e:
        log.exception(e)

    return data


def print_data_csv(data: list, delimiter=',', n_rows=None) -> None:
    """Print data in csv format

    Parameters
    ----------
    data : list
        Data stored in list of dict
    delimiter : str, optional
        Separator of csv format, by default ','
    n_rows : int, optional
        Number of rows to display, by default None
    """
    try:
        if n_rows and len(data) >= n_rows:
            data = data[:n_rows]

        if len(data) == 0:
            return 0

        header = ','.join(get_columns(data))
        print(header)

        for row in data:
            csv_row = ''
            for k, v in row.items():
                if delimiter in str(v):
                    v = f'"{v}"'
                csv_row += delimiter + str(v)
            csv_row = csv_row[1:]
            print(csv_row)
    except Exception as e:
        log.exception(e)


def get_columns(data: list) -> list:
    """Get column names of data

    Parameters
    ----------
    data : list
        Data stored in list of dicts

    Returns
    -------
    list
        List of column names
    """
    columns = []
    try:
        assert data[0]
        columns = data[0].keys()
    except Exception as e:
        log.exception(e)

    return columns


def get_shape(data: list) -> tuple:
    """Get shape of data

    Parameters
    ----------
    data : list
        Dat stored in list of dicts

    Returns
    -------
    tuple
        tuple of number of rows and columns
    """
    return (len(get_columns(data)), len(data))


def data_info(data: list) -> str:
    """Print data summary info

    Parameters
    ----------
    data : list
        Data stored in list of dicts
    """
    cols = get_columns(data)
    shape = get_shape(data)
    return f'cols: {cols}, shape: {shape}'


def get_sorted_data(data: list, sort_by: str, reverse=True) -> list:
    """Get sorted data by column and order

    Parameters
    ----------
    data : list
        Data stored in list of dicts
    sort_by : str
        Sort data by specific column
    reverse : bool, optional
        Flag to determinate order of sorting (False - asc, True - desc), by default True

    Returns
    -------
    list
        Sorted data stored in list of dicts
    """
    return sorted(data, key=lambda k: (k[sort_by] is not None, k[sort_by]), reverse=reverse)


def get_groupped_data(data: list,  group_by: str, agg_column: str, agg_function='mean') -> list:
    """Group data by column and apply aggregation function

    Parameters
    ----------
    data : list
        Data stored in list of dicts
    group_by : str
        Column of groupping operation
    agg_column : str
        Column of aggregation
    agg_function : str, optional
        Aggregation function, by default 'mean'

    Returns
    -------
    list
        Groupped data stored in list of dicts
    """
    groupped_data = []

    for k, v in groupby(data, key=lambda x: x[group_by]):
        group_row = {group_by: k}
        agg_vals = [float(i[agg_column]) for i in v]
        group_row[agg_column] = round(mean(agg_vals), 4)
        groupped_data.append(group_row)

    return groupped_data


def merged_data(data_left: list, data_right: list, join_on: str) -> list:
    """Merge Join two sorted datasets (tables) into one on unique key

    Parameters
    ----------
    data_left : list
        Left data stored in list of dicts 
    data_right : list
        Right data stored in list of dicts
    join_on : str
        Common unique column key of two datasets

    Returns
    -------
    list
        Merged data stored in list of dicts
    """
    # get data right columns with None values in case when right table don`t match with left
    columns_right = data_right[0].keys()
    right_none = {e: None for e in columns_right if e != join_on}

    merged_data = []
    data_r_start = 0
    for row_left in data_left:
        merged_row = {**row_left, **right_none}
        for i in range(data_r_start, len(data_right)):
            if row_left[join_on] == data_right[i][join_on]:
                merged_row = {**row_left, **data_right[i]}
                data_r_start = i
                break
        merged_data.append(merged_row)

    return merged_data


def get_factorized_data(data: list, column: str, delimiter=',') -> list:
    """Factorize column of data which contains multiple 
    categorical data by splitting it on list of categories

    Parameters
    ----------
    data : list
        Data stored in list of dicts
    column : str
        Column name to factorize
    delimiter : str, optional
        Delimiter of values in column, by default ','

    Returns
    -------
    list
        Factorized data stored in list of dicts
    """
    # factorized_data = []

    for row in data:
        row[column] = row[column].split(delimiter)

    return data


def get_categories_of_column(data: list, column: str, delimiter=',') -> list:
    """Get list of unique categories of non-atomic column which contains
    multiple categorical values splitted by delimiter

    Parameters
    ----------
    data : list
        Data stored in list of dicts
    column : str
        Column name which contains multiple values
    delimiter : str, optional
        Delimiter of values in column, by default ','

    Returns
    -------
    list
        Unique list of categories in variable
    """
    column_values = ''
    for row in data:
        column_values += delimiter + str(row[column])

    splitted = column_values.split(delimiter)[1:]
    categories = list(set(splitted))

    return categories


def get_data_with_splitted_col(data: list, column: str, new_column: str, old_col_regex: str, new_col_regex: str) -> list:
    """Split column of data and create new column by regular expression

    Parameters
    ----------
    data : list
        Data stored in list of dicts
    column : str
        Column name you need to split
    new_column : str
        New column name 
    old_col_regex : str
        RegEx used to remove data from first column
    new_col_regex : str
        RegEx used to create new column

    Returns
    -------
    list
        Data stored in list of dicts
    """
    for row in data:
        if re.search(new_col_regex, row[column]):
            new_col_val = re.search(new_col_regex, row[column]).group()
        else:
            new_col_val = None
            log.warning(f'Can`t split column `{column}` in row: {row}')
        row[new_column] = new_col_val
        row[column] = re.sub(old_col_regex, '', row[column])

    return data


def filtered_data_col_contains(data: list, column: str, substring: str) -> list:
    """Filter data in condition if column contains substring

    Parameters
    ----------
    data : list
        Data stored in list of dicts
    column : str
        Filtering column
    substring : str
        Substring of column value

    Returns
    -------
    list
        Filtered data stored in list of dicts
    """
    filtered_data = []

    for row in data:
        if re.search(substring, row[column]):
            filtered_data.append(row)

    return filtered_data


def filtered_data_col_in_range(data: list, column: str, start=None, end=None) -> list:
    """Filter data by slicing integer column

    Parameters
    ----------
    data : list
        Data stored in list of dict
    column : str
        Filtered data column
    start : int, optional
        Lower boundary of range, by default None
    end : int, optional
        Higher boundary of range, by default None

    Returns
    -------
    list
        Filtered data stored in list of dict
    """
    filtered_data = []

    if start and end:
        if start > end:
            return None

        for row in data:
            if not row[column]:
                continue

            val = int(row[column])
            if start >= val and val <= end:
                filtered_data.append(row)
    elif start:
        for row in data:
            if not row[column]:
                continue

            if start <= int(row[column]):
                filtered_data.append(row)
    elif end:
        for row in data:
            if not row[column]:
                continue

            if int(row[column]) <= end:
                filtered_data.append(row)
    else:
        return data

    return filtered_data


def stacked_data(data_top: list, data_bottom: list) -> list:
    """Return vertically stacked data

    Parameters
    ----------
    data_top : list
        First data stored in list of dicts
    data_bottom : list
        Second data stored in list of dicts

    Returns
    -------
    list
        Stacked data
    """
    data_top.extend(data_bottom)
    return data_top


def sliced_data(data: list, start=None, end=None) -> list:
    """Dataset safe slicing method

    Parameters
    ----------
    data : list
        Data stored in list of dicts
    start : [type], optional
        Start index, by default None
    end : [type], optional
        End index, by default None

    Returns
    -------
    list
        Sliced data stored in list of dicts
    """
    if start:
        data = data[start:]
    if end:
        data = data[:end]
    return data


def get_arguments() -> dict:
    """Construct the argument parser and get the arguments

    Returns
    -------
    dict
        Dictionary of arguments and paramenters
    """
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("-n", "--topN", type=int,
                    help="the number of top rated movies for each genre. (example: 3)")
    ap.add_argument("-g", "--genres", type=str,
                    help="user-defined genre filter. can be multiple. (example: Comedy|Adventure)")
    ap.add_argument("-f", "--year_from", type=int,
                    help="the lower boundary of year filter (example: 1980)")
    ap.add_argument("-t", "--year_to", type=int,
                    help="the lower boundary of year filter (example: 2010)")
    ap.add_argument("-r", "--regexp", type=str,
                    help="filter on name of the film (example: love)")

    return vars(ap.parse_args())


def main():
    log.basicConfig(level=log.DEBUG,
                    filename='log/app.log',
                    filemode='w',
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    datefmt='%H:%M:%S')
    log.info('Start')
    # save start time for calculating
    time_start = time.perf_counter()

    # construct args
    log.info('constructing argument parser')
    args = get_arguments()
    log.info('Done!')
    log.debug(f'arguments: {args}')

    # read movies.csv
    log.info('reading movies.csv')
    movies = read_csv(DATA_FOLDER_PATH + 'movies.csv')
    log.info('Done!')
    log.debug(data_info(movies))

    # get year column from title
    log.info('splitting title to year')
    movies = get_data_with_splitted_col(movies, 'title', 'year',
                                        r'\s\(\d\d\d\d\)', r'\d\d\d\d')
    log.info('Done!')
    log.debug(data_info(movies))

    # filter by year
    log.info('filtering data by year_from and year_to')
    movies = filtered_data_col_in_range(
        movies, 'year',
        start=args['year_from'],
        end=args['year_to']
    )
    log.info('Done!')
    log.debug(data_info(movies))

    # filter by title
    if args['regexp']:
        log.info('filtering data by regexp')
        movies = filtered_data_col_contains(movies, 'title', args['regexp'])
        log.info('Done!')
        log.debug(data_info(movies))

    # sort movies
    log.info('sorting movies by movieId')
    movies = get_sorted_data(movies, 'movieId', reverse=False)
    log.info('Done!')

    # read ratings.csv
    log.info('reading ratings.csv')
    ratings = get_groupped_data_from_file(
        DATA_FOLDER_PATH + 'ratings.csv', 'movieId', 'rating')
    log.info('Done!')
    log.debug(data_info(ratings))

    # sort ratings
    log.info('sorting ratings by movieId')
    ratings = get_sorted_data(ratings, 'movieId', reverse=False)
    log.info('Done!')

    # merge data
    log.info('merging movies and ratings')
    data = merged_data(movies, ratings, 'movieId')
    log.info('Done!')
    log.debug(data_info(data))

    # sort data
    log.info('sorting data by rating')
    data = get_sorted_data(data, 'rating', reverse=True)
    log.info('Done!')

    if args['genres']:
        genres = args['genres'].split('|')
        stacked_data = []
        for genre in genres:
            log.info(f'working with {genre}')
            stacked_data.extend(
                sliced_data(
                    filtered_data_col_contains(data, 'genres', genre),
                    end=args['topN'])
            )
            log.info(f'{genre} genre added to output')
        print_data_csv(stacked_data)
        log.info('result printed')
        log.debug(data_info(stacked_data))
    else:
        print_data_csv(data, n_rows=args['topN'])
        log.info('result printed')

    time_elapsed = time.perf_counter() - time_start
    log.info(f'Finish in {time_elapsed:.4f} secs')


if __name__ == "__main__":
    main()
