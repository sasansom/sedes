# Usage: Rscript src/tables.R corpus/*.csv
#
# Display tables of raw counts of καί/καὶ and ἀοιδ*, as in the Spring 2019
# draft of "Where Words Belong: Sedes as Style in Greek Hexameter Poetry" by
# Stephen Sansom.


data <- data.frame()
for (csv_filename in commandArgs(trailingOnly=TRUE)) {
	data <- rbind(data, read.csv(csv_filename, colClasses=c(
		work="character",
		book_n="character",
		line_n="character",
		word_n="integer",
		word="character",
		lemma="character",
		sedes="numeric",
		metrical_shape="character",
		scanned="character",
		num_scansions="integer"
	)))
}
data$work <- factor(
	data$work,
	levels=c("Il.", "Od.", "Hom.Hymn", "Theog.", "W.D.", "Sh."),
	labels=c("Il.", "Od.", "Hy.", "Th.", "WD", "Sh.")
)
data$sedes <- factor(
	data$sedes,
	levels=c("1", "2", "2.5", "3", "4", "4.5", "5", "6", "6.5", "7", "8", "8.5", "9", "10", "10.5", "11", "12")
)

cat("\n")
cat("raw count of sedes of ἀοιδ* in corpus\n")
data_aoidh <- data[substr(data$word, 1, 5) == "ἀοιδ", ]
data_aoidh$sedes <- droplevels(data_aoidh$sedes)
addmargins(table(data_aoidh[, c("sedes", "work")], useNA="always"))

cat("\n")
cat("all occurrences of ἀοιδ* in corpus\n")
data_aoidh

cat("\n")
cat("raw count of sedes of καί/καὶ in corpus\n")
data_kai <- data[data$word %in% c("καί", "καὶ"), ]
addmargins(table(data_kai[, c("sedes", "work")], useNA="always"))
