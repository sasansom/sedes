# Sedes

Metrical position in Greek hexameter.


## Programs

The "src" subdirectory contains a `tei2csv` program
that processes a TEI-encoded XML document as downloaded from Perseus
and produces a CSV file that annotates every word with
its line number and sedes.

The "src/hexameter" subdirectory contains a Python module
that we use for metrical analysis.
It is by Hope Ranker and comes from https://github.com/epilanthanomai/hexameter.


## Corpus

The "corpus" subdirectory contains selected TEI-encoded XML texts downloaded from
[Perseus](https://www.perseus.tufts.edu/hopper/).
These are suitable for input to `tei2csv`.


## Getting started

If you have [GNU Make](https://www.gnu.org/software/make/) installed,
you can analyze all the texts in the corpus using the command
```
make
```

The above command will produce a file `all.csv` that contains
every word in every work, annotated with its work, line number, and sedes.

If you do not have GNU Make, you can analyze texts into separate CSV files.
For example:
```
./src/tei2csv Il. corpus/iliad.xml > corpus/iliad.csv
```
