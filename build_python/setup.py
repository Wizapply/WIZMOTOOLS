# This file is wizmo python module.
# (C) WIZAPPLY CO., LTD. <info@wizapply.com>

from setuptools import setup, find_packages

setup(
    name='wizmo',
    version='4.62',
    license='MIT License',
    description='WIZMO-TOOLS Python Modules',
    
    author='WIZAPPLY CO., LTD.',
    author_email='info@wizapply.com',
    url='https://wizapply.com/',
    
    include_package_data=True,
    packages=find_packages(),
    package_dir={'': '.'},
    package_data={'':['*.dll','*.so',]},
    zipfile=None
)
