This is a partial copy of the CLTK grc_models_cltk repository.
It contains only the lemmatizer models, for local use by SEDES
without bringing in all of CLTK as a dependency.

It comes from https://github.com/cltk/grc_models_cltk
at commit 94c04acac4405e264322d825978a2f2a80d01da5.
It includes only the lemmata subdirectory; and within that subdirectory
it omits the file greek_lemmata_cltk.py, including only
the backoff/*.pickle files.

It corresponds to what you would get in your ~/cltk_data directory
(minus the exceptions listed above) by running:

```
python3 -c 'from cltk.data.fetch import FetchCorpus; FetchCorpus("grc").import_corpus("grc_models_cltk")'
```

The upstream license is found in grc/model/grc_models_cltk/LICENSE.
