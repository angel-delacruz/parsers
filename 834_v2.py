import pandas as pd
import os
from tkinter import *
from tkinter import filedialog


root = Tk()
root.withdraw()

filename = filedialog.askopenfilename(
        parent = root,
        title = 'Choose your 834 file.')

#Read in raw data, initialize empty dataframe, give a preview of the file.
df = pd.read_csv(filename,
        header = None,
        sep = '*',
        lineterminator = '~',)

parsed_df = pd.DataFrame()

print('File Preview:\n', df.head(25))

#Create dictionary of HIPAA 834 values to record + position.
#Can be edited to include more/less information (for example, removing SSNs)

hipaa_dict = {
'First':('NM1', 'IL', 4),
'Last':('NM1', 'IL', 3),
'Employee?':('INS', None, 1),
'SSN':('NM1', 'IL', 9),
'Date of Birth': ('DMG', 'D8', 2),
'Gender':('DMG', 'D8', 3),
'Class':('REF', '3H', 2),
'Division':('REF', 'ZZ', 2),
'Hire Date':('DTP', '336', 3),
'Term Date':('DTP', '337', 3),
'Salary':('ICM', '7', 2),
'Street 1':('N3', None, 1),
'Street 2':('N3', None, 2),
'City':('N4', None, 1),
'State':('N4', None, 2),
'Zip': ('N4', None, 3),
'Benefit':('HD', '030', 3),
'Name/Volume':('HD', '030', 4),
'Start Date':('DTP', '348', 3),
'End Date':('DTP', '349', 3),
}

#Create dictionary of all EE + Dependent starting positions in the file
start_pos = dict()
end_pos = []
counter = 1

for row in df.index:
    if df.loc[row, 0] == 'INS':
        start_pos[counter] = row
        counter += 1

#Get ending position of the last EE/Dep
for row in df.index:
    if df.loc[row, 0] == 'SE':
        end_pos = row

#Create dictionary of each employee to all their info, including dependents
ee_dep_dict = dict()
counter = 1

for item in start_pos:

    if counter + 1 not in start_pos:
        ee_dep_dict[counter] = df[start_pos[counter]:end_pos]
    else:
        ee_dep_dict[counter] = df[start_pos[counter]:start_pos[counter + 1]]
        counter += 1



def parse(ee, dict1=ee_dep_dict, dict2=hipaa_dict, df=parsed_df):
    """Extract info from 834 dataframe based on record and position.

    Works in tandem with the ee_dep_dict and hipaa_dict that were created.
    ee = which ee/dep we're looking up in the ee_dep_dict
    dict1 = ee_dep_dict
    dict2 = hipaa_dict
    df = parsed_df that we're writing to.
    Temp dict created to faciliate easier parsing.

    Extra logic added for Benefit Info & Address Info which slightly deviate
    from the rest of the file.

    From hipaa_dict:
    record = 834 HIPAA record type where this info is found
    position = HIPAA column number


    """

    temp_dict = dict()

    for key in dict2:

        try:
            row = (dict1[ee][0] == dict2[key][0]) & (dict1[ee][1] == dict2[key][1])
            column = dict2[key][2]

            if key in ['Benefit', 'Name/Volume', 'Start Date', 'End Date']:
                counter = 1
                for x in dict1[ee].loc[row].index:
                    temp_dict[key + ' ' + str(counter)] = dict1[ee].loc[x, column]
                    counter += 1

            elif key in ['Street 1', 'Street 2', 'City', 'State', 'Zip', 'Employee?']:
                row = (dict1[ee][0] == dict2[key][0])
                temp_dict[key] = dict1[ee].loc[row, column].item()

            else:
                temp_dict[key] = dict1[ee].loc[row, column].item()

        except ValueError:

            print('Value empty: parse as "None"')
            temp_dict[key] = None

    
    return temp_dict

#Run this parse function over the list of employees to create parsed dict.
#Create parsed df from this dict, rearrange columns.

parsed_dict = {x:parse(x) for x in [key for key in ee_dep_dict]}
parsed_df = pd.DataFrame.from_dict(parsed_dict, orient='index')

benefits_cols = [
'Benefit 1', 'Name/Volume 1','Start Date 1', 'End Date 1', 
'Benefit 2', 'Name/Volume 2','Start Date 2', 'End Date 2',  
'Benefit 3', 'Name/Volume 3','Start Date 3', 'End Date 3', 
'Benefit 4', 'Name/Volume 4','Start Date 4', 'End Date 4', 
'Benefit 5', 'Name/Volume 5','Start Date 5', 'End Date 5', 
'Benefit 6', 'Name/Volume 6','Start Date 6', 'End Date 6', 
'Benefit 7', 'Name/Volume 7','Start Date 7', 'End Date 7', 
'Benefit 8', 'Name/Volume 8','Start Date 8', 'End Date 8', 
'Benefit 9', 'Name/Volume 9','Start Date 9', 'End Date 9', 
'Benefit 10', 'Name/Volume 10','Start Date 10', 'End Date 10', 
]

demo_cols = [
'First', 'Last', 'Employee?', 'SSN', 'Date of Birth', 'Gender', 'Class',
'Division', 'Hire Date','Term Date','Salary','Street 1', 'Street 2', 'City',
'State', 'Zip',
]

rearranged_cols = demo_cols + benefits_cols

#Check for any empty columns and fill with None to prevent Index/KeyError.

for col in benefits_cols:
    if col not in parsed_df:
        parsed_df[col] = [None for x in [key for key in ee_dep_dict]]

parsed_df = parsed_df[rearranged_cols]


#Get carrier and client name to output filename
for row in df.index:
    if df.loc[row, 0] == 'N1' and df.loc[row, 1] == 'P5':
        client = (df.loc[row, 2])
    elif df.loc[row, 0] == 'N1' and df.loc[row, 1] == 'IN':
        carrier = (df.loc[row, 2])

os.chdir('Desktop')
parsed_df.to_csv(f'{client}_{carrier}_parsed834.csv',
        header = True,
        index = False)


