from __future__ import division
import json, os, csv
from collections import Counter
import pandas as pd

###PLEASE DOWNLOAD BUG REPORT FROM JAN 2012 TO DEC 2013 AND SET THE BUG REPORT FOLDER###

# Map crash-related bugs to the commits that introduced them
def mapBugs2CrashInducingCommit(filename):
    with open(filename, 'r') as f:
        crash_inducing_dict = json.load(f)
    return crash_inducing_dict

# Map bugs to commits
def mapBug2Commits(filename):
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

def bugResolution(crash_related_bugs):
    resolution_list = list()
    ###PLEASE SET THE BUG REPORT FOLDER###
    for bug_id in crash_related_bugs:
        if os.path.exists('../bugs/report/%s.json' %bug_id):
            with open('../bugs/report/%s.json' %bug_id, 'r') as jf:
                bug_dict = json.load(jf)
                resolution_list.append(bug_dict['bugs'][0]['resolution'])
    print Counter(resolution_list)
    print 'Total:', len(resolution_list)
    return

if __name__ == '__main__':
    # load bug IDs
    crash_inducing_dict = mapBugs2CrashInducingCommit('bug_to_crash-inducing-commits.json')
    bug_commit_mapping = mapBug2Commits('../metric_analysis/prediction_errors/bug_fixing_commits.csv')
    other_bugs = set(bug_commit_mapping.keys()) - set(crash_inducing_dict.keys())
    # load highly-impactful bug IDs
    df_bugs = pd.read_csv('../raw_data/basic_info.csv')
    df_bugs['bug'] = df_bugs['bug'].astype(str)
    entropy_median = df_bugs['entropy'].median()
    frequency_median = df_bugs['frequency'].median()
    high_impact_bugs = set(df_bugs[(df_bugs.entropy >= entropy_median) & (df_bugs.frequency >= frequency_median)]['bug'])
    # proportional analyses
    bugResolution(high_impact_bugs)
#    bugResolution(crash_inducing_dict)
#    bugResolution(other_bugs)