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

    print(deidentified_text)

    # send redacted prompt to LLM 
    GPT_MODEL = 'gpt-4'
    res = OpenAI().chat.completions.create(
        model=GPT_MODEL,
        messages=[
            {'role': 'system', 'content': 'You are a helpful English-Vietnamese translation assistant.'},
            {'role': 'user', 'content': deidentified_text}
        ]
    )

    res_text = res.choices[0].message.content
    completions['redacted'] = res_text
    print(res_text+'\n')

    # re-identify the anonymous LLM response

    reidentification_request_obj = request_objects.reidentify_text_obj(
        processed_text=[completions["redacted"]], entities=entity_list)

    reidentification_response_obj = client.reidentify_text(
        reidentification_request_obj)

    completions["reidentified"] = reidentification_response_obj.body[0]

    print(completions['reidentified'])

    return {
        "redacted prompt": deidentified_text, 
        "llm output": res_text, 
        "re-identified": completions['reidentified']
    }