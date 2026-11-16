Version numbers are made from a month and a year: for example,
v26.8 is a release that occurred in August 2026.


* Import CLTK Greek lemmatization code and modules into the SEDES source tree (#100).
  SEDES uses only a very small subset of CLTK, which is otherwise a large dependency.
  It also resolve Python version incompatibility with the cltk package (#99).

  It is no longer necessary to create a virtual environment (venv) with cltk;
  however it is still required to install nltk in the virtual environment.
  You may delete the cltk_data directory in your home directory if SEDES was the only project using it,
  because the necessary data files are now included in the SEDES source tree.
  You may also delete your existing venv and recreate it with just nltk,
  in order to save about 5 GB of disk space.

## v26.10

* Override lemma of ἔνθ’ to be ἔνθα (had been εἰμί).
  8983e7c4ae6aef9635536b0e91b034941f356c35
* Change the default always-prepositive words ὁθ’ and ὁτ’ to ὅθ’ and ὅτ’ respectively.
  be0d5276d4aa5f7ef993954831a333db132c5c8e
* Align certain entries in the exception-appositives.csv table for the newer Perseus 6 texts.
* Make some other scansion corrections. 

## v26.8

The first release that has the CSV files under corpus/ in version control for easier reuse.
75cff80e9bf7d2e52c4aade33bc08960d655dfac
