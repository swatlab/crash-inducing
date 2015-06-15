from __future__ import division
import csv, sys
from datetime import datetime, timedelta
import pandas as pd

def changedDate(metric_table):
    print 'Loading commit date ...'
    df = pd.read_csv(metric_table)
    df_date = df[['revision', 'date']]
    return (df_date.set_index('revision').to_dict()['date'], df)

def loadCrashFixesFiles(crash_fixes_filename, rev_date_dict):
    print 'Loading crashed files ...'
    #   Map crash fixing revision to changed files
    crash_fix_file_dict = dict()
    csvreader = csv.reader(open(crash_fixes_filename, 'rb'), delimiter='\t')
    for line in csvreader:
        rev = int(line[0])
        del_cpp = line[1].split(' ')
        mod_cpp = line[2].split(' ')
        add_cpp = line[3].split(' ')
        changed_files = set(mod_cpp + add_cpp + del_cpp) - set([''])
        crash_fix_file_dict[rev] = changed_files
    #   Map crash fixing revision to committed date
    rev_date_list = list()    
    for rev in crash_fix_file_dict:
        if rev in rev_date_dict:
            rev_date = pd.to_datetime(rev_date_dict[rev])
            rev_date_list.append([rev_date, rev])
    df_rev_date = pd.DataFrame(rev_date_list, columns = ['date', 'revision']).sort(['date'], ascending=False)
    fix_date_list = df_rev_date[['date','revision']].values.tolist()  
    return fix_date_list

def buildCommitFileDict(filename, fix_file_dict):
    csvreader = csv.reader(open(filename, 'rb'), delimiter='\t')
    for line in csvreader:
        rev = int(line[0])
        mod_cpp = line[1].split(' ')
        add_cpp = line[2].split(' ')
        del_cpp = line[3].split(' ')
        changed_files = set(mod_cpp + add_cpp + del_cpp) - set(['']) 
        fix_file_dict[rev] = changed_files
    return fix_file_dict

def MapCommitToFiles(crash_free_files, crashed_files):
    print 'Loading crash-free files ...'
    fix_file_dict = dict()
    fix_file_dict = buildCommitFileDict(crash_free_files, fix_file_dict)
    fix_file_dict = buildCommitFileDict(crashed_files, fix_file_dict)
    return fix_file_dict

def beforeCrashedPercentage(rev_date_dict, all_fix_file_dict, fix_date_list):
    print "Computing before crashed files' percentage ..."
    bfr_crash_pct_list = list()
    for rev in rev_date_dict:
        changed_files = all_fix_file_dict[rev]
        commit_date = pd.to_datetime(rev_date_dict[rev])
        six_month_ago = commit_date - timedelta(days=30*6)
        start_idx, end_idx = -1, -1
        i = 0
        for i in range(0, len(fix_date_list)):
            (fix_date, fix_num) = fix_date_list[i]
            if commit_date > fix_date:
                end_idx = i
                break
        i = 0
        for i in range(0, len(fix_date_list)):
            (fix_date, fix_num) = fix_date_list[i]
            if six_month_ago > fix_date:
                start_idx = i
                break
        if len(changed_files) > 0:
            if end_idx >= 0:
                if start_idx < 0:
                    start_idx = len(fix_date_list) - 1
                if start_idx == end_idx:
                    early_crashed_rev = fix_date_list[start_idx][1]
                    early_crashed_files = all_fix_file_dict[early_crashed_rev]
                    intersect_files = early_crashed_files & changed_files
                else:
                    early_crashed_rev = set()
                    early_crashed_files = set()
                    for i in range(end_idx, start_idx+1):
                        early_crashed_rev.add(fix_date_list[i][1])
                    for r in early_crashed_rev:
                        early_crashed_files |= all_fix_file_dict[r]
                    intersect_files = early_crashed_files & changed_files            
                early_crashed_rate = round(len(intersect_files) / len(changed_files), 3)
            else:
                early_crashed_rate = 0.0
        else:
            early_crashed_rate = 0.0
        print rev, '\t', early_crashed_rate
        bfr_crash_pct_list.append([rev, early_crashed_rate])
    pd.DataFrame(bfr_crash_pct_list, columns=['revision', 'before_crashed_files']).to_csv('before_crashed_file_rate.csv', index=False)
    return

if(__name__ == '__main__'):
    csv.field_size_limit(sys.maxsize)
    (rev_date_dict, df_metrics) = changedDate('../results/firefox/metric_table.csv')
    fix_date_list = loadCrashFixesFiles('../bash_data/firefox/changed_files.csv', rev_date_dict)
    all_fix_file_dict = MapCommitToFiles('../file_metrics/crash_free_files/crash_free_cpp.csv', '../file_metrics/crashed_cpp.csv')
    df_before_crashed = beforeCrashedPercentage(rev_date_dict, all_fix_file_dict, fix_date_list)