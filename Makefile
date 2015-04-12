%.txt: %.xml
	./tei2txt "$<" > "$@"
