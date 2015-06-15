import csv, sys, re
import pandas as pd

#   Load all commit logs (including author, date, and message) of Firefox until March 2015
def loadChangedFiles(sourcename):
    cpp_list = list()
    csv_reader = csv.reader(open(sourcename, 'rb'), delimiter='\t')
    for line in csv_reader:
        rev_num = line[0]    
        file_dels = line[1]
        file_mods = line[2]
        file_adds = line[3]
        dels_cpp = ' '.join(set(re.findall(r'\b\S+\.(?:c|cpp|cc|cxx|h|hpp|hxx)\b', file_dels, re.IGNORECASE)))
        mods_cpp = ' '.join(set(re.findall(r'\b\S+\.(?:c|cpp|cc|cxx|h|hpp|hxx)\b', file_mods, re.IGNORECASE)))
        adds_cpp = ' '.join(set(re.findall(r'\b\S+\.(?:c|cpp|cc|cxx|h|hpp|hxx)\b', file_adds, re.IGNORECASE)))
        cpp_list.append([rev_num, mods_cpp, adds_cpp, dels_cpp])
    return pd.DataFrame(cpp_list, columns=['revision', 'mod_files', 'add_files', 'del_files'])

        
if(__name__ == '__main__'):
    csv.field_size_limit(sys.maxsize)
    pd_changed = pd.DataFrame([])
    for i in range(1,11):
        print 'Dealing with Part %d' %i
        pd_part = loadChangedFiles('all_files_parts/part%d.csv' %i)
        pd_changed = pd_changed.append(pd_part)
    pd_sorted = pd_changed.sort(['revision'], ascending=True)
    
    pd_sorted.to_csv('crash_free_cpp.csv', sep='\t', header=False, index=False)