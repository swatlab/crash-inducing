wilcoxon_test <- function(df.crash_inducing, df.crash_free, metric) {
	print(toupper(metric))
	metric.crash_inducing <- df.crash_inducing[metric]
	metric.crash_free <- df.crash_free[metric]
	vector.crash_inducing <- as.vector(t(metric.crash_inducing))
	vector.crash_free <- as.vector(t(metric.crash_free))
	print('Median value:')
	print(sprintf('    Crash-inducing fixes: %f', median(vector.crash_inducing)))
	print(sprintf('    Crash-free fixes: %f', median(vector.crash_free)))
	wilcox.test(vector.crash_inducing, vector.crash_free, alternative = "two.sided", correct=FALSE)
}

df <- read.csv(sprintf('../results/metric_table.csv'), header = TRUE)
df.crash_inducing <- df[df[,'crash_inducing']=='YES',]
df.crash_free <- df[df[,'crash_inducing']=='NO',]

wilcoxon_test(df.crash_inducing, df.crash_free, 'experience')
wilcoxon_test(df.crash_inducing, df.crash_free, 'message_size')
wilcoxon_test(df.crash_inducing, df.crash_free, 'changed_file')
wilcoxon_test(df.crash_inducing, df.crash_free, 'insertion')
wilcoxon_test(df.crash_inducing, df.crash_free, 'deletion')



