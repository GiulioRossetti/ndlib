__author__ = 'Giulio Rossetti'
__license__ = "BSD-2-Clause"
__email__ = "giulio.rossetti@gmail.com"

import ndlib.parser.ExperimentParser as ep
import json
import argparse


def execute():

    parser = argparse.ArgumentParser()

    parser.add_argument('query_file', type=str, help='simulation query file')
    parser.add_argument('result_file', type=str, help='simulation result file')

    args = parser.parse_args()
    query = ""
    with open(args.query_file) as f:
        query = f.read()

    NDQL_parser = ep.ExperimentParser()
    NDQL_parser.set_query(query)
    NDQL_parser.parse()
    iterations = NDQL_parser.execute_query()

    with open(args.result_file, "w") as o:
        o.write(json.dumps(iterations))

