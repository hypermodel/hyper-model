#!/bin/bash

mv ./src/hyper-model/docs/index.rst ./src/hyper-model/docs/index.bkup
mv ./src/hyper-model/docs/*.rst
mv ./src/hyper-model/docs/index.bkup ./src/hyper-model/docs/index.rst

sphinx-apidoc -f -o ./src/hyper-model/docs -H "HyperModel" -A "Growing Data Pty Ltd" -V "0.1.80" ./src/hyper-model/hypermodel/

rm ./src/hyper-model/docs/modules.rst

cd src/hyper-model/docs
make html

cd ../../../