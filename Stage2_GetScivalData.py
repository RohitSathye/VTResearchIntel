#Importing Libraries#
import json
import requests as req
import pandas as pd
from progressbar import ProgressBar
import time
import collections
import os
from datetime import datetime

pbar = ProgressBar()
start = time.time()

con_file_location = 'config.json'

con_file = open(con_file_location)
config = json.load(con_file)
con_file.close()

API_Key = config['apikey']
Base_API_Scival = config['baseapi_Scival']           
Input_File = config['Output_ScopusID']    #Get Input File - Output of Previous program is input to this
Scival_metrics_Output_file = config['Output_Scivalmetrics']
Aff_ID = config['Virginia_Tech_AFID']
VT_COE_Aff_ID = config['VT_COE_AFID']

All_Data_Scival = collections.defaultdict(list)
max_retries = 5
Logs = 'ErrorLog_Scival.txt'

Data = collections.defaultdict(list)

Last_Updated = []
metric_Start_Year = []
metric_End_Year = []
H_value = []
H5_value_2018 = []
H5_value_2019 = []
H5_value_2020 = []
H5_value_2021 = []
H5_value_2022 = []
H5_value_2023 = []
H5_value_2024 = []
citationcount_value = []
citationsperpublications_value = []
AcademicCorporateCollaborationRate_value = []
InternationalCollaborationRate_value = []

if os.path.exists(Scival_metrics_Output_file):
	os.remove(Scival_metrics_Output_file)

file = open(Logs,'a')

file.write(f"--------------------------------------------------------------------\n")
file.write(f"Log Date - {datetime.now()}\n")
file.write("\n")

def extract_column_as_list(csv_file, column_name):
    df = pd.read_csv(csv_file)
    column_list = df[column_name].tolist()
    return column_list

Data['VT-ID'] = extract_column_as_list(Input_File,'ENTITY_IDENTIFIER')
Data['Authors'] = extract_column_as_list(Input_File,'Author Full Name')
Data['Scopus IDs'] = extract_column_as_list(Input_File,'Author ID')

###### Generate Parameters for Metrics #######
def Getparameters_string(metric,Author_ID):
    parameters_list = {'metricTypes':metric,'authors':Author_ID,'yearRange':'5yrsAndCurrentAndFuture','includeSelfCitations':'true','byYear':'false','includedDocs':'AllPublicationTypes','journalImpactType':'CiteScore','showAsFieldWeighted':'false','indexType':'hIndex','apiKey': API_Key}
    return parameters_list

#### Generate Parameters only for H5 indices ################
def Getparameters_H5(Author_ID):
    parameters_h5index = {'metricTypes':'HIndices','authors': Author_ID,'yearRange':'5yrsAndCurrentAndFuture','includeSelfCitations':'true','byYear':'true','includedDocs':'AllPublicationTypes','journalImpactType':'CiteScore','showAsFieldWeighted':'false','indexType':'h5Index','apiKey': API_Key}
    return parameters_h5index

#######################################
#Execute the API for getting H-indices

def ExecuteAPI_Hindices(parameters):
    tries = 1

    while tries <= max_retries:
        response = req.get(Base_API_Scival,params=parameters)
        Response_code = response.status_code

        if Response_code == 200:

            APIresponse = response.json()

            if(APIresponse):
                if(APIresponse['dataSource']):
                
                    APIresponse_dataSource = APIresponse['dataSource']  
                    Last_Updated.append(APIresponse_dataSource['lastUpdated'])
                    metric_Start_Year.append(APIresponse_dataSource['metricStartYear'])
                    metric_End_Year.append(APIresponse_dataSource['metricEndYear'])
                else:
                    file.write(f"No Data source found - {parameters} \n ")
               
                if(APIresponse['results']):      

                    APIresponse_Results_Metrics = APIresponse['results'][0]['metrics'][0]                 
                    H_value.append(APIresponse_Results_Metrics['value'])
                    break 
                else:
                    H_value.append(0) 
                    file.write(f"No Results found for Hindex - f{parameters} \n")
                    break      

            else:
                file.write(f"No API response available for Hindex - f{parameters} \n")
        else:
            # Write to file if connection failed
            file.write(f"Connection failed - Try {tries} - Status Code: {Response_code} - Hindex\n")
            file.write(f"Log - {parameters}\n")
            tries += 1
    else:
        file.write(f"Connection failed {max_retries} times for Hindex - {parameters}\n")

#######################################
#Execute the API for getting H5-indices
def ExecuteAPI_H5indices(parameters):
    tries = 1

    while tries <= max_retries:
        response = req.get(Base_API_Scival,params=parameters)
        Response_code = response.status_code

        if Response_code == 200:

            APIresponse = response.json()

            if(APIresponse):

                if(APIresponse['results']):
                    APIresponse_Results_Metrics = APIresponse['results'][0]['metrics'][0]

                    H5_value_2018.append(APIresponse_Results_Metrics['valueByYear']['2018'])
                    H5_value_2019.append(APIresponse_Results_Metrics['valueByYear']['2019']) 
                    H5_value_2020.append(APIresponse_Results_Metrics['valueByYear']['2020']) 
                    H5_value_2021.append(APIresponse_Results_Metrics['valueByYear']['2021']) 
                    H5_value_2022.append(APIresponse_Results_Metrics['valueByYear']['2022'])
                    H5_value_2023.append(APIresponse_Results_Metrics['valueByYear']['2023'])
                    H5_value_2024.append(APIresponse_Results_Metrics['valueByYear']['2024'])
                    break  

                else:

                    H5_value_2018.append(0)
                    H5_value_2019.append(0)
                    H5_value_2020.append(0)
                    H5_value_2021.append(0)
                    H5_value_2022.append(0)
                    H5_value_2023.append(0)
                    H5_value_2024.append(0)
                    
                    file.write(f"No Results available for H5 Indices - {parameters}\n") 
                    break     
            else:
                file.write(f"No API response available for H5indices - f{parameters} \n")
        else:
            # Write to file if connection failed
            file.write(f"Connection failed - Try {tries} - Status Code: {Response_code} - H5Indices\n")
            file.write(f"Log - {parameters}\n")
            tries += 1
    else:
        file.write(f"Connection failed {max_retries} times for H5indices - {parameters}\n")


#######################################
#Execute the API for getting Citation Count

def ExecuteAPI_Citationcount(parameters):
    tries = 1

    while tries <= max_retries:
        response = req.get(Base_API_Scival,params=parameters)
        Response_code = response.status_code

        if Response_code == 200:
                
            APIresponse = response.json()

            if(APIresponse):
                             
                if(APIresponse['results']):      

                    APIresponse_Results_Metrics = APIresponse['results'][0]['metrics'][0]
                        
                    citationcount_value.append(APIresponse_Results_Metrics.get('value', 'N/A'))
                    break
                        
                else:

                    citationcount_value.append(0) 
                    file.write(f"No Results available for CitationCount - {parameters}\n") 
                    break      

            else:
                file.write(f"No API response available for Citationcount - f{parameters} \n")                
        else:
            file.write(f"Connection failed - Try {tries} - Status Code: {Response_code} - CitationCount\n")
            file.write(f"Log - {parameters}\n")
            tries += 1
    else:
        file.write(f"Connection failed {max_retries} times for CitationCount - {parameters}\n")

#######################################
#Execute the API for getting Citations per Publication Count

def ExecuteAPI_Citationsperpublication(parameters):
    tries = 1

    while tries <= max_retries:
        response = req.get(Base_API_Scival,params=parameters)
        Response_code = response.status_code

        if Response_code == 200:
                
            APIresponse = response.json()

            if(APIresponse):
              
                if(APIresponse['results']):      

                    APIresponse_Results_Metrics = APIresponse['results'][0]['metrics'][0]
                        
                    citationsperpublications_value.append(APIresponse_Results_Metrics.get('value', 'N/A'))
                    break
                else:
                    citationsperpublications_value.append(0) 
                    file.write(f"No Results available for CitationsperPublication - {parameters}\n") 
                    break       

            else:
                file.write(f"No API response available for CitationsperPublication - f{parameters} \n") 
        else:
            file.write(f"Connection failed - Try {tries} - Status Code: {Response_code} - CitationsPerPublication\n")
            file.write(f"Log - {parameters}\n")
            tries += 1       
    else:
        file.write(f"Connection failed {max_retries} times for CitationsperPublication - {parameters}\n")

#######################################
#Execute the API for getting Academic Corporate Collaboration Rate

def ExecuteAPI_AcademicCorporateCollaborationRate(parameters):
    tries = 1

    while tries <= max_retries:
        response = req.get(Base_API_Scival,params=parameters)
        Response_code = response.status_code

        if Response_code == 200:
                
            APIresponse = response.json()

            if(APIresponse):
             
                if(APIresponse['results']):      

                    APIresponse_Results_Metrics = APIresponse['results'][0]['metrics'][0]                        
                    AcademicCorporateCollaborationRate_value.append(APIresponse_Results_Metrics['values'][0].get('percentage', 'N/A'))
                    break
                else:
                    AcademicCorporateCollaborationRate_value.append(0)
                    file.write(f"No Results available for AcademicCorporateCollaborationRate- {parameters}\n")       
                    break
            else:
                file.write(f"No API response available for AcademicCorporateCollaborationRate - f{parameters} \n")
        else:
            file.write(f"Connection failed - Try {tries} - Status Code: {Response_code} - AcademicCorporateCollaborationRate\n")
            file.write(f"Log - {parameters}\n")
            tries += 1
    else:
        file.write(f"Connection failed {max_retries} times for AcademicCorporateCollaborationRate - {parameters}\n")  

#######################################
#Execute the API for getting International Collaboration Rate

def ExecuteAPI_InternationalCollaborationRate(parameters):
    tries = 1

    while tries <= max_retries:
        response = req.get(Base_API_Scival,params=parameters)
        Response_code = response.status_code

        if Response_code == 200:
                
            APIresponse = response.json()

            if(APIresponse):
                
                if(APIresponse['results']):      

                    APIresponse_Results_Metrics = APIresponse['results'][0]['metrics'][0]

                    # Check if the 'values' list has the required index
                    if 'values' in APIresponse_Results_Metrics and len(APIresponse_Results_Metrics['values']) > 1:
                        # Check if the 'percentage' key exists for the given index
                        if 'percentage' in APIresponse_Results_Metrics['values'][1]:
                            InternationalCollaborationRate_value.append(APIresponse_Results_Metrics['values'][1]['percentage'])
                            break
                        else:
                            InternationalCollaborationRate_value.append(0)
                            file.write(f"Percentage not present in InternationalCollabRate - {parameters}\n")
                            break
                    else:
                        file.write(f"Values not present in InternationalCollabRate - {parameters}\n")
                        break
                else:
                    InternationalCollaborationRate_value.append(0)
                    file.write(f"No Results available for InternationalCollaborationRate- {parameters}\n")
                    break       

            else:
                file.write(f"No API response available for InternationalCollaborationRate - f{parameters} \n")
        else:
                file.write(f"Connection failed - Try {tries} - Status Code: {Response_code} - InternationalCollaborationRate\n")
                file.write(f"Log - {parameters}\n")
                tries += 1
    else:
        file.write(f"Connection failed {max_retries} times for InternationalCollaborationRate - {parameters}\n")  
 
def Generate_Results(AuthNames,AuthIds,VT_IDs,Hval,H5_2018,H5_2019,H5_2020,H5_2021,H5_2022,H5_2023,H5_2024,CitCount,CitCountPub,ACCR,ICR):

    All_Data = {
    'ENTITY_IDENTIFIER' : VT_IDs,
    'Author Full Name': AuthNames,
    'Scopus ID': AuthIds,
    'H-index': Hval,
    'H5-2018': H5_2018,
    'H5-2019': H5_2019,
    'H5-2020': H5_2020,
    'H5-2021': H5_2021,
    'H5-2022': H5_2022,
    'H5-2023': H5_2023,
    'H5-2024': H5_2024,
    'Citation Count': CitCount,
    'Citation per Publication Value': CitCountPub,
    'Academic Corporate Collaboration Rate': ACCR,
    'International Collaboration Rate': ICR,   
    }

    return All_Data

def Generate_csv(data):
    try:
        df = pd.DataFrame(data)
        df.to_csv(Scival_metrics_Output_file, sep=',', index=False, encoding='utf-8')
        print("File Generated")
    except ValueError:
        file.write(f"ValueError Exception Occured")
        print("Program Halted - Check Log File")
        exit()

def PrepareOutputFile():

    for IDs in pbar(Data['Scopus IDs']):
        Params1 = Getparameters_string('HIndices',IDs)
        ExecuteAPI_Hindices(Params1)
        
        Params2 = Getparameters_H5(IDs)
        ExecuteAPI_H5indices(Params2)
        
        Params3 = Getparameters_string('CitationCount',IDs)
        ExecuteAPI_Citationcount(Params3)
        
        Params4 = Getparameters_string('CitationsPerPublication',IDs)
        ExecuteAPI_Citationsperpublication(Params4)
        
        Params5 = Getparameters_string('AcademicCorporateCollaboration',IDs)
        ExecuteAPI_AcademicCorporateCollaborationRate(Params5)
        
        Params6 = Getparameters_string('Collaboration',IDs)
        ExecuteAPI_InternationalCollaborationRate(Params6)

        time.sleep(0.5)

PrepareOutputFile()
Result_Data_Scival_metrics = Generate_Results(Data['Authors'],Data['Scopus IDs'],Data['VT-ID'],H_value,H5_value_2018,H5_value_2019,H5_value_2020,H5_value_2021,H5_value_2022,H5_value_2023,H5_value_2024,citationcount_value,citationsperpublications_value,AcademicCorporateCollaborationRate_value,InternationalCollaborationRate_value)
Generate_csv(Result_Data_Scival_metrics)

end = time.time()
file.write("Execution complete - Stage 2\n")
file.close()

print("Execution Complete")
print("Number of authors: ", len(Data['Authors']))
print("Time elapsed: ",end - start)
