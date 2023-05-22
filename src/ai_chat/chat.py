from dotenv import load_dotenv
import openai
import os
from src.chroma.db import recall

# env load
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# states
RECALL_MAX = 2
SYSTEM_PROMPT = "you are a jumango, creative nerd hacker. you answers always very shortly."

def chat_from_global_conv_his(conv_his, prompt):
    with_system = [{ 'role': "system", 'content': SYSTEM_PROMPT }]
    recalls = recall(prompt, RECALL_MAX)
    for r in recalls:
        with_system.append({ 'role': "assistant", 'content': r })
    for history in conv_his:
        with_system.append(history)

    with_system.append({ 'role': "user", 'content': prompt })
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=with_system
    )
    ai_response = response.choices[0].message.content

    return ai_response
