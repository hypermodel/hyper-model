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

NAME = "crashed"
VERSION = "0.0.73"
REQUIRES = [
    "click",
    "kfp",
    "xgboost",
    "pandas",
    "sklearn",
    "xgboost",
    "google-cloud",
    "google-cloud-bigquery",
    "hypermodel",
]

setup(
    name=NAME,
    version=VERSION,
    install_requires=REQUIRES,
    packages=find_packages(),
    python_requires=">=3.5.3",
    include_package_data=True,
    entry_points={"console_scripts": ["crashed = crashed.start:main"]},
)
