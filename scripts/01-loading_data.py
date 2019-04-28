"""
    Loads csvs into a dataframe and save as pickle
"""
import pandas as pd
import numpy as np
from datetime import datetime
import sys

# Progress bar. Ignore.
def progress(count, total, status=''):
    bar_len = 60
    filled_len = int(round(bar_len * count / float(total)))

    percents = round(100.0 * count / float(total), 1)
    bar = '=' * filled_len + '-' * (bar_len - filled_len)

    sys.stdout.write('[%s] %s%s ...%s\r' % (bar, percents, '%', status))


PATH = '../data/raw/original_csvs/{}_unstable_articles.csv'
AGENCIES = [ 'CFE'
            ,'INM'
            ,'SEDENA'
            ,'SENER'
            ,'SSA'
            ,'COFEPRIS'
            ,'PEMEX'
            ,'SEDESOL'
            ,'SEP'
            ,'SSP'
            ,'CONAGUA'
            ,'PGR'
            ,'SEECO'
            ,'SFP'
            ,'IMPI'
            ,'SAGARPA'
            ,'SEGOB'
            ,'SHCP'
            ,'IMSS'
            ,'SCT'
            ,'SEMARNAT'
            ,'SRE'
           ]

#Loading all data
df = pd.DataFrame()
for i,agency in enumerate(AGENCIES):
    progress(i,len(AGENCIES)+3,f"Loading {agency}")
    df_tmp = pd.read_csv(PATH.format(agency),encoding = "latin-1")
    df_tmp['agency'] = agency
    df = pd.concat([df, df_tmp])
    
progress(len(AGENCIES)+1,len(AGENCIES)+3,"Formatting")

#Remove some columns and parsing date into datetime
df = df.loc[:,['source','date','title','byline','section','length','story','agency']]
df['date'] = pd.to_datetime(df['date'])

#Extract length number as a number
df['length'] = df['length'].str.extract('(\d+)')

progress(len(AGENCIES)+2,len(AGENCIES)+3,"Saving dataframe")
df.to_pickle('../data/raw/all_unstable_articles.pkl')
             
progress(len(AGENCIES)+3,len(AGENCIES)+3,"Done")
