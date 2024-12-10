import pandas as pd 
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier

pd.set_option('display.width', 300)
pd.options.display.max_rows = None
file = pd.read_csv("../final_data.csv")

desired_column_order = [
    # "paper_id",  
    # "year", 
    "title", 
    "author_keyword", 
    "index_term", 
    "subject_code", 
    # "subject_area",
    # "subject_abbrev",   
    "country", 
    "city",
    "affiliation",
]


# prepare data

#drop na &dup
ordered_df = file[desired_column_order].dropna().drop_duplicates()


# clean data
one_hot_feature = [
    "title", 
    "author_keyword", 
    "index_term", 
    "country", 
    "city",
]




# one hot encoding

temp = ordered_df[one_hot_feature]
one_hot_df = pd.get_dummies(temp, columns=one_hot_feature,drop_first=True)





feature_column = [
    "title", 
    "author_keyword", 
    "index_term", 
    "subject_code", 
    "country", 
    "city",
]

#remove one hot feature to avoid unexpected label encoding
for col in  one_hot_feature:
    if col in feature_column:
        feature_column.remove(col)



# Initialize the LabelEncoder
le = LabelEncoder()

feature = ordered_df[feature_column]
# Apply label encoding to each of the categorical columns
for col in feature_column:
    feature[col] = le.fit_transform(feature[col])







one_hot_df.columns = one_hot_df.columns.str.replace(',', ' ')
one_hot_df.columns = one_hot_df.columns.str.replace('[', ' ')
one_hot_df.columns = one_hot_df.columns.str.replace(']', ' ')
one_hot_df.columns = one_hot_df.columns.str.replace('<', ' ')

#merge one hot and label encoding feature
final_df = pd.concat([feature, one_hot_df], axis=1)
print(final_df)





# Label encoding target
le = LabelEncoder()

# Separate features and target
X = final_df
y = le.fit_transform(ordered_df["affiliation"].dropna())

# Split data into training and test sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=69)




model = RandomForestClassifier(n_estimators=100, random_state=69)
model.fit(X_train, y_train)

y_pred = model.predict(X_test)

print("Accuracy:", accuracy_score(y_test, y_pred))
print("Confusion Matrix:\n", confusion_matrix(y_test, y_pred))
print("Classification Report:\n", classification_report(y_test, y_pred, target_names=le.classes_))
