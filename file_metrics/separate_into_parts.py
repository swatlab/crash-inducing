import csv, sys
import pandas as pd

csv.field_size_limit(sys.maxsize)

csvreader = csv.reader(open('crash_free_cpp.csv', 'rb'), delimiter='\t')
changed_list = list()
for line in csvreader:
    rev = int(line[0])
    mods = set(line[1].split(' '))
    adds = set(line[2].split(' '))
    dels = set(line[3].split(' '))
    all_changed = (mods | adds | dels) - set([''])
    if len(all_changed):
        for f in all_changed:
            changed_list.append([rev, f])
df = pd.DataFrame(changed_list, columns=['revision', 'file']).sort(['revision'])

rev_file_list = df.values.tolist()


for k in range(0, 10):
    print 'Dealing with Parth %d', k
    sub_list = list()
    for i in range(0, len(rev_file_list)):
        if i%10 == k:
            item = rev_file_list[i]
            sub_list.append(item)
    pd.DataFrame(sub_list).to_csv('crashfree_cpp_parts/part%d.csv' %k, index=False, header=False)
