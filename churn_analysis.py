import re
import pandas as pd

with open('bash_data/churn.txt', 'rb') as f:
    reader = f.read()
    raw_list = reader.split('\n')

churn_list = list()
latest_rev = 0
void_rev = False
for line in raw_list:
    if line[0] == ' ':
        file_match = re.search(r'([0-9]+)\s+file', line)
        if file_match:
            changed_files = int(file_match.group(1))
        insertion_match = re.search(r'([0-9]+)\s+insertion', line)
        if insertion_match:
            insertions = int(insertion_match.group(1))
        deletion_match = re.search(r'([0-9]+)\s+deletion', line)
        if deletion_match:
            deletions = int(deletion_match.group(1))
        #print changed_files, insertions, deletions 
        churn_list.append([latest_rev, changed_files, insertions, deletions])
        void_rev = False
    else:
        if void_rev:
            churn_list.append([latest_rev, 0, 0, 0])
            #print latest_rev, 0, 0, 0
        latest_rev = int(line) 
        void_rev = True

df = pd.DataFrame(churn_list, columns=['revision', 'changed_file', 'insertion', 'deletion'])
df.to_csv('results/churn_table.csv', index=False)