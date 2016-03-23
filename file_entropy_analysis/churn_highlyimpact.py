import pandas as pd



if(__name__ == '__main__'):
    df_crashed = pd.read_csv('crashed_file_entropy.csv')
    df_crashfree = pd.read_csv('crashfree_file_entropy.csv')
    df = pd.concat([df_crashed, df_crashfree])
    df.to_csv('file_entropy.csv', index=False)
    df_impact = pd.read_csv('../results/crashed_commit_impact.csv')
    high_impact_rev = set(df_impact[df_impact.high_impact=='YES']['revision'])
    # Highly-impactful commits
    df_high_impact = df[df['revision'].isin(high_impact_rev)]
    df_high_impact.to_csv('highimpact_file_entropy.csv', index=False)
    # All other commits
    df_other = df[~df['revision'].isin(high_impact_rev)]
    df_other.to_csv('not_highimpact_file_entropy.csv', index=False)
    # Less impactful (crash-inducing) commits
    df_lessimpact = df_other[df_other['revision'].isin(df_crashed['revision'])]
    df_lessimpact.to_csv('lessimpact_file_entropy.csv', index=False)