library(ggplot2)
library(scales)
library(tools)

args <- commandArgs(trailingOnly=TRUE)
dat_filename <- args[[1]]
title_text <- args[[2]]
x <- read.table(dat_filename, col.names=c("count", "frac", "l1", "l2"))

p <- ggplot(x, aes(l1, l2, fill=count/sum(count)))
p <- p + geom_tile()
p <- p + scale_fill_gradient(low="white", high="steelblue", name="fraction", labels=percent, limits=c(0, 0.04))
p <- p + labs(title=title_text)
p <- p + theme(aspect.ratio=1)
ggsave(paste(file_path_sans_ext(dat_filename), ".png", sep=""), p, width=6, height=5, dpi=90)
