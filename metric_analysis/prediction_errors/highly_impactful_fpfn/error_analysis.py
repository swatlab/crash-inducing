import csv
import pandas as pd

def loadFautes(filename):
    faute_set = set()
    with open(filename, 'r') as f:
        csvreader = csv.reader(f)
        next(csvreader, None)
        for line in csvreader:
            false_commmits = line[1].split(' ')
            faute_set |= set(false_commmits)
    return faute_set

def isFalsePositive(row):
    return str(row['revision']) in false_positive_set

def isFalseNegative(row):
    return str(row['revision']) in false_negative_set

if __name__ == '__main__':
    false_positive_set = loadFautes('false_positives.csv')
    false_negative_set = loadFautes('false_negatives.csv')
    df = pd.read_csv('../../../results/metric_table.csv')
    df['false_positive'] = df.apply(isFalsePositive, axis=1)
    df['false_negative'] = df.apply(isFalseNegative, axis=1)
    df[['revision', 'false_positive', 'false_negative']].to_csv('error_table.csv', index=False)
