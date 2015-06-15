library(cvTools)
library(ROSE)

# Set random seed
set.seed(99)

# Initialise variables
model = 'randomForest'
doVIF = 'NO'
tree_number = 100

# Changed types' entropy
df.crashed.types.entropy <- as.data.frame(read.csv(file='../code_metrics/changed_types/crashed_changed_entropy.csv'), header=TRUE)
df.crashfree.types.entropy <- as.data.frame(read.csv(file='../code_metrics/changed_types/crashfree_changed_entropy.csv'), header=TRUE)
df.entropy <- rbind(df.crashed.types.entropy, df.crashfree.types.entropy) 

# Read data from the csv file
df.basic <- as.data.frame(read.csv(file=sprintf('../results/metric_table.csv')), header=TRUE)
df.code <- as.data.frame(read.csv(file=sprintf('../code_metrics/code_metrics.csv')), header=TRUE)
df.before_crashed <- as.data.frame(read.csv(file='../code_metrics/before_crashed_file_rate.csv'), header=TRUE)
df.basic_and_code <- merge(df.basic, df.code, by='revision')
df1 <- merge(df.basic_and_code, df.before_crashed, by='revision')
df <- merge(df1, df.entropy, by='revision')

# Define modelling formula
xcol <- c('experience', 'mozilla_committer', 'supplementary', 'message_size', 'month_day', 'week_day', 'month', 
		'hour', 'changed_file', 
		'loc', 'cyclomatic', 'func_num', 'ratio_comments', 
		'page_rank', 'betweenness', 'closeness','indegree', 'outdegree', 
		'before_crashed_files', 'unique_types', 'entropy', 'is_bug_fix') 
		#'year_day', 'max_nesting' are removed after VIF analysis
formula <- as.formula(paste('crash_inducing ~ ', paste(xcol, collapse= '+')))

#	VIF analysis
if(doVIF == 'YES') {
	library(car)
	formula <- as.formula(paste('crash_inducing ~ ', paste(xcol, collapse= '+')))
	fit <- glm(formula, data = df, family = binomial())
	print(vif(fit))
}

# Separate data into k folds
k <- 10
folds <- cvFolds(nrow(df), K = k, type = 'random')

# Initialise result values
acc.vec = pre.vec = rec.vec = fm.vec = npre.vec = nrec.vec = nfm.vec <- c()

#	Iteratively run validation
for(i in 1:k) {
	print(sprintf('Validation no. %d', i))
	#	Split training and testing data
	trainIndex <- folds$subsets[folds$which != i]	# Extract training index
	testIndex <- folds$subsets[folds$which == i]	# Extract testing index			
	trainset <- df[trainIndex, ] 		# Set the training set
  	testset <- df[testIndex, ] 			# Set the validation set
	#	Balance crash-inducing and crash-free data in the training set
	train.balanced <- ovun.sample(crash_inducing~., data=trainset, p=0.5, seed=1, method='under')$data
		
  	if(model == 'C50') {
		library(C50)
		fit <- C5.0(formula, data = train.balanced, rules = TRUE)
	  	testset[, 'predict'] <- predict(fit, newdata = testset, type = 'class')
		#print(C5imp(fit))
	} else if(model == 'randomForest') {
		library(randomForest)		
		fit <- randomForest(formula, data = train.balanced, ntree = tree_number, mtry = 5, importance = TRUE)
	  	testset[, 'predict'] <- predict(fit, newdata = testset)
		#varImpPlot(fit, cex = 1, main = '')
	} else if(model == 'bayes') {
		library(e1071)
		fit <- naiveBayes(formula, data = train.balanced)
		testset[, 'predict'] <- predict(fit, newdata = testset)
	} else if(model == 'glm') {
		fit <- glm(formula, data = train.balanced, family = 'binomial')
		testset[, 'predict'] <- predict(fit, newdata = testset)
	}
	t <- table(observed = testset[, 'crash_inducing'], predicted = testset[, 'predict'])
	
	actualYES <- testset[testset['crash_inducing'] == 'YES', ]
	actualNO <- testset[testset['crash_inducing'] == 'NO', ]
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
}

print(sprintf('accuracy: %.1f%%', median(acc.vec) * 100))
print(sprintf('crash-inducing pre: %.1f%%', median(pre.vec) * 100))
print(sprintf('crash-inducing rec: %.1f%%', median(rec.vec) * 100))
print(sprintf('crash-inducing f-measure: %.1f%%', median(fm.vec) * 100))
print(sprintf('crash-free pre: %.1f%%', median(npre.vec) * 100))
print(sprintf('crash-free rec: %.1f%%', median(nrec.vec) * 100))
print(sprintf('crash-free f-measure: %.1f%%', median(nfm.vec) * 100))

