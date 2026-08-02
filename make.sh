#!/bin/sh

# This script runs the commands that `make` would run, for systems that do not have GNU Make installed.

set -e

WORKS="aratus argonautica callimachushymns homerichymns iliad nonnusdionysiaca odyssey quintussmyrnaeus shield theocritus theogony worksanddays"

src/tei2csv "Phaen." corpus/aratus.xml > corpus/aratus.csv
src/tei2csv "Argon." corpus/argonautica.xml > corpus/argonautica.csv
src/tei2csv "Callim.Hymn" corpus/callimachushymns-01.xml corpus/callimachushymns-02.xml corpus/callimachushymns-03.xml corpus/callimachushymns-04.xml corpus/callimachushymns-06.xml > "corpus/callimachushymns.csv"
src/tei2csv "Hom.Hymn" corpus/homerichymns-01.xml corpus/homerichymns-02.xml corpus/homerichymns-03.xml corpus/homerichymns-04.xml corpus/homerichymns-05.xml corpus/homerichymns-06.xml corpus/homerichymns-07.xml corpus/homerichymns-08.xml corpus/homerichymns-09.xml corpus/homerichymns-10.xml corpus/homerichymns-11.xml corpus/homerichymns-12.xml corpus/homerichymns-13.xml corpus/homerichymns-14.xml corpus/homerichymns-15.xml corpus/homerichymns-16.xml corpus/homerichymns-17.xml corpus/homerichymns-18.xml corpus/homerichymns-19.xml corpus/homerichymns-20.xml corpus/homerichymns-21.xml corpus/homerichymns-22.xml corpus/homerichymns-23.xml corpus/homerichymns-24.xml corpus/homerichymns-25.xml corpus/homerichymns-26.xml corpus/homerichymns-27.xml corpus/homerichymns-28.xml corpus/homerichymns-29.xml corpus/homerichymns-30.xml corpus/homerichymns-31.xml corpus/homerichymns-32.xml corpus/homerichymns-33.xml > "corpus/homerichymns.csv"
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
src/expectancy corpus/iliad.csv corpus/odyssey.csv corpus/homerichymns.csv corpus/theogony.csv corpus/worksanddays.csv corpus/shield.csv corpus/argonautica.csv corpus/theocritus.csv corpus/callimachushymns.csv corpus/aratus.csv > expectancy.hellenistic+archaic.csv

src/tei2html "Phaen." corpus/aratus.xml expectancy.all.csv > "sedes-web/aratus.html"
src/tei2html "Argon." corpus/argonautica.xml expectancy.all.csv > "sedes-web/argonautica.html"
src/tei2html "Callim.Hymn" corpus/callimachushymns-01.xml corpus/callimachushymns-02.xml corpus/callimachushymns-03.xml corpus/callimachushymns-04.xml corpus/callimachushymns-06.xml expectancy.all.csv > "sedes-web/callimachushymns.html"
src/tei2html "Hom.Hymn" corpus/homerichymns-01.xml corpus/homerichymns-02.xml corpus/homerichymns-03.xml corpus/homerichymns-04.xml corpus/homerichymns-05.xml corpus/homerichymns-06.xml corpus/homerichymns-07.xml corpus/homerichymns-08.xml corpus/homerichymns-09.xml corpus/homerichymns-10.xml corpus/homerichymns-11.xml corpus/homerichymns-12.xml corpus/homerichymns-13.xml corpus/homerichymns-14.xml corpus/homerichymns-15.xml corpus/homerichymns-16.xml corpus/homerichymns-17.xml corpus/homerichymns-18.xml corpus/homerichymns-19.xml corpus/homerichymns-20.xml corpus/homerichymns-21.xml corpus/homerichymns-22.xml corpus/homerichymns-23.xml corpus/homerichymns-24.xml corpus/homerichymns-25.xml corpus/homerichymns-26.xml corpus/homerichymns-27.xml corpus/homerichymns-28.xml corpus/homerichymns-29.xml corpus/homerichymns-30.xml corpus/homerichymns-31.xml corpus/homerichymns-32.xml corpus/homerichymns-33.xml expectancy.all.csv > "sedes-web/homerichymns.html"
src/tei2html "Il." corpus/iliad.xml expectancy.all.csv > "sedes-web/iliad.html"
src/tei2html "Dion." corpus/nonnusdionysiaca.xml expectancy.all.csv > "sedes-web/nonnusdionysiaca.html"
src/tei2html "Od." corpus/odyssey.xml expectancy.all.csv > "sedes-web/odyssey.html"
src/tei2html "Q.S." corpus/quintussmyrnaeus.xml expectancy.all.csv > "sedes-web/quintussmyrnaeus.html"
src/tei2html "Sh." corpus/shield.xml expectancy.all.csv > "sedes-web/shield.html"
src/tei2html "Theoc." corpus/theocritus.xml expectancy.all.csv > "sedes-web/theocritus.html"
src/tei2html "Theog." corpus/theogony.xml expectancy.all.csv > "sedes-web/theogony.html"
src/tei2html "W.D." corpus/worksanddays.xml expectancy.all.csv > "sedes-web/worksanddays.html"
