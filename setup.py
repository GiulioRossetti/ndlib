from setuptools import setup, find_packages
# from codecs import open
# from os import path

__author__ = 'rossetti'
__license__ = "GPL"
__email__ = "giulio.rossetti@gmail.com"

# here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
# with open(path.join(here, 'README.md'), encoding='utf-8') as f:
#    long_description = f.read()

setup(name='ndlib',
      version='2.0',
      license='GNU General Public License v3 or later (GPLv3+)',
      description='Network Diffusion Library',
      url='https://github.com/GiulioRossetti/ndlib',
      author='Giulio Rossetti',
      author_email='giulio.rossetti@gmail.com',
      classifiers=[
          # How mature is this project? Common values are
          #   3 - Alpha
          #   4 - Beta
          #   5 - Production/Stable
          'Development Status :: 5 - Production/Stable',

          # Indicate who your project is intended for
          'Intended Audience :: Developers',
          'Topic :: Software Development :: Build Tools',

          # Pick your license as you wish (should match "license" above)
          'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',

          "Operating System :: OS Independent",

          # Specify the Python versions you support here. In particular, ensure
          # that you indicate whether you support Python 2, Python 3 or both.
          'Programming Language :: Python',
          'Programming Language :: Python :: 2.7'
      ],
      keywords='epidemics opinion-dynamics simulator complex-networks',
      install_requires=['numpy', 'networkx', 'scipy', 'bokeh'],
      packages=find_packages(exclude=["*.test", "*.test.*", "test.*", "test"]),
      )
