#!/bin/sh

# This script generates all.csv, for systems that do not have GNU Make installed.

set -e

WORKS="aratus argonautica callimachushymns homerichymns iliad nonnusdionysiaca odyssey quintussmyrnaeus shield theocritus theogony worksanddays"

src/tei2csv "Phaen." corpus/aratus.xml > corpus/aratus.csv
src/tei2csv "Argon." corpus/argonautica.xml > corpus/argonautica.csv
src/tei2csv "Callim.Hymn" corpus/callimachushymns.xml > corpus/callimachushymns.csv
src/tei2csv "Hom.Hymn" corpus/homerichymns.xml > corpus/homerichymns.csv
src/tei2csv "Il." corpus/iliad.xml > corpus/iliad.csv
src/tei2csv "Dion." corpus/nonnusdionysiaca.xml > corpus/nonnusdionysiaca.csv
src/tei2csv "Od." corpus/odyssey.xml > corpus/odyssey.csv
src/tei2csv "Q.S." corpus/quintussmyrnaeus.xml > corpus/quintussmyrnaeus.csv
src/tei2csv "Sh." corpus/shield.xml > corpus/shield.csv
src/tei2csv "Theoc." corpus/theocritus.xml > corpus/theocritus.csv
src/tei2csv "Theog." corpus/theogony.xml > corpus/theogony.csv
src/tei2csv "W.D." corpus/worksanddays.xml > corpus/worksanddays.csv

WORKS_CSV="$(for work in $WORKS; do echo "corpus/$work.csv"; done)"

src/expectancy $WORKS_CSV > expectancy.all.csv
src/expectancy corpus/iliad.csv corpus/odyssey.csv corpus/homerichymns.csv corpus/theogony.csv corpus/worksanddays.csv corpus/shield.csv corpus/argonautica.csv corpus/theocritus.csv corpus/callimachushymns.csv corpus/aratus.csv > expectancy.hellenic+archaic.csv

src/tei2html corpus/aratus.xml expectancy.all.csv > "web-demo/aratus.html"
src/tei2html corpus/argonautica.xml expectancy.all.csv > "web-demo/argonautica.html"
src/tei2html corpus/callimachushymns.xml expectancy.all.csv > "web-demo/callimachushymns.html"
src/tei2html corpus/homerichymns.xml expectancy.all.csv > "web-demo/homerichymns.html"
src/tei2html corpus/iliad.xml expectancy.all.csv > "web-demo/iliad.html"
src/tei2html corpus/nonnusdionysiaca.xml expectancy.all.csv > "web-demo/nonnusdionysiaca.html"
src/tei2html corpus/odyssey.xml expectancy.all.csv > "web-demo/odyssey.html"
src/tei2html corpus/quintussmyrnaeus.xml expectancy.all.csv > "web-demo/quintussmyrnaeus.html"
src/tei2html corpus/shield.xml expectancy.all.csv > "web-demo/shield.html"
src/tei2html corpus/theocritus.xml expectancy.all.csv > "web-demo/theocritus.html"
src/tei2html corpus/theogony.xml expectancy.all.csv > "web-demo/theogony.html"
src/tei2html corpus/worksanddays.xml expectancy.all.csv > "web-demo/worksanddays.html"
