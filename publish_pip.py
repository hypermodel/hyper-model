from hypermodel import sh

package_path = "src/hyper-model"
pip_credentials = "--username growingdata --password $PYPI_PASSWORD"

sh(f"rm -r dist/*", package_path)
sh(f"python setup.py sdist bdist_wheel", package_path)
sh(f"python -m twine upload dist/* {pip_credentials} --verbose", package_path)
