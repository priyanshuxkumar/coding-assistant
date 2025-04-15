from dotenv import load_dotenv
load_dotenv() 

import json
import os
from google import genai
from google.genai import types

client = genai.Client(api_key=os.environ.get("gemini_api_key2"))

prompt = """
        You are professional judge of coding problems . 
        For given input data you have to analyze the query and output return the "only" score between 1 to 10.
        
        
        Input data contains two items "query" and "output"

        query: this is original user query
        query_output: this is output generated to this user query

        Example: 
        query: write the python program of adding two numbers and put the code on file
        query_output: def add(x, y): return x + y  

        Output: Score is 8
"""

def ask_gemini(query, output):

    inputs = f"""
        {prompt}
    
        Query: {query}
        
        Query Output: {output}
    """

    try:
        response = client.models.generate_content(
            model='gemini-2.0-flash-001', contents=inputs
        )
        return response.text
    except Exception as e:
        print('ask gemini error: ', e)
