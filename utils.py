import pathlib
import yaml
import csv
from urllib.request import urlopen
import inspect


def read_file(path) -> str:
    path = pathlib.Path(path)
    data = None
    try:
        with open(path.resolve().as_posix()) as f:
            data = f.read()
    except Exception as err:
        print(f'Error with function {inspect.currentframe().f_code.co_name} .... ')
        print(err)
        print()

    return data


def write_file(path, data, mode='w+'):
    path = pathlib.Path(path)
    try:
        with open(path.resolve().as_posix(), mode) as f:
            f.write(data)
    except Exception as err:
        print(f'Error with function {inspect.currentframe().f_code.co_name} .... ')
        print(err)
        print()
        return

    return path


def read_yaml(path):
    path = pathlib.Path(path)
    try:
        text = read_file(path)
        data = yaml.load(text, Loader=yaml.Loader)
    except Exception as err:
        print(f'Error with function {inspect.currentframe().f_code.co_name} .... ')
        print(err)
        print()
        return

    return data


def write_yaml(path, data):
    path = pathlib.Path(path)
    try:
        text = yaml.dump(
            data,
            default_flow_style=False,
            sort_keys=False,
            allow_unicode=True,
        )
        output_path = write_file(path, text)

    except Exception as err:
        print(f'Error with function {inspect.currentframe().f_code.co_name} .... ')
        print(err)
        print()
        return

    return output_path


def download_csv(url):
    try:
        response = urlopen(url)
        lines = [line.decode('utf-8') for line in response.readlines()]
        csv_reader = csv.reader(lines, delimiter=',')
        csv_reader = [row for row in csv_reader]
    except Exception as err:
        print(f'Error with function {inspect.currentframe().f_code.co_name} .... ')
        print(err)
        print()
        return

    return csv_reader


def write_csv(path, data, mode='w'):
    path = pathlib.Path(path)
    try:
        with open(path.resolve().as_posix(), mode) as f:
            csvwriter = csv.writer(f)
            csvwriter.writerows(data)
    except Exception as err:
        print(f'Error with function {inspect.currentframe().f_code.co_name} ... ')
        print(err)
        print()
        return

    return path


def read_csv(path):
    path = pathlib.Path(path)
    try:
        with open(path.resolve().as_posix()) as f:
            csv_reader = csv.reader(f)
            data = [row for row in csv_reader]
    except Exception as err:
        print(f'Error with function {inspect.currentframe().f_code.co_name} ... ')
        print(err)
        print()
        return

    return data
