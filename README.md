# NDlib - Network Diffusion Library

[![Build Status](https://travis-ci.org/GiulioRossetti/ndlib.svg?branch=master)](https://travis-ci.org/GiulioRossetti/ndlib)
[![Coverage Status](https://coveralls.io/repos/github/GiulioRossetti/ndlib/badge.svg?branch=master)](https://coveralls.io/github/GiulioRossetti/ndlib?branch=master)
[![Documentation Status](https://readthedocs.org/projects/ndlib/badge/?version=latest)](http://ndlib.readthedocs.io/en/latest/?badge=latest)
[![pyversions](https://img.shields.io/pypi/pyversions/ndlib.svg)](https://badge.fury.io/py/ndlib)
[![Updates](https://pyup.io/repos/github/GiulioRossetti/ndlib/shield.svg)](https://pyup.io/repos/github/GiulioRossetti/ndlib/)
[![PyPI version](https://badge.fury.io/py/ndlib.svg)](https://badge.fury.io/py/ndlib)

![NDlib logo](https://github.com/GiulioRossetti/ndlib/blob/master/docs/ndlogo2.png)

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

## Rationale behind NDlib

- A __simulation__ is univocally identified by a __graph__ and a (__configured__) __model__;
- Each __model__ describes a peculiar kind of diffusion process as an agent-based __simulation__ occurring at discrete time;
- A __configuration__ identifies the initial status of the diffusion and the parameters needed to instantiate the selected __model__;
- Once a model has been __configured__, every __iteration__ of the __simulation__ returns only the nodes which changed their statuses.

## Installation

In order to install the library just download (or clone) the current project and copy the ndlib folder in the root of your application.

Alternatively use pip:
```bash
sudo pip install ndlib
```

## Documentation

For examples, tutorials and an complete reference visit the project documentation website on [ReadTheDocs](http://ndlib.readthedocs.io).

## Collaborate with us!

``NDlib`` is an active project, any contribution is welcome!

If you like to include your model in our library (as well as in [NDlib-REST](https://github.com/GiulioRossetti/ndlib-rest)) feel free to fork the project, open an issue and contact us.
