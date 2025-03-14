#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#####################################################################################################
# non stream response
def query_LLM_ollama_simple_template(prompt, temperature=None, LLM_model=None):
    import ollama
    r = ollama.generate(model=LLM_model, prompt=prompt, options={
        "temperature": temperature if temperature != None else 0.8
    })
    
    if r["response"] =='Yes':
        return True
        
    else:
        return False

