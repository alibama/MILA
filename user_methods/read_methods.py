#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

@author: keam
"""
import rdflib
import pandas as pd
from owlready2 import *


##########################################################################################################            
#Function for reading class labels in the  ontology
def fma_read (ontology_path):
    sync_reasoner()
    print("fin razonador")
    
    onto = get_ontology(ontology_path).load()
    all_onto_classes=list(onto.classes())
    
    #Read all related synonyms from an ontology and returns several dictionaries
    onto_dic={} #Store pairs (term, iri) for each term and class
    onto_classes_dic={} #Store all terms for each class
    onto_pref_dic={} #Store pairs (preferred_term, iri) for class
    
    for c in all_onto_classes:
        #First add preferred terms
        pref_term = c.label[0].lower()
        if pref_term in onto_pref_dic:
            onto_pref_dic[pref_term]=onto_pref_dic[pref_term]+'|'+c.iri
        else:
            onto_pref_dic[pref_term]=c.iri #Store the pair (iri, preferred term)
        #Then, the synonyms
        
        proc_syns=list(set([x.lower() for x in c.synonym+[c.label[0]]]))
        parents=list(c.ancestors() - {c})
        
        syns_in_parents=[parent.label[0].lower() for parent in parents if parent.label!=[] and parent.label[0].lower() in proc_syns]
        if syns_in_parents!=[]:
           proc_syns=list(set(proc_syns)-set(syns_in_parents))
           #print(c.label[0],":",syns_in_parents, proc_syns)
        
        syns="|".join([syn.lower() for syn in proc_syns])
        onto_classes_dic[c.iri]="|"+syns+"|"
        
        #A cada término, le asigno la clase en la que está
        for syn in proc_syns:
          #Chequeo si el sinónimo corresponde al término preferido de una superclase. Si es así, lo elimino:
            
            if syn.lower() in onto_dic:
                onto_dic[syn.lower()]=onto_dic[syn.lower()]+'|'+c.iri
            else:
                onto_dic[syn.lower()]=c.iri
    
    return onto_dic,onto_classes_dic,onto_pref_dic
##########################################################################################################            
#Function for reading class labels in the  ontology
def ncit_neoplasm_read (ontology_path):
    
    onto = get_ontology(ontology_path).load()
    all_onto_classes=list(onto.classes())
    
    #Read all related synonyms from an ontology and returns several dictionaries
    onto_dic={} #Store pairs (term, iri) for each term and class
    onto_classes_dic={} #Store all terms for each class
    onto_pref_dic={} #Store pairs (preferred_term, iri) for class
    
    for c in all_onto_classes:
        #First add preferred terms
        pref_term = c.label[0].lower()
        if pref_term in onto_pref_dic:
            onto_pref_dic[pref_term]=onto_pref_dic[pref_term]+'|'+c.iri
        else:
            onto_pref_dic[pref_term]=c.iri #Store the pair (iri, preferred term)
        
        #Then, the synonyms
        proc_syns=list(set([x.lower() for x in c.P90]))
        
        if "'" in pref_term:
            parents=[]
        else:
            allparents=list(default_world.sparql("""
                   SELECT ?y
                   { ?x rdfs:label '"""+str(c.label[0])+"""' .
                     ?x rdfs:subClassOf* ?y }
                   """))
            parents=[x[0] for x in allparents if 'ncit.neoplas.C' in str(x[0])[:14] and x[0]!=c]
        
        
        syns_in_parents=[parent.label[0].lower() for parent in parents if parent.label!=[] and parent.label[0].lower() in proc_syns]
        
        if syns_in_parents!=[]: #Remove synonyms that are also included as synonyms in parents
           proc_syns=list(set(proc_syns)-set(syns_in_parents))
           #print(c.label[0],":",syns_in_parents, proc_syns)
        
        syns="|".join([syn.lower() for syn in proc_syns])
        onto_classes_dic[c.iri]="|"+syns+"|"
        
        
        for syn in proc_syns:
            if syn in onto_dic:
                onto_dic[syn]=onto_dic[syn]+'|'+c.iri
            else:
                onto_dic[syn]=c.iri
     
    #There are errors in owlready. For example, anscestors of Esophageal Adenocarcinoma incorrectly are {ncit.neoplas.C4025, owl.Thing}.

    for pos,c in enumerate(all_onto_classes):
        if '|' in onto_dic[c.label[0].lower()]:
            #print(c.label[0])
            
            #THE UNDERSTANDING MUST BE FIXED: owlready does not work or the ontology is poorly defined.
            iris=onto_dic[c.label[0].lower()].split('|')
            for iri in list(set(iris)-{c.iri}):
                onto_classes_dic[iri]=onto_classes_dic[iri].replace('|'+c.label[0].lower()+'|','|')
                
                
            onto_dic[c.label[0].lower()]=c.iri
            
    return onto_dic,onto_classes_dic,onto_pref_dic
##########################################################################################################
#Function for reading class labels in the envo ontology
def snomed_read (ontology_path):#,all_onto_classes):
    onto = get_ontology(ontology_path).load()
    all_onto_classes=list(onto.classes())
    #Read all related synonyms from an ontology and returns several dictionaries
    onto_dic={} #Store pairs (term, iri) for each term and class
    onto_classes_dic={} #Store all terms for each class
    onto_pref_dic={} #Store pairs (preferred_term, iri) for class
    
    for c in all_onto_classes:
        #First add preferred terms
        pref_term = c.prefLabel[0].lower()
        if pref_term in onto_pref_dic:
            onto_pref_dic[pref_term]=onto_pref_dic[pref_term]+'|'+c.iri
        else:
            onto_pref_dic[pref_term]=c.iri #Store the pair (iri, preferred term)
            
        termlist=[pref_term]
        #Then, the synonyms
        completesyns=c.altLabel
        if len(completesyns)>0: 
            synlist=[syn.lower() for syn in completesyns] 
            termlist=termlist+synlist
            termlist=list(set(termlist)) #remove duplicates
            terms="|".join(termlist)
            onto_classes_dic[c.iri]='|'+terms+'|' #Store all terms for each class   
        else:
            onto_classes_dic[c.iri]='|'+pref_term+'|'
            
        for syn in termlist:
          if syn in onto_dic:
              onto_dic[syn]=onto_dic[syn]+'|'+c.iri
          else:
              onto_dic[syn]=c.iri
              
    return onto_dic,onto_classes_dic,onto_pref_dic
##########################################################################################################
#Function for reading class labels in the omim ontology
def omim_read (ontology_path):
    onto = get_ontology(ontology_path).load()
    all_onto_classes=list(onto.classes())
    #Read all related synonyms from an ontology and returns several dictionaries
    onto_dic={} #Store pairs (term, iri) for each term and class
    onto_classes_dic={} #Store all terms for each class
    onto_pref_dic={} #Store pairs (preferred_term, iri) for class
    
    for c in all_onto_classes:
        #First add preferred terms
        pref_term = c.label[0].lower()
        if pref_term in onto_pref_dic:
            onto_pref_dic[pref_term]=onto_pref_dic[pref_term]+'|'+c.iri
        else:
            onto_pref_dic[pref_term]=c.iri #Store the pair (iri, preferred term)
            
        termlist=[pref_term]
        #Then, the synonyms
        completesyns=c.hasExactSynonym+c.exactMatch
        if len(completesyns)>0: 
            synlist=[syn.lower() for syn in completesyns] 
            termlist=termlist+synlist
            termlist=list(set(termlist)) #remove duplicates
            terms="|".join(termlist)
            onto_classes_dic[c.iri]='|'+terms+'|' #Store all terms for each class   
        else:
            onto_classes_dic[c.iri]='|'+pref_term+'|'
            
        for syn in termlist:
          if syn in onto_dic:
              onto_dic[syn]=onto_dic[syn]+'|'+c.iri
          else:
              onto_dic[syn]=c.iri
              
    return onto_dic,onto_classes_dic,onto_pref_dic
##########################################################################################################
#Function for reading class labels in the ordo ontology
def ordo_read (ontology_path): 
    onto = get_ontology(ontology_path).load()
    all_onto_classes=list(onto.classes())
    #Read all related synonyms from an ontology and returns several dictionaries
    onto_dic={} #Store pairs (term, iri) for each term and class
    onto_classes_dic={} #Store all terms for each class
    onto_pref_dic={} #Store pairs (preferred_term, iri) for class
    
    for c in all_onto_classes:
        #First add preferred terms
        pref_term = c.label[0].lower()
        if pref_term in onto_pref_dic:
            onto_pref_dic[pref_term]=onto_pref_dic[pref_term]+'|'+c.iri
        else:
            onto_pref_dic[pref_term]=c.iri #Store the pair (iri, preferred term)
            
        termlist=[pref_term]     
        completesyns=c.alternative_term+c.label
        if len(completesyns)>0: 
            synlist=[syn.lower() for syn in completesyns] 
            termlist=termlist+synlist
            termlist=list(set(termlist)) #remove duplicates
            terms="|".join(termlist)
            onto_classes_dic[c.iri]='|'+terms+'|' #Store all terms for each class   
        else:
            onto_classes_dic[c.iri]='|'+pref_term+'|'
            
        for syn in termlist:
          if syn in onto_dic:
              onto_dic[syn]=onto_dic[syn]+'|'+c.iri
          else:
              onto_dic[syn]=c.iri
        
    return onto_dic,onto_classes_dic,onto_pref_dic
##########################################################################################################            
#Function for reading class labels in the ncit ontology
def ncit_read (ontology_path):
    onto = get_ontology(ontology_path).load()
    all_onto_classes=list(onto.classes())
    #Read all related synonyms from an ontology and returns several dictionaries
    onto_dic={} #Store pairs (term, iri) for each term and class
    onto_classes_dic={} #Store all terms for each class
    onto_pref_dic={} #Store pairs (preferred_term, iri) for class
    
    for c in all_onto_classes:
        #First add preferred terms
        pref_term = c.label[0].lower()
        if pref_term in onto_pref_dic:
            onto_pref_dic[pref_term]=onto_pref_dic[pref_term]+'|'+c.iri
        else:
            onto_pref_dic[pref_term]=c.iri #Store the pair (iri, preferred term)
        
        #Then, the synonyms
        proc_syns=list(set([x.lower() for x in c.P90]))
        
        parents=list(c.ancestors() - {c})
        
        syns_in_parents=[parent.label[0].lower() for parent in parents if parent.label!=[] and parent.label[0].lower() in proc_syns]
        
        if syns_in_parents!=[]: #Remove synonyms that are also included as synonyms in parents
           proc_syns=list(set(proc_syns)-set(syns_in_parents))
           #print(c.label[0],":",syns_in_parents, proc_syns)
        
        syns="|".join([syn.lower() for syn in proc_syns])
        onto_classes_dic[c.iri]="|"+syns+"|"
        
        
        for syn in proc_syns:
            if syn in onto_dic:
                onto_dic[syn]=onto_dic[syn]+'|'+c.iri
            else:
                onto_dic[syn]=c.iri
     
    #There are errors in owlready. For example, anscestors of Esophageal Adenocarcinoma incorrectly are {ncit.neoplas.C4025, owl.Thing}.

    for pos,c in enumerate(all_onto_classes):
        if '|' in onto_dic[c.label[0].lower()]:
            #print(c.label[0])
            
            #THE UNDERSTANDING MUST BE FIXED: owlready does not work or the ontology is poorly defined.
            iris=onto_dic[c.label[0].lower()].split('|')
            for iri in list(set(iris)-{c.iri}):
                onto_classes_dic[iri]=onto_classes_dic[iri].replace('|'+c.label[0].lower()+'|','|')
                
                
            onto_dic[c.label[0].lower()]=c.iri
            
    return onto_dic,onto_classes_dic,onto_pref_dic
    
##########################################################################################################
#Function for reading class labels in the doid ontology
def doid_read (ontology_path):
    onto = get_ontology(ontology_path).load()
    all_onto_classes=list(onto.classes())
    #Read all related synonyms from an ontology and returns several dictionaries
    onto_dic={} #Store pairs (term, iri) for each term and class
    onto_classes_dic={} #Store all terms for each class
    onto_pref_dic={} #Store pairs (preferred_term, iri) for class
    
    for c in all_onto_classes:  
      
      if len(c.label)>0: 
          #First add preferred terms
          pref_term = c.label[0].lower()
          if pref_term in onto_pref_dic:
              onto_pref_dic[pref_term]=onto_pref_dic[pref_term]+'|'+c.iri
          else:
              onto_pref_dic[pref_term]=c.iri #Store the pair (iri, preferred term)
          
          termlist=[pref_term] #lower the label
          
          #Then add synonyms
          if len(c.hasExactSynonym)>0: 
              synlist=[syn.lower() for syn in c.hasExactSynonym]
              termlist=termlist+synlist
              termlist=list(set(termlist)) #remove duplicates
              terms="|".join(termlist)
              onto_classes_dic[c.iri]='|'+terms+'|' #Store all terms for each class   
          else:
              onto_classes_dic[c.iri]='|'+pref_term+'|'
              
          for syn in termlist:
            if syn in onto_dic:
                onto_dic[syn]=onto_dic[syn]+'|'+c.iri
            else:
                onto_dic[syn]=c.iri
                
    return onto_dic,onto_classes_dic,onto_pref_dic

##########################################################################################################
#Function for reading class labels in the envo ontology
def envo_read (ontology_path):
    onto = get_ontology(ontology_path).load()
    all_onto_classes=list(onto.classes())
    #Read all related synonyms from an OBO ontology and returns several dictionaries
    onto_dic={} #Store pairs (term, iri) for each term and class
    onto_classes_dic={} #Store all terms for each class
    onto_pref_dic={} #Store pairs (preferred_term, iri) for class
    
    for c in all_onto_classes:
      #First add preferred terms
      
      if len(c.label)>0: 
          
          pref_term=" ".join(c.label[0].lower().split('_')) #Replace '_' by ' '
          if pref_term in onto_pref_dic:
              onto_pref_dic[pref_term]=onto_pref_dic[pref_term]+'|'+c.iri
          else:
              onto_pref_dic[pref_term]=c.iri #Store the pair (iri, preferred term)
          
          termlist=[pref_term] #lower the label
          
          #Add synonyms
          if len(c.hasExactSynonym)>0: 
              synlist=[syn.lower() for syn in c.hasExactSynonym]
              termlist=termlist+synlist
              termlist=list(set(termlist)) #remove duplicates
              terms="|".join(termlist)
              onto_classes_dic[c.iri]='|'+terms+'|' #Store all terms for each class
              
          else:
              onto_classes_dic[c.iri]='|'+pref_term+'|'
          for syn in termlist:
            if syn in onto_dic:
                onto_dic[syn]=onto_dic[syn]+'|'+c.iri
            else:
                onto_dic[syn]=c.iri
                
    return onto_dic,onto_classes_dic,onto_pref_dic

##########################################################################################################
#Function for reading class labels in the sweet ontology
def sweet_read (ontology_path):
    
    onto = get_ontology(ontology_path).load()
    all_onto_classes=list(onto.classes())
    #Read all related synonyms from an OBO ontology and returns several dictionaries
    onto_dic={} #Store pairs (term, iri) for each term and class
    onto_classes_dic={} #Store all terms for each class
    onto_pref_dic={} #Store pairs (preferred_term, iri) for class
    
    import re
    for c in all_onto_classes:
          #Extract preferred terms
      
          # Use a regular expression to insert a space before each uppercase letter (except the first one), and lower the name
          #pref_term=re.sub(r'(?<!^)(?=[A-Z])', ' ', c.name).lower()
          s=re.sub(r'([a-z])([A-Z])', r'\1 \2', c.name)
          pref_term=re.sub(r'([A-Z]+)([A-Z][a-z])', r'\1 \2', s).lower()
          #pref_term=c.name.lower() #Replace '_' by ' '
          if pref_term in onto_pref_dic:
              onto_pref_dic[pref_term]=onto_pref_dic[pref_term]+'|'+c.iri
          else:
              onto_pref_dic[pref_term]=c.iri #Store the pair (iri, preferred term)
          
          onto_classes_dic[c.iri]='|'+pref_term+'|'
          onto_dic[pref_term]=c.iri
          
                
                
    return onto_dic,onto_classes_dic,onto_pref_dic


##########################################################################################################
#Function for reading class labels in the mouse ontology 
def mouse_read (ontology_path):
    onto = get_ontology(ontology_path).load()
    all_onto_classes=list(onto.classes())
    #Read all preferred terms from ontology and returns a dictionary with pairs (term, class) and another with pairs (class, term)
    onto_dic={}
    onto_classes_dic={}
    for c in all_onto_classes:
        
      if len(c.label)>0: 
        if c.label[0].lower() in onto_dic:
            onto_dic[c.label[0].lower()]=onto_dic[c.label[0].lower()]+'|'+c.iri
        else:
            onto_dic[c.label[0].lower()]=c.iri
            
        onto_classes_dic[c.iri]='|'+c.label[0].lower()+'|'
        
    return onto_dic,onto_classes_dic, onto_dic

##########################################################################################################
#Function for reading class labels in the human ontology  
def human_read (ontology_path):
    onto = get_ontology(ontology_path).load()
    all_onto_classes=list(onto.classes())
    #Read all related synonyms from an OBO ontology and returns several dictionaries
    onto_dic={} #Store pairs (term, iri) for each term and class
    onto_classes_dic={} #Store all terms for each class
    onto_pref_dic={} #Store pairs (preferred_term, iri) for class
    
    for c in all_onto_classes:
      #First add preferred terms
      
      if len(c.label)>0: 
          
          pref_term=" ".join(c.label[0].lower().split('_')) #Replace '_' by ' '
          onto_pref_dic[pref_term]=c.iri #Store the pair (iri, preferred term)
          termlist=[pref_term] #lower the label
          
          #Add synonyms
          if len(c.hasRelatedSynonym)>0: 
              termlist=termlist+[syn.label[0].lower() for syn in c.hasRelatedSynonym]
              termlist=list(set(termlist)) #remove duplicates
              terms="|".join(termlist)
              onto_classes_dic[c.iri]='|'+terms+'|' #Store all terms for each class
          else:
              onto_classes_dic[c.iri]='|'+pref_term+'|'
          for syn in termlist:
            if syn in onto_dic:
                onto_dic[syn]=onto_dic[syn]+'|'+c.iri
            else:
                onto_dic[syn]=c.iri
                
    return onto_dic,onto_classes_dic,onto_pref_dic


#####################################################################################################
#Function for reading, extracting and saving reference mapping entities from an rdf file

def extract_and_save_entities_from_rdf(rdf_file, output_file):
    #Extract and save pairs of entities from a rdf file and return the list of the first entities in the pairs
    # Create a graph to hold the RDF data
    graph = rdflib.Graph()

    # Parse the RDF file
    graph.parse(rdf_file)
    
    # Define the default namespace used in the RDF
    NS = "http://knowledgeweb.semanticweb.org/heterogeneity/alignment"

    # Bind the namespace to a prefix for easier use in the query
    graph.bind("alignment", NS)

    # Query to extract entity1 and entity2 pairs from the RDF
    query = """
    PREFIX align: <""" + NS + """>
    SELECT ?entity1 ?entity2
    WHERE {
        ?cell align:entity1 ?entity1 .
        ?cell align:entity2 ?entity2 .
    }
    """
    
    # Execute the query and extract the entity pairs
    result = graph.query(query)
    
    # Create a list of entity pairs
    entity_pairs = [(str(row[0]), str(row[1])) for row in result]
    source_entities=[str(row[0]) for row in result]
    
    # Convert the entity pairs list into a pandas DataFrame
    df = pd.DataFrame(entity_pairs, columns=["SrcEntity", "TgtEntity"])

    # Save the DataFrame to an Excel file
    df.to_excel(output_file, index=False)
    print(f"Entity pairs saved to {output_file}")
    
    return source_entities

#####################################################################################################
def baseline_extraction(excel_file, output_file):
    #Function for reading, extracting and saving reference mapping entities from an Excel file and return the list of the first entities in the pairs
    #Rename the columns
    data = pd.read_excel(excel_file, header=None)
    data = data.reset_index(drop=True)
    # Extract the first two columns
    extracted_columns = data.iloc[:, :2]
    # Rename the columns
    extracted_columns.columns = ['SrcEntity', 'TgtEntity']
    # Extract the first column (i.e., the first column of the DataFrame)
    # Save the DataFrame to an Excel file
    extracted_columns.to_excel(output_file, index=False)
    
    return extracted_columns['SrcEntity'].tolist()


#####################################################################################################
def excel_file_extraction(excel_file, output_file):
    #Other function for reading, extracting and saving reference mapping entities from an Excel file and return the list of the first entities in the pairs
    #Rename the columns
    data = pd.read_excel(excel_file)
    data = data.reset_index(drop=True)
    # Extract the relevant columns
    data = data[['SrcEntity', 'TgtEntity']]

    # Extract the first column (i.e., the first column of the DataFrame)
    # Save the DataFrame to an Excel file
    data.to_excel(output_file, index=False)
    
    return data['SrcEntity'].tolist()


#####################################################################################################
def extract_and_save_entities_from_excel(excel_file, output_file):
    #Function for reading, extracting and saving reference mapping entities from an Excel file and return the list of the first entities in the pairs
    #Rename the columns
    data = pd.read_excel(excel_file, header=None)
    data = data.reset_index()
    # Extract the first two columns
    extracted_columns = data.iloc[:, :2]

    # Rename the columns
    data.columns = ['SrcEntity', 'TgtEntity']

    # Rename the columns
    data.columns = ['SrcEntity', 'TgtEntity']
    # Extract the first column (i.e., the first column of the DataFrame)
    # Save the DataFrame to an Excel file
    data.to_excel(output_file, index=False)
    
    return data['SrcEntity'].tolist()



