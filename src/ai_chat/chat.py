from dotenv import load_dotenv
import openai
import os
from src.chroma.db import recall

# env load
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# states
HISTORY_MAX = 4
RECALL_MAX = 1
histories = []

def chat_response(prompt):
    histories.append({ 'role': "user", 'content': prompt })

    # if history is too long, remove the oldest message
    if len(histories) > HISTORY_MAX:
        for i in range(len(histories) - HISTORY_MAX):
            histories.pop(0)

    with_system = [{ 'role': "system", 'content': "you are a jumango, creative nerd hacker. you answers always very shortly." }]
    recalls = recall(prompt, RECALL_MAX)
    for r in recalls:
        with_system.append({ 'role': "assistant", 'content': r })
    for history in histories:
        with_system.append(history)
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=with_system
    )
    ai_response = response.choices[0].message.content
    histories.append({ 'role': "assistant", 'content': ai_response })

    return '🫧 ' + ai_response

def erase_memory():
    histories = []
