# TODO
# - Fix visualization logic (overwrite vs update),
# - numpy matrix implementation instead of networkx nodes/dict
# Requirements, networkx, numpy, matplotlib, PIL, pyintergraph, python-igraph, tqdm

from ndlib.models.DiffusionModel import DiffusionModel
import future.utils
import os
import networkx as nx
import copy
import numpy as np

import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.animation as animation

__author__ = 'Mathijs Maijer'
__license__ = "BSD-2-Clause"
__email__ = "m.f.maijer@gmail.com"


class ContinuousModel(DiffusionModel):

    def __init__(self, graph, constants=None, clean_status=None, iteration_schemes=None, save_file=None):
        """
        Model Constructor

        :param graph: A networkx graph object
        :param constants: dictionary containing state name as key and float or function returning a float as value
        :param clean_status: boolean indicating whether to set all status values between 0 and 1
        :param iteration_schemes: list of dictionaries for each scheme
            containing a name, function(graph, status), and optional lower and upper bound keys
        :param save_file: string indicating path and file name to save the iterations output to
         """
        super(ContinuousModel, self).__init__(graph)
        self.compartment = {}
        self.compartment_progressive = 0
        self.status_progressive = 0

        self.discrete_state = False

        self.available_statuses = {
            "Infected": 0
        }

        self.clean = True if clean_status else False

        self.constants = constants

        if iteration_schemes:
            self.iteration_schemes = iteration_schemes
            self.iteration_schemes.append({'name': '', 'function': lambda graph, status: graph.nodes})
        else:
            self.iteration_schemes = [{'name': '', 'function': lambda graph, status: graph.nodes}]

        self.visualization_configuration = None

        if save_file:
            if isinstance(save_file, str):
                self.save_file = save_file
            else:
                raise ValueError('save_file should be a string indicating path/and/filename')
        else:
            self.save_file = None

        self.full_status = None

    def configure_visualization(self, visualization_configuration):
        """
        Configure and assert all visualization configuration parameters

        :param visualization_configuration: dictionary containing all visualization options
        """
        if visualization_configuration:
            print('Configuring visualization...')
            self.visualization_configuration = visualization_configuration
            vis_keys = visualization_configuration.keys()

            self.validate_plot_config(visualization_configuration, vis_keys)
            self.validate_color_config(vis_keys)

            if 'pos' not in self.graph.nodes[0].keys():
                self.configure_layout(vis_keys)

            if 'variable_limits' not in vis_keys:
                self.visualization_configuration['variable_limits'] = {key: [-1, 1] for key in list(self.available_statuses.keys())}
            else:
                for key in list(self.available_statuses.keys()):
                    if key not in list(self.visualization_configuration['variable_limits'].keys()):
                        self.visualization_configuration['variable_limits'][key] = [-1, 1]
            if 'animation_interval' not in vis_keys:
                self.visualization_configuration['animation_interval'] = 30
            else:
                if not isinstance(self.visualization_configuration['animation_interval'], int):
                    raise ValueError('animation interval must be an integer')
            print('Done configuring the visualization')
        else:
            raise Exception('Provide a visualization configuration when using this function')

    def configure_layout(self, vis_keys):
        if 'layout' in vis_keys:
            if self.visualization_configuration['layout'] == 'fr':
                import pyintergraph
                Graph = pyintergraph.InterGraph.from_networkx(self.graph.graph)
                G = Graph.to_igraph()
                layout = G.layout_fruchterman_reingold(niter=500)
                positions = {node: {'pos': location} for node, location in enumerate(layout)}
            else:
                if 'layout_params' in vis_keys:
                    pos = self.visualization_configuration['layout'](self.graph.graph, **self.visualization_configuration['layout_params'])
                else:
                    pos = self.visualization_configuration['layout'](self.graph.graph)
                positions = {key: {'pos': location} for key, location in pos.items()}
        else:
            pos = nx.drawing.spring_layout(self.graph.graph)
            positions = {key: {'pos': location} for key, location in pos.items()}

        nx.set_node_attributes(self.graph, positions)

    def validate_plot_config(self, visualization_configuration, vis_keys):
        if 'plot_interval' in vis_keys:
            if isinstance(visualization_configuration['plot_interval'], int):
                if visualization_configuration['plot_interval'] <= 0:
                    raise ValueError('plot_interval must be a positive integer')
            else:
                raise ValueError('plot_interval must be a positive integer')
        else:
            raise ValueError('plot_interval must be included for visualization')
        if 'show_plot' in vis_keys:
            if not isinstance(visualization_configuration['show_plot'], bool):
                raise ValueError('show_plot must be a boolean')
        else:
            self.visualization_configuration['show_plot'] = True
        if 'plot_variable' in vis_keys:
            if not isinstance(visualization_configuration['plot_variable'], str):
                raise ValueError('Plot variable must be a string')
        else:
            self.visualization_configuration['plot_variable'] = None

        if 'plot_title' in self.visualization_configuration.keys():
            if not isinstance(self.visualization_configuration['plot_title'], str):
                raise ValueError('Plot name must be a string')
        else:
            vis_var = self.visualization_configuration['plot_variable']
            self.visualization_configuration['plot_title'] = 'Network simulation of ' + vis_var

        if 'plot_annotation' in vis_keys:
            if not isinstance(self.visualization_configuration['plot_annotation'], str):
                raise ValueError('Plot annotation must be a string')
        else:
            self.visualization_configuration['plot_annotation'] = None

    def validate_color_config(self, vis_keys):
        if 'cmin' in vis_keys:
            if not isinstance(self.visualization_configuration['cmin'], int):
                raise ValueError('cmin must be an integer')
        else:
            self.visualization_configuration['cmin'] = 0

        if 'cmax' in vis_keys:
            if not isinstance(self.visualization_configuration['cmax'], int):
                raise ValueError('cmax must be an integer')
        else:
            self.visualization_configuration['cmax'] = 1

        if 'color_scale' in vis_keys:
            if not isinstance(self.visualization_configuration['color_scale'], str):
                raise ValueError('Color scale must be a string')
        else:
            self.visualization_configuration['color_scale'] = 'RdBu'

    def add_status(self, status_name):
        """
        Add a status/state to the model
        """
        if status_name not in self.available_statuses:
            self.available_statuses[status_name] = self.status_progressive
            self.status_progressive += 1

    def add_rule(self, status, function, rule, schemes=['']):
        """
        Add a rule to the model

        :param status: string indicating the status
        :param function: A function that updates the status value
            it receives the parameters: node, graph, status, attributes, constants
        :param rule: A condition that should be true before the status is updated
        :param schemes: A list of strings matching the names of the schemes in which the rule should be assessed
            If no schemes are provided, the default scheme '' is used, which is assessed for every iteration
        """
        self.compartment[self.compartment_progressive] = (status, function, rule, schemes)
        self.compartment_progressive += 1

    def set_initial_status(self, initial_status_funs, configuration=None):
        """
        Override behaviour of methods in class DiffusionModel.
        Overwrites initial status using given function
        Generates node profiles
        """
        super(ContinuousModel, self).set_initial_status(configuration)

        if not isinstance(initial_status_funs, dict):
            raise ValueError('The initial status should be a dictionary of form status (str): value (int/float/function)')

        # set node status
        for node in self.status:
            status = {}
            for status_fun in initial_status_funs.items():
                if hasattr(status_fun[1], '__call__'):
                    status[status_fun[0]] = status_fun[1](node, self.graph, status, self.constants)
                    continue
                if not isinstance(status_fun[1], float):
                    if not isinstance(status_fun[1], int):
                        raise ValueError('The initial status should be a function, integer, or float')
                status[status_fun[0]] = status_fun[1]
            self.status[node] = status

        self.initial_status = copy.deepcopy(self.status)

    def clean_initial_status(self, valid_status=None):
        """
        For every status, set it to 0 if negative, or to 1 if > 1
        """
        for n, s in future.utils.iteritems(self.status):
            for var_val in s.items():
                if var_val[1] > 1:
                    self.status[n][var_val[0]] = 1
                elif var_val[1] < 0:
                    self.status[n][var_val[0]] = 0

    def iteration(self, node_status=True):
        """
        Execute a single model iteration

        :return: Iteration_id, Incremental node status (dictionary node->status)
        """
        if self.clean:
            self.clean_initial_status()

        # actual_status = {node: nstatus for node, nstatus in future.utils.iteritems(self.status)}
        actual_status = copy.deepcopy(self.status)

        if self.actual_iteration == 0:
            self.actual_iteration += 1
            delta, status_delta = self.status_delta_continuous(self.status)
            if node_status:
                return {"iteration": 0, "status": copy.deepcopy(self.status),
                        "status_delta": copy.deepcopy(status_delta)}
            else:
                return {"iteration": 0, "status": {},
                         "status_delta": copy.deepcopy(status_delta)}

        nodes_data = self.graph.nodes

        for scheme in self.iteration_schemes:

            if 'lower' in scheme and scheme['lower'] > self.actual_iteration:
                continue
            if 'upper' in scheme and scheme['upper'] < self.actual_iteration:
                continue

            nodes = scheme['function'](self.graph, self.status)
            for u in nodes:
                # For all rules
                for i in range(0, self.compartment_progressive):
                    if scheme['name'] in self.compartment[i][3]:
                        # Get and test the condition
                        rule = self.compartment[i][2]
                        test = rule.execute(node=u, graph=self.graph, status=self.status,
                                            status_map=self.available_statuses, attributes=nodes_data,
                                            params=self.params, constants=self.constants)
                        if test:
                            # Update status or network if test succeeds
                            if self.compartment[i][0] == 'network':
                                self.compartment[i][1](u, self.graph, self.status, nodes_data, self.constants)
                            else:
                                val = self.compartment[i][1](u, self.graph, self.status, nodes_data, self.constants)
                                actual_status[u][self.compartment[i][0]] = val

        delta, status_delta = self.status_delta_continuous(actual_status)
        self.status = actual_status
        self.actual_iteration += 1

        if node_status:
            return {"iteration": self.actual_iteration - 1, "status": copy.deepcopy(delta),
                    "status_delta": copy.deepcopy(status_delta)}
        else:
            return {"iteration": self.actual_iteration - 1, "status": {},
                    "status_delta": copy.deepcopy(status_delta)}

    def iteration_bunch(self, bunch_size, node_status=True, progress_bar=False):
        """
        Execute bunch_size of model iterations and save the result if save_file is set

        :param bunch_size: integer number of iterations to execute
        :param node_status: boolean indicating whether to keep the statuses of the nodes
        :param progress_bar: boolean indicating whether to use tqdm to show the estimated duration

        :return: list of outputs for every iteration
        """
        iterations = super().iteration_bunch(bunch_size, node_status, progress_bar=progress_bar)

        if self.save_file:
            split = self.save_file.split('/')
            file_name = split[-1]
            file_path = self.save_file.replace(file_name, '')
            if not os.path.exists(file_path):
                os.makedirs(file_path)
            np.save(self.save_file, iterations)
            print('Saved ' + self.save_file)
        return iterations

    def get_mean_data(self, iterations, mean_type):
        """
        Create a dictionary with statuses as keys, and a list of average value per iteration as value

        :param iterations: iterations output from iteration_bunch
        :param mean_type: A string containing the type to get the average data from
            Should be 'status' or 'status_delta'

        :return: Dictionary containing all statuses as keys,
            and as value a list of the average values of all nodes for that status per iteration
        """
        mean_changes = {}
        for key in self.available_statuses.keys():
            mean_changes[key] = []
        del mean_changes['Infected'] # Todo, fix this line so that infected isn't even in available statuses

        for it in iterations:
            delta = {}

            vals = list(it[mean_type].values())

            for val in vals:
                for key, v in val.items():
                    if key not in delta.keys():
                        delta[key] = {'v': v, 'n': 1}
                    else:
                        delta[key]['v'] += v
                        delta[key]['n'] += 1
            for key in mean_changes.keys():
                if key not in delta.keys():
                    delta[key] = {}
                    delta[key]['v'] = 0
                    delta[key]['n'] = 1

            for k, v in delta.items():
                if k not in mean_changes.keys():
                    mean_changes[k] = []
                mean_changes[k].append(delta[k]['v'] / delta[k]['n'])

        return mean_changes

    def build_full_status(self, iterations):
        """
        Create a list with objects that have all the nodes with their statuses per iteration

        :param iterations: iterations output from iteration_bunch

        :return: a list of status objects that contain an iteration key with its number as value and a status key
            the status value contains per node all its states as keys with the corresponding state values
        """
        statuses = []
        status = {'iteration': 0, 'status': {}}
        for key, val in iterations[0]['status'].items():
            status['status'][key] = val
        statuses.append(status)
        for it in iterations[1:]:
            i = it['iteration']
            status = copy.deepcopy(statuses[-1])
            for node, d in it['status'].items():
                for var, val in d.items():
                    status['status'][node][var] = val
                    status['iteration'] = i
            statuses.append(status)

        return statuses

    def get_means(self, iterations):
        """
        Create a full status and get the mean data for the status key

        :param iterations: iterations output from iteration_bunch

        :return: Dictionary containing all statuses as keys,
            and as value a list of the average value over all nodes for that state per iteration
        """
        self.full_status = self.build_full_status(iterations)
        means = self.get_mean_data(self.full_status, 'status')
        return means

    def build_trends(self, iterations):
        """
        Overwrite build trends of diffusionmodel
        """
        means = self.get_means(iterations)
        means_status_delta_vals = self.get_mean_data(iterations, 'status')
        status_delta = self.get_mean_data(iterations, 'status_delta')

        return {'mean_delta_status_vals': means_status_delta_vals, 'status_delta': status_delta, 'means': means}

    def plot(self, trends, n, delta=None, delta_mean=None):
        """
        Create and show different plots of the trends

        :param trends: output from the build_trends function
        :param n: integer amount of iterations to show
        :param delta: boolean indicating whether to show the mean change per variable per iteration
        :param delta_mean: boolean indicating whether to show the mean value of changed variables per iteration
        """
        x = np.arange(0, n)

        sub_plots = 1
        if delta:
            sub_plots = 2 if (delta and not delta_mean) else 3

        _, axs = plt.subplots(sub_plots)

        # Mean status delta per iterations
        if delta or delta_mean:
            for status, values in trends['means'].items():
                axs[0].plot(x, values, label=status)
            axs[0].set_title("Mean values per variable per iteration")
            axs[0].legend()
        else:
            for status, values in trends['means'].items():
                plt.plot(x, values, label=status)
            plt.title("Mean values per variable per iteration")
            plt.legend()


        if delta:
            for status, values in trends['status_delta'].items():
                axs[1].plot(x, values, label=status)
            axs[1].set_title("Mean change per variable per iteration")
            axs[1].legend()

        i = 2 if delta else 1

        if delta_mean:
            for status, values in trends['mean_delta_status_vals'].items():
                axs[i].plot(x, values, label=status)
            axs[i].set_title("Mean value of changed variables per iteration")
            axs[i].legend()

        plt.show()

    def create_frames(self, iterations):
        """
        Create frames every plot_interval iterations
            by creating a dictionary that contains a list of all node values for a status key per iteration

        :param iterations: iterations output from iteration_bunch

        :return: tuple of a status value dictionary and a list of lists of node colors,
            the dictionary has a status as key and as value a list of lists, the first dimension corresponds with the iteration,
            the second dimension is a list that contains all the different node status values for that iteration,
            the node_colors list first dimension corresponds with the iteration,
            and the second dimension is a list of lists where each index holds the color value of the node at that index
        """
        if not self.full_status:
            self.full_status = self.build_full_status(iterations)
        statuses = list(self.available_statuses.keys())
        statuses.remove('Infected')
        histo_frames = {key: [] for key in statuses}
        node_colors = []
        for i in range(len(self.full_status)):
            if i % self.visualization_configuration['plot_interval'] == 0:
                status_list = {key: [] for key in statuses}
                for node in self.full_status[i]['status'].keys():
                    vals = self.full_status[i]['status'][node]
                    for key in statuses:
                        status_list[key].append(vals[key])

                for key in statuses:
                    histo_frames[key].append(status_list[key])
                node_colors.append([self.full_status[i]['status'][node][self.visualization_configuration['plot_variable']] for node in self.graph.nodes])

        return (histo_frames, node_colors)

    def visualize(self, iterations):
        """
        Visualize the network and color the nodes using a status
        Show histograms of the other statuses beneath the graph
        All visualization options are specified in the visualization_configuration variable
        If show_plot is set to True in the configuration, the visualization will be shown dynamically
        If plot_output is set in the configuration, an animation will be saved

        Currently the graphs are cleared and then completely redrawn, a good optimization would be to only update the changed values

        :param iterations: iterations output from iteration_bunch
        """
        if not self.visualization_configuration:
            raise Exception("Specify a visualization configuration before you visualize the model")

        (histo_frames, node_colors) = self.create_frames(iterations)

        statuses = list(self.available_statuses.keys())
        statuses.remove('Infected')

        n_status = len(statuses)

        fig = plt.figure(figsize=(10,9), constrained_layout=True)
        gs = fig.add_gridspec(6, n_status)

        network = fig.add_subplot(gs[:-1, :])

        axis = []

        for i in range(n_status):
            ax = fig.add_subplot(gs[-1, i])
            ax.set_title(statuses[i])
            ax.get_xaxis().set_ticks([])
            ax.get_yaxis().set_ticks([])
            axis.append(ax)

        n = int(len(iterations)/self.visualization_configuration['plot_interval'])

        cm = plt.cm.get_cmap(self.visualization_configuration['color_scale'])
        vmin = self.visualization_configuration['variable_limits'][self.visualization_configuration['plot_variable']][0]
        vmax = self.visualization_configuration['variable_limits'][self.visualization_configuration['plot_variable']][1]

        def updateData(curr):
            # Clean previous graphs
            network.clear()
            for ax in axis:
                ax.clear()

            # Plot all variable histograms
            for i, ax in enumerate(axis):
                _, bins, patches = ax.hist(histo_frames[statuses[i]][curr], range=self.visualization_configuration['variable_limits'][statuses[i]], density=1, bins=25, edgecolor='black')
                bin_centers = 0.5 * (bins[:-1] + bins[1:])
                col = bin_centers - min(bin_centers)
                col /= max(col)
                for c, p in zip(col, patches):
                    plt.setp(p, 'facecolor', cm(c))
                ax.set_title(statuses[i])
                # ax.set_ylim([0, len(self.graph.nodes)])
                ax.get_xaxis().set_ticks([])
                ax.get_yaxis().set_ticks([])

            # Plot network
            pos = nx.get_node_attributes(self.graph.graph, 'pos')
            nx.draw_networkx_edges(self.graph.graph, pos, alpha=0.2, ax=network)
            nc = nx.draw_networkx_nodes(self.graph.graph, pos, nodelist=self.graph.nodes, node_color=node_colors[curr], vmin=vmin, vmax=vmax, cmap=cm, node_size=50, ax=network)
            nc.set_edgecolor('black')
            network.get_xaxis().set_ticks([])
            network.get_yaxis().set_ticks([])
            network.set_title('Iteration: ' + str(curr * self.visualization_configuration['plot_interval']))

        simulation = animation.FuncAnimation(fig, updateData, n, interval=self.visualization_configuration['animation_interval'], repeat=True)

        norm = mpl.colors.Normalize(vmin=vmin, vmax=vmax)
        sm = plt.cm.ScalarMappable(cmap=cm, norm=norm)
        sm.set_array([])
        fig.colorbar(sm, ax=network)
        fig.suptitle(self.visualization_configuration['plot_title'], fontsize=16)

        if self.visualization_configuration['show_plot']:
            plt.show()

        if 'plot_output' in self.visualization_configuration.keys():
            self.save_plot(simulation)

    def save_plot(self, simulation):
        """
        Save the plot to a file specified in plot_output int he visualization configuration
        The file is generated using the writer from the pillow library

        :param simulation: Output of the matplotlib animation.FuncAnimation function
        """
        print('Saving plot at: ' + self.visualization_configuration['plot_output'] + ' ...')
        split = self.visualization_configuration['plot_output'].split('/')
        file_name = split[-1]
        file_path = self.visualization_configuration['plot_output'].replace(file_name, '')
        if not os.path.exists(file_path):
            os.makedirs(file_path)

        from PIL import Image
        writergif = animation.PillowWriter(fps=5)
        simulation.save(self.visualization_configuration['plot_output'], writer=writergif)
        print('Saved: ' + self.visualization_configuration['plot_output'])
