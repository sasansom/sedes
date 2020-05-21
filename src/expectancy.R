# Adds "x", "z", and "z.alt" columns to a CSV file produced by tei2csv.
# Write the augmented CSV to standard output.

library(data.table)
library(ggplot2)

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

data[, x := .N, by = .(lemma, sedes)]
data[, z := (x - mean(x)) / sd_pop(x), by = .(lemma)]
data[, z.alt := (x - .N/sum(!duplicated(sedes))) / sd_pop(x[!duplicated(sedes)]), by = .(lemma)]

write.csv(data, "", row.names=FALSE)
