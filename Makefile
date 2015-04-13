BASENAMES = homerichymns iliad odyssey theogony worksanddays corpus
DATS = $(addsuffix -1gram.dat,$(BASENAMES)) \
	$(addsuffix -2gram.dat,$(BASENAMES)) \
	$(addsuffix -initial2gram.dat,$(BASENAMES)) \
	$(addsuffix -word2gram.dat,$(BASENAMES))
GRAPHS = $(addsuffix .png,$(basename $(DATS)))

all: $(DATS) $(GRAPHS)

%.txt: %.xml
	./tei2txt "$<" > "$@"

%-1gram.dat %-2gram.dat %-initial2gram.dat %-word2gram.dat: corpus/%.txt
	./ngrams --base "$*" "$<"
corpus-1gram.dat corpus-2gram.dat corpus-initial2gram.dat corpus-word2gram.dat: corpus/*.txt
	./ngrams --base corpus $^

%-1gram.png: %-1gram.dat
	Rscript 1gram.R "$*-1gram.dat" "\"$*\" letter frequency"
%-2gram.png: %-2gram.dat
	Rscript 2gram.R "$*-2gram.dat" "\"$*\" digram frequency"
%-word2gram.png: %-word2gram.dat
	Rscript 2gram.R "$*-word2gram.dat" "\"$*\" within-word digram frequency"
%-initial2gram.png: %-initial2gram.dat
	Rscript 2gram.R "$*-initial2gram.dat" "\"$*\" word-initial digram frequency"
