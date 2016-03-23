wilcoxon_test <- function(df.crash_inducing, df.crash_free, metric) {
	print(toupper(metric))
	metric.crash_inducing <- df.crash_inducing[metric]
	metric.crash_free <- df.crash_free[metric]
	vector.crash_inducing <- as.vector(t(metric.crash_inducing))
	vector.crash_free <- as.vector(t(metric.crash_free))
	print('Median value:')
	print(sprintf('    Crash-inducing fixes: %f', median(vector.crash_inducing)))
	print(sprintf('    Crash-free fixes: %f', median(vector.crash_free)))
	print('Mean value:')
	print(sprintf('    Crash-inducing fixes: %f', mean(vector.crash_inducing)))
	print(sprintf('    Crash-free fixes: %f', mean(vector.crash_free)))
	wilcox.test(vector.crash_inducing, vector.crash_free, alternative = 'two.sided', correct=FALSE)
}



df.crash_inducing <- read.csv('crashed_file_entropy.csv', header=TRUE)
df.crash_free <- read.csv('crashfree_file_entropy.csv', header=TRUE)

wilcoxon_test(df.crash_inducing, df.crash_free, 'file_entropy')

df.highimpact <- read.csv('highimpact_file_entropy.csv', header=TRUE)
df.other <- read.csv('not_highimpact_file_entropy.csv', header=TRUE)
df.lessimpact <- read.csv('lessimpact_file_entropy.csv', header=TRUE)

wilcoxon_test(df.highimpact, df.other, 'file_entropy')
wilcoxon_test(df.highimpact, df.lessimpact, 'file_entropy')


