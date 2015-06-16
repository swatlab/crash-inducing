import csv
from numpy import median
import pandas as pd

def loadFiles(crashed_files, crash_free_files):
    print 'Loading files ...'
    col = ['revision', 'modified', 'added', 'deleted']
    df_crashed = pd.read_csv(crashed_files, sep='\t', index_col=None, names=col)
    df_crash_free = pd.read_csv(crash_free_files, sep='\t', index_col=None, names=col)
    df_all = df_crashed.append(df_crash_free).sort(['revision'])
    return df_all

def combineColumns(df_all):
    print 'Combining files ...'
    combined_dict = dict()
    for idx, item in df_all.iterrows():
        rev = item[0]
        changed_set = set()
        for file_str in item[1:]:
            if type(file_str) == type(''):
                changed_set |= set(file_str.split(' '))
        combined_dict[rev] = changed_set
    return combined_dict

def loadReleaseDate(filename):
    print 'Loading release date ...'
    release_list = list()
    csvreader = csv.reader(open('firefox_release.csv', 'rb'))
    for line in csvreader:
        release_list.append([line[1], line[0]])
        #release_dict[line[0]] = pd.to_datetime(line[1], format='%Y-%m-%d')
    return release_list

def mapCommitToRelease(filename, release_list):
    print 'Mapping commits to release ...'
    rev_release_mapping = dict()
    df = pd.read_csv(filename, index_col=False)
    for idx, item in df.iterrows():
        rev = item['revision'] 
        date = item['date'].split(' ')[0]
        if date < release_list[0][0]:
            release_num = release_list[0][1]
        elif date > release_list[-1][0]:
            release_num = release_list[-1][1]
        else:
            for rel_item in release_list:
                if date >= rel_item[0]:
                    release = rel_item[1]
                else:
                    break
        rev_release_mapping[rev] = release
        print rev_release_mapping
    return rev_release_mapping

def loadCodeMetrics(folder, kind):
    print 'Loading %s metrics ...' %kind
    all_releases_dict = dict()
    for i in range(3, 21):
        metric_dict = dict()
        filename = folder + '%s_metrics_%d.csv' %(kind, i)
        csvreader = csv.reader(open(filename, 'rb'))
        next(csvreader, None)
        for line in csvreader:
            metric_dict[line[0][1:]] = [float(m) for m in line[1:]]
        all_releases_dict[str(i)] = metric_dict
    return all_releases_dict

def computeMetricMedian(combined_dict, rev_release_mapping, complexity_dict, kind):
    print 'Computing median %s metrics for each commit ...' %kind
    code_metric_list = list()
    for rev in combined_dict:
        result_list = [[], [], [], [], []]
        median_list = list()
        file_set = combined_dict[rev]
        release = rev_release_mapping[rev]
        metric_dict = complexity_dict[release]
        for f in file_set:
            if kind == 'code':
                key = f
            elif kind == 'sna':
                key = f.split('.')[0]
            if key in metric_dict:
                metrics = metric_dict[key]
                for i in range(0, len(metrics)):
                    result_list[i].append(metrics[i])
        for sub_list in result_list:
            if len(sub_list):
                median_list.append(median(sub_list))
            else:
                median_list.append(0)        
        code_metric_list.append([int(rev)] + median_list)
    if kind == 'code':
        col = ['revision', 'loc', 'cyclomatic', 'func_num', 'max_nesting', 'ratio_comments']
    elif kind == 'sna':
        col = ['revision', 'page_rank', 'betweenness', 'closeness', 'indegree', 'outdegree']
    df = pd.DataFrame(code_metric_list, columns=col)
    return df
        
if(__name__ == '__main__'):
    df_all = loadFiles('../file_metrics/crashed_cpp.csv', '../file_metrics/crash_free_files/crash_free_cpp.csv')
    combined_dict = combineColumns(df_all)
    release_list = loadReleaseDate('firefox_release.csv')
    rev_release_mapping = mapCommitToRelease('../results/firefox/metric_table.csv', release_list)
    """ IN THE FOLLOWING TWO LINES PLEASE INDICATE THE RIGHT DIRECTORY OF CODE COMPLEXITY AND SNA DATA'S FOLDER """
    """ THESE DATA ARE AVAILABLE AT: https://github.com/swatlab/highly-impactful """
    complexity_dict = loadCodeMetrics('../../../crash_triaging/entropy_result/SNA_analysis/firefox/', 'code')
    sna_dict = loadCodeMetrics('../../../crash_triaging/entropy_result/SNA_analysis/firefox/', 'sna')
    df_complexity = computeMetricMedian(combined_dict, rev_release_mapping, complexity_dict, 'code')
    df_sna = computeMetricMedian(combined_dict, rev_release_mapping, sna_dict, 'sna')
    #df_synthetical = pd.concat([df_complexity, df_sna], axis=1)
    df_synthetical = pd.merge(df_complexity, df_sna, on='revision')
    df_synthetical.to_csv('code_metrics.csv', index=False)
    print df_synthetical
    