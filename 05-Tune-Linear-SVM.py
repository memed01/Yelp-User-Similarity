"""
(V) Hypertune Linear SVM (Best Performing Classifer) & Output Final Classifiers (one per topic) and Print Final Classifier Statistics 
"""

import numpy as np
import pandas as pd
import pickle

from sklearn.cross_validation import train_test_split
from sklearn.grid_search import GridSearchCV
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.svm import LinearSVC
from sklearn.metrics import accuracy_score, precision_score, recall_score, confusion_matrix


##Read in Binary Text Vectorizer
with open("binary_vectorizer.pkl") as f:
    binary_vectorizer = pickle.load(f)
    

##Read In and Clean ABSA Data - Create Binary Flags for Topics & Aggregate to Sentence Level
semeval_data = pd.read_pickle("all_semeval_data.pkl")

food = ["food","FOOD#QUALITY","FOOD#STYLE_OPTIONS","DRINKS#QUALITY","DRINKS#STYLE_OPTIONS","FOOD#GENERAL"]
service = ["service","SERVICE#GENERAL"]
ambience = ["ambience","AMBIENCE#GENERAL"]
value = ["price","FOOD#PRICES","RESTAURANT#PRICES","DRINKS#PRICES"]

topics = ["topic_food","topic_service","topic_ambience","topic_value"]
semeval_data["topic_food"] = 0
semeval_data["topic_service"] = 0
semeval_data["topic_ambience"] = 0 
semeval_data["topic_value"] = 0

semeval_data.ix[absa_data.category.isin(food), "topic_food"] = 1
semeval_data.ix[absa_data.category.isin(service), "topic_service"] = 1
semeval_data.ix[absa_data.category.isin(ambience), "topic_ambience"] = 1
semeval_data.ix[absa_data.category.isin(value), "topic_value"] = 1
semeval_data = absa_data.groupby(by="sentence", as_index=False)[topics].max()


##Test Train Split
semeval_train, semeval_test = train_test_split(semeval_data, test_size=0.25, random_state=4444)


##Function to Hypertune Linear SVM Parameters on Training Set
def tune_linear_svm(vectorizer, train, topic):
	grid={"C": [0.05,0.5,1,1.5,2,5,10], "loss": ["hinge", "squared_hinge"], "class_weight": [None,"balanced"]}

	train_X = vectorizer.transform(train["sentence"]).toarray()
	train_y = train[topic]

	clf = GridSearchCV(LinearSVC(), grid, scoring="recall", cv=3).fit(train_X, train_y)

	print "Best Params for "+topic+":", clf.best_params_
	print "Best Score: "+str(clf.best_score_)
	print ""

	return clf


##Function to Evaluate Final SVM Parameters on Test Set
def final_test_stats(vectorizer, test, clf, topic):
	test_X = vectorizer.transform(test["sentence"]).toarray()
	test_y = test[topic]

	print "Final Statistics for ", topic
	print "Accuracy:  ", accuracy_score(test_y, clf.predict(test_X))
	print "Precision: ", precision_score(test_y, clf.predict(test_X))
	print "Recall:    ", recall_score(test_y, clf.predict(test_X))
	print "Confusion Matrix: "
	print confusion_matrix(test_y, clf.predict(test_X))
	print ""

##Function to Pickle Classifiers for Future Analysis
def pickle_clf(clf, outpickle):
	with open(outpickle, "wb") as f:
		pickle.dump(clf, f)


##Run Functions
print "Grid Searching for Optimal Parameters..."
lsvm_food = tune_linear_svm(binary_vectorizer, semeval_train, "topic_food") 
lsvm_service = tune_linear_svm(binary_vectorizer, semeval_train, "topic_service")
lsvm_ambience = tune_linear_svm(binary_vectorizer, semeval_train, "topic_ambience")
lsvm_value = tune_linear_svm(binary_vectorizer, semeval_train, "topic_value")
print ""

##Print Final Statistics:
print "Tuned Linear SVM Statistics..."
final_test_stats(binary_vectorizer, semeval_test, lsvm_food, "topic_food")
final_test_stats(binary_vectorizer, semeval_test, lsvm_service, "topic_service")
final_test_stats(binary_vectorizer, semeval_test, lsvm_ambience, "topic_ambience")
final_test_stats(binary_vectorizer, semeval_test, lsvm_value, "topic_value")


#Pickle Clasifiers
print "Pickling Classifiers..."
pickle_clf(lsvm_food, "lsvm_food.pkl")
pickle_clf(lsvm_service, "lsvm_service.pkl")
pickle_clf(lsvm_ambience, "lsvm_ambience.pkl")
pickle_clf(lsvm_value, "lsvm_value.pkl")


















