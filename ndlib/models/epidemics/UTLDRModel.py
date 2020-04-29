from ..DiffusionModel import DiffusionModel
import numpy as np
import future

__author__ = ["Giulio Rossetti"]
__license__ = "BSD-2-Clause"


class UTLDRModel(DiffusionModel):

    def __init__(self, graph, seed=None):

        super(self.__class__, self).__init__(graph, seed)

        self.params['nodes']['vaccinated'] = {n: False for n in self.graph.nodes}
        self.params['nodes']['tested'] = {n: False for n in self.graph.nodes}
        self.params['nodes']['ICU'] = {n: False for n in self.graph.nodes}
        self.params['nodes']['filtered'] = {n: [] for n in self.graph.nodes}
        self.icu_b = self.graph.number_of_nodes()
        self.lockdown = False

        self.name = "UTLDR"

        self.available_statuses = {
            "Susceptible": 0,
            "Exposed": 2,
            "Infected": 1,
            "Recovered": 3,
            "Identified_Exposed": 4,
            "Hospitalized_mild": 5,
            "Hospitalized_severe_ICU": 6,
            "Hospitalized_severe": 7,
            "Lockdown_Susceptible": 8,
            "Lockdown_Exposed": 9,
            "Lockdown_Infected": 10,
            "Dead": 11,
            "Vaccinated": 12,
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
                    "descr": "Recovery rate - Mild, Asymptomatic, Paucisymptomatic (1/expected iterations)",
                    "range": [0, 1],
                    "optional": False
                },
                "gamma_t": {
                    "descr": "Recovery rate - Severe in ICU (1/expected iterations)",
                    "range": [0, 1],
                    "optional": True,
                    "default": 0.6
                },
                "gamma_f": {
                    "descr": "Recovery rate - Severe not in ICU (1/expected iterations)",
                    "range": [0, 1],
                    "optional": True,
                    "default": 0.95
                },
                "omega": {
                    "descr": "Death probability - Mild, Asymptomatic, Paucisymptomatic",
                    "range": [0, 1],
                    "optional": True,
                    "default": 0
                },
                "omega_t": {
                    "descr": "Death probability - Severe in ICU",
                    "range": [0, 1],
                    "optional": True,
                    "default": 0
                },
                "omega_f": {
                    "descr": "Death probability - Severe not in ICU",
                    "range": [0, 1],
                    "optional": True,
                    "default": 0
                },
                "phi_e": {
                    "descr": "Testing probability if Exposed",
                    "range": [0, 1],
                    "optional": True,
                    "default": 0
                },
                "phi_i": {
                    "descr": "Testing probability if Infected",
                    "range": [0, 1],
                    "optional": True,
                    "default": 0
                },
                "kappa_e": {
                    "descr": "Test False Negative probability if Exposed",
                    "range": [0, 1],
                    "optional": True,
                    "default": 0.7
                },
                "kappa_i": {
                    "descr": "Test False Negative probability if Infected",
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
                    "descr": "Social restriction due to lockdown (maximum household size)",
                    "range": [0, 1],
                    "optional": True,
                    "default": 1
                },
                "lambda": {
                    "descr": "Lockdown effectiveness (percentage of compliant individuals)",
                    "range": [0, 1],
                    "optional": True,
                    "default": 1
                },
                "mu": {
                    "descr": "Lockdown duration (1/expected iterations)",
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
                    "descr": "Probability of long-range interactions if in Lockdown",
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
                    "descr": "Beds availability in ICU (absolute value)",
                    "range": [0, np.infty],
                    "optional": True,
                    "default": self.graph.number_of_nodes()
                },
                "iota": {
                    "descr": "Severe case probability (needing ICU treatments)",
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
                "v": {
                    "descr": "Probability of vaccination (single chance per agent)",
                    "range": [0, 1],
                    "optional": True,
                    "default": 0
                },
                "f": {
                    "descr": "Probability of Vaccination nullification (inverse of temporal coverage)",
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
                    "default": 1
                },
                "segment": {
                    "descr": "Node class (e.g., age, gender)",
                    "range": str,
                    "optional": True,
                    "default": None
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
            self.icu_b = self.params['model']['icu_b']

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

            # checking social limitations due to quarantine and/or lockdown
            if self.params['nodes']['filtered'][u] is not None and len(self.params['nodes']['filtered'][u]) > 0:
                neighbors = list(set(neighbors) & set(self.params['nodes']['filtered'][u]))

            ####################### Undetected Compartment ###########################

            if u_status == self.available_statuses['Susceptible']:
                actual_status[u] = self.__Susceptible_to_Exposed(u, neighbors, lockdown=False)

            elif u_status == self.available_statuses['Exposed']:

                tested = np.random.random_sample()  # selection for testing
                if not self.params['nodes']['tested'][u] and tested < self.__get_threshold(u, 'phi_e'):
                    res = np.random.random_sample()  # probability of false negative result
                    if res > self.__get_threshold(u, 'kappa_e'):
                        self.__limit_social_contacts(u, neighbors, 'Tested')
                        actual_status[u] = self.available_statuses['Identified_Exposed']
                    self.params['nodes']['tested'][u] = True
                else:
                    at = np.random.random_sample()
                    if at < self.__get_threshold(u, 'sigma'):
                        actual_status[u] = self.available_statuses['Infected']

            elif u_status == self.available_statuses['Infected']:

                tested = np.random.random_sample()  # selection for testing
                if not self.params['nodes']['tested'][u] and tested < self.__get_threshold(u, 'phi_i'):
                    res = np.random.random_sample()  # probability of false negative result
                    if res > self.__get_threshold(u, 'kappa_i'):
                        self.__limit_social_contacts(u, neighbors, 'Tested')

                        icup = np.random.random_sample()  # probability of severe case needing ICU

                        if icup < self.__get_threshold(u, 'iota'):
                            if self.icu_b > 0 and not self.params['nodes']['ICU'][u]:
                                actual_status[u] = self.available_statuses['Hospitalized_severe_ICU']
                                self.icu_b -= 1
                            else:
                                actual_status[u] = self.available_statuses['Hospitalized_severe']
                        else:
                            actual_status[u] = self.available_statuses['Hospitalized_mild']
                    self.params['nodes']['tested'][u] = True

                else:
                    recovered = np.random.random_sample()
                    if recovered < self.__get_threshold(u, 'gamma'):
                        actual_status[u] = self.available_statuses['Recovered']
                    else:
                        dead = np.random.random_sample()
                        if dead < self.__get_threshold(u, 'omega'):
                            actual_status[u] = self.available_statuses['Dead']

            ####################### Quarantined Compartment ###########################

            elif u_status == self.available_statuses['Identified_Exposed']:
                at = np.random.random_sample()
                if at < self.__get_threshold(u, 'sigma'):
                    icup = np.random.random_sample()
                    # icu_avalaibility = np.random.random_sample()
                    if icup < self.__get_threshold(u, 'iota'):
                        if self.icu_b > 0 and not self.params['nodes']['ICU'][u]:
                            actual_status[u] = self.available_statuses['Hospitalized_severe_ICU']
                            self.icu_b -= 1
                        else:
                            actual_status[u] = self.available_statuses['Hospitalized_severe']
                    else:
                        actual_status[u] = self.available_statuses['Hospitalized_mild']
                    self.params['nodes']['ICU'][u] = True

            elif u_status == self.available_statuses['Hospitalized_mild']:
                recovered = np.random.random_sample()
                if recovered < self.__get_threshold(u, 'gamma'):
                    actual_status[u] = self.available_statuses['Recovered']
                else:
                    dead = np.random.random_sample()
                    if dead < self.__get_threshold(u, 'omega'):
                        actual_status[u] = self.available_statuses['Dead']

            elif u_status == self.available_statuses['Hospitalized_severe']:
                recovered = np.random.random_sample()
                if recovered < self.__get_threshold(u, 'gamma_f'):
                    actual_status[u] = self.available_statuses['Recovered']
                else:
                    dead = np.random.random_sample()
                    if dead < self.__get_threshold(u, 'omega_f'):
                        actual_status[u] = self.available_statuses['Dead']

            elif u_status == self.available_statuses['Hospitalized_severe_ICU']:
                recovered = np.random.random_sample()
                if recovered < self.__get_threshold(u, 'gamma_t'):
                    actual_status[u] = self.available_statuses['Recovered']
                    self.icu_b += 1
                else:
                    dead = np.random.random_sample()
                    if dead < self.__get_threshold(u, 'omega_t'):
                        actual_status[u] = self.available_statuses['Dead']
                        self.icu_b += 1

            ####################### Lockdown Compartment ###########################

            elif u_status == self.available_statuses['Lockdown_Susceptible']:
                # test lockdown exit
                exit = np.random.random_sample()  # loockdown acceptance
                if exit < self.__get_threshold(u, 'mu'):
                    actual_status[u] = self.available_statuses['Susceptible']
                    self.__ripristinate_social_contacts(u)

                else:
                    actual_status[u] = self.__Susceptible_to_Exposed(u, neighbors, lockdown=True)

            elif u_status == self.available_statuses['Lockdown_Exposed']:
                # test lockdown exit
                exit = np.random.random_sample()  # loockdown exit
                if exit < self.__get_threshold(u, 'mu'):
                    actual_status[u] = self.available_statuses['Exposed']
                    self.__ripristinate_social_contacts(u)

                else:
                    at = np.random.random_sample()
                    if at < self.__get_threshold(u, 'sigma'):
                        actual_status[u] = self.available_statuses['Lockdown_Infected']

            elif u_status == self.available_statuses['Lockdown_Infected']:
                # test lockdown exit
                exit = np.random.random_sample()  # loockdown exit

                if exit < self.__get_threshold(u, 'mu'):
                    actual_status[0] = self.available_statuses['Infected']
                    self.__ripristinate_social_contacts(u)

                else:
                    dead = np.random.random_sample()
                    if dead < self.__get_threshold(u, 'omega'):
                        actual_status[u] = self.available_statuses['Dead']
                    else:
                        recovered = np.random.random_sample()
                        if recovered < self.__get_threshold(u, 'gamma'):
                            actual_status[u] = self.available_statuses['Recovered']

            ####################### Resolved Compartment ###########################

            elif u_status == self.available_statuses['Recovered']:
                immunity = np.random.random_sample()
                if immunity < self.__get_threshold(u, 's'):
                    actual_status[u] = self.available_statuses['Susceptible']

            elif u_status == self.available_statuses['Vaccinated']:
                failure = np.random.random_sample()
                if failure < self.__get_threshold(u, 'f'):
                    self.params['nodes']['vaccinated'][u] = False
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
        return np.random.choice(a=neighbors, size=int(len(neighbors) * prob), replace=True)

    def add_ICU_beds(self, n):
        """
        Add/Subtract beds in intensive care

        :param n: number of beds to add/remove
        :return:
        """
        self.icu_b = max(0, self.icu_b + n)

    def set_lockdown(self, households=None, workplaces=None):
        """
        Impose the beginning of a lockdown

        :param households: (optional) dictionary specifying the households for each node <node_id -> list(nodes in household)>
        :return:
        """
        actual_status = {node: nstatus for node, nstatus in future.utils.iteritems(self.status)}

        self.lockdown = True

        for u in self.graph.nodes:

            candidate = True
            if workplaces is not None and 'work' in self.params['nodes']:
                if len(set(workplaces) & set(self.params['nodes']['work'][u])) == 0:
                    candidate = False

            if not candidate:
                continue

            la = np.random.random_sample()  # loockdown acceptance
            if la < self.__get_threshold(u, 'lambda'):

                if actual_status[u] == self.available_statuses['Susceptible']:
                    actual_status[u] = self.available_statuses['Lockdown_Susceptible']
                    if households is None or u not in households:
                        self.__limit_social_contacts(u, event="Lockdown")
                    else:
                        self.params['nodes']['filtered'][u] = households[u]

                elif actual_status[u] == self.available_statuses['Exposed']:
                    actual_status[u] = self.available_statuses["Lockdown_Exposed"]
                    if households is None or u not in households:
                        self.__limit_social_contacts(u, event="Lockdown")
                    else:
                        self.params['nodes']['filtered'][u] = households[u]

                elif actual_status[u] == self.available_statuses['Infected']:
                    actual_status[u] = self.available_statuses['Lockdown_Infected']
                    if households is None or u not in households:
                        self.__limit_social_contacts(u, event="Lockdown")
                    else:
                        self.params['nodes']['filtered'][u] = households[u]
            else:
                # node refuses lockdown
                self.params['nodes']['filtered'][u] = None

        delta, node_count, status_delta = self.status_delta(actual_status)
        self.status = actual_status
        return {"iteration": self.actual_iteration - 1, "status": {}, "node_count": node_count.copy(),
                "status_delta": status_delta.copy()}

    def unset_lockdown(self, workplaces=None):
        """
        Remove the lockdown social limitations

        :return:
        """
        actual_status = {node: nstatus for node, nstatus in future.utils.iteritems(self.status)}

        self.lockdown = False

        for u in self.graph.nodes:

            candidate = True
            if workplaces is not None and 'work' in self.params['nodes']:
                if len(set(workplaces) & set(self.params['nodes']['work'][u])) == 0:
                    candidate = False

            if not candidate:
                continue

            self.__ripristinate_social_contacts(u)
            if actual_status[u] == self.available_statuses['Lockdown_Susceptible']:
                actual_status[u] = self.available_statuses['Susceptible']
            elif actual_status[u] == self.available_statuses['Lockdown_Exposed']:
                actual_status[u] = self.available_statuses["Exposed"]
            elif actual_status[u] == self.available_statuses['Lockdown_Infected']:
                actual_status[u] = self.available_statuses['Infected']

        delta, node_count, status_delta = self.status_delta(actual_status)
        self.status = actual_status
        return {"iteration": self.actual_iteration + 1, "status": {}, "node_count": node_count.copy(),
                "status_delta": status_delta.copy()}

    def __limit_social_contacts(self, u, neighbors=None, event='Tested'):

        # already in quarantine or in an household
        if self.params['nodes']['filtered'][u] is None or len(self.params['nodes']['filtered'][u]) > 0:
            return

        if neighbors is None:
            if self.graph.directed:
                neighbors = self.graph.predecessors(u)
            else:
                neighbors = self.graph.neighbors(u)

        if event == 'Tested':
            filtering_prob = self.__get_threshold(u, 'epsilon_e')
            remaining_candidates = [n for n in neighbors if self.params['nodes']['filtered'][n] is not None and len(self.params['nodes']['filtered'][n]) == 0]
            size = min(int(len(neighbors) * (1 - filtering_prob)), len(remaining_candidates))
        else:
            houseold_max_size = self.params['model']['epsilon_l']
            size = list(np.random.choice(a=range(houseold_max_size), size=1))[0]

        # filtering contacts
        to_keep = list(np.random.choice(a=neighbors, size=size, replace=False))
        self.params['nodes']['filtered'][u] = to_keep

        # Lockdown
        if event != "Tested":
            for n in to_keep:
                # if n complies to the lockdown and is not in quarantine
                if self.params['nodes']['filtered'][n] is not None and \
                         self.status[n] not in [self.available_statuses['Identified_Exposed'],
                                                self.available_statuses['Hospitalized_mild'],
                                                self.available_statuses['Hospitalized_severe_ICU'],
                                                self.available_statuses['Hospitalized_severe']]:

                    # imposing an estimate "household" lockdown
                    self.params['nodes']['filtered'][n] = list((set(to_keep) - {n}) | {u})
        else:
            # Quarantine
            for n in set(neighbors) - set(to_keep):
                if self.params['nodes']['filtered'][n] is not None and len(self.params['nodes']['filtered'][n]) > 0:
                    # removing the quarantined node from the neighbors' contacts
                    self.params['nodes']['filtered'][n] = list(set(self.params['nodes']['filtered'][n]) - {u})
                else:
                    if self.status[n] not in [self.available_statuses['Identified_Exposed'],
                                              self.available_statuses['Hospitalized_mild'],
                                              self.available_statuses['Hospitalized_severe_ICU'],
                                              self.available_statuses['Hospitalized_severe']]:

                        if self.graph.directed:
                            n_neighbors = self.graph.predecessors(u)
                        else:
                            n_neighbors = self.graph.neighbors(u)
                        self.params['nodes']['filtered'][n] = list(set(n_neighbors) - {u})

    def __ripristinate_social_contacts(self, u):
        self.params['nodes']['filtered'][u] = []

    ####################### Undetected Compartment ###########################

    def __Susceptible_to_Exposed(self, u, neighbors, lockdown=False):

        # vaccination test
        if self.__get_threshold(u, 'v') > 0 and not self.params['nodes']['vaccinated'][u]:
            v_prob = np.random.random_sample()
            if v_prob < self.__get_threshold(u, 'v'):
                self.params['nodes']['vaccinated'][u] = True
                return self.available_statuses['Vaccinated']

        interactions = list(self.__interaction_selection(neighbors, self.params['nodes']['activity'][u]))
        social_interactions = len(interactions)

        l_range_proba = self.__get_threshold(u, 'p')
        if lockdown:
            l_range_proba = self.__get_threshold(u, 'p_l')

        l_range = np.random.random_sample()  # long range interaction
        if l_range < l_range_proba:
            # filtering out quarantined and dead nodes
            if self.__get_threshold(u, 'z') == 0:
                candidates = [n for n in self.graph.nodes if self.status[n] not in
                              [self.available_statuses['Identified_Exposed'],
                               self.available_statuses['Hospitalized_mild'],
                               self.available_statuses['Dead']]]
            else:
                candidates = [n for n in self.graph.nodes if self.status[n] not in
                              [self.available_statuses['Identified_Exposed'],
                               self.available_statuses['Hospitalized_mild']]
                              ]

            interactions.extend(list(np.random.choice(a=candidates,
                                                      size=int(social_interactions * self.params['model']['lsize']),
                                                      replace=True)))

        for v in interactions:
            if self.status[v] == self.available_statuses['Infected'] or \
                    self.status[v] == self.available_statuses['Lockdown_Infected'] or \
                    self.status[v] == self.available_statuses['Hospitalized_mild']:
                bt = np.random.random_sample()

                if bt < self.__get_threshold(u, 'beta'):
                    if lockdown:
                        return self.available_statuses['Lockdown_Exposed']
                    return self.available_statuses['Exposed']

            elif self.status[v] == self.available_statuses['Dead']:
                zp = np.random.random_sample()
                if zp < self.__get_threshold(u, 'z'):  # infection risk due to partial corpse disposal
                    if lockdown:
                        return self.available_statuses['Lockdown_Exposed']
                    return self.available_statuses['Exposed']

        if lockdown:
            return self.available_statuses['Lockdown_Susceptible']
        return self.available_statuses['Susceptible']

    def __get_threshold(self, u, parameter):
        # stratified population scenario
        if isinstance(self.params['model'][parameter], dict):
            n_class = self.params['nodes']['segment'][u]
            return self.params['model'][parameter][n_class]
        # base scenario, single value
        else:
            return self.params['model'][parameter]

