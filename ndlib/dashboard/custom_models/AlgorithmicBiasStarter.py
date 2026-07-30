import numpy as np
from ndlib.models.DiffusionModel import DiffusionModel
from ndlib.models.compartments.Compartment import Compartiment
from ndlib.models.compartments.NDQLBlocks import Parameter, Constant, Variable, Distribution, Compose, Filter, Selector, Aggregator, Kernel, Transform, ClampNormalize, Schedule, Observe, ExposureRate, TransmissionKernel, DoseResponseBlock, LatencyPeriod, IncubationState, RecoveryKernel, WaningImmunity, VaccinationBlock, QuarantineBlock, TestingBlock, TreatmentBlock, HospitalizationBlock, MortalityBlock, ReinfectionBlock, StrainBlock, SuperSpreaderBlock, SeasonalityBlock, ImportationBlock, RewiringBlock, CommunityMixingBlock, EdgeActivationBlock, SeedSelection, NodeRoleAssignment, AttributeInitializer, GraphImport, CommunityAssignment, RuleAlias, PreviewObservable, ValidationHint, AttributeCoupling, OpinionAffectsInfection, OpinionAffectsRecovery, OpinionAffectsContactRate, InfectionAffectsOpinion, StatusDependentOpinionUpdate, EpidemicDependentBias, PolicyIntervention, CommunityCoupling, OpinionDistribution, OpinionStubbornness, OpinionNoise, OpinionPolarization, OpinionMediaInfluence, OpinionTrustFilter, OpinionConsensusBlock, OpinionRepulsion, OpinionAssimilation, OpinionExternalField, OpinionMultiTopic, OpinionLabelSwitch, OpinionBoundedDrift, _safe_eval, _clamp, _graph_iteration
from ndlib.models.opinions.initial_opinion_distribution import sample_initial_opinions

class AlgorithmicBiasStarter(DiffusionModel):
    def __init__(self, graph, seed=None):
        super().__init__(graph, seed)
        self.discrete_state = False
        self.available_statuses = {'Opinion': 0}
        self.parameters = {
            'model': {
                'initial_opinion_distribution': {
                    'descr': 'Initial opinion distribution in [0, 1]',
                    'choices': [
                        {'value': 'uniform', 'label': 'Uniform'},
                        {'value': 'normal', 'label': 'Normal'},
                        {'value': 'gaussian', 'label': 'Gaussian'},
                        {'value': 'bimodal', 'label': 'Bimodal'},
                        {'value': 'left_skewed', 'label': 'Left skewed'},
                        {'value': 'right_skewed', 'label': 'Right skewed'},
                        {'value': 'polarized', 'label': 'Polarized'},
                    ],
                    'optional': True,
                    'default': 'uniform'
                },
                'epsilon': {
                    'descr': 'Opinion distance threshold (bounded confidence)',
                    'range': [0, 1],
                    'optional': True,
                    'default': 0.1
                },
                'gamma': {
                    'descr': 'Opinion selection bias',
                    'range': [0, 100],
                    'optional': True,
                    'default': 1.5
                },
                'mu': {
                    'descr': 'Opinion compromise strength',
                    'range': [0, 1],
                    'optional': True,
                    'default': 0.5
                },
                'zealot_share': {
                    'descr': 'Share of immutable zealot nodes',
                    'range': [0, 1],
                    'optional': True,
                    'default': 0.1
                },
                'zealot_value': {
                    'descr': 'Fixed zealot opinion value',
                    'range': [0, 1],
                    'optional': True,
                    'default': 0.0
                },
            },
            'nodes': {},
            'edges': {}
        }
        self.name = 'AlgorithmicBiasStarter'
        self.declarations = []
        self.observables = []
        self.update_rules = []
        self.continuous_blocks = {
            'distribution': None,
            'distance_threshold': 'bounded_confidence',
            'selection_bias': 'selection_bias',
            'compromise': 'opinion_compromise',
            'assimilation': None,
            'stubbornness': None,
            'noise': None,
            'repulsion': None,
            'bounded_drift': None,
            'polarization': None,
            'external_field': None,
            'trust_filter': None,
            'consensus': None,
            'memory': None,
            'normalization': 'opinion_normalization',
            'quantization': None,
            'media_influence': None,
            'multi_topic': None,
            'label_switch': None,
            'zealot': 'opinion_zealot'
        }

    def set_initial_status(self, configuration=None):
        import numpy as np
        configuration = configuration or None
        model_params = configuration.get_model_parameters() if configuration is not None else {}
        self.params['nodes'] = {}
        self.params['edges'] = {}
        self.params['status'] = {}
        self.params['model'] = {}
        for param, param_info in self.parameters['model'].items():
            self.params['model'][param] = model_params.get(param, param_info.get('default'))
        from ndlib.models.opinions.initial_opinion_distribution import sample_initial_opinions
        opinions = sample_initial_opinions(
            len(self.status),
            self.params['model'].get('initial_opinion_distribution', 'uniform'),
        )
        zealot_share = float(self.params['model'].get('zealot_share', 0.0) or 0.0)
        zealot_value = float(self.params['model'].get('zealot_value', 0.0) or 0.0)
        zealot_nodes = set()
        if zealot_share > 0.0:
            node_ids = list(self.status.keys())
            zealot_count = int(round(len(node_ids) * zealot_share))
            zealot_count = max(0, min(len(node_ids), zealot_count))
            if zealot_count > 0:
                zealot_nodes = set(np.random.choice(node_ids, zealot_count, replace=False))
        self.zealot_nodes = zealot_nodes
        self.zealot_value = zealot_value
        for node, opinion in zip(self.status, opinions):
            self.status[node] = float(opinion)
            if node in zealot_nodes:
                self.status[node] = zealot_value
            self.graph.nodes[node]['opinion'] = float(self.status[node])
        self.initial_status = self.status.copy()
        return self

    def _select_neighbor(self, node, actual_status):
        import numpy as np
        neighbors = list(self.graph.neighbors(node))
        if self.graph.directed:
            neighbors = list(self.graph.predecessors(node))
        neighbors = [n for n in neighbors if n in actual_status]
        if not neighbors:
            return None
        gamma = self.params['model'].get('gamma', 1.5)
        if gamma <= 0:
            return neighbors[np.random.randint(0, len(neighbors))]
        opinions = np.array([actual_status[neigh] for neigh in neighbors], dtype=float)
        diff = np.abs(opinions - float(actual_status[node]))
        weights = np.power(np.maximum(diff, 1e-5), -gamma)
        total = float(np.sum(weights))
        if not np.isfinite(total) or total <= 0:
            return neighbors[np.random.randint(0, len(neighbors))]
        weights = weights / total
        return neighbors[np.random.choice(len(neighbors), p=weights)]

    def iteration(self, node_status=True):
        import numpy as np
        actual_status = self.status.copy()
        if self.actual_iteration == 0:
            self.actual_iteration += 1
            if node_status:
                return {'iteration': 0, 'status': actual_status.copy(), 'node_count': {}, 'status_delta': {}}
            return {'iteration': 0, 'status': {}, 'node_count': {}, 'status_delta': {}}

        epsilon = self.params['model'].get('epsilon', 0.1)
        mu = self.params['model'].get('mu', 0.5)
        assimilation_rate = self.params['model'].get('assimilation_rate', 0.5)
        stubbornness = self.params['model'].get('stubbornness', 0.0)
        noise_sigma = self.params['model'].get('noise_sigma', 0.0)
        repulsion_strength = self.params['model'].get('repulsion_strength', 0.0)
        bounded_drift_step = self.params['model'].get('bounded_drift_step', 0.0)
        polarization_strength = self.params['model'].get('polarization_strength', 0.0)
        external_target = self.params['model'].get('external_target', 0.5)
        external_strength = self.params['model'].get('external_strength', 0.0)
        trust_threshold = self.params['model'].get('trust_threshold', 1.0)
        consensus_mode = str(self.params['model'].get('consensus_mode', 'mean'))
        consensus_weight = self.params['model'].get('consensus_weight', 0.5)
        memory_alpha = self.params['model'].get('memory_alpha', 0.0)
        quantization_bins = int(self.params['model'].get('quantization_bins', 0))
        media_weight = self.params['model'].get('media_weight', 0.0)
        media_count = int(self.params['model'].get('k', self.params['model'].get('media_count', 0)))
        media_opinions = self.params['model'].get('media_opinions', [])
        if not isinstance(media_opinions, (list, tuple)):
            media_opinions = []
        if media_count > 0 and len(media_opinions) < media_count:
            while len(media_opinions) < media_count:
                media_opinions.append(float(len(media_opinions)) / float(max(1, media_count - 1)) if media_count > 1 else 0.5)
        media_opinions = [float(np.clip(v, 0.0, 1.0)) for v in media_opinions[:max(0, media_count or len(media_opinions))]]
        multi_topic_names = self.params['model'].get('multi_topic_names', [])
        if isinstance(multi_topic_names, str):
            multi_topic_names = [t.strip() for t in multi_topic_names.split(',') if t.strip()]
        multi_topic_coupling = self.params['model'].get('multi_topic_coupling', 0.0)
        nodes_list = list(actual_status.keys())
        if not nodes_list:
            return {'iteration': self.actual_iteration - 1, 'status': {}, 'node_count': {}, 'status_delta': {}}
        for _ in range(len(nodes_list)):
            node = nodes_list[np.random.randint(0, len(nodes_list))]
            if hasattr(self, 'zealot_nodes') and node in self.zealot_nodes:
                continue
            neighbor = self._select_neighbor(node, actual_status)
            if neighbor is None:
                continue
            diff = abs(float(actual_status[node]) - float(actual_status[neighbor]))
            node_val = float(actual_status[node])
            neigh_val = float(actual_status[neighbor])
            trust_gate = min(epsilon, trust_threshold)
            if diff <= trust_gate:
                avg_val = float(np.clip(0.5 * (node_val + neigh_val), 0.0, 1.0))
                node_val = float(np.clip(node_val + mu * (neigh_val - node_val), 0.0, 1.0))
                neigh_val = float(np.clip(neigh_val + assimilation_rate * (avg_val - neigh_val), 0.0, 1.0))
                if consensus_mode.lower() in {'mean', 'average', 'consensus'}:
                    consensus_val = float(np.clip(consensus_weight * avg_val + (1.0 - consensus_weight) * node_val, 0.0, 1.0))
                    node_val = consensus_val
                    neigh_val = consensus_val
            elif repulsion_strength > 0.0:
                if node_val >= neigh_val:
                    node_val = float(np.clip(node_val + repulsion_strength * (1.0 - neigh_val), 0.0, 1.0))
                else:
                    node_val = float(np.clip(node_val - repulsion_strength * neigh_val, 0.0, 1.0))
            elif polarization_strength > 0.0:
                if node_val >= neigh_val:
                    node_val = float(np.clip(node_val + polarization_strength * (1.0 - node_val), 0.0, 1.0))
                else:
                    node_val = float(np.clip(node_val - polarization_strength * node_val, 0.0, 1.0))
            if noise_sigma > 0.0:
                node_val = float(np.clip(np.random.normal(node_val, noise_sigma), 0.0, 1.0))
            if external_strength > 0.0:
                node_val = float(np.clip(node_val + external_strength * (external_target - node_val), 0.0, 1.0))
            if stubbornness > 0.0 and node in self.initial_status:
                node_val = float(np.clip((1.0 - stubbornness) * node_val + stubbornness * float(self.initial_status[node]), 0.0, 1.0))
            actual_status[node] = node_val
            actual_status[neighbor] = neigh_val
        if quantization_bins and quantization_bins > 1:
            step = 1.0 / float(quantization_bins - 1)
            for node in actual_status:
                actual_status[node] = float(np.clip(round(actual_status[node] / step) * step, 0.0, 1.0))
        if media_weight > 0.0 and media_opinions:
            media_vals = np.clip(np.asarray(media_opinions, dtype=float), 0.0, 1.0)
            for node in actual_status:
                if hasattr(self, 'zealot_nodes') and node in self.zealot_nodes:
                    continue
                target_media = float(np.mean(media_vals))
                actual_status[node] = float(np.clip((1.0 - media_weight) * actual_status[node] + media_weight * target_media, 0.0, 1.0))
        if multi_topic_names:
            for node in actual_status:
                node_topics = self.graph.nodes[node].get('opinion_vector') or {}
                if not isinstance(node_topics, dict):
                    node_topics = {}
                for topic in multi_topic_names:
                    topic_val = float(np.clip(actual_status[node] + multi_topic_coupling * (0.5 - actual_status[node]), 0.0, 1.0))
                    node_topics[topic] = topic_val
                    self.graph.nodes[node][topic] = topic_val
                self.graph.nodes[node]['opinion_vector'] = node_topics
                if node_topics:
                    actual_status[node] = float(np.mean(list(node_topics.values())))
        normalize_min = float(self.params['model'].get('normalize_min', 0.0))
        normalize_max = float(self.params['model'].get('normalize_max', 1.0))
        if normalize_max > normalize_min:
            for node in actual_status:
                if hasattr(self, 'zealot_nodes') and node in self.zealot_nodes:
                    continue
                actual_status[node] = float(np.clip(actual_status[node], normalize_min, normalize_max))
        update_rules = self.update_rules if hasattr(self, 'update_rules') else []
        if update_rules:
            iteration_index = int(self.actual_iteration)
            for node in list(actual_status.keys()):
                context = {
                    'node': node,
                    'graph': self.graph,
                    'status': actual_status,
                    'params': self.params,
                    'model': self.params.get('model', {}),
                    'iteration': iteration_index,
                    'opinion': actual_status.get(node, 0.0),
                    'value': actual_status.get(node, 0.0),
                    'np': np,
                    'math': __import__('math'),
                }
                for rule in update_rules:
                    if not isinstance(rule, dict):
                        continue
                    schedule = rule.get('schedule')
                    if isinstance(schedule, dict):
                        start = int(schedule.get('start', 0) or 0)
                        end = int(schedule.get('end', iteration_index) or iteration_index)
                        period = int(schedule.get('period', 1) or 1)
                        phase = int(schedule.get('phase', 0) or 0)
                        if iteration_index < start or iteration_index > end:
                            continue
                        if period > 1 and ((iteration_index - phase) % period) != 0:
                            continue
                    when_expr = rule.get('when')
                    if when_expr is not None and not bool(__import__('ndlib.models.compartments.NDQLBlocks', fromlist=['_safe_eval'])._safe_eval(when_expr, context, default=False)):
                        continue
                    target_name = str(rule.get('target', 'opinion'))
                    expression = rule.get('expression', 'opinion')
                    value = __import__('ndlib.models.compartments.NDQLBlocks', fromlist=['_safe_eval'])._safe_eval(expression, context, default=context.get(target_name, context.get('opinion', 0.0)))
                    if value is None:
                        continue
                    if target_name == 'opinion':
                        value = float(np.clip(value, 0.0, 1.0))
                        actual_status[node] = value
                        self.graph.nodes[node]['opinion'] = value
                    else:
                        self.graph.nodes[node][target_name] = value
                    context[target_name] = value
                    context['opinion'] = actual_status.get(node, context.get('opinion', 0.0))
        for node, opinion in actual_status.items():
            self.graph.nodes[node]['opinion'] = float(opinion)
        self.status = actual_status
        self.actual_iteration += 1
        if node_status:
            return {'iteration': self.actual_iteration - 1, 'status': actual_status.copy(), 'node_count': {}, 'status_delta': {}}
        return {'iteration': self.actual_iteration - 1, 'status': {}, 'node_count': {}, 'status_delta': {}}