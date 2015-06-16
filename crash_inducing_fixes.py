import csv, re, os, json

#   Map bugs to corresponding bug fixes
def mapBugToFixes(csvfile):
    csv_reader = csv.reader(open(csvfile, 'rb'))
    mapping_list = list(csv_reader)[1:]
    bug_rev_dict = dict()
    for tpl in mapping_list:
        aBug = tpl[0]
        aFix = tpl[1]
        if aBug in bug_rev_dict:
            fixes = bug_rev_dict[aBug]
            fixes.append(aFix)
        else:
            bug_rev_dict[aBug] = [aFix]
    return bug_rev_dict

#   Map changed files to bug fix reference
def mapReferenceToFiles(csvfile):
    ref_file_dict = dict()
    csv_reader = csv.reader(open(csvfile, 'rb'))
    for line in csv_reader:
        ref_file_dict[line[2]] = line[1]
    return ref_file_dict

#   Map revisions to corresponding commit date
def revisionDate(filename):
    rev_date_dict = dict()
    with open(filename, 'rb') as f:
        lines = f.read().split('\n')
    for line in lines:
        if re.search(r'^[0-9]+\:[0-9a-z]{12}\t', line):
            elem_list = line.split('\t')
            rev_num = elem_list[0].split(':')[0]
            date_str = re.sub(r'[\-\:\s]', '',elem_list[2][:-6])
            rev_date_dict[rev_num] = date_str
    return rev_date_dict

#   Load crashed date of each bug (for the earlist crash-type, and the latest crash-type)
def bugCrashedDate(csvfile):
    bug_crashed_date_dict = dict()
    csv_reader = csv.reader(open(csvfile, 'rb'))
    for line in csv_reader:
        bugID = line[0]
        date_list = line[1].split(' ')
        earlist_ct_date = date_list[0]  # the first crashed date of the earlist crash-type
        latest_ct_date = date_list[-1]  # the first crashed date of the latest crash-type
        bug_crashed_date_dict[bugID] = (earlist_ct_date, latest_ct_date)
    return bug_crashed_date_dict

#   Load location of each bug (buggy paths or files)
def bugLocation(csvfile):
    bug_location_dict = dict()
    csv_reader = csv.reader(open(csvfile, 'rb'))
    next(csv_reader, None) 
    for line in csv_reader:
        bug_location_dict[line[0]] = set(line[1].split(' '))
    return bug_location_dict

#   Detect changed revision numbers for each bug fix
def identifyChangedRevisions(file_name):
    changed_rev = set()
    block_comment = False
    with open(file_name, 'rb') as f:
        read_data = f.read()
    for line in read_data.split('\n'):
        annotated_line = line.split(':', 1)
        rev_num = annotated_line[0].strip()
        #   filter out the blank lines
        if len(annotated_line) > 1:
            changed_code = annotated_line[1].strip()
        else:
            changed_code = ''
        #   filter out the meaningless lines (i.e., lines without letters), and comment lines
        if len(changed_code) > 0 and re.search(r'[a-zA-Z]', changed_code):
            if block_comment:
                if '*/' in changed_code:
                    block_comment = False
                    valid_code = re.sub(r'.+\*\/', '', changed_code)
            elif ('/*' in changed_code) and ('*/' not in changed_code):
                block_comment = True
                valid_code = re.sub(r'\/\*.+', '', changed_code)
            else:
                valid_code = re.sub(r'\/\*.+\*\/', '', re.sub(r'\/\/.+', '', changed_code))
            #   take only the valid lines as bug-inducing candidates
            if len(valid_code) > 0 and re.search(r'[a-zA-Z]', valid_code):
                #print rev_num, '\t', changed_code
                changed_rev.add(rev_num)
    return changed_rev

#   read annotated files and map candiates to Revisions
def readAnnotatedFiles(file_path):
    print 'Parsing annotated files ...'
    folder_list = sorted(os.listdir(file_path))
    candidate_rev_dict = dict()
    candidate_file_dict = dict()
    last_rev = ''
    last_changed_rev = set()
    #   combine candidate sets for the same revisions
    for f in folder_list:
        if '.txt' in f:
            rev_num = f.split('-')[0]
            changed_rev = identifyChangedRevisions(file_path + f)
            #print changed_rev
            
            
            if rev_num == last_rev:
                last_changed_rev |= changed_rev
            else:
                if len(candidate_rev_dict) > 0:
                    #print last_rev, '\t'*2, last_changed_rev
                    print last_rev
                candidate_rev_dict[rev_num] = changed_rev
                last_rev = rev_num
                last_changed_rev = changed_rev
            #   each candidate's changed files
            ref = f.split('.')[0]
            changed_file = ref_file_dict[ref]
            for r in changed_rev:
                if r in candidate_file_dict:
                    file_set = candidate_file_dict[r]
                    file_set.add(changed_file)
                else:
                    candidate_file_dict[r] = set([changed_file])
    return (candidate_rev_dict, candidate_file_dict)
    
#   Map candidates to Bugs
def mapCandidateToBug(candidate_rev_dict, bug_rev_dict):
    print 'Mapping candidates of crash-inducing fixes to bugs ...'
    bug_candidate_dict = dict()
    for aBug in bug_rev_dict:
        rev_list = bug_rev_dict[aBug]
        candidate_set = set()
        for rev in rev_list:
            #   filter out only files added revisions
            if rev in candidate_rev_dict:
                changed_rev = candidate_rev_dict[rev]
                candidate_set |= changed_rev
        if len(candidate_set) > 0:  #   filter out revisions with only added files
            bug_candidate_dict[aBug] = candidate_set
    return bug_candidate_dict

#   Decide whether a revision changed a file, which caused later crashes in a bug
def intersenctionOfFiles(bug_location_set, files_of_candicate):
    for candidate_file in files_of_candicate:
        for buggy_file in bug_location_set:
            if (candidate_file in buggy_file) or (buggy_file in candidate_file):
                return True
    return False

#   Screening candidate revisions that introduce crashes
def crashInducingCandidates(bug_candidate_dict, rev_date_dict, bug_crashed_date_dict, candidate_file_dict):
    print 'Screening crash-inducing fixes to bugs ...'
    crash_inducing_rev_dict = dict()
    total_crash_inducing_rev = set()
    for aBug in bug_candidate_dict:
        print aBug
        crash_inducing_fix_set = set()
        earlist_date = bug_crashed_date_dict[aBug][0]
        latest_date = bug_crashed_date_dict[aBug][1]
        candidate_set = bug_candidate_dict[aBug]
        for rev_num in candidate_set:
            candidate_date = rev_date_dict[rev_num]
            if(candidate_date < earlist_date):
                crash_inducing_fix_set.add(rev_num)
                total_crash_inducing_rev.add(rev_num)
            elif(candidate_date < latest_date):
                if aBug in bug_location_dict:
                    bug_location_set = bug_location_dict[aBug]
                    files_of_candidate = candidate_file_dict[rev_num]
                    if intersenctionOfFiles(bug_location_set, files_of_candidate):
                        crash_inducing_fix_set.add(rev_num)
                        total_crash_inducing_rev.add(rev_num)
        total_crash_inducing_rev |= crash_inducing_fix_set
        crash_inducing_rev_dict[aBug] = sorted(crash_inducing_fix_set)
    return (crash_inducing_rev_dict, total_crash_inducing_rev)

#   Outputing resutls
def outputResults(crash_inducing_rev_dict, total_crash_inducing_rev):
    print 'Outputing results ...'
    crash_inducing_rev_list = [int(rev) for rev in total_crash_inducing_rev]
    with open('results/crash_inducing_commits.txt', 'w+') as f:
        for rev in sorted(crash_inducing_rev_list):
            f.write(str(rev) + '\n')
    with open('results/bug_to_crash_inducing_commit.json', 'wb') as f:
        json.dump(crash_inducing_rev_dict, f)
    return

if(__name__ == '__main__'):
    print 'Initialising data ...'
    bug_rev_dict = mapBugToFixes('results/bug_fixes.csv')
    ref_file_dict = mapReferenceToFiles('results/rev_file.csv')
    rev_date_dict = revisionDate('bash_data/commit_log.txt')
    bug_crashed_date_dict = bugCrashedDate('raw_data/bug_crashed_date.csv')
    bug_location_dict = bugLocation('results/bug_location.csv')
    (candidate_rev_dict, candidate_file_dict) = readAnnotatedFiles('bash_data/annotated_files/')
    bug_candidate_dict = mapCandidateToBug(candidate_rev_dict, bug_rev_dict)
    (crash_inducing_rev_dict, total_crash_inducing_rev) = crashInducingCandidates(bug_candidate_dict, 
                                                                                    rev_date_dict, 
                                                                                    bug_crashed_date_dict, 
                                                                                    candidate_file_dict)
    outputResults(crash_inducing_rev_dict, total_crash_inducing_rev)
    