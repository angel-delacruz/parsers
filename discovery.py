import os
import pandas as pd
from tkinter import *
from tkinter import filedialog
from tkinter import messagebox

root = Tk()
root.title('Choose a file, then enter a valid Discovery GPID.')
root.geometry('500x200+0+0')

filename = filedialog.askopenfilename(parent = root)

gpid_list  = pd.read_csv(
        filename, 
        header = None, 
        sep = '|', 
        usecols = [0],)
gpid_list = gpid_list.drop(gpid_list.index[0])
gpid_list = gpid_list.drop(gpid_list.index[-1])


root.entry = Entry(root,
        bg = 'lightgreen',
        width = 10)
root.entry.pack()


def validate_gpid():
    global gpid
    gpid = root.entry.get()
    if any(gpid_list[0] == gpid):
        root.destroy()
    else: messagebox.showerror('Error', 'Invalid GPID.') #raise Exception('Invalid GPID.')


validate_button = Button(root,
        text = 'Validate GPID',
        width = 10,
        height = 5,
        bg = 'lightblue',
        command = validate_gpid)
validate_button.pack()

root.mainloop()

raw_df = pd.read_csv(
        filename,
        sep = '|',
        low_memory = False,)

df = raw_df.loc[gpid]

participants = df.loc['PT']
elections = df.loc['EN']
contributions = df.loc['CT']

pt_col_names = ['SSN', '',
        'Discovery Employee Number', 'Last Name', 'First Name',
        '', '', '', '',
        'Date of Birth', 'SSN Repeated',
        'Address 1', 'Address 2', '', '', 'City', 'State', 'ZIP',
        '', '', '', '',
        'Email', '', '', 'Hire Date', 'Division', '', 'Employee Class',
        'Payroll Frequency', '', 'Participant Status',
        'Status Effective Date', '', '', '',
        'Final Payroll Process Date', 'Final Contribution Process Date',]
en_col_names = ['SSN', 'Plan Name', 'Enrollment Effective Date',
        'Participant Election Amount', 'Enrollment Termination Date',
        'Employer Contribution Level', 'Employer Contribution Amount',
        '', '', '', 'Election Amount Indicator', 'HDHP Coverage Level',
        '', '', '', '', '',    '', '', '', '', '',
        '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '',]
ct_col_names = ['SSN', 'Plan Name', 'Contribution Date',
        'Contribution Description', 'Contribution Amount', 'Amount Type', '',
        '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '',
        '', '', '', '', '', '', '', '', '', '', '', '', '', '', '',]

participants = participants.reset_index()
participants.columns = pt_col_names

elections = elections.reset_index()
elections.columns = en_col_names

if not contributions.empty:
    contributions = contributions.reset_index()
    contributions.columns = ct_col_names


pt_en = participants.merge(elections,
        how = 'inner',
        on = 'SSN')
pt_en = pt_en.drop(['_x', '_y'], axis = 1)



if not contributions.empty:
    pt_en_ct = pt_en.merge(contributions,
            how = 'inner',
            on = ['SSN', 'Plan Name'])

os.chdir('Desktop')


if contributions.empty:
    pt_en.to_csv(f'{gpid}_Parsed.csv', header = True, index = False)

if not contributions.empty:
    pt_en_ct.to_csv(f'{gpid}_Parsed.csv', header = True, index = False)



