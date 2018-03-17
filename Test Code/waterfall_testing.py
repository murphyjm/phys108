from data_reduction import DataSheet, xlsx_modulation, df_label_names
from create_data_sheets import mod_DataSheets
import numpy as np
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.pyplot as plt

eps = 0.2

#Now I should have a numpy array of ordered pairs, mod_DataSheets
fig = plt.figure(facecolor='k')
ax = fig.add_subplot(111, axisbg='k')
n_sets, n_curves = len(mod_DataSheets), 100
x = np.linspace(0,1,n_sets)

def matching_volt(volt, temp_sheet):
    #array will have 100 pts, we want to loop through and find the first matching voltage
    temp_set = temp_sheet.combined_set
    for i in range(len(temp_set)):
        temp_volt, sig = temp_set[i]
        if (temp_volt > volt - eps and temp_volt < volt + eps) : 
            return sig
    print("didn't find one")
    
def create_curves(n_sets, n_curves, mod_DataSheets):
    output_array = np.zeros((n_curves, n_sets))
    #loop through the first n_curves pts of set 1 (create a single y array for each)
    sheet1 = mod_DataSheets[0]
    for i in range(n_curves):
        y = np.zeros(n_sets)
        volt,sig = sheet1.combined_set[i]
        #put pair voltage into array
        y[0] = sig
        #loop through all other lists and look for the first point that is between v - eps and v + eps
        for j in range(1, n_sets):
            temp_sheet = mod_DataSheets[j]
            y[j] = matching_volt(volt, temp_sheet)
        output_array[i] = y
    
    #output a size 100 array of (n_sets pts arrays)
    return output_array

#plot
for i in range(n_curves):
    offset = (n_curves-i)*0.1
    output = create_curves(n_sets,n_curves, mod_DataSheets)
    current_curve = output[i]
    ax.plot(x, current_curve + offset, 'w', lw=1.5)
    ax.fill_between(x, current_curve + offset, offset, facecolor='k', lw=0)
plt.show()


