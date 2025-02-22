# -*- coding: utf-8 -*-
"""Chatbot.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1B1FjTd2NWEHf7uTPV2hhjQMDmA8VYiLU
"""

import nltk
import pandas as pd
import numpy as np
import string
from keras.utils import to_categorical
import matplotlib.pyplot as plt

f= open('dialogs.txt', "r")
print(f.read())

df= pd.read_csv('dialogs.txt',names=('Query','Response'), sep=('\t'))

df

df.shape

df.columns

df.info

df.describe()

df.nunique()

df.isnull().sum()

df['Query'].value_counts()

df['Response'].value_counts()



Text=df['Query']

!pip install nltk
import nltk
nltk.download('vader_lexicon')

from nltk.sentiment.vader import SentimentIntensityAnalyzer
sid= SentimentIntensityAnalyzer()
for sentence in Text:
    print(sentence)

    ss=sid.polarity_scores(sentence)
    for k in ss:
      print('{0}:{1},'.format(k,ss[k]),end='')
    print()

analyzer= SentimentIntensityAnalyzer()
df['rating']= Text.apply(analyzer.polarity_scores)
df=pd.concat([df.drop(['rating'],axis=1),df['rating'].apply(pd.Series)],axis=1)

df

from wordcloud import WordCloud
def wordcloud(df,label):

  subset=df[df[label]==1]
  text=df.Query.values
  wc= WordCloud(background_color='black',max_words=1000)

  wc.generate(" ".join(text))

  plt.figure(figsize=(20,20))
  plt.subplot(221)
  plt.axis("off")
  plt.title("Words frequented in {}".format(label), fontsize=20)
  plt.imshow(wc.recolor(colormap='gist_earth', random_state=244), alpha=0.98)

wordcloud(df,'Query')

wordcloud(df,'Response')

import re

punc_lower= lambda x: re.sub('[%s]' % re.escape(string.punctuation),' ',x.lower())

remove_n= lambda x: re.sub("\n"," ",x)

remove_non_ascii= lambda x: re.sub(r'[^\x00-\x7f]',r' ',x)

alphanumeric=lambda x: re.sub('\w*\d\w*',' ',x)

df['Query']= df['Query'].map(alphanumeric).map(punc_lower).map(remove_n).map(remove_non_ascii)

df['Response']= df['Response'].map(alphanumeric).map(punc_lower).map(remove_n).map(remove_non_ascii)

df

pd.set_option('display.max_rows',3800)

df

imp_sent=df.sort_values(by='compound',ascending=False)

imp_sent.head()

pos_sent= df.sort_values(by='pos',ascending=False)

pos_sent.head()

neg_sent= df.sort_values(by='pos',ascending=False)

neg_sent.head()

neu_sent= df.sort_values(by='pos',ascending=False)

neu_sent.head()

from sklearn.feature_extraction.text import TfidfVectorizer

tfidf= TfidfVectorizer()

factors= tfidf.fit_transform(df['Query']).toarray()

tfidf.get_feature_names_out()

!pip install nltk
import nltk
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
import numpy as np
nltk.download('stopwords')
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_distances

def lemmatization_sentence(sentence):
  lemmatizer= WordNetLemmatizer()
  stop_words= set(stopwords.words('english'))
  tokens= nltk.word_tokenize(sentence)
  lemmas= [lemmatizer.lemmatize(word) for word in tokens if word not in stop_words]
  return ' '.join(lemmas)

from sklearn.metrics.pairwise import cosine_distances
from nltk.stem import WordNetLemmatizer
import nltk
nltk.download('wordnet')
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer

# Assuming 'factors', 'df', and 'tfidf' are defined somewhere in your code.

# Define lemmatization function
def lemmatization_sentence(sentence):
    lemmatizer = WordNetLemmatizer()
    tokens = nltk.word_tokenize(sentence)
    lemmatized_tokens = [lemmatizer.lemmatize(token) for token in tokens]
    return ' '.join(lemmatized_tokens)

def chatbot(query):
    query = lemmatization_sentence(query)
    query_vector = tfidf.transform([query]).toarray()
    similar_score = 1 - cosine_distances(factors, query_vector)
    index = similar_score.argmax()

    matching_question = df.loc[index]['Query']
    response = df.loc[index]['Response']
    pos_score = df.loc[index]['pos']
    neg_score = df.loc[index]['neg']
    neu_score = df.loc[index]['neu']
    confidence = similar_score[index]

    chat_dict = {
        'match': matching_question,
        'response': response,
        'score': confidence,
        'pos': pos_score,
        'neg': neg_score,
        'neu': neu_score
    }
    return chat_dict

nltk.download('punkt')

while True:
    query = input('User: ')
    if query.lower() == 'exit':
        break

    response = chatbot(query)

    if response['score'] <= 0.2:
        print('BOT: Please rephrase your question.')
    else:
        print('Logs:')
        print(' Matched Question:', response['match'][0] if isinstance(response['match'], (list, np.ndarray)) else response['match'])
        print(' Confidence Score: {:.2f}%'.format(response['score'][0] * 100) if isinstance(response['score'], (list, np.ndarray)) else ' Confidence Score:', response['score'])
        print(' Positive Score:', response['pos'][0] if isinstance(response['pos'], (list, np.ndarray)) else response['pos'])
        print(' Negative Score:', response['neg'][0] if isinstance(response['neg'], (list, np.ndarray)) else response['neg'])
        print(' Neutral Score:', response['neu'][0] if isinstance(response['neu'], (list, np.ndarray)) else response['neu'])
        print('BOT: ',response['response'])