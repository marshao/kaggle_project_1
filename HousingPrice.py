# /usr/bin/python
# -*- encoding:utf-8 -*-

import xgboost as xgb
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from sklearn.preprocessing import MinMaxScaler
import pandas as pd
import csv

def load_data(file=None):
	# Combine file is the combination of training set and testing set, incase there are any missing feature value in
	# either file. Training: ID:1: 1460, Testing: ID:1461: 2919
	if file is None:
		file = 'combine.csv'
	data = pd.read_csv(file, header=0, index_col='Id')
	pd.set_option('display.width', 200)

	# Replace NA in Alley columns with No_Alley
	data.loc[(data.Alley.isnull()), 'Alley'] = 'No_Alley'

	# For utilities column, there are only [AllPub, NoSwWa] in training set, and [AllPub] only in testing set.
	# So I treat this feature as categorical. There are 2 missing value in testing set. I will just make it a AllPub
	# since AllPub are in most of the houses.
	data.loc[(data.Utilities.isnull()), 'Utilities'] = 'AllPub'

	# There is 1 Nan value in Exterior1st which is also Nan in Exterior2nd. The house is remodeled in 2007.
	# I assume the houses which be built or remodeled in same year should use similar materials.
	# So I choose the most popular material in 2007 for these two missing values
	exterior_miss_years = data.loc[(data.Exterior1st.isnull())]['YearRemodAdd']
	for yr in exterior_miss_years:
		data_exterior = data.loc[data['YearRemodAdd'] == yr][['Exterior1st', 'Exterior2nd']]
		exterior1st = data_exterior.Exterior1st.value_counts().index[0]
		exterior2nd = data_exterior.Exterior2nd.value_counts().index[0]
		data.loc[(data.Exterior1st.isnull()) & (data['YearRemodAdd'] == yr), 'Exterior1st'] = exterior1st
		data.loc[(data.Exterior2nd.isnull()) & (data['YearRemodAdd'] == yr), 'Exterior2nd'] = exterior2nd

	# In columns MasVnrType and MasVnrArea, there are values with None in Type and 0 in Area, and NA in both.I believe
	# the None value is ok value. So just treat the NA value same as None
	data.loc[(data.MasVnrType.isnull()),  'MasVnrArea'] = 0
	data.fillna(value='None', inplace=True)


	one_hot_cols = ['MSZoning', 'Alley', 'LotShape', 'LandContour', 'LotConfig', 'LandSlope', 'Neighborhood',
	                'Condition1', 'Condition2', 'BldgType', 'HouseStyle', 'RoofStyle', 'RoofMatl',
	                'Exterior1st', 'Exterior2nd', 'MasVnrType']
	for col in one_hot_cols:
		data = one_hot_encode(data, col)

	categorical_cols=['Street',  'Utilities']
	for col in categorical_cols:
		data = categorical(data, col)

	min_max_scaler_cols = ['YearBuilt', 'YearRemodAdd']
	data = min_max_scaler(data, min_max_scaler_cols)

	condition_col = ['ExterQual', 'ExterCond']
	for col in condition_col:
		conditions_category(data, col)

	print(data['ExterCond'])


def one_hot_encode(data, column):
	if not include_null(data, column):
		data = data.join(pd.get_dummies(data[column], prefix=column))
		data.drop(column, axis=1, inplace=True)
	return data

def categorical(data, column):
	if not include_null(data, column):
		data[column] = pd.Categorical(data[column]).codes
	return data

def min_max_scaler(data, column):
	data_before  = data[column]
	scaler = MinMaxScaler()
	scaler.fit(data_before)
	data[column] = scaler.transform(data_before)
	return data

def conditions_category(data, column):
	# Define Condition list
	conditions = ['Ex', 'Gd', 'TA', 'Fa', 'Po']
	if not include_null(data, column):
		for idx, cond in enumerate(conditions):
			print(cond)
			data.loc[(data[column] == cond), column] = idx + 1
	return data

def include_null(data, col):
	if len(data.loc[(data[col].isnull())]) > 0:
		return True
	else:
		return False







if __name__ == "__main__":
	load_data()