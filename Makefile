WORKS = \
	aratus \
	argonautica \
	callimachushymns \
	homerichymns \
 	iliad \
	nonnusdionysiaca \
 	odyssey \
	quintussmyrnaeus \
 	shield \
	theocritus \
 	theogony \
 	worksanddays \

WORK_IDENTIFIER_aratus           = Phaen.
WORK_IDENTIFIER_argonautica      = Argon.
WORK_IDENTIFIER_callimachushymns = Callim.Hymn
WORK_IDENTIFIER_homerichymns     = Hom.Hymn
WORK_IDENTIFIER_iliad            = Il.
WORK_IDENTIFIER_nonnusdionysiaca = Dion.
WORK_IDENTIFIER_odyssey          = Od.
WORK_IDENTIFIER_quintussmyrnaeus = Q.S.
WORK_IDENTIFIER_shield           = Sh.
WORK_IDENTIFIER_theocritus       = Theoc.
WORK_IDENTIFIER_theogony         = Theog.
WORK_IDENTIFIER_worksanddays     = W.D.

EXPECTANCY_FILES = expectancy.all.csv expectancy.hellenic+archaic.csv
WORKS_CSV = $(addprefix corpus/,$(addsuffix .csv,$(WORKS)))
WORKS_HTML = $(addprefix web-demo/,$(addsuffix .html,$(WORKS)))

.PHONY: all
all: $(EXPECTANCY_FILES) $(WORKS_HTML)

expectancy.all.csv: $(WORKS_CSV)
	src/expectancy $^ > "$@"

expectancy.hellenic+archaic.csv: corpus/iliad.csv corpus/odyssey.csv corpus/homerichymns.csv corpus/theogony.csv corpus/worksanddays.csv corpus/shield.csv corpus/argonautica.csv corpus/theocritus.csv corpus/callimachushymns.csv corpus/aratus.csv
	src/expectancy $^ > "$@"

corpus/%.csv: corpus/%.xml
	src/tei2csv "$(WORK_IDENTIFIER_$*)" "$<" > "$@"

web-demo/%.html: corpus/%.xml expectancy.all.csv
	src/tei2html $^ > "$@"

PYTHON = python3

.PHONY: test
test:
	(cd src && "$(PYTHON)" -m unittest)

.PHONY: fonts
fonts: \
	web-demo/fonts/SIL\ Open\ Font\ License.txt \
	web-demo/fonts/Cardo-Regular.woff \
	web-demo/fonts/Cardo-Italic.woff \
	web-demo/fonts/Cardo-Bold.woff

web-demo/fonts/SIL\ Open\ Font\ License.txt: fonts/cardo.zip
	unzip -D -o "$<" "$(notdir $@)"
	mv -f "$(notdir $@)" "$@"

%.ttf: fonts/cardo.zip
	unzip -D -o "$<" "$(notdir $@)"

web-demo/fonts/%.woff: %.ttf
	mkdir -p web-demo/fonts
	fontforge -lang ff -script fonts/subset-greek.ff "$<" "$@"

.PHONY: clean
clean:
	rm -f $(WORKS_CSV) $(WORKS_HTML)

.DELETE_ON_ERROR:
