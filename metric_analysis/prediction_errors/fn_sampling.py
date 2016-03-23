import pandas as pd

df = pd.read_csv('error_table.csv')
fn_revisions = set(df[df.false_negative==True]['revision'])
print(fn_revisions)