library(cvTools)
library(ROSE)

# Set random seed
# PLEASE SET A SEED NUMBER HERE
set.seed(0)

# Initialise variables
model = 'glm'
doVIF = 'NO'
tree_number = 100

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
df <- merge(df1, df.entropy, by='revision')
# Whether a commit will induce highly-impactful bugs
df.highimpact <- as.data.frame(read.csv(file=sprintf('../results/crashed_commit_impact.csv')), header=TRUE)
df <- merge(df, df.highimpact, by='revision')

nrow(df[df['high_impact'] == 'YES', ])
nrow(df)


# Define modelling formula
xcol <- c('experience', 'mozilla_committer', 'supplementary', 'message_size', 'month_day', 'week_day', 'month', 
		'hour', 'changed_file', 'file_entropy',
		'loc', 'cyclomatic', 'func_num', 'ratio_comments', 
		'page_rank', 'betweenness', 'closeness','indegree', 'outdegree', 
		'before_crashed_files', 'unique_types', 'entropy', 'is_bug_fix') 
		#'year_day', 'max_nesting' are removed after VIF analysis
		#'meridiem', 'time_zone' are considered as trivial metrics
formula <- as.formula(paste('high_impact ~ ', paste(xcol, collapse= '+')))

#	VIF analysis
if(doVIF == 'YES') {
	library(car)
	formula <- as.formula(paste('high_impact ~ ', paste(xcol, collapse= '+')))
	fit <- glm(formula, data = df, family = binomial())
	print(vif(fit))
}

# Separate data into k folds
k <- 10
folds <- cvFolds(nrow(df), K = k, type = 'random')

# Initialise result values
#tp.sum = tn.sum = fp.sum = fn.sum <- 0
acc.vec = pre.vec = rec.vec = fm.vec = npre.vec = nrec.vec = nfm.vec <- c()
false.positives <- matrix(nrow=k, ncol=2, dimnames=list(c(),c('round', 'false_positive')))
false.negatives <- matrix(nrow=k, ncol=2, dimnames=list(c(),c('round', 'false_negatives')))

#	Iteratively run validation
for(i in 1:k) {
	print(sprintf('Validation no. %d', i))
	#	Split training and testing data
	trainIndex <- folds$subsets[folds$which != i]	# Extract training index
	testIndex <- folds$subsets[folds$which == i]	# Extract testing index			
	trainset <- df[trainIndex, ] 		# Set the training set
  	testset <- df[testIndex, ] 			# Set the validation set
	#	Balance crash-inducing and crash-free data in the training set
	train.balanced <- ovun.sample(high_impact~., data=trainset, p=0.3, seed=1, method='under')$data
	#train.balanced = trainset
		
  	if(model == 'C50') {
		library(C50)
		fit <- C5.0(formula, data = train.balanced, rules = TRUE)
	  	testset[, 'predict'] <- predict(fit, newdata = testset, type = 'class')
		#print(C5imp(fit))
	} else if(model == 'randomForest') {
		library(randomForest)		
		fit <- randomForest(formula, data = train.balanced, ntree = tree_number, mtry = 5, importance = TRUE)
	  	testset[, 'predict'] <- predict(fit, newdata = testset)
		varImpPlot(fit, cex = 1, main = '')
	} else if(model == 'cforest') {
		library(party)
		data.controls <- cforest_unbiased(ntree = tree_number, mtry = 5)
		fit <- cforest(formula, data = train.balanced, controls = data.controls)
		testset[, 'predict'] <- predict(fit, newdata = testset)
	} else if(model == 'ctree') {
		library(party)
		data.controls <- ctree_control(maxsurrogate = 3)
		fit <- ctree(formula, data = train.balanced)
		testset[, 'predict'] <- predict(fit, newdata = testset)
	} else if(model == 'bayes') {
		library(e1071)
		fit <- naiveBayes(formula, data = train.balanced)
		testset[, 'predict'] <- predict(fit, newdata = testset)
	} else if(model == 'glm') {
		fit <- glm(formula, data = train.balanced, family = 'binomial')
		testset[, 'predict'] <- predict(fit, newdata = testset)
	}
	t <- table(observed = testset[, 'high_impact'], predicted = testset[, 'predict'])
	
	actualYES <- testset[testset['high_impact'] == 'YES', ]
	actualNO <- testset[testset['high_impact'] == 'NO', ]
	if(model == 'glm'){
		threshold = 0.5
		tp <- nrow(actualYES[actualYES[,'predict'] > threshold,])
		tn <- nrow(actualNO[actualNO[, 'predict'] <= threshold,])
		fp <- nrow(actualNO[actualNO[, 'predict'] > threshold,])
		fn <-  nrow(actualYES[actualYES[,'predict'] <= threshold,])
	} else {
		tp <- nrow(actualYES[actualYES[,'predict'] == 'YES',])
		tn <- nrow(actualNO[actualNO[, 'predict'] == 'NO',])
		fp <- nrow(actualNO[actualNO[, 'predict'] == 'YES',])
		fn <- nrow(actualYES[actualYES[,'predict'] == 'NO',])
	}
	
	pre <- tp/(tp+fp)
	rec <- tp/(tp+fn)
	npre <- tn/(tn+fn)
	nrec <- tn/(tn+fp)
	acc.vec <- c(acc.vec, (tn+tp)/(tn+fp+fn+tp))
	pre.vec <- c(pre.vec, pre)
	rec.vec <- c(rec.vec, rec)
	fm.vec <- c(fm.vec, 2*pre*rec/(pre+rec))
	npre.vec <- c(npre.vec, npre)
	nrec.vec <- c(nrec.vec, nrec)
	nfm.vec <- c(nfm.vec, 2*npre*nrec/(npre+nrec))
	
	print(pre)
	print(rec)
	
	# extract false positives 
	fp.revision = actualNO[actualNO[, 'predict'] == 'YES',]$revision
	fp.str = paste(as.character(fp.revision), collapse = ' ')
	false.positives[i,] = c(i, fp.str)
	# extract false negatives
	fn.revision = actualYES[actualYES[,'predict'] == 'NO',]$revision
	fn.str = paste(as.character(fn.revision), collapse = ' ')
	false.negatives[i,] = c(i, fn.str)
}

print(sprintf('accuracy: %.1f%%', median(acc.vec) * 100))
print(sprintf('crash-inducing pre: %.1f%%', median(pre.vec) * 100))
print(sprintf('crash-inducing rec: %.1f%%', median(rec.vec) * 100))
print(sprintf('crash-inducing f-measure: %.1f%%', median(fm.vec) * 100))
print(sprintf('crash-free pre: %.1f%%', median(npre.vec) * 100))
print(sprintf('crash-free rec: %.1f%%', median(nrec.vec) * 100))
print(sprintf('crash-free f-measure: %.1f%%', median(nfm.vec) * 100))

# output false positives and false negatives in the prediction
#write.table(false.positives, 'prediction_errors/highly_impactful_fpfn/false_positives.csv', row.names = FALSE, col.names=TRUE, sep = ',')
#write.table(false.negatives, 'prediction_errors/highly_impactful_fpfn/false_negatives.csv', row.names = FALSE, col.names=TRUE, sep = ',')
