from dotenv import load_dotenv
load_dotenv() 

import os
import json
from openai import OpenAI
from helper import judge, run_command

client = OpenAI(
    api_key=os.environ.get("gemini_api_key"),
    base_url="https://generativelanguage.googleapis.com/v1beta/"
)

available_tools = {
    "run_command": {
        "fn": run_command,
        "description": "Takes a command as input to execute on system and returns ouput"
    },
    "judge": {
        "fn": judge,
        "description" : "Takes user_query and output as input and returns score between 1 to 10"
    }
}

system_prompt = """
    You are a coding assistant who are professional in coding 

    You can only answer coding related questions. If the question is not related to coding you don't need to analyze and perform any action."

    You work on start, analyze, action and observe mode.

    For a given query and available tools, plan the step by step execution, based on planning select the relevent tool from the available tools. and based on the selected tool you perform an action to call/execute the tool. Wait for the observation and based on the observation from the tool call resolve the user query. and help user to solve along with explanation.

    Rules:
    - Follow the Output JSON Format.
    - Always perform one step at a time and wait for next input
    - Carefully analyse the user query

    Output JSON Format:
    {{
        "step": "string",
        "content": "string",
        "function": "The name of function if the step is action",
        "input": "The input parameter for the function",
    }}

    Available Tools:
    - run_command: Takes a command as input to execute on system and returns output
    - judge: Takes user_query and output as input and returns score between 1 to 10


    Examples:

    Input: Create a python file and write a program of add two numbers on it.
    Output: {{ "step": "analyze", "content":  "The user is asking to create a Python file with adding two numbers program on it." }}
    Output: {{ "step": "analyze", "content":  "From the available_tools I should call run_command" }}
    Output: {{ "step": "action",  "function": "run_command", "input": cat > add.py << 'EOF' def add(a, b): return a + b EOF }}
    Output: {{ "step": "observe", "output":   "Add function has written on add.py" }}
    Output: {{ "step": "analyze", "content":  "From the available_tools i should use "judge" function to validate the output" }}
    Output: {{ "step": "action",  "function": "judge", "input": { 
                                                            "query": "Create a python file and write a program of add two numbers on it", 
                                                            "output": "def add(a, b): return a + b"
                                                        } 
            }}
    Output: {{ "step": "observe", "content":  "Judge return score 8 . Everything gone fine proceding to final output" }}
    Output: {{ "step": "output",  "content":  "Everything goes fine your file has been successfully created with required code." }}
"""


messages = [
    {"role" : "system", "content" : system_prompt },
]

while True:
    user_input = input("> ")
    messages.append({"role" : "user", "content" : user_input })


    while True:
        try:
            response = client.chat.completions.create(
                model="gemini-1.5-flash",
                response_format={"type": "json_object"},
                messages=messages
            )
            
            parsed_res = json.loads(response.choices[0].message.content)

            messages.append({ "role": "assistant", "content": json.dumps(parsed_res) })

            if parsed_res.get("step") == "analyze":
                print(f"🧠: {parsed_res.get("content")}")
                continue
            
            if parsed_res.get("step") == "action":
                tool_name = parsed_res.get("function")
                tool_input = parsed_res.get("input")

                if available_tools.get(tool_name, False) != False:
                    output = available_tools[tool_name].get("fn")(tool_input)
                    messages.append({ "role": "assistant", "content": json.dumps({ "step": "observe", "output":  output}) })
                    continue
            
            if parsed_res.get("step") == "observe":
                print(f"👁️: {parsed_res.get("content")}")
                continue

            if parsed_res.get("step") == "output":
                print(f"🤖: {parsed_res.get("content")}")
                break

        except Exception as e:
            print(f"❌: Error occured while generating response {e}")
            break