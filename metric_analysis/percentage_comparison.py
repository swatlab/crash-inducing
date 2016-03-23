from __future__ import division
import pandas as pd
from stop_words import get_stop_words

#   Mozilla committers' percentage
def mozillaCommitterProportion(df):
    mozilla_committer = df[df['mozilla_committer'] == 'YES']
    print len(mozilla_committer) / len(df)
    return
 
    
#   Commits' percentage to fix a bug
def bugFixProportion(df):
    bug_fixes = df[df['is_bug_fix'] == 'YES']
    print len(bug_fixes) / len(df)
    return

if(__name__ == '__main__'):
    high_impact = True
    #   Load metrics
    if high_impact:
        df_commits = pd.read_csv('../results/metric_table.csv')
        df_highimpact = pd.read_csv('../results/crashed_commit_impact.csv')
        df_combined = pd.merge(df_commits, df_highimpact, on='revision')
        df_target = df_combined[df_combined['high_impact'] == 'YES']
        df_other = df_combined[df_combined['high_impact'] == 'NO']
    else:
        df_commits = pd.read_csv('../results/metric_table.csv')
        df_target = df_commits[df_commits['crash_inducing'] == 'YES']
        df_other = df_commits[df_commits['crash_inducing'] == 'NO']
    #   Split data for crash-inducing / crash-free commits 
    df_target = df_commits[df_commits['crash_inducing'] == 'YES']
    df_other = df_commits[df_commits['crash_inducing'] == 'NO']
    #   Compare the proportion of mozilla developers' commits 
    print "Mozilla developers' proportion on crash-inducing commits"
    mozillaCommitterProportion(df_target)
    print "Mozilla developers' proportion on crash-free commits"
    mozillaCommitterProportion(df_other)
    #   Compare the proportion of bug fixes
    print 'The proportion of bug fixes on crash-inducing commits'
    bugFixProportion(df_target)
    print "The proportion of bug fixes on crash-free commits"
    bugFixProportion(df_other)
    