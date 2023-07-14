
import signal
from fastapi import FastAPI
import gradio as gr
import os
import openai
import uvicorn
from emails import send_out_email
from read_doc import read_my_doc
from dotenv import load_dotenv, find_dotenv

_ = load_dotenv(find_dotenv()) # read local .env file

openai.api_key  = os.environ['OPENAI_API_KEY']


def get_completion_from_messages(messages, 
                    model="gpt-3.5-turbo-16k", 
                    temperature=0.0, 
                    max_tokens=100):
    try:
        response = openai.ChatCompletion.create(model=model,
                                                messages=messages,
                                                temperature=temperature, # this is the degree of randomness of the model's output
                                                max_tokens=max_tokens, # the maximum number of tokens the model can ouptut 
                                                )
        return response.choices[0].message["content"]
    
    except Exception as e:  # to be improved to handle any possible errors such as service overload
        print("Network error:", e)
        return "Sorry, there is a technical issue on my side... \
        please wait a few seconds and try again."


# read google doc
professional_information = read_my_doc()
if professional_information:
    print("\ndoc is read successfully!\n")

def process_user_message(user_input, all_messages):
    delimiter = "```"
    system_message = f"""
    You are a virtual professional assitant for Amin and you only answer questions about him. \
    Respond in a friendly and helpful tone, with short answers from the relevant information available to you. \   
    Do not answer any questions that are not relevant to Amin's profile, e.g. coding, general irrelevant questions, etc. 
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

# Define a signal handler function
def handle_termination(signal, frame):
    # Print the content of chat_history
    print("Signal Received\nTermination Activated\n")
    send_out_email(chat_history)
    print("Email sent out!")
    # Exit the application
    exit(0)


print("\n===chatbot started======\n")
with gr.Blocks(css="footer {visibility: hidden}") as demo:
    chatbot = gr.Chatbot([["","Hello from Amin's Personal Assistant! \nDo you have any specific question about Amin's background or experience?\
                           \n (--Please note that Amin will receive a summary of this conversation--)"]])
    msg = gr.Textbox()
    clear = gr.ClearButton([msg, chatbot])

    def respond(message, chat_history):
        global context
        response, context = process_user_message(message, context)
        context.append({'role':'assistant', 'content':f"{response}"})
        chat_history.append((message, response))
        print(chat_history)
        return "", chat_history

    msg.submit(respond, [msg, chatbot], [msg, chatbot])
gr.mount_gradio_app(app, demo, path="/chatbot")


if __name__ == "__main__":

    print("\n======api started to redirect=====\n")

    # Register the signal handler for SIGTERM  handles Ctrl-C locally
    signal.signal(signal.SIGTERM, handle_termination)

    uvicorn.run(app, host='0.0.0.0', port=8080)
else:
    # handles Cloud Run container termination
    signal.signal(signal.SIGTERM, handle_termination)


