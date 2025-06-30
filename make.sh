#!/bin/sh

# This script runs the commands that `make` would run, for systems that do not have GNU Make installed.

set -e

WORKS="aratus argonautica iliad nonnusdionysiaca odyssey quintussmyrnaeus shield theocritus theogony worksanddays"

src/tei2csv "Phaen." corpus/aratus.xml > corpus/aratus.csv
src/tei2csv "Argon." corpus/argonautica.xml > corpus/argonautica.csv
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
src/expectancy corpus/iliad.csv corpus/odyssey.csv corpus/theogony.csv corpus/worksanddays.csv corpus/shield.csv corpus/argonautica.csv corpus/theocritus.csv corpus/aratus.csv > expectancy.hellenistic+archaic.csv

src/tei2html "Phaen." corpus/aratus.xml expectancy.all.csv > "sedes-web/aratus.html"
src/tei2html "Argon." corpus/argonautica.xml expectancy.all.csv > "sedes-web/argonautica.html"
src/tei2html "Il." corpus/iliad.xml expectancy.all.csv > "sedes-web/iliad.html"
src/tei2html "Dion." corpus/nonnusdionysiaca.xml expectancy.all.csv > "sedes-web/nonnusdionysiaca.html"
src/tei2html "Od." corpus/odyssey.xml expectancy.all.csv > "sedes-web/odyssey.html"
src/tei2html "Q.S." corpus/quintussmyrnaeus.xml expectancy.all.csv > "sedes-web/quintussmyrnaeus.html"
src/tei2html "Sh." corpus/shield.xml expectancy.all.csv > "sedes-web/shield.html"
src/tei2html "Theoc." corpus/theocritus.xml expectancy.all.csv > "sedes-web/theocritus.html"
src/tei2html "Theog." corpus/theogony.xml expectancy.all.csv > "sedes-web/theogony.html"
src/tei2html "W.D." corpus/worksanddays.xml expectancy.all.csv > "sedes-web/worksanddays.html"
