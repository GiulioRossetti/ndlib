# NDlib - Network Diffusion Library

[![pyversions](https://img.shields.io/pypi/pyversions/ndlib.svg)](https://badge.fury.io/py/ndlib)
[![Build Status](https://travis-ci.org/GiulioRossetti/ndlib.svg?branch=master)](https://travis-ci.org/GiulioRossetti/ndlib)
[![Coverage Status](https://coveralls.io/repos/github/GiulioRossetti/ndlib/badge.svg?branch=master)](https://coveralls.io/github/GiulioRossetti/ndlib?branch=master)
[![Documentation Status](https://readthedocs.org/projects/ndlib/badge/?version=latest)](http://ndlib.readthedocs.io/en/latest/?badge=latest)
[![DOI](https://zenodo.org/badge/59556819.svg)](https://zenodo.org/badge/latestdoi/59556819)
[![Downloads](https://pepy.tech/badge/ndlib)](https://pepy.tech/project/ndlib)
[![Downloads](https://pepy.tech/badge/ndlib/month)](https://pepy.tech/project/ndlib)
[![SBD++](https://img.shields.io/badge/Available%20on-SoBigData%2B%2B-green)](https://sobigdata.d4science.org/group/sobigdata-gateway/explore?siteId=20371853)


![plot](./docs/NDlib_logo_full.png)


NDlib provides implementations of several spreading and opinion dynamics models.

The project documentation can be found on [ReadTheDocs](http://ndlib.readthedocs.io).

If you use ``NDlib`` as support to your research consider citing:

> G. Rossetti, L. Milli, S. Rinzivillo, A. Sirbu, D. Pedreschi, F. Giannotti.
> **NDlib: a Python Library to Model and Analyze Diffusion Processes Over Complex Networks.**
> Journal of Data Science and Analytics. 2017. 
> [DOI:0.1007/s41060-017-0086-6](https://doi.org/10.1007/s41060-017-0086-6) (pre-print available on [arXiv](https://arxiv.org/abs/1801.05854))

> G. Rossetti, L. Milli, S. Rinzivillo, A. Sirbu, D. Pedreschi, F. Giannotti.
> "**NDlib: Studying Network Diffusion Dynamics**", 
> IEEE International Conference on Data Science and Advanced Analytics, DSAA. 2017.

## Promo Video

[![Promo](https://img.youtube.com/vi/tYHNOuKJwbE/0.jpg)](https://www.youtube.com/watch?v=tYHNOuKJwbEE)

## Installation

To install the library just download (or clone) the current project and copy the ndlib folder in the root of your application.

Alternatively use pip:
```bash
sudo pip install ndlib
```

## Interactive Dashboard

NDlib includes a browser-based dashboard service for quick, code-free experimentation with diffusion and opinion models.

The dashboard lets you:

- build or load a network
- configure model and graph parameters from the UI
- run simulations in a strict three-step workflow
- inspect network state, trends, prevalence, and opinion evolution
- select infected seeds directly from the graph preview for epidemic models
- use community-aware layouts to expose modular structure
- separate the visual model builder into epidemic, continuous-opinion, discrete-opinion, and coupled use cases
- load starter templates such as `SIR`, `Algorithmic Bias`, `Majority Rule`, and a coupled starter layout
- copy the generated NDQL script or download the generated Python class after saving a custom pipeline
- build opinion-only custom models without an `Infected` class when the selected use case does not require one

Run it from the repository root with:

```bash
python ndlib/dashboard/server.py
```

If the package is installed, you can also launch it with the bundled command:

```bash
ndlib-dashboard
```

Once the server starts, open the local URL printed in the terminal.

| Configuration view | Network view |
| --- | --- |
| ![NDlib dashboard configuration view](docs/_static/dashboard/dashboard-config.png) | ![NDlib dashboard network view](docs/_static/dashboard/dashboard-network.png) |

### Visual Model Builder 

NDlib includes an interactive Visual Model Builder that allows designing custom compartmental models by drag-and-drop using a node-graph workflow. Visual models are compiled to standard Python classes and NDQL (Network Diffusion Query Language) scripts, and can be simulated or deleted directly from the dashboard.

The builder now starts from a use-case selector:

- **Epidemics**: discrete compartmental models with infection, threshold, and attribute-driven rules.
- **Continuous Opinions**: numeric-opinion layouts centered on numerical checks and continuous-variable style routing.
- **Discrete Opinions**: label-based opinion layouts with categorical and stochastic influence blocks.
- **Coupled / Advanced**: a mixed workspace that exposes every block for richer custom experiments.

Custom opinion starters now initialize their own statuses directly, so they no longer inherit the epidemic-only `Infected` requirement from the base diffusion model.

Starter templates are provided for the most common layouts, so you can begin from a working example instead of a blank canvas.

Draggable building blocks include:
- **Status Node**: Declares compartmental states (e.g., Susceptible, Infected, Recovered).
- **Node Stochastic**: Propagates state change stochastically if neighbors match a status.
- **Node Threshold**: Implements fraction-based cascading activation.
- **Edge Stochastic**: Evaluates link-level propagation conditions.
- **Count Down**: Implements fixed iteration-based delays (e.g., recovery after $D$ ticks).
- **Node Categorical Attribute**: Checks categorical node properties (e.g., gender, city).
- **Node Numerical Attribute**: Performs numerical checks on node variables (e.g., age ranges).
- **Node Numerical Variable**: Compares numeric opinion-like values or attributes against a threshold.
- **Conditional Composition**: Composes decision logic gates by nesting condition, if-true, and if-false branches.


| Use-case-aware Builder |
| --- |
| ![Use-case-aware Visual Model Builder](docs/_static/dashboard/dashboard-builder-usecases.png) |

The sidebar also includes:

- a live NDQL preview with a one-click copy action
- a per-model download button for the generated Python source
- example templates that can populate the canvas with a starter layout

See the full builder guide in [`docs/visual_model_builder_opinion_epidemic_guide.md`](docs/visual_model_builder_opinion_epidemic_guide.md).

## Documentation, Tutorials and Online Environments

For examples, tutorials and a complete reference visit the project documentation website on [ReadTheDocs](http://ndlib.readthedocs.io).

If you would like to test ``NDlib`` functionalities without installing anything on your machine consider using the preconfigured Jupyter Hub instances offered by [SoBigData RI](https://sobigdata.d4science.org/group/sobigdata-gateway/explore?siteId=20371853).


## Jupyter Notebook Tutorial

Interested in an extensive tutorial on NDlib? Check out the official Jupyter Notebooks!

[NDlib Overview](https://colab.research.google.com/github/KDDComplexNetworkAnalysis/CNA_Tutorials/blob/master/NDlib.ipynb#scrollTo=d80DUNRkKIn4)

## Collaborate with us!

``NDlib`` is an active project, any contribution is welcome!

If you like to include your model in NDlib feel free to fork the project, open an issue and contact us.

### How to contribute to this project?

Contributing is good, doing it correctly is better! Check out our [rules](https://github.com/GiulioRossetti/ndlib/blob/master/.github/CONTRIBUTING.md), issue a proper [pull request](https://github.com/GiulioRossetti/ndlib/blob/master/.github/PULL_REQUEST_TEMPLATE.md) /[bug report](https://github.com/GiulioRossetti/ndlib/blob/master/.github/ISSUE_TEMPLATE/bug_report.md) / [feature request](https://github.com/GiulioRossetti/ndlib/blob/master/.github/ISSUE_TEMPLATE/feature_request.md).

Do you want to be part of the NDlib community to discuss enhancements, desiderata, bug fix? Join us on **Slack**!

[<img align="middle" width="150" src="docs/join-slack-team.png">](https://join.slack.com/t/ndlib/shared_invite/enQtNTA2ODk1MzQzODE0LTU2YWEzZjAzNDFiNTBlY2QxN2IyODAwMjgyMDBmYjQ2NzhjZjA4NzA1M2U0ZmZlN2I1NGM5OTI2N2I4ZTFmMzQ)

We are a welcoming community... just follow the [Code of Conduct](https://github.com/GiulioRossetti/ndlib/blob/master/.github/CODE_OF_CONDUCT.md).
