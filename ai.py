#%%
from openai import OpenAI
import os
from dotenv import load_dotenv
from IPython.display import display, Markdown
#%%
load_dotenv()
#%%
openai_api_key = os.getenv("OPENAI_API_KEY")
if openai_api_key:
    print(f"OpenAI API KEY loaded successfully. Key starts with: {openai_api_key[:10]}:")
else:
    print("API key not found")
#%%
openai_client = OpenAI(api_key=openai_api_key)
#%%
def get_ai_response(messages, tools):
    response = openai_client.chat.completions.create(
        model="gpt-5-mini",
        messages=messages,
        tools=tools,
    )
    return response