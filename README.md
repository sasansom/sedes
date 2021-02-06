# Sedes

Metrical position in Greek hexameter.

See https://sasansom.github.io/sedes/ for a
web-based demonstration of the visualizations
produced by this system.


## Setup

Sedes depends on [The Classical Language Toolkit](http://cltk.org/)
for lemmatization.
You first need to [install CLTK](https://docs.cltk.org/en/latest/installation.html)
in a virtual environment:
```
python3 -m venv venv
source venv/bin/activate
pip3 install cltk bs4 lxml
```

Next, [install the `greek_models_cltk` corpus](https://docs.cltk.org/en/latest/importing_corpora.html):
```
python3 -c 'from cltk.corpus.utils.importer import CorpusImporter; CorpusImporter("greek").import_corpus("greek_models_cltk")'
```

The corpus is stored in a `cltk_data` subdirectory of your home directory.
The authors have used commit
[a68b9837](https://github.com/cltk/grc_models_cltk/commit/a68b983734d34df16fd49661f11c4ea037ab173a)
of the `greek_models_cltk` corpus.

You only need to do the steps above once.
Thereafter, every time you start a new shell,
you need to run only the single command
```
source venv/bin/activate
```

## Programs

The "src" subdirectory contains a `tei2csv` program
that processes a TEI-encoded XML document as downloaded from Perseus
and produces a CSV file that annotates every word with
its line number and sedes. For example:
```
./src/tei2csv "Il." corpus/iliad.xml > corpus/iliad.csv
```

The `expectancy.R` program annotates one or more CSV files
as produced by `tei2csv` with statistics about expectancy for each word.
```
Rscript src/expectancy.R corpus/*.csv > expectancy.all.csv
```

The `tei2html` program produces an HTML representation of
a TEI-encoded XML document, with visual highlighting of word expectancy.
If you put the HTML file in the web-demo directory,
it will have access to locally installed web fonts for Greek.
```
./src/tei2html corpus/iliad.xml expectancy.all.csv > web-demo/iliad.html
```

The `join-expectancy` program takes a work-specific CSV file (as
produced by `tei2csv`) and augments it with lemma/sedes expectancy
numbers.
```
./src/join-expectancy corpus/iliad.csv expectancy.all.csv > iliad-expectancy.csv
```

The "src/hexameter" subdirectory contains a Python module
that we use for metrical analysis.
It is by Hope Ranker and comes from https://github.com/epilanthanomai/hexameter.


## Corpus

The "corpus" subdirectory contains selected TEI-encoded XML texts downloaded from
[Perseus](https://www.perseus.tufts.edu/hopper/).
These are suitable for input to `tei2csv` and `tei2html`.


## Getting started

If you have [GNU Make](https://www.gnu.org/software/make/) installed,
you can analyze all the texts in the corpus using the command
```
make
```

The above command will produce a file `all.csv` that contains
every word in every work, annotated with its work, line number, and sedes.

If you do not have GNU Make, the script `make.sh` runs the
same commands as `make` would:
```
./make.sh
```


## Data format

The output of `tei2csv` is
[CSV](https://en.wikipedia.org/wiki/Comma-separated_values)
that may be imported into a spreadsheet or further processed
by another program.

Greek text is represented as UTF-8 Unicode text.
Characters are stored in decomposed form using
[Normalization Form D (NFD)](https://jktauber.com/articles/python-unicode-ancient-greek/#normalization);
this means that diacritics are separate
combining characters.
For example, the word ἀοιδή is stored as the sequence of characters
```
U+03B1 GREEK SMALL LETTER ALPHA
U+0313 COMBINING COMMA ABOVE
U+03BF GREEK SMALL LETTER OMICRON
U+03B9 GREEK SMALL LETTER IOTA
U+03B4 GREEK SMALL LETTER DELTA
U+03B7 GREEK SMALL LETTER ETA
U+0301 COMBINING ACUTE ACCENT
```
After UTF-8 encoding, this sequence is
`\xce\xb1\xcc\x93\xce\xbf\xce\xb9\xce\xb4\xce\xb7\xcc\x81`.
