import csv, sys, re
import hashlib
import pandas as pd

csv_writer = csv.writer(open('crashed_cpp_modified.csv', 'wb'))

csv.field_size_limit(sys.maxsize)
csv_reader = csv.reader(open('crashed_files.csv', 'rb'), delimiter='\t')
cpp_list = list()
for line in csv_reader:
    rev_num = line[0]    
    file_mods = line[1]
    file_adds = line[2]
    file_dels = line[3]
    mods_set = set(re.findall(r'\b\S+\.(?:c|cpp|cc|cxx|h|hpp|hxx)\b', file_mods, re.IGNORECASE))
    mods_cpp = ' '.join(set(re.findall(r'\b\S+\.(?:c|cpp|cc|cxx|h|hpp|hxx)\b', file_mods, re.IGNORECASE)))
    adds_cpp = ' '.join(set(re.findall(r'\b\S+\.(?:c|cpp|cc|cxx|h|hpp|hxx)\b', file_adds, re.IGNORECASE)))
    dels_cpp = ' '.join(set(re.findall(r'\b\S+\.(?:c|cpp|cc|cxx|h|hpp|hxx)\b', file_dels, re.IGNORECASE)))
    cpp_list.append([rev_num, mods_cpp, adds_cpp, dels_cpp])
    if len(mods_set):
        for f in mods_set:
            hashid = hashlib.sha1(rev_num + ':' + f).hexdigest()
            ext = f.split('.')[1]
            csv_writer.writerow([rev_num, f, hashid+'.'+ext])
pd_cpp = pd.DataFrame(cpp_list, columns=['revision', 'mod_files', 'add_files', 'del_files'])
pd_cpp.to_csv('crashed_cpp.csv', sep='\t', header=False, index=False)
