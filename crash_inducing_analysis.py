from __future__ import division
import csv, json, re
import pandas as pd
from stop_words import get_stop_words

#   Load all commit logs (including author, date, and message) of Firefox until March 2015
def loadCommitLogs(filename):
    print 'Loading all commit logs from Mozilla VCS ...'
    commit_list = list()    
    with open(filename, 'rb') as f:
        lines = f.read().split('\n')
    for line in lines:
        if re.search(r'^[0-9]+\:[0-9a-z]{12}\t', line):
            elem_list = line.split('\t')
            rev_num = int(elem_list[0].split(':')[0])
            author = elem_list[1]
            date = elem_list[2]
            message = '\t'.join(elem_list[3:])
            if elem_list[2][:-6] < '2013-01-01 00:00:00':    #   The studied crash reports are from Jan 2012 to Dec 2012
                commit_list.append([rev_num, author, date, message])
    df = pd.DataFrame(commit_list, columns=['revision', 'author', 'date', 'message'])
    #print df
    return (commit_list, df)

#   Load crash-inducing commits
def loadCrashInducingRevNum(filename):
    with open(filename) as f:
        reader = f.read().strip()
    return set(map(int, reader.split('\n')))

#   Compute authors' committed experience and extract their email extension
def authorAnalysis(df):
    print "Computing authors' experience and identify whehter they are from mozilla ..."
    author_dict = dict()
    exp_list = list()
    from_mozilla = list()
    for this_author in df_commits.sort(['date'], ascending=False)['author'].values:
        pre_occur = author_dict.get(this_author, 0)
        author_dict[this_author] = pre_occur + 1
        exp_list.append(pre_occur + 1)
        is_mozilla_committer = 'NO'
        if '@' in this_author:
            if 'mozilla' in this_author.split('@')[1]:
                is_mozilla_committer = 'YES'
        from_mozilla.append(is_mozilla_committer)
    df['experience'] = exp_list[::-1]
    df['mozilla_committer'] = from_mozilla[::-1]
    return df

#   Identify the commits that fix the same bugs
def identifySupplementaryFixes(filename, df):
    print 'Classifying commit type by attempt times ...'
    rev_date_dict = df_commits[['revision', 'date']].set_index('revision').to_dict()['date']
    incomplete_set = set()
    supplementary_set = set()
    with open(filename) as f:    
        bug_dict = json.load(f)       
    for bugID in bug_dict:
        rev_set = set(bug_dict[bugID])
        if len(rev_set) > 1:
            fix_group = list()
            num_group = set()
            for rev_num in rev_set:
                if rev_num in rev_date_dict:
                    commit_date = rev_date_dict[rev_num]
                    fix_group.append((commit_date, rev_num))
                    num_group.add(rev_num)
            if len(fix_group):
                incomplete_rev = min(fix_group)[1]
                num_group.discard(incomplete_rev)
                incomplete_set.add(incomplete_rev)
                supplementary_set |= num_group
                #print incomplete_rev, num_group
    return (bug_dict, incomplete_set, supplementary_set)

#   Classify fixes as sole, incomplete, or supplementary
def classifyFixesByAttempt(df, incomplete_set, supplementary_set):
    attempt_type_list = list()
    supplementary_list = list()
    for rev_num in df['revision'].values:
        if rev_num in incomplete_set:
            attempt_type_list.append('incomplete')
            supplementary_list.append('NO')
        elif rev_num in supplementary_set:
            attempt_type_list.append('supplementary')
            supplementary_list.append('YES')
        else:
            attempt_type_list.append('sole')
            supplementary_list.append('NO')
    df['attempt_type'] = attempt_type_list
    df['supplementary'] = supplementary_list
    return df

def isBugFix(df, bug_dict):
    print 'Check whether a commit is to fix a bug ...'
    is_bug_fix_list = list()
    bug_fix_revs = set()
    for bugID in bug_dict:
        rev_set = set(bug_dict[bugID])
        bug_fix_revs |= rev_set
    for rev_num in df['revision'].values: 
        if rev_num in bug_fix_revs:
            is_bug_fix_list.append('YES')
        else:
            is_bug_fix_list.append('NO')
    df['is_bug_fix'] = is_bug_fix_list
    return df

#   Compute words in messages
def messageSize(df):
    print 'Computing message size ...'
    msg_size_list = list()
    for msg in df['message'].values:
        word_cnt = len(re.findall(r'(\S+)', msg))
        msg_size_list.append(word_cnt)
    df['message_size'] = msg_size_list
    return df

#   Extract time metrics
def timeMetrics(df):
    print 'Extracting time metrics ...'
    time_metric_list = list()
    for date_str in df['date'].values:
        date = pd.to_datetime(date_str[:-6], format='%Y-%m-%d %H:%M:%S')
        year_day = date.strftime('%j')
        month_day = date.strftime('%d')
        week_day = date.strftime('%a')
        month = date.strftime('%b')
        hour = date.strftime('%H')
        meridiem = date.strftime('%p')
        time_zone = date_str[-5:]
        time_metric_list.append([year_day, month_day, week_day, month, hour, meridiem, time_zone, date])
    df_time = pd.DataFrame(time_metric_list, columns=['year_day', 'month_day', 'week_day', 'month', 'hour', 'meridiem', 'time_zone', 'date'])
    return pd.concat([df, df_time], axis=1)

#   Load and merge churn metrics
def churnMetrics(df):
    series_rev = df['revision']
    pd_churn = pd.read_csv('results/churn_table.csv')
    pd_churn_studied = pd_churn[pd_churn['revision'].isin(series_rev)]
    return pd.merge(df, pd_churn_studied, on='revision')

#   Identify whether a commit will introduce crashes
def isCrashInducing(df, crash_inducing_rev):
    print 'Identify crash inducing commits ...'
    crash_inducing_list = list()
    for rev_num in df['revision'].values:
        if rev_num in crash_inducing_rev:
            crash_inducing_list.append('YES')
        else:
            crash_inducing_list.append('NO')
    df['crash_inducing'] = crash_inducing_list
    return df

#   Output metrics into a csv file
def outputData(df_commits):
    print 'Writing results to a csv file ...'
    s_rev = df_commits['revision']
    df_metrics = df_commits.loc[ : , 'experience':'crash_inducing']
    df_output = pd.concat([s_rev, df_metrics], axis=1)
    #print df_output
    df_output.to_csv('results/metric_table.csv', index=False)
    return

#   Find top words in the committed messages
def wordFrequency(message_list, stop_words, filename):
    word_base = list()
    for msg in message_list:
        word_list = re.findall(r'[a-zA-Z]{2,}', msg)
        l = list()
        for w in word_list:
            if w.lower() not in stop_words:
                word_base.append(w.lower())
    series_words = pd.Series(word_base)
    top_words = series_words.value_counts().head(100)
    top_words.to_csv('results/' + filename + '.csv')
    return

if(__name__ == '__main__'):
    #   Loading data
    (commit_list, df_commits) = loadCommitLogs('bash_data/commit_log.txt')
    crash_inducing_rev = loadCrashInducingRevNum('results/crash_inducing_commits.txt')
            
    #   Authors' experience and email extension
    df_commits = authorAnalysis(df_commits)    
    #   Fix attempt types: sole, incomplete, or supplementary
    (bug_dict, incomplete_set, supplementary_set) = identifySupplementaryFixes('results/all_fixes.json', df_commits)
    df_commits = classifyFixesByAttempt(df_commits, incomplete_set, supplementary_set)
    #   Is bug fix?
    df_commits = isBugFix(df_commits, bug_dict)
    #   Message size
    df_commits = messageSize(df_commits)
    #   Time metrics
    df_commits = timeMetrics(df_commits)
    #   Churn metrics
    df_commits = churnMetrics(df_commits)
    #   Is a commit crash-inducing?
    df_commits = isCrashInducing(df_commits, crash_inducing_rev)
    #   Output data to a csv file
    outputData(df_commits)
    
    print 'Output top words for crash-inducing and crash free commits ...'
    df_crash_inducing = df_commits[df_commits['crash_inducing'] == 'YES']
    df_crash_free = df_commits[df_commits['crash_inducing'] == 'NO']
    stop_words = get_stop_words('english') + ['bug']
    wordFrequency(df_crash_inducing['message'].values, stop_words, 'crash_inducing_words')
    wordFrequency(df_crash_inducing['message'].values, stop_words, 'crash_free_words')
    
    print 'Done.'
    