WORKS = \
	homerichymns \
 	iliad \
 	odyssey \
 	shield \
 	theogony \
 	worksanddays \

WORKS_CSV = $(addprefix corpus/,$(addsuffix .csv,$(WORKS)))

all.csv: $(WORKS_CSV)
	(sed -n -e '1p' "$<"; for x in $^; do sed -e '1d' $$x; done) > "$@"

corpus/argonautica.csv:  WORK_IDENTIFIER = Argon.
corpus/callimachushymns.csv: WORK_IDENTIFIER = Callim. Hymn
corpus/homerichymns.csv: WORK_IDENTIFIER = Hymns
corpus/iliad.csv:        WORK_IDENTIFIER = Il.
corpus/odyssey.csv:      WORK_IDENTIFIER = Od.
corpus/shield.csv:       WORK_IDENTIFIER = Shield
corpus/theogony.csv:     WORK_IDENTIFIER = Theog.
corpus/worksanddays.csv: WORK_IDENTIFIER = WD
%.csv: %.xml
	src/tei2csv "$(WORK_IDENTIFIER)" "$<" > "$@"
.INTERMEDIATE: $(WORKS_CSV)

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

.DELETE_ON_ERROR:
