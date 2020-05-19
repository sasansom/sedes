# Adds "x", "z", and "z.alt" columns to a CSV file produced by tei2csv.
# Write the augmented CSV to standard output.

library(data.table)
library(ggplot2)

data <- data.table()
for (csv_filename in commandArgs(trailingOnly=TRUE)) {
	data <- rbind(data, fread(csv_filename, na.strings=c("")))
}

# Infer unknown lemmata.
data[is.na(lemma), lemma := word]

data[, x := .N, by = .(lemma, sedes)]
data[, z := (x - mean(x)) / sd(x), by = .(lemma)]
data[, z.alt := (x - .N/sum(!duplicated(sedes))) / sd(x[!duplicated(sedes)]), by = .(lemma)]

write.csv(data, "", row.names=FALSE)
