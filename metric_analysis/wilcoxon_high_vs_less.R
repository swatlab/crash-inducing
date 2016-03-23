library(effsize)

wilcoxon_test <- function(df.high_impact, df.other, metric) {
	print(toupper(metric))
	metric.high_impact <- df.high_impact[metric]
	metric.other <- df.other[metric]
	vector.high_impact <- as.vector(t(metric.high_impact))
	vector.other <- as.vector(t(metric.other))
	print('Median value:')
	print(sprintf('    High-impact commits: %f', median(vector.high_impact)))
	print(sprintf('    Less-impact commits: %f', median(vector.other)))
	print('Mean value:')
	print(sprintf('    High-impact commits: %f', mean(vector.high_impact)))
	print(sprintf('    Less-impact commits: %f', mean(vector.other)))
	wilcox.test(vector.high_impact, vector.other, alternative = "two.sided", correct=FALSE)
}

df <- read.csv('../results/metric_table.csv', header = TRUE)
df.highimpact <- read.csv('../results/crashed_commit_impact.csv', header = TRUE)
df <- merge(df, df.highimpact, by='revision')
df.crashed <- df[df[,'crash_inducing']=='YES',]

df.high_impact <- df.crashed[df.crashed[,'high_impact']=='YES',]
df.other <- df.crashed[df.crashed[,'high_impact']=='NO',]

wilcoxon_test(df.high_impact, df.other, 'experience')
wilcoxon_test(df.high_impact, df.other, 'message_size')
wilcoxon_test(df.high_impact, df.other, 'changed_file')
wilcoxon_test(df.high_impact, df.other, 'insertion')
wilcoxon_test(df.high_impact, df.other, 'deletion')



