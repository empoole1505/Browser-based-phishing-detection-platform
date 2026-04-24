import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer #import libraries

email_data = pd.read_csv('/home/ethan/Desktop/arc/archive/bigger_phish.csv', low_memory=False) #read the dataset in the location
email_data.columns = email_data.columns.str.strip().str.lower() 

email_data.dropna(subset=['body', 'label', 'subject'], inplace=True) #drop empty rows

x = email_data['body', 'subject'].astype(str) 
y = email_data['label'] 
#assign x data to the body and subject of an email and then assign y to label of whether emails are phishing or benign
Xtrain, Xtest, Ytrain, Ytest = train_test_split(
x, y, test_size=0.2, random_state=50, stratify=y  #split data into train and test data
)

vectorizer = TfidfVectorizer(lowercase=True, stop_words='english', max_features=5000) #enumerate body and subject of data into vectors (test and train data) and asign the enumerated data to new variable
X_train_tfidf = vectorizer.fit_transform(Xtrain)
X_test_tfidf = vectorizer.transform(Xtest)

clf = RandomForestClassifier(n_estimators=100, n_jobs=-1, random_state=42) 
clf.fit(X_train_tfidf, Ytrain)
joblib.dump(clf, '/home/ethan/Desktop/wellysai.pkl')
joblib.dump(vectorizer, '/home/ethan/Desktop/vectorizer.pkl')
#train the machine learning model using the training data and output the trained ml to a pkl file