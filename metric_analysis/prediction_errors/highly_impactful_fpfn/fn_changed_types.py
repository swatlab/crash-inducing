import pandas as pd

if __name__ == '__main__':
    pd.options.display.float_format = '{:.1f}%'.format
    
    df = pd.read_csv('error_table.csv')
    fp_list = list(df[df['false_positive'] == True]['revision'])
    fn_list = list(df[df['false_negative'] == True]['revision'])
    
    print 'False positive commits changed types:'
    df_types = pd.read_csv('../../../code_metrics/changed_types/crashed_changed_types.csv')
    df_fn_types = df_types[df_types['revision'].isin(fn_list)]
    series_fn = df_fn_types.ix[:,1:].sum(axis=0)
    series_fn_pct = series_fn / series_fn.sum() * 100
    print series_fn_pct.round(decimals=1).order(ascending=False)
    
    print '\nClean commits changed types:'
    df_types = pd.read_csv('../../../code_metrics/changed_types/crashfree_changed_types.csv')
    df_clean_types = df_types[df_types['revision'].isin(fp_list)==False]
    series_clean = df_clean_types.ix[:,1:].sum(axis=0).order(ascending=False)
    series_clean_pct = series_clean / series_clean.sum() * 100
    print series_clean_pct.round(decimals=1).order(ascending=False)