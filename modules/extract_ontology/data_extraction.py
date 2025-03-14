import pandas as pd
import sqlite3
import os

#####################################################
def ensure_directory_exists(path):
    if not os.path.exists(path):
        os.makedirs(path)


#####################################################
def extract_entities_from_ontology (ontology, ontology_path, KB_path, PT_read_method):

    
    #Define a function to read your ontology. Each ontology has a different syntax
    
    term_class_dic, class_term_dic, pref_term_dic=PT_read_method(ontology_path)
    #Save results
    # Ensure the results directory exists
    ensure_directory_exists('data/ontology_data')
         
    #Store preferred terms
    plabel_pd = {'Term':list(pref_term_dic.keys()),'Entity':list(pref_term_dic.values())}
    pref_term_df = pd.DataFrame(plabel_pd)
    
    #Store every term
    label_pd = {'Term':list(term_class_dic.keys()),'Entity':list(term_class_dic.values())}
    term_onto_df = pd.DataFrame(label_pd)
    
    #Store every class
    class_pd = {'Entity':list(class_term_dic.keys()),'Term':list(class_term_dic.values())}
    class_onto_df = pd.DataFrame(class_pd)
    
    #Store for tracing
    
    # Create an SQLite database
    db_path = KB_path + ".db"  # Archivo SQLite
    conn = sqlite3.connect(db_path)

    # Save every DataFrame in a diferent table in the database
    pref_term_df.to_sql("PreferredTerms", conn, if_exists="replace", index=False)
    term_onto_df.to_sql("Terms", conn, if_exists="replace", index=False)
    class_onto_df.to_sql("Classes", conn, if_exists="replace", index=False)

    # Cerrar la conexión
    conn.close()
    
    return pref_term_df, term_onto_df, class_onto_df
