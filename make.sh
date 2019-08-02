#!/bin/sh

# This script generates all.csv, for systems that do not have GNU Make installed.

set -e

WORKS="homerichymns iliad odyssey shield theogony worksanddays"

src/tei2csv "Hymns" corpus/homerichymns.xml > corpus/homerichymns.csv
src/tei2csv "Il." corpus/iliad.xml > corpus/iliad.csv
src/tei2csv "Od." corpus/odyssey.xml > corpus/odyssey.csv
src/tei2csv "Shield" corpus/shield.xml > corpus/shield.csv
src/tei2csv "Theog." corpus/theogony.xml > corpus/theogony.csv
src/tei2csv "WD" corpus/worksanddays.xml > corpus/worksanddays.csv

WORKS_CSV="$(for work in $WORKS; do echo "corpus/$work.csv"; done)"
(sed -n -e '1p' corpus/homerichymns.csv; sed -e '1d' $WORKS_CSV) > all.csv
rm -f $(for work in $WORKS; do echo "corpus/$work.csv"; done)
