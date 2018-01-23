__author__ = 'Giulio Rossetti'
__license__ = "BSD-2-Clause"
__email__ = "giulio.rossetti@gmail.com"

import ndlib.parser.ExperimentParser as ep
import argparse


def translate():

    parser = argparse.ArgumentParser()

    parser.add_argument('query_file', type=str, help='simulation query file')
    parser.add_argument('python_file', type=str, help='Python script file')

    args = parser.parse_args()
    query = ""
    with open(args.query_file) as f:
        query = f.read()

    NDQL_parser = ep.ExperimentParser()
    NDQL_parser.set_query(query)
    NDQL_parser.parse()

    with open(args.python_file, "w") as o:
        o.write(NDQL_parser.script)

