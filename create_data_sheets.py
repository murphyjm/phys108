from data_reduction import DataSheet, xlsx_modulation, df_label_names
import numpy as np
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.pyplot as plt

NUM_SHEETS_MOD = 32

mod_DataSheets = []
for j in range(NUM_SHEETS_MOD):
    data_sheet_j = DataSheet(xlsx_modulation, 'modulation', sheet_num = j)
    data_sheet_j.mean_subtract()
    data_sheet_j.combine_sets()
    data_sheet_j.combined_set = data_sheet_j.sort_set(data_sheet_j.combined_set)
    mod_DataSheets.append(data_sheet_j)

for i in range(len(mod_DataSheets)):
        sheet = mod_DataSheets[i]
        sheet.combined_set = sheet.window_avg(sheet.combined_set, n=30)
