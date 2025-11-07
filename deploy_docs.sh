#!/bin/bash
# Script for manual deployment to GitHub Pages

echo "Building documentation..."
cd docs
make html
cd ..

echo "Preparing gh-pages branch..."
git checkout --orphan gh-pages
git rm -rf .
cp -r docs/_build/html/* .
touch .nojekyll

echo "Deploying to GitHub Pages..."
git add .
git commit -m "Deploy documentation"
git push -f origin gh-pages

echo "Done! Check your GitHub Pages settings."
git checkout main
