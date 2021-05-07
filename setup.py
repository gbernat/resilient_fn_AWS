#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
import glob
import ntpath


def get_module_name(module_path):
    """
    Return the module name of the module path
    """
    return ntpath.split(module_path)[1].split(".")[0]


def snake_to_camel(word):
    """
    Convert a word from snake_case to CamelCase
    """
    return ''.join(x.capitalize() or '_' for x in word.split('_'))


setup(
    name="fn_aws",
    version="1.0.0",
    license="MIT",
    author="Guido Bernat",
    author_email="guido.bernat@gmail.com",
    url="https://xelere.com",
    description="Resilient Circuits Components for AWS",
    long_description="""Ability to orchestrate with AWS in information gathering activities such as getting data from EC2 Instances or Security Groups, 
        as well as performing actions like stopping/terminating EC2 Instances, creating snapshots, assigning security groups, tagging objects, deleting key pairs and execution of Lambda functions. 
        The use of specific credentials (access keys) in each action is allowed if required.""",
    install_requires=[
        "resilient_circuits>=30.0.0",
        'boto3>=1.10.6'
    ],
    packages=find_packages(),
    include_package_data=True,
    platforms="any",
    classifiers=[
        "Programming Language :: Python",
    ],
    entry_points={
        "resilient.circuits.components": [
            # When setup.py is executed, loop through the .py files in the components directory and create the entry points.
            "{}FunctionComponent = fn_aws.components.{}:FunctionComponent".format(snake_to_camel(get_module_name(filename)), get_module_name(filename)) for filename in glob.glob("./fn_aws/components/[a-zA-Z]*.py")
        ],
        "resilient.circuits.configsection": ["gen_config = fn_aws.util.config:config_section_data"],
        "resilient.circuits.customize": ["customize = fn_aws.util.customize:customization_data"],
        "resilient.circuits.selftest": ["selftest = fn_aws.util.selftest:selftest_function"]
    }
)
