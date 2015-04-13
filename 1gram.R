library(ggplot2)
library(scales)
library(tools)

args <- commandArgs(trailingOnly=TRUE)
dat_filename <- args[[1]]
title_text <- args[[2]]
x <- read.table(dat_filename, col.names=c("count", "frac", "letter"))

p <- ggplot(x, aes(letter, count/sum(count)))
p <- p + geom_bar(stat="identity")
p <- p + scale_y_continuous(labels=percent)
p <- p + labs(title=title_text, y="fraction")
ggsave(paste(file_path_sans_ext(dat_filename), ".png", sep=""), p, width=5, height=3, dpi=90)
