# DataFrame Structures

For our tasks, we've developed some standardized DataFrame structures to facilitate re-use.

It is encouraged to re-format any new data into the same structures.

## Input Standard DataFrame

`data/processed/input_standard_dataframe.pkl`

![img](https://i.imgur.com/7gXFkDk.png)
- `id` : Unique ID identifying each newspaper article
- `source`: Source of a newspaper article (for example newspaper name)
- `date`: Date of publishing
- `title`: Article title
- `byline`: Author of article
- `section`: Section and page of newspaper
- `length`: number of words in article
- k fields where k is the number of agencies or groups. Each field is a binary variable consisting of 0 or 1, 1 indicating that article mentions agency.
- `agencies`: array of all agencies mentioned by an article
- `story_sentences`: array of sentences of article
- `num_sentences`: number of sentences
- `story_sentence_index`: sentence index where an agency is mentioned

## Article Sentiment Standard Dataframe

This dataframe is the same as the Input Standard Dataframe, but with a few columns added.

`data/processed/article_sentiment_standard_dataframe.pkl`

![img](https://i.imgur.com/RSg9HoP.png)

- `id` : Unique ID identifying each newspaper article
- `source`: Source of a newspaper article (for example newspaper name)
- `date`: Date of publishing
- `title`: Article title
- `byline`: Author of article
- `section`: Section and page of newspaper
- `length`: number of words in article
- k fields where k is the number of agencies or groups. Each field is a binary variable consisting of 0 or 1, 1 indicating that article mentions agency.
- `agencies`: array of all agencies mentioned by an article
- `story_sentences`: array of sentences of article
- `num_sentences`: number of sentences
- `story_sentence_index`: dictionary of list. sentence index where an agency is mentioned
- `buffered_story_sentence_index`: dictionary of list. sentence indices which takes into account the buffer specified.
- `senti_per_agency`: same structure as `buffered_story_sentence_index`. However, each buffered sentence is converted to its sentiment score.
- `senti_avg_per_agency` Each agency in `senti_per_agency` contains multiple buffered sentences. These sentences' sentiment scores are average.
- `senti_full_article` sentiment of the entire article
