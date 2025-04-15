import os
from gemini import ask_gemini

def run_command(command):
    result = os.system(command=command)
    return result


#Takes chatgpt_output as paramater 
def judge(input : dict): 
    query = input.get("query")
    output = input.get("output")
    gemini_score = ask_gemini(query, output)
    return gemini_score