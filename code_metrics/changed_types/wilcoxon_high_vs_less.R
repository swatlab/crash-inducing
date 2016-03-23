wilcoxon_test <- function(df.high_impact, df.other, metric) {
	print(toupper(metric))
	metric.high_impact <- df.high_impact[metric]
	metric.other <- df.other[metric]
	vector.high_impact <- as.vector(t(metric.high_impact))
	vector.other <- as.vector(t(metric.other))
	print('Median value:')
	print(sprintf('    High-impact commits: %f', median(vector.high_impact)))
	print(sprintf('    Other commits: %f', median(vector.other)))
	print('Mean value:')
	print(sprintf('    High-impact commits: %f', mean(vector.high_impact)))
	print(sprintf('    Other commits: %f', mean(vector.other)))
	wilcox.test(vector.high_impact, vector.other, alternative = 'two.sided', correct=FALSE)
}

df.crashed <- read.csv('crashed_changed_entropy.csv', header=TRUE)
df.impact <- read.csv('../../results/crashed_commit_impact.csv', header = TRUE)
df <- merge(df.crashed, df.impact, by='revision', all.x=TRUE)
df.highimpact <- df[df[,'high_impact']=='YES',]
df.other <- df[df[,'high_impact']=='NO',]

wilcoxon_test(df.highimpact, df.other, 'unique_types')
wilcoxon_test(df.highimpact, df.other, 'entropy')

