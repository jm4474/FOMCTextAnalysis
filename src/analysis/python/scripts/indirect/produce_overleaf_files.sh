rm -r ../../output/overleaf_files
mkdir ../../output/overleaf_files
for f in *.py; do python "$f"; done
