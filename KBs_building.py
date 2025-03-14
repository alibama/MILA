#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: keam
"""
import importlib
from modules.extract_ontology.data_extraction import extract_entities_from_ontology
from modules.build_KB.index_creation import create_vector_kb
from utils import load_config

##############################################################################################################
def extract_ontology_data (ontology, ontology_path, ontology_extension,output_path, PT_read_method):
    """
    Extract data from the given ontology using the specified read method.
    
    Args:
        ontology_name (str): Name of the ontology (e.g., 'mouse', 'human').
        ontology_path (str): Path where the ontology file is stored.
        ontology_extension (str): Extension of the ontology file (e.g., 'owl', 'obo').
        output_path (str): Path where the extracted data should be stored.
        PT_read_method (function): Method for reading preferred terms from the ontology (default is baseline_read).
    
    Returns:
        None
    """
    
    ontology_full_path=ontology_path+ontology+"."+ontology_extension
    output_full_path=output_path+ontology
     
    # Extract entities from the ontology using the appropriate reading method
    return extract_entities_from_ontology (ontology, ontology_full_path, output_full_path,PT_read_method)


##############################################################################################################

if __name__ == "__main__":
    import time
    ini=time.time()
    # Load configuration
    config = load_config("data/configurations/config.yaml")
    
    # Extract paths and settings from the config
    original_ontology_path = config['ontology']['original_data_path']
    ontology_path = config['ontology']['ontology_data_path']
    KBs_path = config['ontology']['vector_kb_path']
    source_ontology = config['ontology']['source_ontology']
    target_ontology = config['ontology']['target_ontology']
    ontology_extension = config['ontology']['ontology_extension']
    read_methods_path = config['read_methods']['read_method_path']
    # Dynamically import the module containing user functions
    read_method_module = importlib.import_module(read_methods_path)
    
    # Read method functions
    
    source_PT_read_method = config['read_methods']['source_PT_read_method']
    # Access the function from the module
    source_PT_read_method = getattr(read_method_module, source_PT_read_method)
    
    target_PT_read_method = config['read_methods']['target_PT_read_method']
    target_PT_read_method = getattr(read_method_module, target_PT_read_method)
    
    # Read default values 
    k = config['default_settings']['k']
    threshold = config['default_settings']['threshold']
    model = config['default_settings']['model']
    store_embeddings = config['default_settings']['store_embeddings']
    
    ###################################################################
    
    
    #Step1: Extraction of Data from source and target ontologies to data/ontology_data

    extract_ontology_data(source_ontology,original_ontology_path,ontology_extension,ontology_path,source_PT_read_method)
   
    extract_ontology_data(target_ontology,original_ontology_path,ontology_extension,ontology_path,target_PT_read_method)
    
    
   #Step2: Build and save vector KB from data stored into data/ontology_data
    
    create_vector_kb (source_ontology,target_ontology,ontology_path,KBs_path,k,threshold,model,store_embeddings)
    create_vector_kb (target_ontology,source_ontology,ontology_path,KBs_path,k,threshold,model,store_embeddings)
    
    fin=time.time()
    print(f'Time:{fin-ini}')
    