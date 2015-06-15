import csv, re, json
import pandas as pd

#   Load all commit logs (including author, date, and message) of Firefox until March 2015
def loadCommitLogs(filename):
    print 'Loading all commit logs from Mozilla VCS ...'
    log_list = list()
    with open(filename, 'rb') as f:
        lines = f.read().split('\n')
    current_rev = -1
    for line in lines:
        if re.search(r'^[0-9]+\:[0-9a-z]{12}\t', line):
            if current_rev >= 0:
                log_list.append([current_rev, rev_hash, author, date, current_message])
            elem_list = line.split('\t')
            current_rev = int(elem_list[0].split(':')[0])
            rev_hash = elem_list[0].split(':')[1]
            author = elem_list[1]
            date = elem_list[2]
            current_message = '\t'.join(elem_list[3:])
        else:
            current_message = current_message + '\n' + line
    df = pd.DataFrame(log_list, columns=['revision', 'hash', 'author', 'date', 'message'])
    #print df
    return df
    
#   Identify bug fixes for each crash-related bug
def identifyCrashRelatedBugFixes(df):
    print 'Identifying bug fixes for each crash-related bug ...'
    bug_list = pd.read_table('raw_data/basic_info.csv', sep=',')['bug'].values
    mapping_list = list()    
    for rev_num, commit_message in df[['revision', 'message']].values:
        number_list = re.findall(r'[1-9][0-9]+', commit_message)
        #   the fixes of each bug
        for a_number in number_list:
            bug_num = int(a_number)
            if bug_num in bug_list:                
                mapping_list.append((bug_num, rev_num))
    return mapping_list

#   Rematch backed out bug fixes
def backoutFixes(backout_list, rev_dict, bug_dict):
    print 'Rematching backed out bug fixes ...'
    for rev_num, msg in backout_list:
        results = re.findall(r'\b[a-z0-9]{12}\b', msg)
        for aHash in results:
            if aHash in rev_dict:
                bug_set = rev_dict[aHash]
                for bugID in bug_set:
                    bug_dict[bugID].add(rev_num)
    return bug_dict

#   Identify bug fixes for each crash-related bug
def identifyAllBugFixes(df):
    print 'Identifying all bug fixes in the history ...'
    bug_dict = dict()
    rev_dict = dict()
    backout_list = list()    
    for rev_num, rev_hash, commit_message in df[['revision', 'hash', 'message']].values:
        number_list = re.findall(r'(?:bug|bugzilla|b=|bg|issue|id=|#)[s\s\-#=]*([1-9][0-9]+)', commit_message, re.IGNORECASE)
        number_list += re.findall(r'\(.+([0-9]{4,9})\,.+(?:r|a|rs)=[a-z]+', commit_message, re.IGNORECASE)
        number_list += re.findall(r'^[0-9]{4,9}', commit_message)
        number_list += re.findall(r'([0-9]{4,9})_\s\-\s', commit_message)
        number_list += re.findall(r'for\s([0-9]{4,9})', commit_message, re.IGNORECASE)
        for a_number in number_list:
            bugID = int(a_number)            
            #   the fixes of each bug
            if bugID in bug_dict:
                rev_set = bug_dict[bugID]
                rev_set.add(rev_num)
            else:
                bug_dict[bugID] = set([rev_num])
            #   the bugs of each revision
            if rev_hash in rev_dict:
                bug_set = rev_dict[rev_hash]
                bug_set.add(bugID)
            else:
                rev_dict[rev_hash] = set([bugID])
        #   backed out or reverted bug fixes
        if len(number_list) == 0:
            if(re.search(r'(back(ed)?\s?out|revert)', commit_message, re.IGNORECASE)):
                if not 'no bug' in commit_message.lower():
                    backout_list.append((rev_num, commit_message))
    bug_dict = backoutFixes(backout_list, rev_dict, bug_dict)  
    return bug_dict
    
#   Output the identified bug fixes
def outputBugFixes(mapping_list, bug_dict):
    print 'Outputing results into files ...'
    #   write the mapping to a file
    df = pd.DataFrame(mapping_list, columns=['BugID', 'Revision'])
    df.sort(['BugID', 'Revision'], ascending=False).to_csv('results/bug_fixes.csv', index=False)
    #   write only bug fix numbers into a file
    df['Revision'].sort(ascending=False, inplace=False).to_csv('results/fix_numbers.txt', index=False, header=False)
    #   write bug dict into JSON
    bug_json_dict = dict()
    for bugID in bug_dict:
        bug_json_dict[bugID] = sorted(bug_dict[bugID])
    with open('results/all_fixes.json', 'wb') as f:
        json.dump(bug_json_dict, f)
    return

if(__name__ == '__main__'):
    df_commits = loadCommitLogs('bash_data/commit_log.txt')
    mapping_list = identifyCrashRelatedBugFixes(df_commits)
    bug_dict = identifyAllBugFixes(df_commits)

    outputBugFixes(mapping_list, bug_dict)
    