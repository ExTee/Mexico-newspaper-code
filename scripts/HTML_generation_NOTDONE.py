import pandas as pd
from tqdm import tqdm

html_HEADER = """
<HTML>
	<HEAD>
		<meta charset="UTF-8">
		<STYLE TYPE="text/css">
			<!--
.c0 { text-align: center; }
.c1 { text-align: center; margin-top: 0em; margin-bottom: 0em; }
.c2 { font-family: 'Times New Roman'; font-size: 10pt; font-style: normal; font-weight: normal; color: #000000; text-decoration: none; }
.c3 { text-align: center; margin-left: 13%; margin-right: 13%; }
.c4 { font-family: 'Times New Roman'; font-size: 10pt; font-style: normal; font-weight: bold; color: #CC0033; text-decoration: none; }
.c5 { text-align: left; }
.c6 { text-align: left; margin-top: 0em; margin-bottom: 0em; }
.c7 { font-family: 'Times New Roman'; font-size: 14pt; font-style: normal; font-weight: bold; color: #000000; text-decoration: none; }
.c8 { font-family: 'Times New Roman'; font-size: 10pt; font-style: normal; font-weight: bold; color: #000000; text-decoration: none; }
.c9 { text-align: left; margin-top: 1em; margin-bottom: 0em; }
.c10 { page-break-before: always; }
.c11 { font-family: 'Times New Roman'; font-size: 14pt; font-style: normal; font-weight: bold; color: #CC0033; text-decoration: none; }
.c12 { margin-left: 30pt; margin-right: 0pt; margin-top: 0em; margin-bottom: 0em; list-style: none; }
.c13 { margin-left: 0pt; margin-right: 0pt; }
.c14 { margin-top: 0em; margin-bottom: 0em; }
.c15 { text-align: left; margin-left: 30pt; margin-top: -12pt; }
.c16 { border-collapse: collapse; table-layout: auto; width:100%; }
.c17 { width: 480pt; }
.c18 { text-align: left; padding-left: 2pt; vertical-align: top; padding-right: 2pt; }
.c19 { font-family: 'Courier New',Courier; font-size: 10pt; font-style: normal; font-weight: normal; color: #000000; text-decoration: none; }
.c20 { font-family: 'Courier New',Courier; font-size: 10pt; font-style: normal; font-weight: bold; color: #CC0033; text-decoration: none; }
.c21 { font-size: 24pt; font-weight: bold; font-family: 'Cambria'}
.c22 { font-size: 18pt; font-weight: bold; font-family: 'Cambria'}
.c23 { font-family: 'Times New Roman'; font-size: 10pt; font-style: normal; font-weight: bold; color: #1414ba; text-decoration: none; }
.box {width: 20px;
  padding: 2px;
  border: 1px solid gray;
  margin: 0;}
-->
		</STYLE>
        </HEAD>
"""
html_TITLE = """<center><SPAN CLASS="c21">Anomalies for {}</SPAN></center><hr>"""
html_ARTICLE_INFO = """

	<BODY>
		<A NAME="DOC_ID_0_0"></A>
		<!-- Hide XML section from browser
<DOC NUMBER=1><DOCFULL> -->
		<BR>
			<DIV CLASS="c0">
				<P CLASS="c1">
					<SPAN CLASS="c2">{var_cur_doc_number} of {var_total_doc_number} DOCUMENTS</SPAN>
				</P>
			</DIV>
			<BR>
				<DIV CLASS="c0">
					<BR>
						<P CLASS="c1">
							<SPAN CLASS="c2">Reforma (Mexico)</SPAN>
						</P>
					</DIV>
					<BR>
						<DIV CLASS="c3">
							<P CLASS="c1">
								<SPAN CLASS="c2">{var_date}</SPAN>
							</P>
						</DIV>
						<BR>
							<DIV CLASS="c5">
								<P CLASS="c6">
									<SPAN CLASS="c7">
										{var_title}	
									</SPAN>
									</P>
								</DIV>
								<BR>
									<DIV CLASS="c5">
										<P CLASS="c6">
											<SPAN CLASS="c8">BYLINE: </SPAN>
											<SPAN CLASS="c2"> {var_byline} </SPAN>
										</P>
									</DIV>
										<DIV CLASS="c5">
											<P CLASS="c6">
												<SPAN CLASS="c8">SECTION: </SPAN>
												<SPAN CLASS="c2"> {var_section} </SPAN>
												
											</P>
										</DIV>
											<DIV CLASS="c5">
												<P CLASS="c6">
													<SPAN CLASS="c8">LENGTH: </SPAN>
													<SPAN CLASS="c2">{var_num_sentences} sentences</SPAN>
                                                    <BR>
                                                    <SPAN CLASS="c8">ARTICLE ID: </SPAN>
													<SPAN CLASS="c2">{var_article_id}</SPAN>
                                                    <BR>
                                                    <SPAN CLASS="c8">AVERAGE SENTIMENT (for agency): </SPAN>
													<SPAN CLASS="c2">{var_avg_sentiment}</SPAN>
                                                    <BR>
                                                    <SPAN CLASS="c8">ARTICLE OVERALL SENTIMENT: </SPAN>
													<SPAN CLASS="c2">{var_article_sentiment}</SPAN>
												</P>
											</DIV>
    <DIV CLASS="c5"><P CLASS="c9">
"""

html_NORMAL_SENTENCE = """<br><br><SPAN CLASS="c2">[{var_sentence_idx}]&nbsp&nbsp&nbsp&nbsp{var_sentence}</SPAN>"""

html_RED_SENTENCE = """<br><br><SPAN CLASS="c4">[{var_sentence_idx}]&nbsp&nbsp&nbsp&nbsp{var_sentence}</SPAN>"""

html_BLUE_SENTENCE = """<br><br><SPAN CLASS="c23">[{var_sentence_idx}]&nbsp&nbsp&nbsp&nbsp{var_sentence}</SPAN>"""

html_SENTIMENT_BOX = """ <SPAN CLASS="box"> {var_sentiment_score} </SPAN> """


html_ARTICLE_FOOTER = """</DIV><BR>"""

html_FOOTER = """
</BODY></HTML>
"""



#Reading dataframes

#Dataframe containing sentiments of sentences
df_sentiment_processed_anomalies = pd.read_pickle('../data/processed/sentiment_processed_anomalies_v3.pkl')

anomaly_information = pd.read_pickle('data/new_anomaly_df.pkl')
cols = list(anomaly_information.columns.values)
anomaly_information.reset_index(inplace=True)
anomaly_information.columns = ['id'] + cols
anomaly_information.head()

#Loop through all anomalies detected
for anomaly_id in tqdm(list(anomaly_information.id.unique())): 
    _info = anomaly_information[anomaly_information['id'] == anomaly_id].iloc[0]
    start_date = _info['Start Date']
    end_date = _info['End Date']
    agency = _info['Agency']
    
    #Create new html file, write headers and date
    with open(f'data/dataframe_for_aaron/output_htmls_v3/ANOMALY_{anomaly_id}.HTML','w') as f:
        f.write(html_HEADER)
        f.write(html_TITLE.format(agency))
        f.write("""<hr><br><center><SPAN CLASS="c22">Anomaly date: {} to {}</center><br><hr>""".format(start_date, end_date))
    
        #Get anomalous articles for each anomaly
        _anomaly_articles = df_sentiment_processed_anomalies.loc[df_sentiment_processed_anomalies['anomaly_id'] == anomaly_id]
        
        len_df = len(_anomaly_articles)
        #Loop through all articles in an anomaly
        for i in range(len_df):
            series = _anomaly_articles.iloc[i]
            f.write(html_ARTICLE_INFO.format(
                        var_cur_doc_number=i,
                        var_total_doc_number=len_df,
                        var_date=series.date,
                        var_title=series.title,
                        var_byline=series.byline,
                        var_section=series.section,
                        var_num_sentences=series.num_sentences,
                        var_article_id=series.id,
                        var_avg_sentiment=("{0:.3f}".format(series.senti_avg_per_agency[agency])),
                        var_article_sentiment=("{0:.3f}".format(series.senti_full_article))
                    ))
            
            for idx, sentence in enumerate(series.story_sentences):
                if idx in series.buffered_story_sentence_index[agency]:

                    aidx = series.buffered_story_sentence_index[agency].index(idx) #This is the index within the array of located sentences
                    
                    #Write blue sentence for the sentence that matched, red for sentences around.
                    if idx in series.story_sentence_index[agency]:
                        f.write(html_BLUE_SENTENCE.format(var_sentence_idx=idx, var_sentence=sentence))
                    else:
                        f.write(html_RED_SENTENCE.format(var_sentence_idx=idx, var_sentence=sentence))
                        
                    sentiment_score = "{0:.3f}".format(series.senti_per_agency[agency][aidx])
                    f.write(html_SENTIMENT_BOX.format(var_sentiment_score=sentiment_score))
                else:
                    f.write(html_NORMAL_SENTENCE.format(var_sentence_idx=idx, var_sentence=sentence))

            f.write(html_ARTICLE_FOOTER)
        f.write(html_FOOTER) 
    