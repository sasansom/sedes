# Usage: Rscript src/tables.R all.csv
#
# Display tables of raw counts of καί/καὶ and ἀοιδ*, as in the Spring 2019
# draft of "Where Words Belong: Sedes as Style in Greek Hexameter Poetry" by
# Stephen Sansom.


args <- commandArgs(trailingOnly=TRUE)
if (length(args) != 1) {
	stop("Need an input CSV filename.")
}
input_filename <- args[[1]]

data <- read.csv(input_filename, colClasses=c(
	work="character",
	book_n="character",
	line_n="character",
	word_n="integer",
	word="character",
	num_scansions="integer",
	sedes="character"
))
data$work <- factor(
	data$work,
	levels=c("Il.", "Od.", "Hymns", "Theog.", "WD", "Shield"),
	labels=c("Il.", "Od.", "Hy.", "Th.", "WD", "Sh.")
)
data[data$sedes == "", ]$sedes <- NA
data$sedes <- factor(
	data$sedes,
	levels=c("1", "1.5", "2", "3", "3.5", "4", "5", "5.5", "6", "7", "7.5", "8", "9", "9.5", "10", "11", "12")
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
