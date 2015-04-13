%.txt: %.xml
	./tei2txt "$<" > "$@"

%-1gram.dat %-2gram.dat %-initial2gram.dat %-word2gram.dat: corpus/%.txt
	./ngrams --base "$*" "$<"

corpus-1gram.dat corpus-2gram.dat corpus-initial2gram.dat corpus-word2gram.dat: corpus/*.txt
	./ngrams --base corpus $^
