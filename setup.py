from setuptools import setup, find_packages
from codecs import open
from os import path

__author__ = 'Giulio Rossetti'
__license__ = "BSD-2-Clause"
__email__ = "giulio.rossetti@gmail.com"

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()


setup(name='ndlib',
      version='5.1.1',
      license='BSD-Clause-2',
      description='Network Diffusion Library',
      url='https://github.com/GiulioRossetti/ndlib',
      author='Giulio Rossetti',
      author_email='giulio.rossetti@gmail.com',
      use_2to3=True,
      entry_points={
          'console_scripts': [
              'NDQL_translate = scripts.NDQL_translate:translate',
              'NDQL_execute = scripts.NDQL_execute:execute'
          ],
      },
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
          'License :: OSI Approved :: BSD License',

          "Operating System :: OS Independent",

          # Specify the Python versions you support here. In particular, ensure
          # that you indicate whether you support Python 2, Python 3 or both.
          'Programming Language :: Python',
          'Programming Language :: Python :: 3'
      ],
      keywords='epidemics opinion-dynamics simulator complex-networks',
      long_description=long_description,
      long_description_content_type='text/markdown',
      install_requires=['netdispatch', 'python-igraph', 'numpy', 'networkx', 'dynetx', 'scipy', 'bokeh', 'future', ''],
      packages=find_packages(exclude=["*.test", "*.test.*", "test.*", "test", "ndlib.test", "ndlib.test.*"]),
      )
