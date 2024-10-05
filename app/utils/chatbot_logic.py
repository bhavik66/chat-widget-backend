import os
from typing import Dict
from langchain.memory import ConversationBufferMemory
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from dotenv import load_dotenv
load_dotenv()

google_api_key = os.getenv("GOOGLE_API_KEY")

# Create an instance of the LLM, using the 'gemini-pro' model with a specified creativity level
llm = ChatGoogleGenerativeAI(model='gemini-pro', temperature=0.9, api_key=google_api_key)

# # Set up conversation memory to track the state of the conversation
# memory = ConversationBufferMemory(memory_key="chat_history")

# Set up a prompt template
prompt = PromptTemplate.from_template('''
You are a support chatbot. Based on the previous conversation: {chat_history}, respond to the following question, keeping the response under 250 characters: {user_message}
''')
chain = LLMChain(llm=llm, prompt=prompt, verbose=True)


def convert_to_chat_history(messages: list) -> str:
    chat_history = []

    # Loop through each message and format it as "User:" or "AI:"
    for message in messages:
        sender = "Human" if message.sender == "user" else "AI"
        content = message.content.strip()  # Remove leading/trailing whitespace
        chat_history.append(f"{sender}: {content}")

    # Join the list into a single string with new lines separating each message
    return "\n".join(chat_history)


def generate_ai_response(user_message: str, messages: list) -> Dict:

    chat_history = convert_to_chat_history(messages)

    input_dict = {
        'chat_history': chat_history,
        'user_message': user_message
    }
    response_text = chain.run(input_dict)
    # response_text = response.get('text')
    actions = None

    if "Learn More".lower() in response_text:
        actions = {
            "action1": "Learn More",
            "action2": "Get Help"
        }
    elif "Account Issue".lower() in response_text:
        actions = {
            "action1": "Account Issues",
            "action2": "Technical Support"
        }

    response = {
        "content": response_text,
        "actions": actions
    }
    return response
