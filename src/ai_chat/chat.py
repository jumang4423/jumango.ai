from dotenv import load_dotenv
import openai
import os

# env load
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# states
HISTORY_MAX = 4
histories = []

def chat_response(prompt):
    histories.append({ 'role': "user", 'content': prompt })

    # if history is too long, remove the oldest message
    if len(histories) > HISTORY_MAX:
        for i in range(len(histories) - HISTORY_MAX):
            histories.pop(0)

    with_system = [{ 'role': "system", 'content': "you are a jumango. your answer always very very short." }]
    for history in histories:
        with_system.append(history)
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=with_system
    )
    ai_response = response.choices[0].message.content
    histories.append({ 'role': "assistant", 'content': ai_response })

    return '🫧 ' + ai_response
