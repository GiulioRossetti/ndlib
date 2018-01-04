from __future__ import absolute_import
import unittest
import ndlib.parser.ExperimentParser as ep

__author__ = 'Giulio Rossetti'
__license__ = "BSD-2-Clause"
__email__ = "giulio.rossetti@gmail.com"


class NdlibParserTest(unittest.TestCase):

    def test_node_stochastic(self):
        query = "NDEFINE g1\n" \
                "NETWORK_TYPE erdos_renyi_graph\n" \
                "PARAM n 300\n" \
                "PARAM p 0.1\n" \
                "\n" \
                "MCREATE model1\n" \
                "\n" \
                "STATUS Susceptible\n" \
                "\n" \
                "STATUS Infected\n" \
                "\n" \
                "STATUS Removed\n" \
                "\n" \
                "CDEF c1\n" \
                "TYPE NodeStochastic\n" \
                "PARAM rate 0.1\n" \
                "TRIGGER Infected\n" \
                "\n" \
                "CDEF c2\n" \
                "TYPE NodeStochastic\n" \
                "PARAM rate 0.1\n" \
                "COMPOSE c1\n" \
                "TRIGGER Infected\n" \
                "\n" \
                "CDEF c3\n" \
                "TYPE NodeStochastic\n" \
                "PARAM rate 0.1\n" \
                "\n" \
                "RDEF\n" \
                "FROM Susceptible\n" \
                "TO Infected\n" \
                "COMPARTMENT c2\n" \
                "\n" \
                "RDEF\n" \
                "FROM Infected\n" \
                "TO Removed\n" \
                "COMPARTMENT c3\n" \
                "\n" \
                "MCONF\n" \
                "SET Infected 0.1\n" \
                "\n" \
                "EXECUTE model1 ON g1 FOR 100"

        parser = ep.ExperimentParser()
        parser.set_query(query)
        iterations = parser.parse()
        self.assertEqual(len(iterations), 100)

    def test_ifcompose(self):
        query = "NDEFINE g1\n" \
                "NETWORK_TYPE erdos_renyi_graph\n" \
                "PARAM n 300\n" \
                "PARAM p 0.1\n" \
                "\n" \
                "MCREATE model1\n" \
                "\n" \
                "STATUS Susceptible\n" \
                "\n" \
                "STATUS Infected\n" \
                "\n" \
                "STATUS Removed\n" \
                "\n" \
                "CDEF c1\n" \
                "TYPE NodeStochastic\n" \
                "PARAM rate 0.1\n" \
                "TRIGGER Infected\n" \
                "\n" \
                "CDEF c2\n" \
                "TYPE NodeStochastic\n" \
                "PARAM rate 0.1\n" \
                "TRIGGER Infected\n" \
                "\n" \
                "CDEF c3\n" \
                "TYPE NodeStochastic\n" \
                "PARAM rate 0.1\n" \
                "\n" \
                "IF c1 THEN c2 ELSE c3 AS r1\n" \
                "\n" \
                "RDEF\n" \
                "FROM Infected\n" \
                "TO Removed\n" \
                "COMPARTMENT r1\n" \
                "\n" \
                "MCONF\n" \
                "SET Infected 0.1\n" \
                "\n" \
                "EXECUTE model1 ON g1 FOR 100"

        parser = ep.ExperimentParser()
        parser.set_query(query)
        iterations = parser.parse()
        self.assertEqual(len(iterations), 100)