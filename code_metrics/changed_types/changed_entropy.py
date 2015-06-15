from __future__ import division
import csv, math
import pandas as pd

def changedEntropy(rev_type):
    csvreader = csv.reader(open(rev_type + '_changed_types.csv', 'rb'))
    next(csvreader, None)

    entropy_list = list()
    for line in csvreader:
        rev = int(line[0])
        changed_types = line[1:]
        ct_list = list()
        for ct in changed_types:
            if int(ct) > 0:
                ct_list.append(int(ct))
        unique_ct = len(ct_list)
        ct_cnt = 15
        entropy = 0
        if ct_cnt == 1:
            entropy = 1
        else:
            for ct in ct_list:
                p_ct = ct / sum(ct_list)
                entropy += -(p_ct * math.log(p_ct, ct_cnt))
        entropy_list.append([rev, unique_ct, round(entropy, 3)])
    df = pd.DataFrame(entropy_list, columns=['revision', 'unique_types', 'entropy']).sort('revision')
    df.to_csv(rev_type + '_changed_entropy.csv', index=False)
    return

if(__name__ == '__main__'):
    changedEntropy('crashed')
    changedEntropy('crashfree')
