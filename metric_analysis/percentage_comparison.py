from __future__ import division
import pandas as pd
from stop_words import get_stop_words

#   Mozilla committers' percentage
def mozillaCommitterProportion(df):
    mozilla_committer = df[df['mozilla_committer'] == 'YES']
    print len(mozilla_committer) / len(df)
    return
 
#   Incomplete commits' percentage  
def incompleteProportion(df):
    supplementary_fixes = df[df['attempt_type'] == 'incomplete']
    print len(supplementary_fixes) / len(df)
    return

#   Supplementary commits' percentage
def supplementaryProportion(df):
    supplementary_fixes = df[df['attempt_type'] == 'supplementary']
    print len(supplementary_fixes) / len(df)
    return
    
#   Commits' percentage to fix a bug
def bugFixProportion(df):
    bug_fixes = df[df['is_bug_fix'] == 'YES']
    print len(bug_fixes) / len(df)
    return

if(__name__ == '__main__'):
    #   Load metrics
    df_commits = pd.read_csv('../results/metric_table.csv')
    df_crash_inducing = df_commits[df_commits['crash_inducing'] == 'YES']
    df_crash_free = df_commits[df_commits['crash_inducing'] == 'NO']
    
    #   Split data for crash-inducing / crash-free commits 
    df_crash_inducing = df_commits[df_commits['crash_inducing'] == 'YES']
    df_crash_free = df_commits[df_commits['crash_inducing'] == 'NO']
    #   Compare the proportion of mozilla developers' commits 
    print "Mozilla developers' proportion on crash-inducing commits"
    mozillaCommitterProportion(df_crash_inducing)
    print "Mozilla developers' proportion on crash-free commits"
    mozillaCommitterProportion(df_crash_free)
    #   Compare the proportion of incomplete bug fixes
    print 'The proportion of incomplete fixes on crash-inducing commits'
    incompleteProportion(df_crash_inducing)
    print "The proportion of incomplete fixes on crash-free commits"
    incompleteProportion(df_crash_free)
    #   Compare the proportion of supplementary bug fixes
    print 'The proportion of supplementary fixes on crash-inducing commits'
    supplementaryProportion(df_crash_inducing)
    print "The proportion of supplementary fixes on crash-free commits"
    supplementaryProportion(df_crash_free)
    #   Compare the proportion of bug fixes
    print 'The proportion of bug fixes on crash-inducing commits'
    bugFixProportion(df_crash_inducing)
    print "The proportion of bug fixes on crash-free commits"
    bugFixProportion(df_crash_free)
    