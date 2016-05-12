library(ggplot2)
library(scales)

pos_sort_key <- function(pos) {
	parts <- strsplit(as.character(pos), "/")
	# Map "?" to a high number.
	parts <- lapply(parts, function(x) {as.numeric(ifelse(x=="?", 100, x))})
	# Prepend number of matches.
	lapply(parts, function(x) {c(length(x), x)})
}

x <- read.table("n1.out", sep="\t", quote="",
	col.names=c("work", "ref", "pos", "form", "text"),
	colClasses=c(work="factor", ref="character", pos="factor", form="character", text="character"))
x <- x[!grepl("/", x$pos), ]
x <- droplevels(x)
x$pos <- factor(x$pos, levels=levels(x$pos)[order(as.numeric(levels(x$pos)))])

p <- ggplot(x, aes(pos, group=work))
p <- p + geom_bar(aes(y=..prop..))
p <- p + scale_y_continuous(labels=percent)
p <- p + facet_grid(work ~ .)
ggsave("ἐν.png", p, dpi=120)
