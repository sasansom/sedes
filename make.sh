#!/bin/sh

# This script generates all.csv, for systems that do not have GNU Make installed.

set -e

WORKS="aratus argonautica callimachushymns homerichymns iliad nonnusdionysiaca odyssey quintussmyrnaeus shield theocritus theogony worksanddays"

src/tei2csv "Aratus" corpus/aratus.xml > corpus/aratus.csv
src/tei2csv "Argon." corpus/argonautica.xml > corpus/argonautica.csv
src/tei2csv "Callim. Hymn" corpus/callimachushymns.xml > corpus/callimachushymns.csv
src/tei2csv "Hymns" corpus/homerichymns.xml > corpus/homerichymns.csv
src/tei2csv "Il." corpus/iliad.xml > corpus/iliad.csv
src/tei2csv "Dion." corpus/nonnusdionysiaca.xml > corpus/nonnusdionysiaca.csv
src/tei2csv "Od." corpus/odyssey.xml > corpus/odyssey.csv
src/tei2csv "Quint. Smyrn." corpus/quintussmyrnaeus.xml > corpus/quintussmyrnaeus.csv
src/tei2csv "Shield" corpus/shield.xml > corpus/shield.csv
src/tei2csv "Theoc." corpus/theocritus.xml > corpus/theocritus.csv
src/tei2csv "Theog." corpus/theogony.xml > corpus/theogony.csv
src/tei2csv "WD" corpus/worksanddays.xml > corpus/worksanddays.csv

WORKS_CSV="$(for work in $WORKS; do echo "corpus/$work.csv"; done)"
(sed -n -e '1p' corpus/homerichymns.csv; for x in $WORKS_CSV; do sed -e '1d' $x; done) > all.csv
rm -f $(for work in $WORKS; do echo "corpus/$work.csv"; done)
