library(data.table)
library(ggplot2)

is.archaic.or.hellenistic <- function(work) {
	work %in% c(
		"Il.",
		"Od.",
		"Hom.Hymn",
		"Theog.",
		"W.D.",
		"Sh.",
		"Argon.",
		"Theoc.",
		"Callim.Hymn",
		"Phaen."
	)
}

data <- fread("all.csv", na.strings=c(""))
data[, work := factor(work, levels=unique(c(
	"Il.",
	"Od.",
	"Hom.Hymn",
	"Theog.",
	"W.D.",
	"Sh.",
	"Argon.",
	"Theoc.",
	"Callim.Hymn",
	"Phaen."
), levels(work)))]
# Infer unknown lemmata.
data[is.na(lemma), lemma := word]

# Archaic & Hellenistic only.
data <- data[is.archaic.or.hellenistic(work)]

# TODO
# data[is.na(sedes)]

# table(data$sedes)
# ggplot(data, aes(sedes)) + geom_bar()

cat("raw count of sedes of ἀοιδή (lemma) in corpus\n")
table(data[lemma == "a)oidh/", .(sedes, work)])
table(data[lemma == "a)oidh/", .(work)])

cat("\n")

data[, x := .N, by = .(lemma, sedes)]
data[, z := (x - mean(x)) / sd(x), by = .(lemma)]
data[, z.alt := (x - .N/sum(!duplicated(sedes))) / sd(x[!duplicated(sedes)]), by = .(lemma)]

# data[work == "Od." & lemma == "a)oidh/"]
selection <- data[work == "Od."][book_n == 1][!is.na(as.integer(line_n))][as.integer(line_n) >= 345 & as.integer(line_n) <= 359]
write.csv(selection, "selection.csv", row.names=FALSE)
