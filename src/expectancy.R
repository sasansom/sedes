# Computes an expectancy score for each unique lemma/sedes pair in the input
# files, as produced by tei2csv.
#
# Usage:
#   Rscript expectancy.R *.csv
#
# Writes CSV to standard output. Besides lemma and sedes, there are three
# columns:
#   x: The number of times this lemma/sedes pair appears
#   z: The expectancy score, weighted as if each x value were repeated x times.
#   z.alt: The unweighted expectancy score, where each x value is counted only
#          once. The unweighted score is no longer used for anything.

library(data.table)

# Population standard deviation.
sd_pop <- function(x) {
	sd(x) * sqrt((length(x) - 1) / length(x))
}

data <- data.table()
for (csv_filename in commandArgs(trailingOnly=TRUE)) {
	data <- rbind(data, fread(csv_filename, na.strings=c("")))
}

# Infer unknown lemmata.
data[is.na(lemma), lemma := word]

data <- data[, .(x = .N), by = .(lemma, sedes)]
data[, z := (x - mean(rep(x, x))) / sd_pop(rep(x, x)), by = .(lemma)]
data[, z.alt := (x - mean(x)) / sd_pop(x), by = .(lemma)]

setkey(data, "lemma", "sedes")
write.csv(data, "", row.names=FALSE)
