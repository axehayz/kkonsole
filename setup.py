
# setup.py used to generate setup scripts for Windows CLI executable compatibility. a.k.a for Dan Kelly. :shrug

from setuptools import setup, find_packages

setup(
    name='kkonsole',
    version='0.9',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'Click',
        'requests',
    ],
    entry_points='''
        [console_scripts]
        kkonsole=kkonsole:kkonsole
        kperform=kperform.kperform:kperform
        klookup=klookup.klookup:klookup
        kstats=klookup.klookup:stats
    ''',
)