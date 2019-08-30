cd ../docs || exit
sphinx-apidoc -o source/modules bobocep
make html
