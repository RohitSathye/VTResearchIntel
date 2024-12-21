import pandas as pd
import json
import os

con_file_location = 'config.json'

con_file = open(con_file_location)
config = json.load(con_file)
con_file.close()
   
Input_File = config['Author_Name_ScopusID']    #Get Input File
Scival_Data_Output = config['Output_Scivalmetrics']
Output_File = config['Output_Merged_Stage_3']

if os.path.exists(Output_File):
	os.remove(Output_File)

# Load the CSV files into pandas DataFrames
df1 = pd.read_csv(Input_File)
df2 = pd.read_csv(Scival_Data_Output)

# Merge the DataFrames based on a common key
merged_df = pd.merge(df2, df1, on='ENTITY_IDENTIFIER')

#cols_to_remove = ['CURRENT_FULL_NAME','Unnamed: 21','Unnamed: 20']
cols_to_remove = ['CURRENT_FULL_NAME']

merged_df.drop(columns=cols_to_remove, inplace=True)

# Write the merged DataFrame to a new CSV file
merged_df.to_csv(Output_File, index=False)

print("Stage 3 Completed")
