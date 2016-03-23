import json
import pandas as pd

import collections

def mapBuggyCommits2Bugs(filename):
    commit2bug_dict = dict()
    with open(filename, 'r') as f:
        json_dict = json.load(f)
        for bug_id in json_dict:
            commit_list = json_dict[bug_id]
            for commit_id in commit_list:
                if commit_id in commit2bug_dict:
                    commit2bug_dict[commit_id].add(bug_id)
                else:
                    commit2bug_dict[commit_id] = set([bug_id])
    return commit2bug_dict

def hasHighImpact(row, median_entropy,median_frequency):
    if row['entropy'] >= median_entropy and row['frequency'] >= median_frequency:
        return True
    return False

def loadCrashRelatedBugs(filename):
    df = pd.read_csv(filename)
    median_entropy = df['entropy'].median()
    median_frequency = df['frequency'].median()
    df['high_impact'] = df.apply(hasHighImpact, axis=1, args=(median_entropy,median_frequency,))
    return set(df[df['high_impact'] == True].bug)

def loadAllCommits(filename):
    df = pd.read_csv(filename)
    return list(df['revision'])

def commitImpact(commit2bug_dict, high_impact_bugs, all_commits):
    commit_impact_list = list()
    for commit_int in all_commits:
        commit_id = str(commit_int)
        if commit_id in commit2bug_dict:
            bug_set = commit2bug_dict[commit_id]
            high_impact = 'NO'
            for bug_id in bug_set:
                if int(bug_id) in high_impact_bugs:
                    high_impact = 'YES'
                    break
            commit_impact_list.append([commit_id, high_impact])
        else:
            commit_impact_list.append([commit_id, 'NO'])
    df = pd.DataFrame(commit_impact_list, columns=['revision', 'high_impact'])    
    df.to_csv('results/crashed_commit_impact.csv', index=False)
    return

if __name__ == '__main__':
    commit2bug_dict = mapBuggyCommits2Bugs('results/bug_to_crash-inducing-commits.json')    
    high_impact_bugs = loadCrashRelatedBugs('raw_data/basic_info.csv')
    all_commits = loadAllCommits('results/metric_table.csv')
    commitImpact(commit2bug_dict, high_impact_bugs, all_commits)
    print 'Done.'
    