from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))

requirements = [
    "bw_projects",
    'appdirs',
    'peewee',
    'stats_arrays',
    'wrapt',
]
test_requirements = ['pytest']

v_temp = {}
with open("bw_io/version.py") as fp:
    exec(fp.read(), v_temp)
version = ".".join((str(x) for x in v_temp['version']))


setup(
    name='bw_io',
    version=version,
    packages=find_packages(exclude=['tests']),
    author='Chris Mutel',
    author_email='cmutel@gmail.com',
    license="NewBSD 3-clause; LICENSE",
    # Only if you have non-python data (CSV, etc.). Might need to change the directory name as well.
    # package_data={'your_name_here': package_files(os.path.join('bw_io', 'data'))},
    install_requires=requirements,
    tests_require=requirements + test_requirements,
    url="https://github.com/brightway-lca/bw_io",
    long_description_content_type='text/markdown',
    long_description=open(path.join(here, "README.md")).read(),
    description='I/O functions for Brightway framework',
    classifiers=[
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Scientific/Engineering :: Information Analysis',
        'Topic :: Scientific/Engineering :: Mathematics',
    ],
)
