import csv
import pandas as pd

#   Combine items
def combineColumns(df, columnname):
    column_types = [columnname+'_added', columnname+'_deleted', columnname+'_modified']
    df[columnname] = df[column_types].sum(axis=1)
    df.drop(column_types, axis=1, inplace=True)
    return df

#   Combine multiple columns into a new column
def combineColumnsAs(df, columns, as_name):
    df[as_name] = df[columns].sum(axis=1)
    df.drop(columns, axis=1, inplace=True)
    return df

#   Combine detailed types
def combineDetailedTypes(df):
    col_list = list(df.columns)[1:]    
    for col in col_list[::3]:
        col_name = col.split('_added')[0]
        df = combineColumns(df, col_name)
    return df

#   Combien data parts
def combineData(folder):
    #   Combine 10 parts of data
    df_list = list()
    for i in range(0, 10):
        print 'Dealing with Part %d ...' %i
        df_part = pd.read_csv('%s/part%d.csv' %(folder,i), index_col=False)
        df_part = combineDetailedTypes(df_part)
        df_list.append(df_part)
    df = pd.concat(df_list).fillna(0)
    return df

#   Manually select or combine columns
def selectColumns(df): 
    df = combineColumnsAs(df, ['cpp:define', 'cpp:elif', 'cpp:else', 'cpp:endif', 'cpp:error', \
        'cpp:file', 'cpp:if', 'cpp:ifdef', 'cpp:ifndef', 'cpp:include', 'cpp:line', 'cpp:pragma', 
        'cpp:undef', 'cpp:value', 'macro'], 'preprocessor')
    df = combineColumnsAs(df, ['param', 'parameter_list', 'argument', 'argument_list'], 'parameter')
    df = combineColumnsAs(df, ['while', 'do', 'if', 'else', 'break', 'goto', 'for', 'foreach', \
        'continue', 'then', 'switch', 'case', 'return', 'condition', 'incr', 'default'], 'flow_control_stmt')
    df = combineColumnsAs(df, ['super', 'public', 'private', 'protected', 'extern', 'template'], 'oop')
    df = combineColumnsAs(df, ['enum', 'struct', 'struct_decl', 'typedef', 'union', 'union_decl'], 'data_type')
    df = combineColumnsAs(df, ['asm', 'decl', 'decl_stmt', 'using', 'namespace', 'range', 'specifier'], 'declaration')
    #df = combineColumnsAs(df, ['block', 'expr', 'expr_stmt', 'escape', 'index', 'sizeof'], 'code')
    #   Merge some columns into an existing column
    df['refactoring'] = df[['refactoring', 'name', 'typename', 'label']].sum(axis=1)
    df.drop(['name', 'typename'], axis=1, inplace=True)
    df['constructor'] = df[['constructor', 'constructor_decl']].sum(axis=1)
    df.drop(['constructor_decl'], axis=1, inplace=True)
    df['destructor'] = df[['destructor', 'destructor_decl']].sum(axis=1)
    df.drop(['destructor_decl'], axis=1, inplace=True)
    df['class'] = df[['class', 'class_decl', 'member_list']].sum(axis=1)
    df.drop(['class_decl', 'member_list'], axis=1, inplace=True)
    df['function'] = df[['function', 'function_decl']].sum(axis=1)
    df.drop(['function_decl'], axis=1, inplace=True)
    if 'cpp:directive' in df:
        df['preprocessor'] = df[['preprocessor', ]].sum(axis=1)
        df.drop(['cpp:directive'], axis=1, inplace=True)    
    #   Put the selected columns into a new dataframe
    #print df
    df_selected = df[['file', 'call', 'comment', 'refactoring', 'init', 'type', 'preprocessor', 'parameter', \
        'flow_control_stmt', 'oop', 'data_type', 'declaration', 'constructor', 'destructor', 'class', 'function']]    
    return df_selected

if(__name__ == '__main__'):
    #   Crashed files' changed types
    df = combineData('crashed')
    df_selected = selectColumns(df)
    df_selected.to_csv('crashed_file_types.csv', index=False)
    #   Crash-free files' changed types
    df = combineData('crashfree')
    df_selected = selectColumns(df)
    df_selected.to_csv('crashfree_file_types.csv', index=False)


    
    