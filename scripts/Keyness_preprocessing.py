#!/usr/bin/env python
# coding: utf-8

# In[1]:


import numpy as np

import scipy as sp

import pandas as pd

import pickle

from tqdm import tqdm


# In[2]:



#Load the dataframe
with open('./data/temp_anomaly_df.pkl', 'rb') as handle:
       temp_anomaly_df = pickle.load(handle)



# In[3]:


#Check the type
type(temp_anomaly_df)


# In[4]:


temp_anomaly_df.head()


# In[5]:


np.size(temp_anomaly_df)


# In[14]:

#Extract the list of agencies
agencies = np.unique(temp_anomaly_df["Agency"])
np.size(agencies)


# In[15]:


agencies


# In[16]:



with open('./data/dataframe_for_aaron/sentiment_processed_anomalies_v3.pkl', 'rb') as handle:
        anomaly_df = pickle.load(handle)


# In[17]:

#extracting the index of anomalies
anomaly_id = anomaly_df["id"]
anomaly_id


# In[18]:



#anomaly_path = './data/tf-idf/anomaly_by_agencies.feather'
#anomaly_by_agencies = feather.read_dataframe(anomaly_path)
with open('./data/temp_article_df.pkl', 'rb') as handle:
       temp_article_df = pickle.load(handle)



# In[19]:

#Extract nonanonalies
temp_nonanomaly_df = temp_article_df[~temp_article_df["id"].isin(anomaly_id)]


#Let's take 147-th row as an example to see whether it works
# In[11]:


temp_nonanomaly_df.loc[147]


# In[12]:


temp_anomaly_df.loc[147]


# In[13]:


["".join(flatten_to_strings(temp_anomaly_df["all_text"][147]))]


# In[26]:


temp_anomaly_df["Agency"][147]




# In[20]:

#Build a dictionary of non-anomalies

dict_nonanomalies = {}

for j in tqdm(np.arange(22)):
    dict_nonanomalies[agencies[j]]= ["".join(temp_nonanomaly_df[temp_nonanomaly_df["agency"] ==agencies[j]]["full_text"].tolist())]


# In[43]:


temp_anomaly_df["Agency"]


# In[21]:
#Flatten the list of sentences into one big string

def flatten_to_strings(A):
    rt = []
    for i in A:
        if isinstance(i,list): rt.extend(flatten_to_strings(i))
        else: rt.append(i)
    return rt


# In[22]:

#Make a dictionary of sub-dictionaries where each sub-dictionary will have {(ANOMALY:anomaly texts), (NONANOMALY:non-anomaly texts)}
dict_of_dicts = {}
s = " "
for i in tqdm(np.arange(149)):
    dict_of_dicts[i] = {"ANOMALY":[s.join(flatten_to_strings(temp_anomaly_df["all_text"][i]))] , "NONANOMALY": dict_nonanomalies[temp_anomaly_df["Agency"][i]] }


# In[49]:

#Take a look
#dict_of_dicts[0]
dict_of_dicts[0]
#dict_of_dicts[0]["NONANOMALY"]


# In[24]:

#Extract it so that we can take in the R script a
for i in tqdm(np.arange(149)):
    pd.DataFrame(data=dict_of_dicts[i]).to_feather("./data/Keyness_dfs/keyness_"+str(i+1)+".feather")


# In[29]:


dummy_df.to_feather("./data/dummy_INM_keyness_df.feather")






