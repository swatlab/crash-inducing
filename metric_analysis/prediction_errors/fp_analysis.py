from __future__ import division
import pandas as pd

def loadBugInducingCommits(filename):
    bug_inducing_commits = set()
    with open(filename, 'r') as f:
        reader = f.read().split('\n')
        for line in reader:
            if len(line):
                bug_inducing_commits.add(int(line))
    return bug_inducing_commits

if __name__ == '__main__':
    bug_inducing_commits = loadBugInducingCommits('bug_inducing_commits.txt')
    df = pd.read_csv('error_table.csv')
    fp_list = list(df[df['false_positive'] == True]['revision'])
    buggy_fp_cnt = 0
    for commit_id in fp_list:
        if commit_id in bug_inducing_commits:
            buggy_fp_cnt += 1
    print buggy_fp_cnt, len(fp_list)
    print 'FP commits that introduced bugs: %.1f%%' %(buggy_fp_cnt / len(fp_list) * 100)