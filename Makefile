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

EXPECTANCY_FILES = expectancy.all.csv expectancy.hellenistic+archaic.csv
WORKS_CSV = $(addprefix corpus/,$(addsuffix .csv,$(WORKS)))
WORKS_HTML = $(addprefix sedes-web/,$(addsuffix .html,$(WORKS)))

.PHONY: all
all: $(EXPECTANCY_FILES) $(WORKS_HTML)

$(EXPECTANCY_FILES): .EXTRA_PREREQS = src/expectancy
expectancy.all.csv: $(WORKS_CSV)
	src/expectancy $^ > "$@"
expectancy.hellenistic+archaic.csv: corpus/iliad.csv corpus/odyssey.csv corpus/homerichymns.csv corpus/theogony.csv corpus/worksanddays.csv corpus/shield.csv corpus/argonautica.csv corpus/theocritus.csv corpus/callimachushymns.csv corpus/aratus.csv
	src/expectancy $^ > "$@"

$(WORKS_CSV): .EXTRA_PREREQS = src/tei2csv src/known.py src/lemma.py src/appositive.py src/lemma-overrides.csv src/exceptional-appositives.csv
corpus/%.csv: corpus/%.xml
	src/tei2csv --word-unit=appositive-group "$(WORK_IDENTIFIER_$*)" "$<" > "$@"

$(WORKS_HTML): .EXTRA_PREREQS = src/tei2html src/known.py src/lemma.py src/appositive.py src/lemma-overrides.csv src/exceptional-appositives.csv
sedes-web/%.html: corpus/%.xml expectancy.all.csv
	src/tei2html --word-unit=appositive-group "$(WORK_IDENTIFIER_$*)" $^ > "$@"

PYTHON = python3

.PHONY: test
test:
	(cd src && "$(PYTHON)" -m unittest)

.PHONY: fonts
fonts: \
	sedes-web/fonts/SIL\ Open\ Font\ License.txt \
	sedes-web/fonts/Cardo-Regular.woff \
	sedes-web/fonts/Cardo-Italic.woff

sedes-web/fonts/SIL\ Open\ Font\ License.txt: fonts/SIL\ Open\ Font\ License.txt
	cp -f "$^" "$@"

.INTERMEDIATE: Cardo99s.ttf Cardoi99.ttf
Cardo99s.ttf: fonts/cardo99.zip
Cardoi99.ttf: fonts/cardoita.zip
Cardo99s.ttf Cardoi99.ttf:
	unzip -D -o "$<" "$@"

sedes-web/fonts/Cardo-Regular.woff: Cardo99s.ttf
sedes-web/fonts/Cardo-Italic.woff: Cardoi99.ttf

sedes-web/fonts/Cardo-Regular.woff sedes-web/fonts/Cardo-Italic.woff:
	mkdir -p sedes-web/fonts
	fontforge -lang ff -script fonts/subset-greek.ff "$<" "$@"

.PHONY: clean
clean:
	rm -f $(WORKS_CSV) $(WORKS_HTML)

.DELETE_ON_ERROR:
