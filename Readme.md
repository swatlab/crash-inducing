#An Empirical Study of Crash-inducing Commits in Mozilla Firefox

#Requirements
- Python 2.7 or newer
- R 3.1 or newer
- MySQL

#File description
- **revision_analysis.py**: parses commit logs to identify bug fixes of the studied crash-realted bugs. It will generate *fix_numbers.txt* in the folder **results**.
- **file_analysis.py**: links each of the crash-related bug fixes to its corresponding fixing files. It outputs *rev_file.csv* to the folder **results**.
- **extract_comments.py**: extracts files or methods from the crashed stack trace of each bug. It outputs *bug_location.csv* to the folder **results**.
- **crash_inducing_fix.py**: identifies crash-inducing commits, and output *crash_inducing_commits.txt* and *bug_to_crash_inducing_commit.json* to the folder **results**.
- **crash_inducing_analysis.py**: analyses characteristics of crash-inducing commits, and extracts metrics for prediciton models. It outputs *metric_table.csv* to the folder **results**.
- **raw_data** folder: contains data on crash-related bug IDs and their crashed dates generated by the scripts in: https://github.com/swatlab/highly-impactful.
- **bash_data** folder: contains data generated by bash scripts.
- **results** folder: contains data generated by the above scripts.
- **extract_bug_reports** folder: contains scripts to download bug reports, which are not available in the Bugzilla SQL database.
- **metric_analysis** folder: contains the scripts to analyse the characteristics of crash-inducing commits (hypothesis tests) and to predict these commits.
	- **percentage_comparison.py** and **wilcoxon_test.R** compare several characteristics between crash-inducing commits and crash-free commits.
	- **prediction.R** predicts crash-inducing commits.
- **code_metrics** folder: contains scripts and data to compute code complexity and SNA metrics. Some scripts are based on the data in: https://github.com/swatlab/highly-impactful.
- **file_metrics** folder: contains scripts and data to link crash-inducing/crash-free commits to their corresponding files. These data could be used for changd type analysis. 
	- **separate_into_parts.py** separates a bug table into small parts in order to enhance the analysis speed.
- **diff_analysis** folder: contains scripts and data to analyse changed types of commits.
	- **analytic_code** folder only contains a sample of the analysed source code. For the full data, please download from:
	http://swat.polymtl.ca/anle/data/Crash-inducing-commits/
	- **diff_analysis.py** recursively identifies changed types in files.
	- **rename_source.py** renames studied file names to the right format.

#How to use the script
- To identify crash-inducing commits:
	1. Run **revision_analysis.py** to identify crash-realted bug fixes.
	2. Then use *results/fix_numbers.txt* and run the following bash script to extract changed files of each crash-related bug fixes. Put the result *changed_files.csv* in the folder **bash_data**.
	```bash
	cat $"fix_numbers.txt" | while read rev_num; do hg log --template "{rev}\t{file_dels}\t{file_mods}\t{file_adds}\n" -r $rev_num; done > changed_files.csv
	```
	3. Run **file_analysis.py** to map crash-related bug fixes to their files.
	4. Then use *rev_file.csv* and run the following bash script to output annotated files of each file in the crash-related fixes. Put the folder **annotated_files** in the folder **bash_data**.
	```bash
	export IFS=","
	cat "rev_file.csv" | while read rev file ref; do echo $ref $file; hg annotate $file -r $rev -w -b -B > annotated_files/$ref.txt; done
	```
	5. Run **extract_commits.py** to generate locations of crash-related bugs.
	6. Then run **crash_inducing_fix.py** to identify crash-inducing commits.
- To analyse crash-inducing commits:
	- Run **crash_inducing_analysis.py** to output metrics for the Wilcoxon test and prediction.
	- Please set your database's host, user and password in line 9 of **extract_comments.py**.
	- In **prediction.R**, please set the prediction algorithm: GLM, bayes, C50, or randomForest (in line 8), and set whether need a VIF analysis (in line 9).
	- Before using the scripts in **code_metrics**, you should refer to https://github.com/swatlab/highly-impactful to generate code complexity and SNA data (the generated data on Firefox are also available in this repository).
   
#Data source
- Mozilla Bugzilla local database is available in:
    http://swat.polymtl.ca/anle/data/Mozilla_bugs/
- Socorro local crash reports are available in:
    https://crash-analysis.mozilla.com
- Firefox' Mercurial repository:
	https://developer.mozilla.org/en-US/docs/Mozilla/Developer_guide/Source_Code/Mercurial

#Reference
<p id="refone">[1] Le An and Foutse Khomh. An Empirical Study of Highly-impactful Bugs in Mozilla Projects. In
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<i>Proceedings of the 2015 IEEE International Conference on Software Quality, Reliability and 
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Security (QRS)</i>.</p>

#For any questions
Please send email to le.an@polymtl.ca
