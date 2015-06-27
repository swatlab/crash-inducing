import pandas as pd
import csv
    
def loadFileToRevDict(filename):
    print 'Loading file ...'
    file_rev_dict = dict()
    csvreader = csv.reader(open(filename, 'rb'))
    for item in csvreader:
        rev = item[0]
        file = item[2]+'.xml'
        file_rev_dict[file] = rev
    return file_rev_dict
    
def loadFilePartsToRevDict(folder):
    print 'Loading files ...'
    file_rev_dict = dict()
    for i in range(0, 10):
        csvreader = csv.reader(open('%s/part%d.csv' %(folder,i), 'rb'))
        for item in csvreader:
            rev = item[0]
            file = item[2]+'.xml'
            file_rev_dict[file] = rev
    return file_rev_dict

def mapTypesToRev(file_rev_dict, file_to_types, rev_to_types):
    print 'Mapping changed types to revisions ...'
    changed_type_dict = dict()
    df = pd.read_csv(file_to_types, index_col=False)
    for idx, items in df.iterrows():
        rev = int(file_rev_dict[items[0]])
        #print type(items[1:])
        if rev in changed_type_dict:
            type_values = changed_type_dict[rev]
            type_values += items[1:]
        else:
            changed_type_dict[rev] = items[1:]
    df = pd.DataFrame.from_dict(changed_type_dict, orient='index')
    df['index_col'] = range(0, len(df))
    df['file'] = df.index
    df = df.reindex_axis(['file'] + list(df.columns[:-1]), axis=1)
    df.set_index(['index_col'], inplace = True)
    df = df[:].astype(int)
    df.rename(columns={'file': 'revision'}, inplace=True) 
    df.sort(['revision']).to_csv(rev_to_types, index=False)
    return

if(__name__ == '__main__'):
    #   Output crashed-inducing revisions' changed types
    file_rev_dict = loadFileToRevDict('../../file_metrics/crashed_cpp_modified.csv')
    mapTypesToRev(file_rev_dict, 'crashed_file_types.csv', 'crashed_changed_types.csv')
    #   Output crash-free revisions' changed types
    file_rev_dict = loadFilePartsToRevDict('../../file_metrics/crash_free_files/mod_cpp_parts')
    mapTypesToRev(file_rev_dict, 'crashfree_file_types.csv', 'crashfree_changed_types.csv')
