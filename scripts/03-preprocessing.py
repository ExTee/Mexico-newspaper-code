"""
    Preprocessing script.
    
    Input:
        - Deduplicated and restructured dataframe of articles
    
    Does the following:
        - Lists agencies mentioned in each article
        - Separates each story into sentences
        - Counts sentences

"""
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from nltk.tokenize import sent_tokenize
from utils import progress
from utils import REGEXES
import re

progress(0,10,"Loading articles")
articles = pd.read_pickle('../data/processed/all_unstable_nodup_title_index.pkl')


def get_sentences(text):
    """
        Add a space after periods (Scraping sometimes omits spaces after periods.
        Use NLTK's sent_tokenize to tokenize
    """
    text = re.sub('\.', '. ', text)
    return sent_tokenize(text)


def plot_sentence_count_distribution():
    """
        Plots the distribution of the number of sentences in an article.
        Only call after counting number of sentences
    """
    plt.figure(figsize=(10,5))
    plt.xlim(0,100)
    plt.title('Distribution of number of sentences')
    bins = list(range(0,200)) + [max(articles['num_sentences'])]
    sns.distplot(articles['num_sentences'], 
                 hist=True, kde=False, 
                 bins=bins, color = 'red',
                 hist_kws={'edgecolor':'black','cumulative':False},
                ).set(xlabel='num_sentences', ylabel='num_articles')
    plt.savefig('../figures/sentence_count_distribution.png')
    plt.close()
    
def get_sentence_idx_from_agencies(series):  
    """
        Goes through one article corresponding to one row of dataframe.
        For each sentence in article, perform a regex search and notes down index where mention appears.
    """
    sentences = series.story_sentences
    agencies = series.agencies
    
    d = {}
    for i, sentence in enumerate(sentences):
        for agency in agencies:
            ag_regex = re.compile(REGEXES[agency])
            if ag_regex.search(sentence.lower()):
                try:
                    d[agency].append(i)
                except:
                    d[agency] = [i]
                    
    # Quality Check. This will indicate if there weren't any matches for a particular agency.
    for agency in agencies:
        try:
            tmp = d[agency]
        except:
            failed_ids.add(series.id)
    return d    


#---- Create list that contains all agencies an article mentions ----#
progress(1,10,"Creating agency list")
agency_list = []
for i in range(articles.shape[0]):
    progress(i,articles.shape[0])
    tmp = articles.iloc[i,8:]
    agency_list.append(tmp[tmp > 0].index.values)

articles['agencies'] = agency_list

#---- Splitting sentences ----#
progress(1,10,"Splitting sentences")
articles['story_sentences'] = articles['story'].apply(lambda s : get_sentences(s))

#---- Counting number of sentences ----#
articles['num_sentences'] = articles['story_sentences'].apply(lambda s : len(s))

plot_sentence_count_distribution()

#---- Locating target sentences (sentences that mention agency) ----#
failed_ids = set()
sentence_locations = articles.apply(get_sentence_idx_from_agencies, axis=1)

#Gets ids that were empty (ones that were not covered
def get_empty_ids():
    tmp = pd.DataFrame({'sentence_locations' : sentence_locations, 'id':articles.id})
    return tmp[tmp['sentence_locations'] == {}]['id'].values
get_empty_ids()

def remove_uncovered():
    tmp = articles
    tmp['story_sentence_index'] = sentence_locations
    tmp = tmp[~tmp['id'].isin(failed_ids)]
    tmp = tmp[~tmp['id'].isin(get_empty_ids())]
    
    print("Coverage: {0:.5}%".format(((len(tmp) / len(articles)) ) * 100))
    return tmp

articles = remove_uncovered()

#---- Saving dataframe ----#
articles.to_pickle('../data/processed/df_comprehensive_REGEX.pkl')