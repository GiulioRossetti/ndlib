import inspect
from collections import OrderedDict

from ndlib.models.compartments import NDQLBlocks as ndql_blocks

CORE_BLOCK_TYPES = (
    "Parameter",
    "Constant",
    "Variable",
    "Distribution",
    "Selector",
    "Filter",
    "Aggregator",
    "Kernel",
    "Transform",
    "Compose",
    "Schedule",
    "Observe",
    "ClampNormalize",
)

EPIDEMIC_BLOCK_TYPES = (
    "ExposureRate",
    "TransmissionKernel",
    "DoseResponseBlock",
    "LatencyPeriod",
    "IncubationState",
    "RecoveryKernel",
    "WaningImmunity",
    "VaccinationBlock",
    "QuarantineBlock",
    "TestingBlock",
    "TreatmentBlock",
    "HospitalizationBlock",
    "MortalityBlock",
    "ReinfectionBlock",
    "StrainBlock",
    "SuperSpreaderBlock",
    "SeasonalityBlock",
    "ImportationBlock",
    "RewiringBlock",
    "CommunityMixingBlock",
    "EdgeActivationBlock",
)

OPINION_BLOCK_TYPES = (
    "OpinionDistribution",
    "OpinionDistanceThreshold",
    "OpinionSelectionBias",
    "OpinionCompromise",
    "OpinionStubbornness",
    "OpinionNoise",
    "OpinionPolarization",
    "OpinionExternalField",
    "OpinionTrustFilter",
    "OpinionConsensusBlock",
    "OpinionRepulsion",
    "OpinionAssimilation",
    "OpinionMemory",
    "OpinionNormalization",
    "OpinionQuantization",
    "OpinionMediaInfluence",
    "OpinionZealot",
    "OpinionMultiTopic",
    "OpinionLabelSwitch",
    "OpinionBoundedDrift",
)

LEGACY_OPINION_ALIAS_TYPES = (
    "OpinionDistanceThreshold",
    "OpinionSelectionBias",
    "OpinionMemory",
    "OpinionNormalization",
    "OpinionQuantization",
    "OpinionZealot",
)

HYBRID_BLOCK_TYPES = (
    "AttributeCoupling",
    "OpinionAffectsInfection",
    "OpinionAffectsRecovery",
    "OpinionAffectsContactRate",
    "InfectionAffectsOpinion",
    "StatusDependentOpinionUpdate",
    "EpidemicDependentBias",
    "PolicyIntervention",
    "CommunityCoupling",
)

UTILITY_BLOCK_TYPES = (
    "SeedSelection",
    "NodeRoleAssignment",
    "AttributeInitializer",
    "GraphImport",
    "CommunityAssignment",
    "RuleAlias",
    "PreviewObservable",
    "ValidationHint",
)

OPINION_DISTRIBUTIONS = (
    "uniform",
    "normal",
    "gaussian",
    "bimodal",
    "left_skewed",
    "right_skewed",
    "polarized",
)

BLOCK_FAMILIES = OrderedDict(
    [
        ("core", {"label": "Core", "types": CORE_BLOCK_TYPES}),
        ("epidemic", {"label": "Epidemic", "types": EPIDEMIC_BLOCK_TYPES}),
        ("opinion", {"label": "Opinion", "types": OPINION_BLOCK_TYPES}),
        ("hybrid", {"label": "Hybrid", "types": HYBRID_BLOCK_TYPES}),
        ("utility", {"label": "Utility", "types": UTILITY_BLOCK_TYPES}),
    ]
)


def all_block_types():
    for family in BLOCK_FAMILIES.values():
        for block_type in family["types"]:
            yield block_type


def all_supported_block_types():
    for block_type in all_block_types():
        yield block_type
    for block_type in LEGACY_OPINION_ALIAS_TYPES:
        yield block_type


def block_family_for_type(block_type):
    for family_key, family in BLOCK_FAMILIES.items():
        if block_type in family["types"]:
            return family_key
    return "unknown"


def _sanitize_default(value):
    if isinstance(value, (list, tuple)):
        return [_sanitize_default(item) for item in value]
    if isinstance(value, dict):
        return {key: _sanitize_default(item) for key, item in value.items()}
    return value


def _infer_kind(default):
    if default is inspect._empty:
        return "unknown"
    if isinstance(default, bool):
        return "bool"
    if isinstance(default, int):
        return "int"
    if isinstance(default, float):
        return "float"
    if isinstance(default, (list, tuple)):
        return "list"
    if isinstance(default, dict):
        return "dict"
    return type(default).__name__.lower()


def build_block_schema_registry():
    registry = {}
    for block_type in all_block_types():
        block_cls = getattr(ndql_blocks, block_type, None)
        if block_cls is None:
            continue

        signature = inspect.signature(block_cls.__init__)
        parameters = OrderedDict()
        required = []
        for name, param in signature.parameters.items():
            if name in {"self", "kwargs"}:
                continue
            if param.kind in {inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD}:
                continue
            default = param.default
            has_default = default is not inspect._empty
            if not has_default:
                required.append(name)
            parameters[name] = {
                "required": not has_default,
                "default": _sanitize_default(default) if has_default else None,
                "kind": _infer_kind(default),
            }

        if block_type in {"Distribution", "OpinionDistribution"} and "family" in parameters:
            parameters["family"]["choices"] = [
                {"value": value, "label": value.replace("_", " ").title()}
                for value in OPINION_DISTRIBUTIONS
            ]

        registry[block_type] = {
            "family": block_family_for_type(block_type),
            "class_name": block_type,
            "parameters": parameters,
            "required_parameters": required,
        }
    return registry


BLOCK_SCHEMA_REGISTRY = build_block_schema_registry()


def get_block_schema(block_type):
    return BLOCK_SCHEMA_REGISTRY.get(block_type)


def validate_model_payload(model_data):
    """
    Validate a custom model payload before save.

    The validator is intentionally permissive on extra parameters because many
    block classes accept arbitrary kwargs for compatibility. It focuses on
    known structural errors that would break save/load round-tripping.
    """
    errors = []
    warnings = []

    if not isinstance(model_data, dict):
        return [{"severity": "error", "path": "$", "message": "Model payload must be a JSON object"}]

    name = str(model_data.get("name", "")).strip()
    if not name:
        errors.append({"severity": "error", "path": "$.name", "message": "Model name is required"})

    compartments = model_data.get("compartments", [])
    if not isinstance(compartments, list):
        errors.append({"severity": "error", "path": "$.compartments", "message": "Compartments must be a list"})
        compartments = []

    for index, compartment in enumerate(compartments):
        path = f"$.compartments[{index}]"
        if not isinstance(compartment, dict):
            errors.append({"severity": "error", "path": path, "message": "Compartment must be an object"})
            continue

        comp_type = compartment.get("type")
        if not comp_type:
            errors.append({"severity": "error", "path": f"{path}.type", "message": "Compartment type is required"})
            continue
        if get_block_schema(comp_type) is None and comp_type not in {"NodeStochastic", "NodeThreshold", "EdgeStochastic", "CountDown", "NodeCategoricalAttribute", "NodeNumericalAttribute", "NodeNumericalVariable", "EdgeCategoricalAttribute", "EdgeNumericalAttribute", "ConditionalComposition"} and comp_type not in LEGACY_OPINION_ALIAS_TYPES:
            errors.append({"severity": "error", "path": f"{path}.type", "message": f"Unsupported compartment type '{comp_type}'"})

        params = compartment.get("params", {})
        if not isinstance(params, dict):
            errors.append({"severity": "error", "path": f"{path}.params", "message": "Compartment params must be an object"})
            continue

        if comp_type == "OpinionMediaInfluence":
            k_value = params.get("k", 1)
            try:
                k_int = int(round(float(k_value)))
            except (TypeError, ValueError):
                errors.append({"severity": "error", "path": f"{path}.params.k", "message": "OpinionMediaInfluence.k must be an integer"})
                k_int = None
            if k_int is not None and k_int < 1:
                errors.append({"severity": "error", "path": f"{path}.params.k", "message": "OpinionMediaInfluence.k must be at least 1"})

            media_opinions = params.get("media_opinions")
            if media_opinions is not None and not isinstance(media_opinions, (list, tuple)):
                errors.append({"severity": "error", "path": f"{path}.params.media_opinions", "message": "media_opinions must be a list"})
            elif isinstance(media_opinions, (list, tuple)) and k_int is not None and len(media_opinions) < k_int:
                errors.append({"severity": "error", "path": f"{path}.params.media_opinions", "message": "Provide one opinion value for each media source"})

        if comp_type == "OpinionZealot":
            share = params.get("share")
            if share is not None:
                try:
                    share_value = float(share)
                except (TypeError, ValueError):
                    share_value = None
                if share_value is None or not 0.0 <= share_value <= 1.0:
                    errors.append({"severity": "error", "path": f"{path}.params.share", "message": "OpinionZealot.share must be in [0, 1]"})
            fixed_value = params.get("fixed_value")
            if fixed_value is not None:
                try:
                    fixed_value = float(fixed_value)
                except (TypeError, ValueError):
                    fixed_value = None
                if fixed_value is None or not 0.0 <= fixed_value <= 1.0:
                    errors.append({"severity": "error", "path": f"{path}.params.fixed_value", "message": "OpinionZealot.fixed_value must be in [0, 1]"})

        if comp_type == "OpinionDistribution":
            family = str(params.get("family", "uniform")).lower()
            if family not in OPINION_DISTRIBUTIONS:
                errors.append({"severity": "error", "path": f"{path}.params.family", "message": f"Unsupported opinion distribution family '{family}'"})
            bounds = params.get("bounds", [0.0, 1.0])
            if isinstance(bounds, (list, tuple)) and len(bounds) >= 2:
                try:
                    low = float(bounds[0])
                    high = float(bounds[1])
                    if high < low:
                        warnings.append({"severity": "warning", "path": f"{path}.params.bounds", "message": "Bounds will be normalized to ascending order"})
                except (TypeError, ValueError):
                    errors.append({"severity": "error", "path": f"{path}.params.bounds", "message": "OpinionDistribution.bounds must contain numeric values"})

    initial_opinion_distribution = model_data.get("initial_opinion_distribution")
    if isinstance(initial_opinion_distribution, dict):
        family = str(initial_opinion_distribution.get("family", "uniform")).lower()
        if family not in OPINION_DISTRIBUTIONS:
            errors.append({"severity": "error", "path": "$.initial_opinion_distribution.family", "message": f"Unsupported opinion distribution family '{family}'"})
    elif initial_opinion_distribution is not None:
        family = str(initial_opinion_distribution).lower()
        if family not in OPINION_DISTRIBUTIONS:
            errors.append({"severity": "error", "path": "$.initial_opinion_distribution", "message": f"Unsupported opinion distribution family '{family}'"})

    return errors + warnings
