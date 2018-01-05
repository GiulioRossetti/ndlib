from __future__ import absolute_import
import unittest
import ndlib.parser.ExperimentParser as ep

__author__ = 'Giulio Rossetti'
__license__ = "BSD-2-Clause"
__email__ = "giulio.rossetti@gmail.com"


class NdlibParserTest(unittest.TestCase):

    def test_node_stochastic(self):
        query = "CREATE_NETWORK g1\n" \
                "TYPE erdos_renyi_graph\n" \
                "PARAM n 300\n" \
                "PARAM p 0.1\n" \
                "\n" \
                "MODEL model1\n" \
                "\n" \
                "STATUS Susceptible\n" \
                "\n" \
                "STATUS Infected\n" \
                "\n" \
                "STATUS Removed\n" \
                "\n" \
                "COMPARTMENT c1\n" \
                "TYPE NodeStochastic\n" \
                "PARAM rate 0.1\n" \
                "TRIGGER Infected\n" \
                "\n" \
                "COMPARTMENT c2\n" \
                "TYPE NodeStochastic\n" \
                "PARAM rate 0.1\n" \
                "COMPOSE c1\n" \
                "TRIGGER Infected\n" \
                "\n" \
                "COMPARTMENT c3\n" \
                "TYPE NodeStochastic\n" \
                "PARAM rate 0.1\n" \
                "\n" \
                "RULE\n" \
                "FROM Susceptible\n" \
                "TO Infected\n" \
                "USING c2\n" \
                "\n" \
                "RULE\n" \
                "FROM Infected\n" \
                "TO Removed\n" \
                "USING c3\n" \
                "\n" \
                "INITIALIZE\n" \
                "SET Infected 0.1\n" \
                "\n" \
                "EXECUTE model1 ON g1 FOR 100"

        parser = ep.ExperimentParser()
        parser.set_query(query)
        iterations = parser.parse()
        self.assertEqual(len(iterations), 100)

    def test_ifcompose(self):
        query = "CREATE_NETWORK g1\n" \
                "TYPE erdos_renyi_graph\n" \
                "PARAM n 300\n" \
                "PARAM p 0.1\n" \
                "\n" \
                "MODEL model1\n" \
                "\n" \
                "STATUS Susceptible\n" \
                "\n" \
                "STATUS Infected\n" \
                "\n" \
                "STATUS Removed\n" \
                "\n" \
                "COMPARTMENT c1\n" \
                "TYPE NodeStochastic\n" \
                "PARAM rate 0.1\n" \
                "TRIGGER Infected\n" \
                "\n" \
                "COMPARTMENT c2\n" \
                "TYPE NodeStochastic\n" \
                "PARAM rate 0.1\n" \
                "TRIGGER Infected\n" \
                "\n" \
                "COMPARTMENT c3\n" \
                "TYPE NodeStochastic\n" \
                "PARAM rate 0.1\n" \
                "\n" \
                "IF c1 THEN c2 ELSE c3 AS r1\n" \
                "\n" \
                "RULE\n" \
                "FROM Infected\n" \
                "TO Removed\n" \
                "USING r1\n" \
                "\n" \
                "INITIALIZE\n" \
                "SET Infected 0.1\n" \
                "\n" \
                "EXECUTE model1 ON g1 FOR 100"

        parser = ep.ExperimentParser()
        parser.set_query(query)
        iterations = parser.parse()
        self.assertEqual(len(iterations), 100)