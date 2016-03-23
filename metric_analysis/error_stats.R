library(effsize)

wilcoxon_test <- function(df1, df2, obj, metric) {
	print(toupper(metric))
	vector1 <- as.vector(t(df1[metric]))
	vector2 <- as.vector(t(df2[metric]))
	cat('Median value:\n')
	cat(sprintf('    %s commits: %.1f\n', obj, median(vector1)))
	cat(sprintf('    other commits: %.1f\n', median(vector2)))
	print(wilcox.test(vector1, vector2, alternative = "two.sided", correct=FALSE))
#	print(cliff.delta(vector1, vector2))
}

comparison <- function(metrics, compared_key) {
	df.sub1 <- df[df[ ,compared_key]=='True',]
	df.sub2 <- df[df[ ,compared_key]=='False',]
	for (m in metrics){
		wilcoxon_test(df.sub1, df.sub2, sub('_', ' ', compared_key), m)
	}
}

# Files' entropy and changed types' entropy
df.crashed.types.entropy <- as.data.frame(read.csv(file='../code_metrics/changed_types/crashed_changed_entropy.csv'), header=TRUE)
df.crashfree.types.entropy <- as.data.frame(read.csv(file='../code_metrics/changed_types/crashfree_changed_entropy.csv'), header=TRUE)
df.types.entropy <- rbind(df.crashed.types.entropy, df.crashfree.types.entropy) 
df.crashed.file.entropy <- as.data.frame(read.csv(file='../file_entropy_analysis/crashed_file_entropy.csv'), header=TRUE)
df.crashfree.file.entropy <- as.data.frame(read.csv(file='../file_entropy_analysis/crashfree_file_entropy.csv'), header=TRUE)
df.file.entropy <- rbind(df.crashed.file.entropy, df.crashfree.file.entropy)
df.entropy <- merge(df.types.entropy, df.file.entropy, by='revision')

# Read data from the csv file
df.basic <- as.data.frame(read.csv(file=sprintf('../results/metric_table.csv')), header=TRUE)
df.code <- as.data.frame(read.csv(file=sprintf('../code_metrics/code_metrics.csv')), header=TRUE)
df.before_crashed <- as.data.frame(read.csv(file='../code_metrics/before_crashed_file_rate.csv'), header=TRUE)
df.basic_and_code <- merge(df.basic, df.code, by='revision')
df1 <- merge(df.basic_and_code, df.before_crashed, by='revision')
df.pred <- merge(df1, df.entropy, by='revision')
# Load false positives
df.fp <- as.data.frame(read.csv(file='prediction_errors/error_table.csv'), header=TRUE)
df <- merge(df.pred, df.fp, by='revision')


metrics = c('experience', 'message_size', 'closeness', 'changed_file', 'loc', 'insertion', 'deletion', 'file_entropy', 'unique_types', 'entropy')
comparison(metrics, 'false_positive')

comparison(metrics, 'false_negative')

