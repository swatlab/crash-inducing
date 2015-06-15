import csv, sys, re
import hashlib
import pandas as pd

df = pd.read_csv('crash_free_cpp.csv', sep='\t', header=None, index_col=False, names=['revision', 'mod_files', 'add_files', 'del_files'])
df_mods = df[['revision', 'mod_files']]
parts_dict = dict()
for idx, item in df_mods.iterrows():
    rev = int(item[0])
    file_str = item[1]
    if type(file_str) == type(''):
        file_set = set(file_str.split(' '))
        rev_file_hash_list = list()
        for f in file_set:
            hashid = hashlib.sha1(str(rev) + ':' + f).hexdigest()
            ext = f.split('.')[1]
            rev_file_hash_list.append([rev, f, hashid+'.'+ext])
        group = rev%10
        if group in parts_dict:
            parts_dict[group] += rev_file_hash_list
        else:
            parts_dict[group] = rev_file_hash_list
for k in parts_dict:
    sub_list = parts_dict[k]
    df = pd.DataFrame(sub_list)
    df.to_csv('mod_cpp_parts/part%d.csv' %k, header=False, index=False)

