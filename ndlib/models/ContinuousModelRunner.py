class ContinuousModelRunner(object):
    def __init__(self, ContinuousModel, config, N, iterations_list,  initial_statuses, constants_list=None, node_status=True):
        self.model = ContinuousModel
        self.config = config
        self.N = N
        self.iterations_list = iterations_list
        self.node_status = node_status
        self.constants_list = constants_list
        self.initial_statuses = initial_statuses

    def run(self):
        results = []

        n_iterations = len(self.iterations_list)
        n_initial_statuses = len(self.initial_statuses)

        if self.constants_list:
            n_constants = len(self.constants_list)

        for i in range(self.N):
            print('\nRunning simulation ' + str(i + 1) + '/' + str(self.N) + '\n')
            if self.constants_list:
                self.model.constants = self.constants_list[i % n_constants]
            self.model.set_initial_status(self.initial_statuses[i % n_initial_statuses], self.config)
            output = self.model.iteration_bunch(self.iterations_list[i % n_iterations], node_status=self.node_status)
            results.append(output)

        return results
