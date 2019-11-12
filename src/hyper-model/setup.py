# Copyright 2019 Growing Data Pty Ltd [https://growingdata.com.au]
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from setuptools import setup, find_packages

NAME = "hypermodel"
VERSION = "0.1.78"
REQUIRES = [
    "click",
    "kfp==0.1.34",
    "pandas",
    "joblib",
    "google-cloud",
    "google-cloud-bigquery",
    # Nice progress indicators
    "tqdm",
    # Gitlab
    "python-gitlab",
    # API Serving
    "flask",
    "waitress",
    "sphinx_rtd_theme",
    "kubernetes>=8.0.0, <=9.0.0",
]

setup(
    name=NAME,
    version=VERSION,
    description="Hyper Model provides functionality to support MLOps",
    author="Growing Data",
    install_requires=REQUIRES,
    packages=find_packages(),
    classifiers=[
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Topic :: Scientific/Engineering",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.5.3",
    include_package_data=True,
    entry_points={"console_scripts": ["hml = hypermodel.cli.cli_start:main"]},
)
