"""
    Removes all duplicated articles
    Restructures dataframe:
        - Binary variable for mention of agency
        - Description of articles
"""
import pandas as pd
from utils import progress
import numpy as np
import sys
import re


progress(0,5,"Loading articles")
    
#Load articles
articles = pd.read_pickle('../data/raw/all_unstable_articles.pkl')
articles = articles.reset_index()
del articles['index']
articles = articles.reset_index()
articles.columns = ['id','source', 'date','title', 'byline', 'section', 'length', 'story','agency']

progress(1,5,"Dropping duplicates")

#Drop any obvious duplicates
articles.drop_duplicates(inplace=True)


#Mask for any articles that have a story which is not a string.
def clean_integer_story():
    acopy = articles.copy()
    acopy['story_type'] = acopy['story'].apply(lambda x : type(x))
    return acopy[acopy['story_type'] != str]

#Remove articles that aren't strings
articles = articles.drop(clean_integer_story()['id'].values)

#Create a hash for each story
articles['story_hash'] = articles['story'].apply(lambda text : hash(tuple(text.split())))

#Remove any stories that share the same hash
articles = articles.drop_duplicates(['agency','story_hash'])

# Make all stories consistent (This removes any discrepancy due to spaces)
articles['story'] = articles.loc[:,['story','story_hash']].groupby('story_hash').transform('first')

progress(2,5,"Restructuring dataframe")

#Flip dataframe. We use article title as key now
#Right hand side of new frame will be a binary variable for each agency
RHS = articles.groupby(['story_hash','agency']).agg('count')['story'].unstack()
RHS.fillna(0,inplace=True)
RHS = RHS.astype(int)

#Left hand side is description for each article
LHS = articles.groupby(['story_hash'], as_index=True).first().loc[:,['id','source','date','title','byline','section','length','story']]

#Merging both parts
merged = pd.concat([LHS,RHS], axis=1, join='inner')
merged.reset_index(inplace=True)
merged.drop('story_hash',axis=1,inplace=True)

progress(3,5,"Removing close duplicates")
#Removing similar length articles that share certain characteristics
#Heuristic removal to prevent errors in scraping resulting in duplicates

def get_titles_equals_two(df):
    tmp = pd.DataFrame(df.groupby(['title']).count().loc[:,['story']])
    tmp2 = tmp[tmp['story'] == 2]
    return tmp2.index.values

def get_ids_to_be_removed():
    ids = []

    for title in get_titles_equals_two(merged):
        tmp = merged[merged['title'] == title]
        a = tmp.iloc[0,:8]
        b = tmp.iloc[1,:8]
        
        #Allow for a 5% difference between lengths or a 10 word difference
        div_perc = (abs(int(a.length) - int(b.length))/ np.mean([int(a.length),int(b.length)]))
        div_abs = abs(int(a.length) - int(b.length))
        if (div_perc < 0.05) or (div_abs < 10):
            ids.append(b.id)
            
    return ids

#Obtain ids that require removal
ids_to_be_removed = get_ids_to_be_removed()

#Remove articles that have ids in ids_to_be_removed
final = merged[~merged['id'].isin(ids_to_be_removed)]

#Remove copyright sign -> Move to preprocessing
final['story'] = final['story'].apply(lambda x : re.sub('Copyright ©.*' , '',  x))

progress(4,5,"Saving dataframe")

#Save resulting dataframe
final.to_pickle('../data/processed/all_unstable_nodup_title_index.pkl')

progress(5,5,"Done.")
