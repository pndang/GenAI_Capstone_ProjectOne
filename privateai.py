from privateai_client import PAIClient
from privateai_client import request_objects
from openai import OpenAI 
from dotenv import load_dotenv
import os

load_dotenv()

# Set up configurations

PRIVATEAI_API_KEY = os.getenv("PRIVATEAI_API_KEY")
PRIVATEAI_URL = os.getenv("PRIVATEAI_URL")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

openai_client = OpenAI(api_key=OPENAI_API_KEY)


# wrapper function

def private_ai_pipeline(prompt):

    client = PAIClient(url=PRIVATEAI_URL, api_key=PRIVATEAI_API_KEY)

    # build local entities map 
    completions = {}

    completions["raw_text"] = prompt
    redaction_request_obj = request_objects.process_text_obj(text=[prompt])
    redaction_response_obj = client.process_text(redaction_request_obj)

    # store redactions
    deidentified_text = redaction_response_obj.processed_text[0]
    completions["redacted_text"] = deidentified_text
    entity_list = redaction_response_obj.get_reidentify_entities()

    # send redacted prompt to LLM 
    GPT_MODEL = 'gpt-4'

    PREPROMPT = 'Any placeholders are for privacy purposes, please proceed and use the placeholders as=is\n\n'

    res = OpenAI().chat.completions.create(
        model=GPT_MODEL,
        messages=[
            {'role': 'system', 'content': 'You are a helpful English-Vietnamese translation assistant.'},
            {'role': 'user', 'content': PREPROMPT+deidentified_text}
        ]
    )

    print(f"\n\nPrompt sent to LLM:\n\n {PREPROMPT+deidentified_text}\n")

    res_text = res.choices[0].message.content
    completions['redacted'] = res_text

    print("LLM response:\n")
    print(res_text+'\n')

    # re-identify the anonymous LLM response

    reidentification_request_obj = request_objects.reidentify_text_obj(
        processed_text=[completions["redacted"]], entities=entity_list)

    reidentification_response_obj = client.reidentify_text(
        reidentification_request_obj)

    completions["reidentified"] = reidentification_response_obj.body[0]

    print("Response to user:\n")
    print(completions['reidentified'])

    return {
        "redacted prompt": deidentified_text, 
        "llm output": res_text, 
        "re-identified": completions['reidentified']
    }