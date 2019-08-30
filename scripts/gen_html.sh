echo "gen_html"

echo "moving to docs"
cd docs || exit

echo "generating apidoc"
sphinx-apidoc -o source/modules bobocep

echo "making html"
make html
