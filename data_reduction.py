import pandas as pd
import numpy as np

# Read the two relevant files up front and load them into the global scope
xlsx_temp_series = pd.ExcelFile('temp_series_final_03_07_18_copy_0.xlsx')
xlsx_modulation  = pd.ExcelFile('modulation_flux_bias_final_03_08_18_copy_0.xlsx')

df_label_names = {'set 1 chan 1':'Unnamed: 1', 'set 1 chan 2':'Unnamed: 2', 'set 2 chan 1':'Unnamed: 4', 'set 2 chan 2':'Unnamed: 5', 
'set 3 chan 1':'Unnamed: 7', 'set 3 chan 2':'Unnamed: 8', 'srs gain':'Unnamed: 9', 'distance':'Unnamed: 10', 
'resistance':'Unnamed: 11', 'flux bias current':'Unnamed: 12'}

# DataSheet object for our data from the scope traces of one data collection run (i.e. one sheet of data on the Excel files).
class DataSheet:
	def __init__(self, xlsx, filename_str='', sheet_num = 0):
		'''
		Create a data object given its Excel Pandas object and sheet number. (And also a string that says which filename it comes from)
		'''

		self.description = 'From "{}", sheet number {}'.format(filename_str, sheet_num)

		sheet_data = pd.read_excel(xlsx, sheet_num)

		# Get the three data sets
		set_1 = []
		set_2 = []
		set_3 = []

		for i in range(1, 1001): # Data is in rows 1 to 1000 (inclusive)

			tuple_1 = (sheet_data.loc[i, df_label_names['set 1 chan 1']], sheet_data.loc[i, df_label_names['set 1 chan 2']])
			set_1.append(tuple_1)

			tuple_2 = (sheet_data.loc[i, df_label_names['set 2 chan 1']], sheet_data.loc[i, df_label_names['set 2 chan 2']])
			set_2.append(tuple_2)

			tuple_3 = (sheet_data.loc[i, df_label_names['set 3 chan 1']], sheet_data.loc[i, df_label_names['set 3 chan 2']])
			set_3.append(tuple_3)

		self.set_1 = set_1
		self.set_2 = set_2
		self.set_3 = set_3

		# Dictionary with the setup parameters for when the data set was taken
		setup_params = {'srs gain':sheet_data.loc[1, df_label_names['srs gain']], 'distance':sheet_data.loc[1, df_label_names['distance']], 
		'resistance':sheet_data.loc[1, df_label_names['resistance']], 'flux bias current':sheet_data.loc[1, df_label_names['flux bias current']]}

		self.setup_params = setup_params


	# Sorts data sheet set by the channel 1 reading
	def sort_set(data_sheet_set):

		data_sheet_set = sorted(data_sheet_set, key = lambda x: x[0])
		return data_sheet_set

	# Combine all three data sets for a single sheet
	def combine_sets(data_sheet):

		set_1 = data_sheet.set_1
		set_2 = data_sheet.set_2
		set_3 = data_sheet.set_3

		combined_set = []

		for i in range(len(set_1)):
			combined_set.append(set_1[i])
			combined_set.append(set_2[i])
			combined_set.append(set_3[i])

		return combined_set

	# Mean subtract all of the sets of the data sheet object
	def mean_subtract(data_sheet):

		set_1 = data_sheet.set_1
		set_2 = data_sheet.set_2
		set_3 = data_sheet.set_3

		chan_2_set_1 = np.asarray([x[1] for x in set_1])
		chan_2_set_2 = np.asarray([x[1] for x in set_2])
		chan_2_set_3 = np.asarray([x[1] for x in set_3])

		set_1_mean = np.mean(chan_2_set_1)
		set_2_mean = np.mean(chan_2_set_2)
		set_3_mean = np.mean(chan_2_set_3)

		chan_2_set_1 = list(chan_2_set_1 - set_1_mean)
		chan_2_set_2 = list(chan_2_set_2 - set_2_mean)
		chan_2_set_3 = list(chan_2_set_3 - set_3_mean)

		set_1 = [(x[0], y) for x,y in zip(set_1, chan_2_set_1)]
		set_2 = [(x[0], y) for x,y in zip(set_2, chan_2_set_2)]
		set_3 = [(x[0], y) for x,y in zip(set_3, chan_2_set_3)]

		data_sheet.set_1 = set_1
		data_sheet.set_2 = set_2
		data_sheet.set_3 = set_3

