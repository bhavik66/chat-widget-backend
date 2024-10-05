import os
from typing import Dict
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from dotenv import load_dotenv
load_dotenv()

google_api_key = os.getenv("GOOGLE_API_KEY")

# Create an instance of the LLM, using the 'gemini-pro' model with a specified creativity level
llm = ChatGoogleGenerativeAI(model='gemini-1.5-flash', temperature=0.9, api_key=google_api_key)

# Set up a prompt template
prompt = PromptTemplate.from_template('''
Consider your self as chatbot for support, Give them answer in plain text under 250 character for {user_message}
''')
chain = LLMChain(llm=llm, prompt=prompt, verbose=True)


def generate_ai_response(user_message: str) -> Dict:
    response = chain.invoke(input=user_message)
    response_text = response.get('text')
    if "Learn More" in response_text:
        actions = {
            "action1": "Learn More",
            "action2": "Get Help"
        }
    elif "Account Issues" in response_text:
        actions = {
            "action1": "Account Issues",
            "action2": "Technical Support"
        }
    else:
        actions = None

    response = {
        "content": response_text,
        "actions": actions
    }
    return response
