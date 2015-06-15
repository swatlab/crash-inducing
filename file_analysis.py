import csv
import pandas as pd

def loadChangedFiles(csvname):
    changed_file_dict = dict()
    csv_reader = csv.reader(open(csvname, 'rb'), delimiter='\t')
    for row in csv_reader:
        rev_num = int(row[0])
        del_files = row[1].split(' ')
        mod_files = row[2].split(' ')
        changed_file_dict[rev_num] = {'dels': del_files, 'mods': mod_files}
    return changed_file_dict

def writeToCSV(rev_num, file_list, mapping_list, i):
    for f in file_list:
        if len(f) > 0:
            if(i < 10):
                idx = '0' + str(i)
            else:
                idx = str(i)
            ref = str(rev_num) + '-' + idx
            mapping_list.append([rev_num, f, ref])
            i += 1
    return i

def outputForBash(changed_file_dict):
    mapping_list = list()
    for rev_num in changed_file_dict:
        del_files = changed_file_dict[rev_num]['dels']
        mod_files = changed_file_dict[rev_num]['mods']
        idx = writeToCSV(rev_num, del_files, mapping_list, 1)
        writeToCSV(rev_num, mod_files, mapping_list, idx)
    df = pd.DataFrame(mapping_list, columns=['Revision', 'File', 'Reference'])
    sorted_df = df.sort(['Revision', 'Reference'], ascending=[False, True])
    sorted_df.to_csv('results/rev_file.csv', index=False, header=False)
    return

if(__name__ == '__main__'):
    changed_file_dict = loadChangedFiles('bash_data/changed_files.csv')
    outputForBash(changed_file_dict)