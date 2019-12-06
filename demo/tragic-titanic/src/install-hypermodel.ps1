cd ..\..\..
cd src\hyper-model
python -m pip install -e .
python setup.py install
cd ..\..
cd demo\tragic-titanic\src
python setup.py install
