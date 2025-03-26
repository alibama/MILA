#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: keam
"""

import pandas as pd
import sqlite3
from sentence_transformers import SentenceTransformer, util
import torch
import time

#########################################################
def procesa_query_for_SBERT(term):
    #print(term)
    return term[0].upper()+term[1:]+"."
#########################################################
def process_corpus(listofterms):
    return [procesa_query_for_SBERT (term) for term in listofterms]
#########################################################
#Load ontology dataframes
def load_ontology_dataframes (ontology,ontology_path, df_name_1,df_name_2):
    
    # Load the Excel file of ontology
    file_path = ontology_path+ontology+'.xlsx'

    # Get sheet's DataFrame
    df1 = pd.read_excel(file_path, sheet_name=df_name_1)
    df1 = df1.reset_index(drop=True)
    
    df2 = pd.read_excel(file_path, sheet_name=df_name_2)
    df2 = df2.reset_index(drop=True)
    
    return df1,df2

#########################################################
#Load ontology from sqlite3 database
def load_ontology_dataframes_from_sql(ontology,ontology_path, column_1,column_2):
    
    db_path = ontology_path+ontology+'.db'
    # Load the DB
    conn = sqlite3.connect(db_path)

    # Leer cada tabla en un DataFrame
    df1 = pd.read_sql("SELECT * FROM "+ column_1, conn)
    df2 = pd.read_sql("SELECT * FROM "+column_2, conn)

    # Cerrar conexión
    conn.close()
    
    return df1,df2


#########################################################

#def create_vector_kb (ontology1,ontology2,ontology_path,KBs_path,k=5,threshold=0.75,model='multi-qa-distilbert-cos-v1', store_embeddings=False):
def create_vector_kb (ontology1,ontology2,ontology_path,KBs_path,entity_list, k=5,threshold=0.75,model='multi-qa-distilbert-cos-v1', store_embeddings=False):
        
    """
    Creates a vector knowledge base by aligning terms from two ontologies using sentence embeddings and cosine similarity.

    Args:
        ontology1 (str): Source ontology name.
        ontology2 (str): Target ontology name.
        ontology_path (str): Path to the ontology data.
        k (int): Number of top results to return for each term (default 5).
        threshold (float): Cosine similarity threshold to consider a match (default 0.75).
        model (str): Pretrained sentence transformer model to use (default 'multi-qa-distilbert-cos-v1').
        store_embeddings (bool): Whether to store the embeddings for future use (default False).
        
    Returns:
        None: Saves the result as an Excel file.
    """
    #Print information
    print(f"Generating vector KB with parameters: k={k}, threshold={threshold}, model={model}")
    
    """    
    #Load source and target ontology dataframes
    source_pref_terms,source_classes = load_ontology_dataframes (ontology1,ontology_path, 'PreferredTerms','Classes')
    target_terms,target_classes = load_ontology_dataframes (ontology2,ontology_path, 'Terms','Classes')
    """
    ini_KBBuilding=time.time()
    #Load source and target ontology dataframes
    source_pref_terms,source_classes = load_ontology_dataframes_from_sql (ontology1,ontology_path, 'PreferredTerms','Classes')
    target_terms,target_classes = load_ontology_dataframes_from_sql (ontology2,ontology_path, 'Terms','Classes')
    # Load the sentence transformer model
    embedder = SentenceTransformer(model)
    
    #Create corpus for target
    corpus = process_corpus(target_terms['Term'].to_list())
    corpus_embeddings = embedder.encode(corpus, convert_to_tensor=True)
    fin_KBBuilding=time.time()
    print(f'Time for building KB relative to {ontology2}: {fin_KBBuilding-ini_KBBuilding}')
    # Get query classes from source ontology to be mapped
    query_classes = entity_list

    # Initialize dictionaries to collect results
    query_PT_dict = {}
    candidate_dict = {}
    score_dict = {}
    cand_PT_dict = {}
    candidate_list=[]

    for query_class in query_classes:
          
          tgt_c_score={}
          #print(query_class)
          # Get terms for the current query class
          
          query_c_terms=source_classes[source_classes['Entity']==query_class]['Term'].values.tolist()[0][1:-1].split('|')
          
          # Get the Preferred Term (PT) for the current query class
          query_PTs=source_pref_terms[source_pref_terms['Entity']==query_class]['Term'].values.tolist()
          query_PT = query_PTs[0] if len(query_PTs)>0 else source_classes[source_classes['Entity'] == query_class]['Term'].values.tolist()[0].split('|')[1]
          query_PT_dict[query_class] = query_PT
          
          for term in query_c_terms:
           if term!='': 
            query_for_SBert=procesa_query_for_SBERT (term)
            query_embedding = embedder.encode(query_for_SBert, convert_to_tensor=True)

            # Calculate cosine similarity between the query and corpus
            cos_scores = util.cos_sim(query_embedding, corpus_embeddings)[0]
            top_results = torch.topk(cos_scores, k=min(k, len(corpus)))
            
            # Evaluate the top results
            i=0
            score=float(top_results[0][i])
            while i<len(top_results[0]) and score>=threshold:
                tgt_tensor=top_results[1][i]
                tgt_term=corpus[tgt_tensor][0:-1].lower()
                tgt_cs=target_terms[target_terms['Term']==tgt_term]['Entity'].tolist()[0].split('|')
                
                # Update the target class score
                for tgt_c in tgt_cs:
                    tgt_c_score[tgt_c] = max(tgt_c_score.get(tgt_c, 0), score)
                
                i+=1
                if i<len(top_results[0]):
                    score=float(top_results[0][i])
                
               
          # Sort the target classes by score
           
          sorted_pairs = sorted(tgt_c_score.items(), key=lambda item: item[1], reverse=True)
        
          # Collect results for output
          cand_list=[tgt_c for tgt_c, _ in sorted_pairs]
          candidate_dict[query_class] = "|".join(cand_list)
          score_dict[query_class] = "|".join([str(score) for _, score in sorted_pairs])
          cand_PT_dict[query_class] = "|".join([target_classes[target_classes['Entity'] == tgt_c]['Term'].values.tolist()[0].split('|')[0] for tgt_c, _ in sorted_pairs])
          
          candidate_list=candidate_list + cand_list
        
                  
    # Create the final dataframe for the results
    
    result_pd = {'Query Class':query_classes,#query_list,
                 'Query Preferred Term': [query_PT_dict.get(query_class, "") for query_class in query_classes],
                'Candidate List':[candidate_dict.get(query_class, "") for query_class in query_classes],
                'Score':[score_dict.get(query_class, "") for query_class in query_classes]
                
                }

    result_df = pd.DataFrame(result_pd)
    
    # Save the results to an Excel file
    result_df.to_excel(f'{KBs_path}SBERTcandidates{ontology1}2{ontology2}.xlsx', index=False)
    
    #Create the final dataframe for the results
    
    # Create an SQLite database
    db_name=f'{KBs_path}SBERTcandidates{ontology1}2{ontology2}'
    db_path = f'{KBs_path}SBERTcandidates{ontology1}2{ontology2}.db'  # Archivo SQLite
    conn = sqlite3.connect(db_path)
    # Save the DataFrame in a table in the database
    result_df.to_sql(db_name, conn, if_exists='replace', index=False)

    # Cerrar la conexión
    conn.close()
    # Optionally, store the embeddings if required
    if store_embeddings: 
        print("Embeddings will be stored.")
        import pickle
        with open(KBs_path+ontology2+'_embeddings.pickle', 'wb') as pkl:
            pickle.dump(corpus_embeddings, pkl)
        
    else:
        print("Embeddings will NOT be stored.")
    
     
    return list(set(candidate_list))