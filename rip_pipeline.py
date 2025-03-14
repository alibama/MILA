"""
Created on Wed Apr 24 19:18:29 2024

@author: keam
# para que no se reinicie el kernel
pip install transformers
conda install pytorch torchvision torchaudio -c pytorch
"""
import importlib
from modules.identify_correspondences.retrieve_identify_prompt import retrieve_identify_prompt
from utils import load_config
import pandas as pd
import sqlite3

import time

##############################################################################################################
def extract_reference_data (input_file, output_file, file_path, extraction_method, file_extension='xlsx' ):
    
    
    input_file_path=file_path+input_file+"."+file_extension
    output_file_path=file_path+output_file+".xlsx"
    
   
    # Extract data from the input_file using the appropriate reading method
    # Return the source entities to be matched
    return extraction_method (input_file_path, output_file_path)

##############################################################################################################
def extract_candidates_from_DB(db_path):
    # Connect to the database
    conn = sqlite3.connect(db_path)

    # Get the table name dynamically
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")

    table_name = db_path[0:-3] #cursor.fetchone()[0]  # Fetch the first (and only) table name

    # Load the table into a DataFrame
    #loaded_df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)

    # Fix the SQL query by wrapping the table name in double quotes
    query = f'SELECT * FROM "{table_name}"'

    # Load table into DataFrame
    loaded_df = pd.read_sql_query(query, conn)
    loaded_df=loaded_df.reset_index(drop=True)
    
    conn.close()
    
    return loaded_df

#########################################################
#Load ontology from sqlite3 database
def load_ontology_dataframes_from_sql(ontology,ontology_path, column_1,column_2):
    
    db_path = ontology_path+ontology+'.db'
    # Load the DB
    conn = sqlite3.connect(db_path)

    # Leer cada tabla en un DataFrame
    df1 = pd.read_sql("SELECT * FROM "+ column_1, conn)
    df1=df1.reset_index(drop=True)
    df2 = pd.read_sql("SELECT * FROM "+column_2, conn)
    df2=df2.reset_index(drop=True)

    # Cerrar conexión
    conn.close()
    
    return df1,df2



##############################################################################################################


if __name__ == "__main__":
    ini=time.time()
    # Load configuration
    config = load_config("data/configurations/config.yaml")
    
    # Extract paths and settings from the config
    
    KBs_path = config['ontology']['vector_kb_path']
    ontology_path = config['ontology']['ontology_data_path']
    source_ontology = config['ontology']['source_ontology']
    target_ontology = config['ontology']['target_ontology']
    
    test_path = config['test']['test_path']
    file_extension = config['test']['file_extension']
    input_file = config['test']['input_file']
    test_output_file = config['test']['output_file']
    
    correspondence_path = config['correspondences']['correspondence_path']
    correspondence_output_file = config['correspondences']['output_file']
    
    template_path = config['prompt']['template_path']
    template = config['prompt']['template']
    
    temperature = config['default_settings']['temperature']
    LLM_model = config['default_settings']['LLM_model']
    
    # Dynamically import the module containing read functions defined by the user
    read_methods_path = config['read_methods']['read_method_path']
    read_method_module = importlib.import_module(read_methods_path)
    
    # Dynamically import the module containing read functions defined by the user
    LLM_methods_path = config['LLM_methods']['LLM_method_path']
    LLM_method_module = importlib.import_module(LLM_methods_path)
    
    
    # Read method functions
   
    extraction_method = config['read_methods']['extraction_method']
    # Access the function from the module
    extraction_method = getattr(read_method_module, extraction_method)
    
    
    query_LLM_method = config['LLM_methods']['query_LLM_method']
    # Access the function from the module
    query_LLM_method = getattr(LLM_method_module, query_LLM_method)
    
    
    
    ###################################################################

    
    # Load data and build full names for files
    

    # Load priorized lists for all entities (source and target)
    src2tgt=extract_candidates_from_DB(f'{KBs_path}SBERTcandidates{source_ontology}2{target_ontology}.db')
    tgt2src=extract_candidates_from_DB(f'{KBs_path}SBERTcandidates{target_ontology}2{source_ontology}.db')
    # Load preferred terms for target ontology
    pref_terms_pd, target_classes_pd=load_ontology_dataframes_from_sql(target_ontology,ontology_path, 'PreferredTerms','Classes')
    
    
    # Define full path for different files
    corresp_file_path=correspondence_path+correspondence_output_file+".xlsx"
    template_file=template_path+template+".txt"
    
    #Step1: Extraction of source entities to be matched
    
    source_entities=extract_reference_data(input_file, test_output_file, test_path, extraction_method, file_extension)
    
    #Step3: Identify all bidirectional correspondences (BC). If a bidirectional correspondence is of high confidence, return the mapping. 
    #In any case, return the priorized list of bidirectional correspondences to he prompted
    
    retrieve_identify_prompt (source_ontology, target_ontology, source_entities, src2tgt, tgt2src, corresp_file_path, template_file, pref_terms_pd,target_classes_pd,query_LLM_method, temperature, LLM_model)
    
    fin=time.time()
    print(f'tiempo:{fin-ini} s')     
   