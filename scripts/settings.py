"""
    Settings for running scripts
"""

#Source newspaper (Reforma or Universal)
SOURCE_NEWSPAPER = 'El Universal (Mexico)'
# SOURCE_NEWSPAPER = 'Reforma (Mexico)'
# Each source = new dataframe? or everything together? Then SOURCE_NEWSPAPER should be a list

#Number of sentences around target sentence to consider for sentiment analysis
SENTENCE_BUFFER_WINDOW = 1