wilcoxon_test <- function(df.crash_inducing, df.crash_free, metric) {
	print(toupper(metric))
	metric.crash_inducing <- df.crash_inducing[metric]
	metric.crash_free <- df.crash_free[metric]
	vector.crash_inducing <- as.vector(t(metric.crash_inducing))
	vector.crash_free <- as.vector(t(metric.crash_free))
	print('Median value:')
	print(sprintf('    Crash-inducing fixes: %f', median(vector.crash_inducing)))
	print(sprintf('    Crash-free fixes: %f', median(vector.crash_free)))
	wilcox.test(vector.crash_inducing, vector.crash_free, alternative = 'two.sided', correct=FALSE)
}

df.crash_inducing <- read.csv('crashed_changed_types.csv', header=TRUE)
df.crash_free <- read.csv('crashfree_changed_types.csv', header=TRUE)

head(df.crash_inducing)
#head(df.crash_free)

wilcoxon_test(df.crash_inducing, df.crash_free, 'call')
wilcoxon_test(df.crash_inducing, df.crash_free, 'comment')
wilcoxon_test(df.crash_inducing, df.crash_free, 'refactoring')
wilcoxon_test(df.crash_inducing, df.crash_free, 'init')
wilcoxon_test(df.crash_inducing, df.crash_free, 'type')
wilcoxon_test(df.crash_inducing, df.crash_free, 'preprocessor')
wilcoxon_test(df.crash_inducing, df.crash_free, 'parameter')
wilcoxon_test(df.crash_inducing, df.crash_free, 'flow_control_stmt')
wilcoxon_test(df.crash_inducing, df.crash_free, 'access')
wilcoxon_test(df.crash_inducing, df.crash_free, 'cpp_feature')
wilcoxon_test(df.crash_inducing, df.crash_free, 'data_type')
wilcoxon_test(df.crash_inducing, df.crash_free, 'declaration')
#wilcoxon_test(df.crash_inducing, df.crash_free, 'code')
wilcoxon_test(df.crash_inducing, df.crash_free, 'constructor')
wilcoxon_test(df.crash_inducing, df.crash_free, 'destructor')
wilcoxon_test(df.crash_inducing, df.crash_free, 'class')
wilcoxon_test(df.crash_inducing, df.crash_free, 'function.')

df.entropy.crash_inducing <- read.csv('crashed_changed_entropy.csv', header=TRUE)
df.entropy.crash_free <- read.csv('crashfree_changed_entropy.csv', header=TRUE)

wilcoxon_test(df.entropy.crash_inducing, df.entropy.crash_free, 'unique_types')
wilcoxon_test(df.entropy.crash_inducing, df.entropy.crash_free, 'entropy')

