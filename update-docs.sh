#!/bin/bash

mv ./src/hyper-model/docs/index.rst ./src/hyper-model/docs/index.bkup
mv ./src/hyper-model/docs/*.rst
mv ./src/hyper-model/docs/index.bkup ./src/hyper-model/docs/index.rst

sphinx-apidoc -f -o ./src/hyper-model/docs -H "HyperModel" -A "Growing Data Pty Ltd" -V "0.1.75" ./src/hyper-model/hypermodel/