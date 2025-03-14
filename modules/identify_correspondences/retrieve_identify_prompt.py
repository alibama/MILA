import pandas as pd

###################################################################################################################

def is_nan(value):
    """Check if a value is NaN."""
    return value != value
###################################################################################################################

###################################################################################################################

def get_candidate_list(df, query_class):
    """Helper function to fetch candidate list based on Query Class."""
    candidates = df[df['Query Class'] == query_class]    
    
    if candidates.empty:
        return [], ""
    else:
        #Return the list of candidates and the preferred term
        return candidates['Candidate List'].tolist()[0], candidates['Query Preferred Term'].values.tolist()[0]
    

###################################################################################################################

def get_scores(df, query_class):
    """Helper function to fetch scores based on Query Class."""
    
    scores = df[df['Query Class'] == query_class]['Score'].tolist()[0].split('|')
    return [float(x) for x in scores]

###################################################################################################################

def load_template_from_file(file_path):
    with open(file_path, "r") as file:
        return file.read()
    
    
###################################################################################################################

def generate_dynamic_prompt(template_text, src_onto_fullname, tgt_onto_fullname, src_term,tgt_term):
    
    return template_text.format(src_onto_fullname, tgt_onto_fullname, src_term, tgt_term)


###################################################################################################################

def retrieve_identify_prompt (source_ontology, target_ontology, source_entities, src2tgt, tgt2src,output_file,template_file,pref_terms_pd, target_classes_pd, query_LLM_method, temperature=None, LLM_model=None):
    import time
    ini=time.time()
    LLM_query_number=0
    
    # Load prompt template in a string
    template_text=load_template_from_file(template_file)
    
    
    correspondence_type=[]
    correspondence=[]
    cands_to_prompt=[]
    scores_to_prompt=[]
    RAGCands=[]
    queries_PT=[]
    
    
    for query_no,query in enumerate(source_entities):
        
      # Get target candidates for the source query
      tgt_cands, query_PT = get_candidate_list(src2tgt, query)
      
      if tgt_cands: # Query is in the vector KB
      
        queries_PT.append(query_PT)
        
        if is_nan(tgt_cands): #There is no results from embedding similarity
            correspondence_type.append('Unmatched by embedding similarity')
            cands_to_prompt.append([])
            scores_to_prompt.append([])
            RAGCands.append([])
            correspondence.append([])
        else:
            
            tgt_cands=tgt_cands.split('|')
            RAGCands.append(tgt_cands)
            
            direct_scores = get_scores(src2tgt, query)
                        
            if is_nan(get_candidate_list(tgt2src, tgt_cands[0])):      
                correspondence_type.append('Unmatched by embedding similarity')
                cands_to_prompt.append([])
                scores_to_prompt.append([])
                correspondence.append([])
     
            else: 
                direct_max_score=direct_scores[0]
                cand_list, score_list = [], []
                
                # Look for bidirectional/HCB correspondences
                j=0
                while j<len(tgt_cands) and round(float(direct_scores[j]),5)==round(float(direct_max_score),5):
                    
                    srccands_for_tgt_cand, _ = get_candidate_list(tgt2src, tgt_cands[j])
                    srccands_for_tgt_cand=srccands_for_tgt_cand.split('|')
                    inverse_scores = get_scores(tgt2src, tgt_cands[j])
                    
                    k=0
                    max_inverse_score=inverse_scores[0]
                    while k<len(srccands_for_tgt_cand) and round(float(inverse_scores[k]),5)==round(float(max_inverse_score),5):
                        src_cand=srccands_for_tgt_cand[k]
                        
                        if src_cand==query:
                            cand_list.append(tgt_cands[j])
                            score_list.append(direct_scores[j])

                        k+=1
                
                    j+=1          
                
                if len(cand_list)>0: #It is a HCB correspondence
                    cands_to_prompt.append(cand_list)
                    scores_to_prompt.append(score_list)
                    correspondence_type.append('HCB Correspondence')
                    correspondence.append(cand_list)
                        
                else: #Look for bidirectional correspondence
                    cand_list, score_list = [], []
                    
                    for pos, tgt_cand in enumerate(tgt_cands):
                     if len(tgt2src[(tgt2src['Query Class']==tgt_cand) & (tgt2src['Candidate List'].notnull())])>0:
                         
                        direct_score=direct_scores[pos]
                        srccands_for_tgt_cand = get_candidate_list(tgt2src, tgt_cand)[0].split('|') 
                        
                        
                        if query in srccands_for_tgt_cand:
                            cand_list.append(tgt_cand)
                            score_list.append(direct_score)
                    
                    
                    #Annotate if there is one or more candidates that are bidirectional correspondences
                    if not score_list: # There is no bidirectional correspondence
                        correspondence_type.append('No Bidirectional Correspondence')
                        correspondence.append([])
                    else:
                        correspondence_type.append('Bidirectional Correspondence')
                        #correspondence.append([])
                        
                        # Query the LLM until it confirms a bidirectional correspondence
                        i=0
                        confirmed=False
                        #print(cand_list)
                        while i<len(cand_list):
                            
                            #Get the preferred term for tgt_cand
                            tgt_cand=cand_list[i]
                            
                            tgt_term = target_classes_pd[target_classes_pd['Entity'] == tgt_cand]['Term'].values.tolist()[0].split('|')[1]
                            
                            prompt=generate_dynamic_prompt(template_text, source_ontology, target_ontology, query_PT, tgt_term)
                            confirmed=query_LLM_method(prompt, temperature, LLM_model)
                            LLM_query_number+=1
                            
                                
                            i+=1
                            if confirmed:
                                i=len(cand_list)
                                correspondence.append([tgt_cand])
                                
                        if not confirmed:
                            correspondence.append([])
                    scores_to_prompt.append(score_list)
                    cands_to_prompt.append(cand_list)
                    
                    

      else:
          correspondence_type.append('Error: the source entity is not in the vector KB')
          cands_to_prompt.append([])
          scores_to_prompt.append([])  
          queries_PT.append('')
          RAGCands.append([])
          correspondence.append([])
         
          
    #Store results
    

    result_pd = {'Query Class':source_entities,
                 'Query Class Label': queries_PT,
                'Candidate List':[x[0] if len(x)==1 else "|".join(x) for x in cands_to_prompt],
                'Score':["" if len(x)==0 else "|".join([str(y) for y in x]) for x in scores_to_prompt],
                'Type of correspondence':correspondence_type,
                'Correspondence': [x[0] if len(x)==1 else "|".join(x) for x in correspondence],
                'List of RAG candidates':[x[0] if len(x)==1 else "|".join(x) for x in RAGCands]
                
                }
    identified_mappings = pd.DataFrame(result_pd)
    identified_mappings.to_excel(output_file,index=False)
    print(f"Identified correspondences saved to {output_file}")
    fin=time.time()
    print(f'Time:{fin-ini}')
    print(f'Number of LLM queries: {LLM_query_number} ')
    
