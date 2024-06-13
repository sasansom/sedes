# Usage:
#   Rscript linetype.r corpus-appositive/shield.csv > shield-linetype.csv
#   Rscript linetype.r corpus-appositive/*.csv > corpus-linetype.csv
#
# Collapses a SEDES corpus CSV file to one row per line and adds the columns:
# - line_metrical_shape
# - line_type_metrical_shape
# - line_type_caesurae
# - caesurae_schematic
#
# line_metrical_shape is the concatenation of the metrical_shape of each of the
# words in the line, in order.
#
# line_type_metrical_shape summarizes the line_metrical_shape as an integer
# from 0 to 31. A dactyl becomes a 0 bit and a spondee becomes a 1 bit, with
# feet to the left being more significant. The final foot, which is always a
# spondee, is not counted. So, for example, the line_metrical_shape
# –––––⏑⏑–⏑⏑–––– becomes the line_type_metrical_shape 25 (11001 in binary).
#
# line_type_caesurae summarizes where caesurae appear in the line, as an
# integer. There are, at most, 16 sedes in a line where a caesura may appear.
# Where there is a caesura, we record a 1 bit; and where there is not, we
# record a 0 bit, according to the bit positions shown below:
#      | – | ⏑ | ⏑ | – | ⏑ | ⏑ | – | ⏑ | ⏑ | – | ⏑ | ⏑ | – | ⏑ | ⏑ | – | – |
#          ^   ^   ^   ^   ^   ^   ^   ^   ^   ^   ^   ^   ^   ^   ^   ^
# sedes    2  2.5  3   4  4.5  5   6  6.5  7   8  8.5  9  10 10.5 11  12
# bitpos  15  14  13  12  11  10   9   8   7   6   5   4   3   2   1   0
# So, for example, a line whose pattern of caesurae is
#   –⏑|⏑|–––|⏑⏑|–⏑⏑|–|⏑⏑––
# (caesurae at sedes 2.5, 3, 6, 7, 9, and 10) would have line_type_caesurae
# 25240 (0110001010011000 in binary).
#
# caesurae_schematic is a visual representation of line_type_caesurae, with an
# empty space at sedes where there is no caesura, and a "|" character where
# there is a caesura. Note that, in order to represent every possible position
# where a caesura may appear in any line, the prototypical line metrical shape
# used for caesurae_schematic consists of all dactyls (except for the final
# spondee). It does *not* reflect the line_metrical_shape of the line. The
# caesurae_schematic for the example pattern of caesurae shown above would be
#   – ⏑|⏑|– ⏑ ⏑ –|⏑ ⏑|– ⏑ ⏑|–|⏑ ⏑ – –

library("bitops")
library("tidyverse")

line_metrical_shape_to_type <- function(line_metrical_shape) {
	type <- 0
	i <- rep(1, length(line_metrical_shape))
	# First 5 feet may be dactyl (0) or spondee (1).
	for (foot in 1:5) {
		m <- str_extract(str_sub(line_metrical_shape, i), "^(–⏑⏑|––)")
		type <- type*2 + case_when(
			m == "–⏑⏑" ~ 0,
			m == "––"  ~ 1,
		)
		i <- i + str_length(m)
	}
	# Final foot must be spondee (doesn't contribute to type number)
	type <- type + case_when(
		str_sub(line_metrical_shape, i) == "––" ~ 0,
	)
	type
}

text <- bind_rows(lapply(
	commandArgs(trailingOnly = TRUE),
	read_csv,
	na = character(),
	col_types = cols_only(
		work = col_factor(),
		book_n = col_character(),
		line_n = col_character(),
		word_n = col_integer(),
		sedes = col_double(),
		metrical_shape = col_character(),
		line_text = col_character(),
	),
)) |>
	mutate(unique_line_n = cumsum(
		replace_na(line_n, "") != replace_na(coalesce(lag(line_n), line_n), "") |
		word_n <= coalesce(lag(word_n), word_n)
	))

line_text <- text |>
	group_by(work, book_n, unique_line_n) |>
	summarize(
		line_n = first(line_n),
		line_text = first(line_text),
		.groups = "drop",
	) |>
	ungroup()

line_type_metrical_shape <- text |>
	group_by(work, book_n, unique_line_n) |>
	arrange(word_n) |>
	summarize(
		line_n = first(line_n),
		line_metrical_shape = str_flatten(metrical_shape),
		.groups = "drop",
	) |>
	ungroup() |>
	mutate(line_type_metrical_shape = line_metrical_shape_to_type(line_metrical_shape))

line_type_caesurae <- text |>
	group_by(work, book_n, unique_line_n) |>
	arrange(sedes, word_n) |>
	summarize(
		line_n = first(line_n),
		line_type_caesurae = sedes |>
			# Collapse adjacent caesurae with identical sedes.
			unique() %>%
			# Remove the pseudo "caesura" at the start of line.
			(function (sedes) sedes[sedes != 1]) %>%
			# Map each caesura position to a bit position.
			(function (sedes) 2^case_when(
				sedes ==  2   ~ 15,
				sedes ==  2.5 ~ 14,
				sedes ==  3   ~ 13,
				sedes ==  4   ~ 12,
				sedes ==  4.5 ~ 11,
				sedes ==  5   ~ 10,
				sedes ==  6   ~ 9,
				sedes ==  6.5 ~ 8,
				sedes ==  7   ~ 7,
				sedes ==  8   ~ 6,
				sedes ==  8.5 ~ 5,
				sedes ==  9   ~ 4,
				sedes == 10   ~ 3,
				sedes == 10.5 ~ 2,
				sedes == 11   ~ 1,
				sedes == 12   ~ 0,
			)) |>
			# Sum into a line subtype.
			sum(),
		.groups = "drop",
	) |>
	ungroup() |>
	mutate(
		caesurae_schematic = sprintf(
			# Interleave caesurae/non-caesurae markers with a prototypical metrical shape.
			"–%s⏑%s⏑%s–%s⏑%s⏑%s–%s⏑%s⏑%s–%s⏑%s⏑%s–%s⏑%s⏑%s–%s–",
			# Convert line_type_caesurae into a sequence of blanks and pipes according to binary representation.
			ifelse(bitAnd(line_type_caesurae, 2^15) == 0, " ", "|"),
			ifelse(bitAnd(line_type_caesurae, 2^14) == 0, " ", "|"),
			ifelse(bitAnd(line_type_caesurae, 2^13) == 0, " ", "|"),
			ifelse(bitAnd(line_type_caesurae, 2^12) == 0, " ", "|"),
			ifelse(bitAnd(line_type_caesurae, 2^11) == 0, " ", "|"),
			ifelse(bitAnd(line_type_caesurae, 2^10) == 0, " ", "|"),
			ifelse(bitAnd(line_type_caesurae, 2^9 ) == 0, " ", "|"),
			ifelse(bitAnd(line_type_caesurae, 2^8 ) == 0, " ", "|"),
			ifelse(bitAnd(line_type_caesurae, 2^7 ) == 0, " ", "|"),
			ifelse(bitAnd(line_type_caesurae, 2^6 ) == 0, " ", "|"),
			ifelse(bitAnd(line_type_caesurae, 2^5 ) == 0, " ", "|"),
			ifelse(bitAnd(line_type_caesurae, 2^4 ) == 0, " ", "|"),
			ifelse(bitAnd(line_type_caesurae, 2^3 ) == 0, " ", "|"),
			ifelse(bitAnd(line_type_caesurae, 2^2 ) == 0, " ", "|"),
			ifelse(bitAnd(line_type_caesurae, 2^1 ) == 0, " ", "|"),
			ifelse(bitAnd(line_type_caesurae, 2^0 ) == 0, " ", "|")
		),
	)

by <- c("work", "book_n", "line_n", "unique_line_n")
write_csv(
	line_type_metrical_shape |>
		left_join(line_type_caesurae, by = by) |>
		left_join(line_text, by = by) |>
		select(!unique_line_n),
	stdout(),
	na = "",
)
