# SEDES

Metrical position in Greek hexameter.

See https://sasansom.github.io/sedes/ for
web-based visualizations
produced by this system.

See the tag [tapa-version](https://github.com/sasansom/sedes/releases/tag/tapa-version)
to reproduce the figures from the _TAPA_ article,
["Sedes as Style in Greek Hexameter: A Computational Approach."](https://muse.jhu.edu/article/819768)

See support [here](https://sasansom.github.io/sedes/dhq2023/)
for the _DHQ_ article, ["SEDES: Metrical Position in Greek Hexameter."](https://digitalhumanities.org/dhq/vol/17/2/000675/000675.html)

See support [here](https://sasansom.github.io/epic-rhythm/)
for the _GRBS_ article, ["Epic Rhythm: Metrical Shapes in Greek Hexameter."](https://grbs.library.duke.edu/index.php/grbs/article/view/17015)

## Setup

Sedes depends on [The Classical Language Toolkit](http://cltk.org/)
for lemmatization.
You first need to [install CLTK](https://docs.cltk.org/en/latest/installation.html)
in a virtual environment:
```
python3 -m venv venv
source venv/bin/activate
pip3 install -U pip setuptools wheel
pip3 install cltk bs4 lxml
```

Next, [install the `grc_models_cltk` corpus](https://docs.cltk.org/en/latest/data.html):
```
python3 -c 'from cltk.data.fetch import FetchCorpus; FetchCorpus("grc").import_corpus("grc_models_cltk")'
```

The corpus is stored in a `cltk_data` subdirectory of your home directory.
The authors have used commit
[94c04ac](https://github.com/cltk/grc_models_cltk/commit/94c04acac4405e264322d825978a2f2a80d01da5)
of the `grc_models_cltk` corpus.

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
src/tei2csv "Il." corpus/iliad.xml > corpus/iliad.csv
```

The `expectancy` program annotates one or more CSV files
as produced by `tei2csv` with statistics about expectancy for each word.
```
src/expectancy corpus/*.csv > expectancy.all.csv
```

The `tei2html` program produces an HTML representation of
a TEI-encoded XML document, with visual highlighting of word expectancy.
If you put the HTML file in the sedes-web directory,
it will have access to locally installed web fonts for Greek.
```
src/tei2html "Il." corpus/iliad.xml expectancy.all.csv > sedes-web/iliad.html
```

The `join-expectancy` program takes a work-specific CSV file (as
produced by `tei2csv`) and augments it with lemma/sedes expectancy
numbers.
```
src/join-expectancy corpus/iliad.csv expectancy.all.csv > iliad-expectancy.csv
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
make -j4
```

The above command will run tei2csv, expectancy, and tei2html
to produce HTML visualizations in the sedes-web directory,
as well as intermediary files.

If you do not have GNU Make, the script `make.sh` runs the
same commands as `make` would:
```
./make.sh
```


## Controlling the variables used to calculate expectancy

You can control what variables are used to group the input
for expectancy calculation using the
`--by` command-line option of the expectancy and tei2html programs.
By default the programs compute the *sedes* expectancy of each distinct lemma,
as if you had used `--by sedes/lemma`.

The syntax of the `--by` option is
<code><var>dist_vars</var>/<var>cond_vars</var></code>,
with "distribution variables" on the left of the slash and
"condition variables" on the right.
On either side of the slash, there may be zero or more variable names,
separated by commas.
To calculate expectancy, the programs first partition the input
into groups according to distinct values of the condition variables.
Then, they find the expectancy of each of the distinct values
of the distribution variables.

For example, by default, the programs first divide the input
into groups, where each group represents one distinct lemma.
Then, within each lemma group, they find what *sedes*
are more and less expected.

To use variables other than the default,
you will have to run the component programs manually,
rather than using `make`.

This is an example of calculating *sedes* expectancy
after first grouping by metrical shape, rather than lemma:
```
src/expectancy --by sedes/metrical_shape corpus/*.csv > expectancy.sedes-metrical_shape.csv
src/tei2html --by sedes/metrical_shape "Phaen." corpus/aratus.xml expectancy.sedes-metrical_shape.csv > aratus.sedes-metrical_shape.html
```

If you want a summary of the expectancy of a single variable
across the entire input, without any grouping at all,
you can do that too.
For example, to count the number of occurrences of each unique word:
```
src/expectancy --by word/ corpus/*.csv
```

Or to calculate the overall *sedes* expectancy,
without first grouping by lemma or any other variable:
```
src/expectancy --by sedes/ corpus/*.csv
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

The characters that mark long and short metrical values
are respectively `–` U+2013 EN DASH
and `⏑` U+23D1 METRICAL BREVE.
