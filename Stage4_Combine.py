import pandas as pd
import json
import os

con_file_location = 'config.json'

con_file = open(con_file_location)
config = json.load(con_file)
con_file.close()
   
Input_File = config['Author_Name_ScopusID']    #Get Input File
No_Scopus_ID_Output_file = config['Output_NoScopusID']
Stage3_Output_File = config['Output_Merged_Stage_3']
Output_File_All_Data = config['All_Data_Merged_Stage_4']

if os.path.exists(Output_File_All_Data):
	os.remove(Output_File_All_Data)

# Load the CSV files into pandas DataFrames
df1 = pd.read_csv(Input_File)
df2 = pd.read_csv(No_Scopus_ID_Output_file)
df3 = pd.read_csv(Stage3_Output_File)

# Merge the DataFrames based on a common key
no_scopus_df = pd.merge(df2, df1, on='ENTITY_IDENTIFIER')

cols_to_remove = ['CURRENT_FULL_NAME','Unnamed: 21','Unnamed: 20']

no_scopus_df.drop(columns=cols_to_remove, inplace=True)

final_combined_df = pd.concat([df3, no_scopus_df], ignore_index=True)

# Write the merged DataFrame to a new CSV file
final_combined_df.to_csv(Output_File_All_Data, index=False)

print("Stage 4 Completed")
print("ETL Author Data Pipeline Executed Succesfully")
