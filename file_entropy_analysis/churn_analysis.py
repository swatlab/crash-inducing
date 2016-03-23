from __future__ import division
import re, math
import pandas as pd

#   Extract changed lines for each file in each revisioin
def extractChangedFiles(folder):
    changed_dict = dict()
    for i in range(0, 10):
        with open('%s/churn%d.txt' %(folder,i), 'rb') as f:
            reader = f.read().split('\n')
        new_file = False
        for line in reader:
            if re.search(r'\s[0-9]+\sfiles changed', line):
                #print line
                new_file = False
                churns = line.split(',')
                add_lines = int(churns[1].strip().split(' ')[0])
                del_lines = int(churns[2].strip().split(' ')[0])
                if current_rev in changed_dict:
                    file_changed_list = changed_dict[current_rev]
                    file_changed_list.append(add_lines+del_lines)
                else:
                    changed_dict[current_rev] = [add_lines+del_lines]
            elif re.search(r'^.+', line):
                #print line
                new_file = True
                current_rev = int(line.split(' ')[0])
    return changed_dict

#   Compute entropy value for each commit
def computeEntropy(changed_dict, filename):
    entropy_list = list()
    for rev in changed_dict:
        changed_lines_list = changed_dict[rev]
        entropy = 0
        file_cnt = len(changed_lines_list)
        if file_cnt > 0: 
            if file_cnt == 1:
                entropy = 0
            else:
                for line_num in changed_lines_list:
                    p_file = line_num / sum(changed_lines_list)
                    entropy += -(p_file * math.log(p_file, file_cnt))
            entropy_list.append([rev, entropy])
            #print rev, changed_lines_list, entropy
    df = pd.DataFrame(entropy_list, columns=['revision', 'file_entropy']).sort(['revision'])
    df.to_csv(filename, index=False)
    return

if(__name__ == '__main__'):
    changed_dict = extractChangedFiles('crashed')
    computeEntropy(changed_dict, 'crashed_file_entropy.csv')
    changed_dict = extractChangedFiles('crashfree')
    computeEntropy(changed_dict, 'crashfree_file_entropy.csv')
    
    