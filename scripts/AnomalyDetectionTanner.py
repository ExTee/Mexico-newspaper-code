# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""
import pandas as pd
import numpy as np
from statsmodels.tsa.seasonal import seasonal_decompose
from sklearn.preprocessing import StandardScaler

from PyAstronomy.pyasl import generalizedESD

PREPROCESSED_DF = '../data/processed/Input_Standard_Dataframe.pkl'
reforma_df = pd.read_pickle(PREPROCESSED_DF)[pd.read_pickle(PREPROCESSED_DF)['source'] == 'Reforma (Mexico)']

def buildDFCollection(df):
    
    

    df_sat = df.set_index('date').resample('w-sat',label='left').sum().iloc[:,1:-1]
    df_sun = df.set_index('date').resample('w-sun',label='left').sum().iloc[:,1:-1]
    df_mon = df.set_index('date').resample('w-mon',label='left').sum().iloc[:,1:-1]
    df_tue = df.set_index('date').resample('w-tue',label='left').sum().iloc[:,1:-1]
    df_wed = df.set_index('date').resample('w-wed',label='left').sum().iloc[:,1:-1]
    df_thu = df.set_index('date').resample('w-thu',label='left').sum().iloc[:,1:-1]
    df_fri = df.set_index('date').resample('w-fri',label='left').sum().iloc[:,1:-1]
    
    
    df_collection = [(df_sat, "Saturday"),
                          (df_sun,   "Sunday"),
                          (df_mon, "Monday"), 
                          (df_tue, "Tuesday"),
                          (df_wed, "Wednesday"),
                          (df_thu, "Thursday"),
                          (df_fri, "Friday")                          
                         ]
    return df_collection



def buildWeeklyMentions(df_collection, entity_names):
    entity_weekly_aggregations = []
    for entity_name in entity_names: # iterate over all agencies
                
        entity_data = []     
        for (df, day) in df_collection: # iterate over the collection of data frame that vary be week start time
            entity_mentions = df[entity_name].values
            
            entity_data.append(entity_mentions)
            
        entity_data = np.array(entity_data)  
        entity_data = np.transpose(entity_data)
    
        # we'll add the agency name to each column name to make it easier to remember which agency's data you're viewing
        
        headers = []
        days = ["Saturday", "Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
        for day in days:
            day_w_entity = entity_name + ": " + day
            headers.append(day_w_entity)
    
        
        entity_df = pd.DataFrame(data = entity_data, columns=headers)
        
        entity_df.name = entity_name
        
        entity_weekly_aggregations.append(entity_df)
        
    return entity_weekly_aggregations


def normalize_df(df):
    sc = StandardScaler()
    return pd.DataFrame(data = sc.fit_transform(df), index = df.index, columns = df.columns)

    
def seasonal_decompose_df(df):
    df_seasonal = df.copy()
    df_trend = df.copy()
    df_residual = df.copy()
    
    for col in df.columns:
        d = seasonal_decompose(df[col])
        df_seasonal[col] = d.seasonal
        df_trend[col] = d.trend
        df_residual[col] = d.resid
    
    return (
        df_seasonal,
        df_trend,
        df_residual
           )
    
    
def agencyAnomalyByStartday(df_collection_SD, days):
    
    ESD_output_by_start_day = []
    for day_index, start_time_df in enumerate(df_collection_SD):
        df = start_time_df[-1] # get residual df
        
        output = {}
        for col_index, agency in enumerate(df.columns):
            esd_out = generalizedESD(df[agency].fillna(0).values, 12, alpha = 0.1, fullOutput=False)
            output[agency] = list(sorted(esd_out[1]))
            

        ESD_output_by_start_day.append((days[day_index], output))
    
    return ESD_output_by_start_day

def aggregateAgencyAnomaly(ESD_output_by_start_day, entities, days):
    ESD_output_by_entity = []
    for entity in entities:
        entity_data = [entity]
        anomaly_dict = {}
        for index, ESD in enumerate(ESD_output_by_start_day):
            anomaly_dict[days[index]] = list(sorted(ESD[1][entity]))
        entity_data.append(anomaly_dict)
        ESD_output_by_entity.append(entity_data)
        
    return ESD_output_by_entity

def sortTup(tuplist):
     return sorted(tuplist, key=lambda x: x[0])

def mergeIntervals(interval_list):
    anomaly_ranges_final = []
    front = interval_list[0][0]
    back  = interval_list[0][1]
    
    for interval in interval_list:
        if interval[0] >= front and interval[0] <= back: # start of interval in previous interval range
            if interval[1] > back: #end of this interval greater than current back
                back = interval[1]
            else: # entire interval contained in current range, do nothing
                pass
                
        else: # beginning of cur interval greater than range of front and back, we have a new interval
            anomaly_ranges_final.append((front, back)) # we add old range to our interval list and begin a new interval
            front = interval[0]
            back = interval[1]
    
    anomaly_ranges_final.append((front, back))
    return anomaly_ranges_final

def mergeAnomalies(ESD_output_by_agency, df_collection, datelist):
    anomalies_foreach_agency = []

    for agency_data in ESD_output_by_agency:    
        anomalies = agency_data[1]
        all_agency_intervals = [agency_data[0]]
        interval_list = []
    
        for week_index, week in enumerate(anomalies):        
            anomaly_list = anomalies[week]
            
            for anomaly in anomaly_list: 
                # we're going to get a list of indices from the datelist for each anomaly
                # e.g. Saturday: index 250 will map to datelist[1750]
                tup = df_collection[week_index]
                df = tup[0]                         # dataframe corresponding to the week_index
                date = df.index.values[anomaly]
                datelist_index = datelist.index(date)
    
                indices = (datelist_index, datelist_index+6) # indices of the datelist that encompany the anomaly week
    
                interval_list.append(indices)
                
            
    #     no_duplicates_intervals = list(set(interval_list)) 
    #     sorted_intervals = sortTup(no_duplicates_intervals)   
    #     merged_intervals = mergeIntervals(sorted_intervals)
        
            
        all_agency_intervals.append(mergeIntervals(sortTup(list(set(interval_list))))) # appends list of indices, sorted by 1st element, merged, with duplicates removed    
        anomalies_foreach_agency.append(all_agency_intervals)
        
    return anomalies_foreach_agency 

    # now we want to smooth the intervals to a find a date range that encompasses the whole anomaly

def rangeToDates(anomaly_ranges, datelist):
    anomaly_dates_foreach_entity = []
    for anomalies in anomaly_ranges:
        entity_name = anomalies[0]
        anomalies = anomalies[1]
        anomaly_dates = [entity_name]
        for anomaly in anomalies:
            date_start = pd.to_datetime(datelist[anomaly[0]]).date()
            date_end = pd.to_datetime(datelist[anomaly[1]]).date()
            date_range = (date_start, date_end)
            anomaly_dates.append(date_range)
        anomaly_dates_foreach_entity.append(anomaly_dates)
        
    return anomaly_dates_foreach_entity


def buildAnomalyDF(article_df):
    entities = article_df.columns.values[8:30]

    df_collection = buildDFCollection(article_df)

#    entity_weekly_aggregations = buildWeeklyMentions(df_collection, entities)
    
    
    df_collection_normalized = [normalize_df(agency[0]) for agency in df_collection]
    

#    df_start_times_normalized = [normalize_df(df) for df in entity_weekly_aggregations]
    
    
    
    df_collection_SD = [] # reforma collection with normalization and seasonal decomposition
    for df in df_collection_normalized:
        (seasonal, trend, residual) = seasonal_decompose_df(df)
        df_collection_SD.append((seasonal,trend,residual))
        
    days = ['Saturday', 'Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    
    
    ESD_output_by_start_day = agencyAnomalyByStartday(df_collection_SD, days)
    
    
    ESD_output_by_entity= aggregateAgencyAnomaly(ESD_output_by_start_day, entities, days)
    
    
    start = df_collection[0][0].index[0]
    end = df_collection[-1][0].index[-1]
    
    # datelist
    datelist = pd.date_range(start, end).tolist()  # contains every day in dataframe
    datelist = [time.to_datetime64() for time in datelist]  


    
    anomaly_ranges = mergeAnomalies(ESD_output_by_entity, df_collection, datelist)
    
    anomaly_dates = rangeToDates(anomaly_ranges, datelist)
    
    
    
    
    
    start_dates = []
    end_dates = []
    name_list = []
    for entity in anomaly_dates:
        entity_name = entity[0]
        entity_dates = entity[1:]    
        
        
        for date in entity_dates:
            start_dates.append(date[0])
            end_dates.append(date[1])
            name_list.append(entity_name)
            
    anomaly_df = pd.DataFrame(data = [name_list,start_dates, end_dates])
    anomaly_df = anomaly_df.transpose()
    anomaly_df.columns = ['entity', 'start_date', 'end_date']
    anomaly_df = anomaly_df.sort_values(by=['start_date'])
    anomaly_df = anomaly_df.reset_index(drop=True)
    
    
    ############## will need to create different ID to aaron's liking #####
    anomaly_df['id'] = anomaly_df.index.values
    ########################################################
    
    
    
    
    return anomaly_df
    
    
    
reforma_df = pd.read_pickle(PREPROCESSED_DF)[pd.read_pickle(PREPROCESSED_DF)['source'] == 'Reforma (Mexico)']

anomaly_df = buildAnomalyDF(reforma_df)

anomaly_df.to_pickle('anomaly_df.pkl')
print(anomaly_df)



