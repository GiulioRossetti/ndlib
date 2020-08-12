from ndlib.models.DiffusionModel import DiffusionModel
import future.utils
import os
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import copy
import numpy as np
from PIL import Image
import io

__author__ = 'Mathijs Maijer'
__license__ = "BSD-2-Clause"
__email__ = "m.f.maijer@gmail.com"


class ContinuousModel(DiffusionModel):

    def __init__(self, graph, constants=None, clean_status=None, visualization_configuration=None):
        """
             Model Constructor
             :param graph: A networkx graph object
         """
        super(self.__class__, self).__init__(graph)
        self.compartment = {}
        self.compartment_progressive = 0
        self.status_progressive = 0

        self.discrete_state = False

        self.available_statuses = {
            "Infected": 0
        }

        self.clean = True if clean_status else False

        self.constants = constants

        if visualization_configuration:
            self.configure_visualization(visualization_configuration)
        else:
            self.visualization_configuration = None

    def configure_visualization(self, visualization_configuration):
        if visualization_configuration:
            self.visualizations = []
            self.visualization_configuration = visualization_configuration
            vis_keys = visualization_configuration.keys()
            if 'plot_interval' in vis_keys:
                if isinstance(visualization_configuration['plot_interval'], int):
                    if visualization_configuration['plot_interval'] <= 0:
                        raise ValueError('plot_interval must be a positive integer')
                else:
                    raise ValueError('plot_interval must be a positive integer')
            else:
                raise ValueError('plot_interval must be included for visualization')

            if 'plot_variable' in vis_keys:
                if not isinstance(visualization_configuration['plot_variable'], str):
                    raise ValueError('Plot variable must be a string')
            else:
                self.visualization_configuration['plot_variable'] = None

            self.visualization_configuration['save_plot'] = True if self.visualization_configuration['save_plot'] else False
            if self.visualization_configuration['save_plot']:
                if 'plot_output' not in vis_keys:
                    self.visualization_configuration['plot_output'] = './visualization/network.gif'
                elif not isinstance(self.visualization_configuration['plot_output'], str):
                    raise ValueError('plot_output must be a string')
                # Todo create regex for plot output

            if 'plot_title' in self.visualization_configuration.keys():
                if not isinstance(self.visualization_configuration['plot_title'], str):
                    raise ValueError('Plot name must be a string')
            else:
                vis_var = self.visualization_configuration['plot_variable'] if self.visualization_configuration['plot_variable'] else '# Neighbours'
                self.visualization_configuration['plot_title'] = 'Network simulation of ' + vis_var

            if 'plot_annotation' in vis_keys:
                if not isinstance(self.visualization_configuration['plot_annotation'], str):
                    raise ValueError('Plot annotation must be a string')
            else:
                self.visualization_configuration['plot_annotation'] = None

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
                self.visualization_configuration['color_scale'] = 'YlGnBu'

    def add_status(self, status_name):
        if status_name not in self.available_statuses:
            self.available_statuses[status_name] = self.status_progressive
            self.status_progressive += 1

    def add_rule(self, status, function, rule):
        self.compartment[self.compartment_progressive] = (status, function, rule)
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

        if self.visualization_configuration and self.actual_iteration % self.visualization_configuration['plot_interval'] == 0:
            self.plot_graph()

        if self.actual_iteration == 0:
            self.actual_iteration += 1
            delta, status_delta = self.status_delta_continuous(self.status)
            if node_status:
                return {"iteration": 0, "status": copy.deepcopy(self.status),
                        "status_delta": copy.deepcopy(status_delta)}
            else:
                return {"iteration": 0, "status": {},
                         "status_delta": copy.deepcopy(status_delta)}

        nodes_data = self.graph.nodes(data=True)

        for u in self.graph.nodes:

            # For all rules
            for i in range(0, self.compartment_progressive):
                # Get and test the condition
                rule = self.compartment[i][2]
                test = rule.execute(node=u, graph=self.graph, status=self.status,
                                    status_map=self.available_statuses, attributes=nodes_data,
                                    params=self.params, constants=self.constants)
                if test:
                    # Update status if test succeeds
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

    def get_mean_data(self, iterations, mean_type):
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
        full_status = self.build_full_status(iterations)
        means = self.get_mean_data(full_status, 'status')
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
        x = np.arange(0, n)

        sub_plots = 1
        if delta:
            sub_plots = 2 if (delta and not delta_mean) else 3

        fig, axs = plt.subplots(sub_plots)

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

    def plot_graph(self):
        edge_x = []
        edge_y = []
        for edge in self.graph.edges():
            x0, y0 = self.graph.nodes[edge[0]]['pos']
            x1, y1 = self.graph.nodes[edge[1]]['pos']
            edge_x.append(x0)
            edge_x.append(x1)
            edge_x.append(None)
            edge_y.append(y0)
            edge_y.append(y1)
            edge_y.append(None)

        edge_trace = go.Scatter(
            x=edge_x, y=edge_y,
            line=dict(width=0.5, color='#888'),
            hoverinfo='none',
            mode='lines')

        node_x = []
        node_y = []
        for node in self.graph.nodes():
            x, y = self.graph.nodes[node]['pos']
            node_x.append(x)
            node_y.append(y)

        node_trace = go.Scatter(
            x=node_x, y=node_y,
            mode='markers',
            hoverinfo='text',
            marker=dict(
                showscale=True,
                # colorscale options
                #'Greys' | 'YlGnBu' | 'Greens' | 'YlOrRd' | 'Bluered' | 'RdBu' |
                #'Reds' | 'Blues' | 'Picnic' | 'Rainbow' | 'Portland' | 'Jet' |
                #'Hot' | 'Blackbody' | 'Earth' | 'Electric' | 'Viridis' |
                colorscale=self.visualization_configuration['color_scale'],
                reversescale=True,
                color=[],
                size=10,
                cmin=self.visualization_configuration['cmin'],
                cmax=self.visualization_configuration['cmax'],
                colorbar=dict(
                    thickness=15,
                    title=self.visualization_configuration['plot_variable'],
                    xanchor='left',
                    titleside='right',
                ),
                line_width=2))

        node_value = []
        node_text = []

        if self.visualization_configuration['plot_variable']:
            for node in self.graph.nodes():
                value = self.status[node][self.visualization_configuration['plot_variable']]
                node_value.append(value)
                node_text.append(self.visualization_configuration['plot_variable'] + ': ' + str(value))
        else:
            for node in self.graph.nodes():
                n_neighbors = len(self.graph.neighbors(node))
                node_value.append(n_neighbors)
                node_text.append('# of connections: ' + str(n_neighbors))

        node_trace.marker.color = node_value
        node_trace.text = node_text

        self.visualizations.append([edge_trace, node_trace])

    def visualize(self):
        if not self.visualization_configuration:
            print('Visualization stopped because no configuration is defined')
            return
        self.plot_graph() # Also save last network state

        frames = []
        for v in self.visualizations:
            frames.append(go.Frame(data=[v[0], v[1]]))

        fig = go.Figure(data=[self.visualizations[0][0], self.visualizations[0][1]],
             layout=go.Layout(
                title=self.visualization_configuration['plot_title'],
                titlefont_size=16,
                showlegend=False,
                hovermode='closest',
                margin=dict(b=20,l=5,r=5,t=40),
                annotations=[ dict(
                    text=self.visualization_configuration['plot_annotation'],
                    showarrow=False,
                    xref="paper", yref="paper",
                    x=0.005, y=-0.002 ) ],
                updatemenus=[dict(
                    type="buttons",
                    buttons=[dict(label="Play",
                          method="animate",
                          args=[None])])],
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
                ),
                frames=frames
            )

        fig.show()

        if self.visualization_configuration['save_plot']:
            # Create byte images
            images = []
            for i, f in enumerate(self.visualizations):
                fig = go.Figure(data=[self.visualizations[i][0], self.visualizations[i][1]],
                layout=go.Layout(
                    title=self.visualization_configuration['plot_title'],
                    titlefont_size=16,
                    showlegend=False,
                    hovermode='closest',
                    margin=dict(b=20,l=5,r=5,t=40),
                    annotations=[ dict(
                        text=self.visualization_configuration['plot_annotation'],
                        showarrow=False,
                        xref="paper", yref="paper",
                        x=0.005, y=-0.002 ) ])
                ).to_image(format="png")

                images.append(Image.open(io.BytesIO(fig)))
            # Create gif of byte image array

            split_dir = self.visualization_configuration['plot_output'].split('/')
            path = '/'.join(split_dir[0:-1])
            filename = split_dir[-1]

            if not os.path.exists(path):
                os.makedirs(path)

            images[0].save(self.visualization_configuration['plot_output'],
                save_all=True, append_images=images[1:], duration=500)
            print('Saved ' + self.visualization_configuration['plot_output'])
