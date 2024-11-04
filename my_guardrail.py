import asyncio
import openai
from dotenv import load_dotenv
import os

load_dotenv()

GPT_MODEL = 'gpt-4o-mini'


# API Configuration
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
openai.api_key = os.getenv("OPENAI_API_KEY")


system_prompt = "You are a helpful language assistant."


async def get_chat_response(user_request):
    print("Getting LLM response")
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_request},
    ]
    response = openai.chat.completions.create(
        model=GPT_MODEL, messages=messages, temperature=0.5
    )
    print("Got LLM response")

    return response.choices[0].message.content


async def topical_guardrail(user_request):
    print("Checking topical guardrail")
    messages = [
        {
            "role": "system",
            "content": "Your role is to assess whether the user message is allowed or not. The allowed topic is translation only. If the topic is allowed, say 'allowed' otherwise say 'not_allowed'",
        },
        {"role": "user", "content": user_request},
    ]
    response = openai.chat.completions.create(
        model=GPT_MODEL, messages=messages, temperature=0
    )

    print("Got guardrail response")
    return response.choices[0].message.content


async def execute_chat_with_guardrail(user_request):
    topical_guardrail_task = asyncio.create_task(topical_guardrail(user_request))
    chat_task = asyncio.create_task(get_chat_response(user_request))

    while True:
        done, _ = await asyncio.wait(
            [topical_guardrail_task, chat_task], return_when=asyncio.FIRST_COMPLETED
        )
        if topical_guardrail_task in done:
            guardrail_response = topical_guardrail_task.result()
            if guardrail_response == "not_allowed":
                chat_task.cancel()
                print("Topical guardrail triggered")
                return "I can only translate, please resubmit your translation inquiry."
            elif chat_task in done:
                chat_response = chat_task.result()
                return chat_response
        else:
            await asyncio.sleep(0.1)  # sleep for a bit before checking the tasks again