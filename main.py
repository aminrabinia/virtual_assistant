
import requests
from fastapi import FastAPI
import gradio as gr
import os
import openai
import uvicorn
import json
from contact import UserData
from emails import send_out_email
from read_doc import read_my_doc
from dotenv import load_dotenv, find_dotenv

_ = load_dotenv(find_dotenv()) # read local .env file

openai.api_key  = os.environ['OPENAI_API_KEY']

user = UserData()

functions=[
    {
        "name": "get_user_info",
        "description": "Collect user's name and email and their message.",
        "parameters": {
            "type": "object",
            "properties": {
                "user_name": {"type": "string", 
                                  "description": "name of user"},        
                "user_email": {"type": "string",
                                   "description": "user's email address"},
                "email_body": {"type": "string", 
                                 "description": "the message that user wants to leave"}
            },
            "required": ["user_name", "user_email", "email_body"],
        },
    }
]

def save_and_email_leads():
    print('\n*******sending out email')
    send_out_email(my_user=user)
    print('\n*******email has been sent')
    # clean the object
    user.user_name = ""
    user.user_email = ""
    user.email_body = ""


def call_openai_api(messages, 
                    model="gpt-3.5-turbo-16k", 
                    temperature=0.0, 
                    max_tokens=100, 
                    call_type="none"):
    try:
        response = openai.ChatCompletion.create(model=model,
                                                messages=messages,
                                                temperature=temperature, # this is the degree of randomness of the model's output
                                                max_tokens=max_tokens, # the maximum number of tokens the model can ouptut 
                                                functions=functions,
                                                function_call=call_type,
        )
        return response
    
    except requests.exceptions.RequestException as e:  # to be improved to handle any possible errors such as service overload
        print("Network error:", e)
        return "Sorry, there is a technical issue on my side... \
        please wait a few seconds and try again."

def get_completion_from_messages(messages):

    # print("all msg history:\n", messages)

    # if all the arguments present, write to file and send email
    if user.user_name and user.user_email and user.email_body:
        save_and_email_leads()
        # if function call activated it returns content null, 
        # so call api again to get response without function call
        return call_openai_api(messages = [
                                {'role': 'system', 'content': f"Thank user for providing information. \
                                Ensure them someone will be in touch with them to follow up."}],  
                                call_type="none"
                                ).choices[0].message["content"]  # return content 

    # else if args not complete, continue the chat and look for function activation
    api_response = call_openai_api(messages, 
                                    call_type="auto")
    gpt_response = api_response["choices"][0]["message"]
    # print('gpt response------: ', gpt_response)

    if gpt_response.get("function_call"):
        function_name = gpt_response["function_call"]["name"]
        if function_name == "get_user_info":
            arguments = json.loads(gpt_response["function_call"]["arguments"])
            user.get_user_info(
                                user_name=arguments.get("user_name"),
                                user_email=arguments.get("user_email"),
                                email_body=arguments.get("email_body")
                                )
            # if args collected, continue the chat with no function activation
            return call_openai_api(messages = messages,  
                                     call_type="none"
                                     ).choices[0].message["content"]

    else: 
        print("No function activated")
        return api_response.choices[0].message["content"]

# read google doc
professional_information = read_my_doc()
if professional_information:
    print("\ndoc is read successfully!\n")

def process_user_message(user_input, all_messages):
    delimiter = "```"
    system_message = f"""
    You are a personal assitant for Amin. \
    Respond in a friendly and helpful tone, with short answers from the relevant information available to you. \
    Ask user if they want to leave a message and then collect their name, email and message. \
    Don't make assumptions about what values to plug into functions for name, email and messages.    
    """
    messages = [
        {'role': 'system', 'content': system_message},
        {'role': 'user', 'content': f"{delimiter}{user_input}{delimiter}"},
        {'role': 'assistant', 'content': f"you are a personal assistant"}
    ]

    final_response = get_completion_from_messages(all_messages + messages)
    all_messages = all_messages + messages[1:]
    
    return final_response, all_messages
    

app = FastAPI()

@app.get('/')
def root():
    return {"message": "hello from chatbot! Redirect to /chatbot"}


context = [{'role': 'assistant', 'content': f"Relevant information about Amin:\n{professional_information}. \
            Outside work Amin is a part time artist. He plays piano for 15 years, he plays guitar and paints watercolor beautifully.\
            He also plays tennis and is physically active."}]
chat_history = []

print("\n===chatbot started======\n")
with gr.Blocks(css="footer {visibility: hidden}") as demo:
    chatbot = gr.Chatbot([["...","Hello from Amin's Personal Assistant! Do you have any specific question?"]])
    msg = gr.Textbox()
    clear = gr.ClearButton([msg, chatbot])

    def respond(message, chat_history):
        global context
        response, context = process_user_message(message, context)
        context.append({'role':'assistant', 'content':f"{response}"})
        chat_history.append((message, response))
        return "", chat_history

    msg.submit(respond, [msg, chatbot], [msg, chatbot])
gr.mount_gradio_app(app, demo, path="/chatbot")



if __name__ == "__main__":
    print("\n======api started to redirect=====\n")
    uvicorn.run(app, host='0.0.0.0', port=8080)


