#!/bin/bash

mv ./src/hyper-model/doc/index.rst ./src/hyper-model/doc/index.bkup
mv ./src/hyper-model/doc/*.rst
mv ./src/hyper-model/doc/index.bkup ./src/hyper-model/doc/index.rst

sphinx-apidoc -f -o ./src/hyper-model/doc -H "HyperModel" -A "Growing Data Pty Ltd" -V "0.1.75" ./src/hyper-model/hypermodel/