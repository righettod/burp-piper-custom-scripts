#!/bin/bash
############################################################
## Script run all static audit steps for the project
## Created to ease usage in the GH CI actions
## System dependencies: "jq"
############################################################
cdir=$(pwd)
echo "[+] Current folder: $cdir"
exit_rc=0
echo "[+] Extract 'flake8' and 'bandit' configuration from VSCode workspace file..."
flake8Args=$(cat project.code-workspace | jq -r '.settings["python.linting.flake8Args"]|join(" ")')
banditArgs=$(cat project.code-workspace | jq -r '.settings["python.linting.banditArgs"]|join(" ")')
echo "flake8Args     = $flake8Args"
echo "banditArgs     = $banditArgs"
echo "[+] Run flake8..."
python -m flake8 $flake8Args $cdir
rc=$?
exit_rc=$((exit_rc+rc))
echo "[+] Run bandit..."
python -m bandit $banditArgs $cdir 
rc=$?
exit_rc=$((exit_rc+rc))
if [ $exit_rc -ne 0 ]
then
    echo "[!] Some check failed !!!"
else
    echo "[+] Audit OK."
fi
echo "Exit return code is $exit_rc"
exit $exit_rc