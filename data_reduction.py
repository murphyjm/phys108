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

		self.combined_set = []

		# Dictionary with the setup parameters for when the data set was taken
		setup_params = {'srs gain':sheet_data.loc[1, df_label_names['srs gain']], 'distance':sheet_data.loc[1, df_label_names['distance']], 
		'resistance':sheet_data.loc[1, df_label_names['resistance']], 'flux bias current':sheet_data.loc[1, df_label_names['flux bias current']]}

		self.setup_params = setup_params


	# Sorts data sheet set by the channel 1 reading
	def sort_set(self, data_sheet_set):

		data_sheet_set = sorted(data_sheet_set, key = lambda x: x[0])
		return data_sheet_set

	# Combine all three data sets for a single sheet
	def combine_sets(self):

		set_1 = self.set_1
		set_2 = self.set_2
		set_3 = self.set_3

		combined_set = []

		for i in range(len(set_1)):
			combined_set.append(set_1[i])
			combined_set.append(set_2[i])
			combined_set.append(set_3[i])

		self.combined_set = combined_set
		return combined_set

	# Mean subtract all of the sets of the data sheet object
	def mean_subtract(self):

		set_1 = self.set_1
		set_2 = self.set_2
		set_3 = self.set_3

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

		self.set_1 = set_1
		self.set_2 = set_2
		self.set_3 = set_3

	# Average the points of a data set given a window size of number of points
	def window_avg(self, data_set, n=10):

		avg_data = []

		data_set = self.sort_set(data_set)

		for i in range(0, len(data_set), n):

			curr_sum_x = 0
			curr_sum_y = 0

			for j in range(n):

				curr_sum_x += data_set[i + j][0]
				curr_sum_y += data_set[i + j][1]

			avg_x = curr_sum_x / n
			avg_y = curr_sum_y / n

			avg_data.append((avg_x, avg_y))

		return avg_data

	# # Helper function for linear_gnd_trend()
	# # Don't call as a client. Should be private.
	# def find_kink_locs(self, data_set):

	# 	chan_1, chan_2 = list(zip(*data_set))

	# 	d_dx_size = 15
	# 	curr_size = len(data_set)

	# 	window_size = int(curr_size / d_dx_size)

	# 	avg_set = self.window_avg(data_set, n=window_size)

	# 	chan_1_avg, chan_2_avg = list(zip(*avg_set))

	# 	chan_2_diffs = np.diff(chan_2_avg)
	# 	chan_1_diffs = np.diff(chan_1_avg)

	# 	# Take element wise derivative
	# 	chan_1_diffs = chan_1_diffs + 1e-10 # Padding so we don't divide by zero
	# 	d_dx = np.divide(chan_2_diffs, chan_1_diffs)
	# 	#d_dx = np.insert(d_dx, 0, d_dx[0]) # d_dx length will be reduced by 1 so just prepend the first element to it

	# 	# Find value of the slope in the superconducting region
	# 	idx_zero = np.abs(chan_1_avg).argmin() 

	# 	super_slope = d_dx[idx_zero]

	# 	slopes = np.divide(d_dx, super_slope) # Normalize the slopes by the size of the slope in the superconducting region

	# 	#threshold = 3 # Should be obvious where the kinks are in the slope

	# 	slope_diffs = np.diff(slopes)
	# 	slope_diffs = np.append(slope_diffs, slope_diffs[-1])

	# 	slope_diffs = np.abs(slope_diffs)

	# 	mid_idx = int(len(slope_diffs) / 2.0)

	# 	loc_1 = slope_diffs[0:mid_idx].argmax() + 1
	# 	loc_2 = slope_diffs[mid_idx:len(slope_diffs)].argmax() + len(slope_diffs[0:mid_idx]) + 1

	# 	# loc_1 = 0
	# 	# loc_2 = 0

	# 	# for i in range(len(slope_diffs)):

	# 	# 	if loc_1 == 0 and abs(slope_diffs[i]) >= threshold:
	# 	# 		loc_1 = i + 1

	# 	# 	if loc_1 != 0 and abs(slope_diffs[i]) >= threshold:
	# 	# 		loc_2 = i + 1

	# 	chan_1_loc_1 = np.abs(np.asarray(chan_1) - chan_1_avg[loc_1]).argmin()
	# 	chan_1_loc_2 = np.abs(np.asarray(chan_1) - chan_1_avg[loc_2]).argmin()

	# 	return chan_1_loc_1, chan_1_loc_2, d_dx, idx_zero


	# # Computes the linear grounding trend that is seen in the modulation series. Returns a set with it removed and the fit characteristics
	# def linear_gnd_trend(self, data_set):

	# 	loc_1, loc_2, d_dx, idx_zero = self.find_kink_locs(data_set)

	# 	chan_1, chan_2 = zip(*data_set)

	# 	chan_1 = np.asarray(chan_1)
	# 	chan_2 = np.asarray(chan_2)

	# 	chan_1_super = chan_1[loc_1:loc_2]
	# 	chan_2_super = chan_2[loc_1:loc_2]

	# 	m, b = np.polyfit(chan_1_super, chan_2_super, 1)

	# 	print("Average slope over superconducting region: {}".format((chan_2[loc_2] - chan_2[loc_1])/(chan_1[loc_2] - chan_1[loc_1])))

	# 	print("Polyfit slope over superconducting region: {}".format(m))

	# 	linear_trend = chan_1 * m + b

	# 	chan_2 = chan_2 - linear_trend

	# 	new_set = list(zip(chan_1, chan_2))

	# 	return new_set, m, b, loc_1, loc_2, d_dx, idx_zero


