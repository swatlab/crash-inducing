from __future__ import division
import json, os, csv
import pandas as pd

###PLEASE DOWNLOAD BUG REPORT FROM JAN 2012 TO DEC 2013 AND SET THE BUG REPORT FOLDER###

# Map crash-related bugs to the commits that introduced them
def mapBugs2CrashInducingCommit(filename):
    with open(filename, 'r') as f:
        crash_inducing_dict = json.load(f)
    return crash_inducing_dict
    
# Map bugs to commits
def mapBug2Commits(filename):
    print 'Mapping bugs to commits ...'
    bug_commit_mapping = dict()
    with open(filename, 'r') as f:
        csvreader = csv.reader(f)
        next(csvreader, None)
        for line in csvreader:
            commit_id = line[1]
            bug_opening_date = None
            bugs = line[2].split('^')
            for bug_id in bugs:
                if bug_id in bug_commit_mapping:
                    bug_commit_mapping[bug_id].add(commit_id)
                else:
                    bug_commit_mapping[bug_id] = set([commit_id])
    return bug_commit_mapping

# Load bug opening date
def bugReopening(bug_id):
    ###PLEASE SET THE BUG REPORT FOLDER###
    if os.path.exists('../bugs/history/%s.json' %bug_id):
        with open('../bugs/history/%s.json' %bug_id, 'r') as jf:
            bug_dict = json.load(jf)
            for change in bug_dict['bugs'][0]['history']:
                for activity in change['changes']:
                    if 'reopened' == activity['added'].lower():
                        return True
    return False

def countSupplementaryBugFixes(crashed_bugs, bug_commit_mapping):
    print 'Analysing supplementary bug fixes ...'
    multiple_fixed_bug_set = set()
    for bug_id in bug_commit_mapping:
        if len(bug_commit_mapping[bug_id]) > 1:
            multiple_fixed_bug_set.add(bug_id)
    multiple_fixed_crashed_bugs = multiple_fixed_bug_set & crashed_bugs
    other_multiple_fixed_bugs = multiple_fixed_bug_set - crashed_bugs
    other_bugs = set(bug_commit_mapping.keys()) - crashed_bugs
    print '\tCrash-related bugs that require supplementary fixes: %.1f%%' %(len(multiple_fixed_crashed_bugs)/len(crashed_bugs)*100)
    print '\tOther bugs that require supplementary fixes: %.1f%%' %(len(other_multiple_fixed_bugs)/len(other_bugs)*100)
    return

def countReopeningPercentage(crashed_bugs, bug_commit_mapping):
    print 'Analysing bug reopening ...'
    # count reopened bugs from the studied bug dataset
    reopened_bugs = set()
    i = 0
    for bug_id in bug_commit_mapping:
        if DEBUG:
            i += 1
            if i > 5000:
                break
        if bugReopening(bug_id):
            reopened_bugs.add(bug_id)
    # count reopened bugs from crashed-related bugs
    crashed_reopened_bugs = set()
    for bug_id in crashed_bugs:
        if bug_id in reopened_bugs:
            crashed_reopened_bugs.add(bug_id)
    other_bug_set = set(bug_commit_mapping.keys()) - crashed_bugs
    other_reopened_bugs = reopened_bugs - crashed_reopened_bugs
    
    print len(other_reopened_bugs), len(other_bug_set)
    
    print 'Reopening percentage of crash-related bugs: %.1f%%' %(len(crashed_reopened_bugs) / len(crashed_bugs) *100)
    print 'Reopening percentage of other bugs: %.1f%%' %(len(other_reopened_bugs) / len(other_bug_set) *100)
    return

if __name__ == '__main__':
    DEBUG = False
    crash_inducing_dict = mapBugs2CrashInducingCommit('../results/bug_to_crash-inducing-commits.json')
    bug_commit_mapping = mapBug2Commits('../metric_analysis/prediction_errors/bug_fixing_commits.csv')
    df_bugs = pd.read_csv('../raw_data/basic_info.csv')
    df_bugs['bug'] = df_bugs['bug'].astype(str)
    entropy_median = df_bugs['entropy'].median()
    frequency_median = df_bugs['frequency'].median()
    high_impact_bugs = set(df_bugs[(df_bugs.entropy >= entropy_median) & (df_bugs.frequency >= frequency_median)]['bug'])
    # compute and output results
    print '  Crash-inducing commits vs. crash-free commits'
    countSupplementaryBugFixes(set(crash_inducing_dict.keys()), bug_commit_mapping)
    countReopeningPercentage(set(crash_inducing_dict.keys()), bug_commit_mapping)    
    print '  Highly-impactful crash-inducing commits vs. other commits'
    countSupplementaryBugFixes(high_impact_bugs, bug_commit_mapping)
    countReopeningPercentage(high_impact_bugs, bug_commit_mapping)