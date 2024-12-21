import json
import requests as req
import pandas as pd
from progressbar import ProgressBar
import time
import os
import collections
from datetime import datetime
import sys

pbar = ProgressBar()
start = time.time()

con_file_location = 'config.json'

con_file = open(con_file_location)
config = json.load(con_file)
con_file.close()

API_Key = config['apikey']
Base_API_AUID = config['baseapi_AUID']           
Input_File = config['Author_Name_ScopusID']    #Get Input File
Scopus_ID_Output_file = config['Output_ScopusID']
No_Scopus_ID_Output_file = config['Output_NoScopusID']
Aff_ID = config['Virginia_Tech_AFID']
VT_COE_Aff_ID = config['VT_COE_AFID']

Author_ID_Valid_Ids,Author_ID_No_exist = [],[]
VT_ID_with_scopus , VT_ID_without_scopus = [],[]
FNs,LNs = [],[]
Data = {}
Author_Names_No_ID , Author_Names_Scopus_ID = [],[]

All_Data_Scopus_ID = collections.defaultdict(list)
All_Data_No_Scopus_ID = collections.defaultdict(list)

max_retries = 5    # Maximum retries to the API
fraction = int(sys.argv[1])     # This variable divides the data into a specific fraction which we send to the pipeline.
Logs = 'ErrorLog_Scopus.txt'

if os.path.exists(Scopus_ID_Output_file):
	os.remove(Scopus_ID_Output_file)
if os.path.exists(No_Scopus_ID_Output_file):
    os.remove(No_Scopus_ID_Output_file)

file = open(Logs,'a')

file.write(f"--------------------------------------------------------------------\n")
file.write(f"Log Date - {datetime.now()}\n")
file.write("\n")

def extract_column_as_list(csv_file, column_name):
    df = pd.read_csv(csv_file)
    column_list = df[column_name].tolist()
    return column_list

Data['VT-ID'] = extract_column_as_list(Input_File,'ENTITY_IDENTIFIER')
Data['Authors'] = extract_column_as_list(Input_File,'CURRENT_FULL_NAME')

Data['Authors'] = [per for per in Data['Authors'] if not pd.isna(per)]
Data['VT-ID'] = [gen for gen in Data['VT-ID'] if not pd.isna(gen)]

Data['Authors'] = Data['Authors'][:len(Data['Authors'])//fraction]
Data['VT-ID'] = Data['VT-ID'][:len(Data['VT-ID'])//fraction]

def Getparameters_AUID(First_name,Last_name):
    Genstring = f"(authlast({Last_name}) and authfirst({First_name})) and (af-id({Aff_ID}) or af-id({VT_COE_Aff_ID}))"
    parameters_AUID = {'query': Genstring,'apiKey': API_Key}
    return parameters_AUID

def ExecuteAPI_AUID(parameters):
    tries = 1

    while tries <= max_retries:
        response = req.get(Base_API_AUID, params=parameters)
        Response_code = response.status_code

        if Response_code == 200:
            APIresponse = response.json()
            if APIresponse:
                Results = APIresponse['search-results']
                Search_Results = int(Results['opensearch:totalResults'])  # Gives total results

                if Search_Results != 0:
                    Temp_auid = Results['entry'][0]['dc:identifier']
                    Auth_ID = Temp_auid.split(':')[1]
                    return Auth_ID

                elif Search_Results > 1:
                    Auth_ID = Search_Results
                    return Auth_ID

                else:
                    Auth_ID = 0
                    return Auth_ID
            else:
                # Write to file if API response is unavailable
                file.write(f"API response Unavailable for {parameters}\n")
        else:
            # Write to file if connection failed
            file.write(f"Connection failed - Try {tries} - Status Code: {Response_code}\n")
            file.write(f"Log - {parameters}\n")
            tries += 1
    else:
        file.write(f"Connection failed 5 times for {parameters}")

def Generate_Results(AuthNames,AuthIds,VT_IDs):

    All_Data = {
    'ENTITY_IDENTIFIER' : VT_IDs,
    'Author Full Name': AuthNames,
    'Author ID': AuthIds,    
    }

    return All_Data

def Generate_csv(data,filecode):
    if filecode == 1:
        try:
            df = pd.DataFrame(data)
            df.to_csv(Scopus_ID_Output_file, sep=',', index=False, encoding='utf-8')
            print("File Generated - Scopus IDs")
        except ValueError:
            print(data)
            exit()
    else:
        try:
            df = pd.DataFrame(data)
            df.to_csv(No_Scopus_ID_Output_file, sep=',', index=False, encoding='utf-8')
            print("File Generated - No Scopus Ids")
        except ValueError:
            print(data)
            exit()

def PrepareOutputFile():

    for i,j,k in pbar(zip(FNs,LNs,Data['VT-ID'])):
        Params1 = Getparameters_AUID(i,j)
        AUID = ExecuteAPI_AUID(Params1)
        if AUID == 0:
            Author_ID_No_exist.append(AUID)
            Author_Names_No_ID.append(i + " " + j)
            VT_ID_without_scopus.append(k)
        else:
            Author_ID_Valid_Ids.append(AUID)
            Author_Names_Scopus_ID.append(i + " " + j)
            VT_ID_with_scopus.append(k)

        time.sleep(0.5)


for Auth in Data['Authors']:
    try:
        if ', ' in Auth:
            FNs.append(Auth.split(', ')[1].split()[0])
            LNs.append(Auth.split(', ')[0])
     
        elif ',' in Auth:
            FNs.append(Auth.split(',')[1].split()[0])
            LNs.append(Auth.split(',')[0])
     
    except Exception as e:
        file.write(f"{Auth} with Exception {e}\n")

PrepareOutputFile()
Result_Data_Scopus_ID = Generate_Results(Author_Names_Scopus_ID,Author_ID_Valid_Ids,VT_ID_with_scopus)
Generate_csv(Result_Data_Scopus_ID,1)
Result_Data_No_Scopus_ID = Generate_Results(Author_Names_No_ID,Author_ID_No_exist,VT_ID_without_scopus)
Generate_csv(Result_Data_No_Scopus_ID,0)

end = time.time()
file.write("Execution Complete - Stage 1\n")
file.close()

print("Execution Complete")
print("Number of authors: ", len(Data['Authors']))
print("Time elapsed: ",end - start)