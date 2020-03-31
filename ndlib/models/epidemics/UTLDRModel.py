from ..DiffusionModel import DiffusionModel
import numpy as np
import future

__author__ = ["Giulio Rossetti"]
__license__ = "BSD-2-Clause"


class UTLDRModel(DiffusionModel):

    def __init__(self, graph, seed=None):

        super(self.__class__, self).__init__(graph, seed)

        self.old_graph = None

        self.name = "UTLDR"

        self.available_statuses = {
            "Susceptible": 0,
            "Exposed": 2,
            "Infected": 1,
            "Recovered": 3,
            "Tested_E": 4,
            "Tested_I": 5,
            "Tested_H": 6,
            "Lockdown_S": 7,
            "Lockdown_E": 8,
            "Lockdown_I": 9,
            "Dead": 10
        }
        self.parameters = {
            "model": {
                "sigma": {
                    "descr": "Incubation rate (1/expected iterations)",
                    "range": [0, 1],
                    "optional": False
                },
                "beta": {
                    "descr": "Infection rate (1/expected iterations)",
                    "range": [0, 1],
                    "optional": False
                },
                "gamma": {
                    "descr": "Recovery rate (1/expected iterations)",
                    "range": [0, 1],
                    "optional": False
                },
                "gamma_t": {
                    "descr": "Recovery rate, quarantine (1/expected iterations)",
                    "range": [0, 1],
                    "optional": True,
                    "default": 0.05
                },
                "omega": {
                    "descr": "Death probability",
                    "range": [0, 1],
                    "optional": False
                },
                "omega_t": {
                    "descr": "Death probability, quarantine",
                    "range": [0, 1],
                    "optional": True,
                    "default": 0.1
                },
                "phi_e": {
                    "descr": "Testing probability if exposed",
                    "range": [0, 1],
                    "optional": True,
                    "default": 0
                },
                "phi_i": {
                    "descr": "Testing probability if infected",
                    "range": [0, 1],
                    "optional": True,
                    "default": 0
                },
                "kappa_e": {
                    "descr": "Test False Negative probability if exposed",
                    "range": [0, 1],
                    "optional": True,
                    "default": 0.7
                },
                "kappa_i": {
                    "descr": "Test False Negative probability if infected",
                    "range": [0, 1],
                    "optional": True,
                    "default": 0.9
                },
                "epsilon_e": {
                    "descr": "Social restriction due to quarantine (percentage of pruned edges)",
                    "range": [0, 1],
                    "optional": True,
                    "default": 1
                },
                "epsilon_l": {
                    "descr": "Social restriction due to lockdown (percentage of pruned edges)",
                    "range": [0, 1],
                    "optional": True,
                    "default": 0.25
                },
                "lambda": {
                    "descr": "Lockdown effectiveness (percentage of compliant individuals)",
                    "range": [0, 1],
                    "optional": True,
                    "default": 1
                },
                "mu": {
                    "descr": "Lockdown length (1/expected iterations)",
                    "range": [0, 1],
                    "optional": True,
                    "default": 1
                },
                "p": {
                    "descr": "Probability of long-range interactions",
                    "range": [0, 1],
                    "optional": True,
                    "default": 0
                },
                "p_l": {
                    "descr": "Probability of long-range interactions if in lockdown",
                    "range": [0, 1],
                    "optional": True,
                    "default": 0
                },
                "lsize": {
                    "descr": "Percentage of long-range interactions w.r.t short-range ones",
                    "range": [0, 1],
                    "optional": True,
                    "default": 0.25
                },
                "icu_b": {
                    "descr": "Beds availability in ICU (as percentage of the population)",
                    "range": [0, 1],
                    "optional": True,
                    "default": 1
                },
                "iota": {
                    "descr": "ICU case probability",
                    "range": [0, 1],
                    "optional": True,
                    "default": 1
                },
                "z": {
                    "descr": "Probability of infection from corpses",
                    "range": [0, 1],
                    "optional": True,
                    "default": 0
                },
                "s": {
                    "descr": "Probability of absent immunization",
                    "range": [0, 1],
                    "optional": True,
                    "default": 0
                },
            },
             "nodes": {
                "activity": {
                    "descr": "Node interactions per iteration (sample size of existing social relationships, "
                             "with replacement)",
                    "range": [0, 1],
                    "optional": True,
                    "default": 0.1
                },
             },
            "edges": {},
        }

    def iteration(self, node_status=True):
        """

        :param node_status:
        :return:
        """

        self.clean_initial_status(self.available_statuses.values())

        actual_status = {node: nstatus for node, nstatus in future.utils.iteritems(self.status)}

        if self.actual_iteration == 0:
            self.actual_iteration += 1
            delta, node_count, status_delta = self.status_delta(actual_status)
            if node_status:
                return {"iteration": 0, "status": actual_status.copy(),
                        "node_count": node_count.copy(), "status_delta": status_delta.copy()}
            else:
                return {"iteration": 0, "status": {},
                        "node_count": node_count.copy(), "status_delta": status_delta.copy()}

        for u in self.graph.nodes:

            u_status = self.status[u]

            if self.graph.directed:
                neighbors = self.graph.predecessors(u)
            else:
                neighbors = self.graph.neighbors(u)

            ####################### Undetected Compartment ###########################

            if u_status == self.available_statuses['Susceptible']:
                actual_status[u] = self.__Susceptible_to_Exposed(u, neighbors, lockdown=False)

            elif u_status == self.available_statuses['Exposed']:

                tested = np.random.random_sample()  # selection for testing
                if tested < self.params['model']['phi_e']:
                    res = np.random.random_sample()  # probability of false negative result
                    if res > self.params['model']['kappa_e']:
                        self.__limit_social_contacts(u, neighbors, 'Tested')
                        actual_status[u] = self.available_statuses['Tested_E']
                else:
                    at = np.random.random_sample()
                    if at < self.params['model']['sigma']:
                        actual_status[u] = self.available_statuses['Infected']

            elif u_status == self.available_statuses['Infected']:

                tested = np.random.random_sample()  # selection for testing
                if tested < self.params['model']['phi_i']:
                    res = np.random.random_sample()  # probability of false negative result
                    if res > self.params['model']['kappa_i']:
                        self.__limit_social_contacts(u, neighbors, 'Tested')
                        actual_status[u] = self.available_statuses['Tested_I']
                else:
                    dead = np.random.random_sample()
                    if dead < self.params['model']['omega']:
                        actual_status[u] = self.available_statuses['Dead']
                    else:
                        recovered = np.random.random_sample()
                        if recovered < self.params['model']['gamma']:
                            actual_status[u] = self.available_statuses['Recovered']


            ####################### Quarantined Compartment ###########################

            elif u_status == self.available_statuses['Tested_E']:
                at = np.random.random_sample()
                if at < self.params['model']['sigma']:
                    icup = np.random.random_sample()
                    icu_avalaibility = np.random.random_sample()
                    if icup < self.params['model']['iota'] and icu_avalaibility < self.params['model']['icu_b']:
                        actual_status[u] = self.available_statuses['Tested_H']
                    else:
                        actual_status[u] = self.available_statuses['Tested_I']

            elif u_status == self.available_statuses['Tested_I']:
                dead = np.random.random_sample()
                if dead < self.params['model']['omega']:
                    actual_status[u] = self.available_statuses['Dead']
                else:
                    recovered = np.random.random_sample()
                    if recovered < self.params['model']['gamma']:
                        actual_status[u] = self.available_statuses['Recovered']

            elif u_status == self.available_statuses['Tested_H']:
                dead = np.random.random_sample()
                if dead < self.params['model']['omega_t']:
                    actual_status[u] = self.available_statuses['Dead']
                else:
                    recovered = np.random.random_sample()
                    if recovered < self.params['model']['gamma_t']:
                        actual_status[u] = self.available_statuses['Recovered']

            ####################### Lockdown Compartment ###########################

            elif u_status == self.available_statuses['Lockdown_S']:
                # test lockdown exit
                exit = np.random.random_sample()  # loockdown acceptance
                if exit < self.params['model']['mu']:
                    actual_status[u] = self.available_statuses['Susceptible']
                    self.__ripristinate_social_contacts(u)

                else:
                    actual_status[u] = self.__Susceptible_to_Exposed(u, neighbors, lockdown=True)

            elif u_status == self.available_statuses['Lockdown_E']:
                # test lockdown exit
                exit = np.random.random_sample()  # loockdown exit
                if exit < self.params['model']['mu']:
                    actual_status[u] = self.available_statuses['Exposed']
                    self.__ripristinate_social_contacts(u)

                else:
                    at = np.random.random_sample()
                    if at < self.params['model']['sigma']:
                        actual_status[u] = self.available_statuses['Lockdown_I']

            elif u_status == self.available_statuses['Lockdown_I']:
                # test lockdown exit
                exit = np.random.random_sample()  # loockdown exit

                if exit < self.params['model']['mu']:
                    actual_status[0] = self.available_statuses['Infected']
                    self.__ripristinate_social_contacts(u)

                else:
                    dead = np.random.random_sample()
                    if dead < self.params['model']['omega']:
                        actual_status[u] = self.available_statuses['Dead']
                    else:
                        recovered = np.random.random_sample()
                        if recovered < self.params['model']['gamma']:
                            actual_status[u] = self.available_statuses['Recovered']

            ####################### Resolved Compartment ###########################

            elif u_status == self.available_statuses['Recovered']:
                immunity = np.random.random_sample()
                if immunity < self.params['model']['s']:
                    actual_status[u] = self.available_statuses['Susceptible']

            elif u_status == self.available_statuses['Dead']:
                pass

        delta, node_count, status_delta = self.status_delta(actual_status)
        self.status = actual_status
        self.actual_iteration += 1

        if node_status:
            return {"iteration": self.actual_iteration - 1, "status": delta.copy(),
                    "node_count": node_count.copy(), "status_delta": status_delta.copy()}
        else:
            return {"iteration": self.actual_iteration - 1, "status": {},
                    "node_count": node_count.copy(), "status_delta": status_delta.copy()}

    ###################################################################################################################

    @staticmethod
    def __interaction_selection(neighbors, prob):
        return np.random.choice(a=neighbors, size=int(len(neighbors)*prob), replace=True)

    def set_lockdown(self):
        actual_status = {node: nstatus for node, nstatus in future.utils.iteritems(self.status)}

        self.old_graph = self.graph  # saving graph current state

        for u in self.graph.nodes:

            la = np.random.random_sample()  # loockdown acceptance
            if la < self.params['model']['lambda']:

                if actual_status[u] == self.available_statuses['Susceptible']:
                    actual_status[u] = self.available_statuses['Lockdown_S']
                    self.__limit_social_contacts(u, type="Lockdown")

                elif actual_status[u] == self.available_statuses['Exposed']:
                    actual_status[u] = self.available_statuses["Lockdown_E"]
                    self.__limit_social_contacts(u, type="Lockdown")

                elif actual_status[u] == self.available_statuses['Infected']:
                    actual_status[u] = self.available_statuses['Lockdown_I']
                    self.__limit_social_contacts(u, type="Lockdown")

        delta, node_count, status_delta = self.status_delta(actual_status)
        self.status = actual_status
        return {"iteration": self.actual_iteration - 1, "status": {}, "node_count": node_count.copy(),
                 "status_delta": status_delta.copy()}

    def unset_lockdown(self, graph=None):
        actual_status = {node: nstatus for node, nstatus in future.utils.iteritems(self.status)}

        # restoring previous graph state (or new one if data available)
        if graph is None:
            self.graph = self.old_graph
        else:
            self.graph = graph

        for u in self.graph.nodes:
            if actual_status[u] == self.available_statuses['Lockdown_S']:
                actual_status[u] = self.available_statuses['Susceptible']
            elif actual_status[u] == self.available_statuses['Lockdown_E']:
                actual_status[u] = self.available_statuses["Exposed"]
            elif actual_status[u] == self.available_statuses['Lockdown_I']:
                actual_status[u] = self.available_statuses['Infected']

        delta, node_count, status_delta = self.status_delta(actual_status)
        self.status = actual_status
        return {"iteration": self.actual_iteration - 1, "status": {}, "node_count": node_count.copy(),
                "status_delta": status_delta.copy()}

    def __limit_social_contacts(self, u, neighbors=None, type='Tested'):

        if neighbors is None:
            if self.graph.directed:
                neighbors = self.graph.predecessors(u)
            else:
                neighbors = self.graph.neighbors(u)

        if type == 'Tested':
            filtering_prob = self.params['model']['epsilon_l']
        else:
            filtering_prob = self.params['model']['epsilon_e']
        to_remove = list(np.random.choice(a=neighbors, size=int(len(neighbors)*filtering_prob), replace=False))
        self.graph.remove_edges(u, to_remove)

    def __ripristinate_social_contacts(self, u):

        if self.old_graph.directed:
            to_add = self.old_graph.predecessors(u)
        else:
            to_add = self.old_graph.neighbors(u)
        self.graph.add_edges(u, to_add)


    ####################### Undetected Compartment ###########################


    def __Susceptible_to_Exposed(self, u, neighbors, lockdown=False):
        interactions = list(self.__interaction_selection(neighbors, self.params['nodes']['activity'][u]))
        social_interactions = len(interactions)

        l_range_proba = self.params['model']['p']
        if lockdown:
            l_range_proba = self.params['model']['p_l']

        l_range = np.random.random_sample()  # long range interaction
        if l_range < l_range_proba:
            # filtering out quarantined and dead nodes
            if self.params['model']['z'] == 0:
                candidates = [n for n in self.graph.nodes if self.status[n] not in [self.available_statuses['Tested_E'], self.available_statuses['Tested_I'], self.available_statuses['Dead']]]
            else:
                candidates = [n for n in self.graph.nodes if self.status[n] not in [self.available_statuses['Tested_E'],
                                                                                    self.available_statuses['Tested_I']]]

            interactions.extend(list(np.random.choice(a=candidates, size=int(social_interactions*self.params['model']['lsize']), replace=True)))

        for v in interactions:
            if self.status[v] == self.available_statuses['Infected'] or self.status[v] == self.available_statuses['Lockdown_I'] or self.status[v] == self.available_statuses['Tested_I']:
                bt = np.random.random_sample()
                if bt < self.params['model']['beta']:
                    if lockdown:
                        return self.available_statuses['Lockdown_E']
                    return self.available_statuses['Exposed']

            elif self.status[v] == self.available_statuses['Dead']:
                zp = np.random.random_sample()
                if zp < self.params['model']['z']:
                    if lockdown:
                        return self.available_statuses['Lockdown_E']
                    return self.available_statuses['Exposed']

        if lockdown:
            return self.available_statuses['Lockdown_S']
        return self.available_statuses['Susceptible']
