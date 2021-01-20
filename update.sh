#! /bin/bash

where=$(dirname $0 | xargs readlink -f)
outdir="$where/mizsdata"

# download fresh school COVID-19 data from the MIZŠ github
wget -q https://github.com/GK-MIZS/covid/blob/main/api.json -P "$outdir"
wget -q https://github.com/GK-MIZS/covid/blob/main/oddelki.csv -P "$outdir"
wget -q https://github.com/GK-MIZS/covid/blob/main/ucenci.csv -P "$outdir"
wget -q https://github.com/GK-MIZS/covid/blob/main/zaposleni.csv-P "$outdir"

# prepare it for sledilnik
python parse_school_cases.py
python parse_absences.py
