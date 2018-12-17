import setuptools
import json
import glob
import os

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="tfe",

    version="0.5.1",
    python_requires='>=3.5.0',

    author="HappyPathway",
    author_email="info@happypathway.com",
    description="Utilities for working with Terraform Enterprise API",
    install_requires = [
        "requests", 
        "jinja2",
        "pyhcl",
        "hvac"
    ],
    long_description=long_description,
    url="https://github.com/HappyPathway/PyTFE-Core",
    scripts=[
    ],
    packages=[
        "tfe.core",
        "tfe"
    ],
    py_modules=[
        "tfe.core.configuration",
        "tfe.core.exception",
        "tfe.core.oauth_client",
        "tfe.core.organization",
        "tfe.core.run",
        "tfe.core.sentinel",
        "tfe.core.session",
        "tfe.core.state",
        "tfe.core.team_access",
        "tfe.core.tfe",
        "tfe.core.variable",
        "tfe.core.workspace",
        "tfe.workspace",
        "tfe.organization"
    ],
    package_data={
        "tfe.core": [
            "templates/hcl/*",
            "templates/json/*"
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    zip_safe = False
)
