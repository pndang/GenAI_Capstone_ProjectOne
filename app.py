from profanity_check import predict
import guardrails as gd
from guardrails.validators import Validator, EventDetail, register_validator
from typing import Dict, List
from rich import print
from openai import OpenAI
import streamlit as st 
from dotenv import load_dotenv
import os

load_dotenv()

GPT_MODEL = 'gpt-4o'

# API Configuration
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
OpenAI.api_key = os.getenv("OPENAI_API_KEY")


def without_guardrails(text):

    prompt = [
        {"role": "user", "content": 
         "Translate the texts to English language\n"+text},
    ]

    response = OpenAI().chat.completions.create(
        model=GPT_MODEL, 
        messages=prompt,
        max_tokens=2055,
        temperature=0.5
    )

    result = response['choices'][0].message.content

    return result


rail_str = """
<rail version="0.1">

<script language='python'>

@register_validator(name="is-profanity-free", data_type="string")
class IsProfanityFree(Validator):
    global predict
    global EventDetail
    def validate(self, key, value, schema) -> Dict:
        text = value
        prediction = predict([value])
        if prediction[0] == 1:
            raise EventDetail(
                key,
                value,
                schema,
                f"Value {value} contains profanity language",
                "",
            )
        return schema
</script>

<output>
    <string
        name="translated_statement"
        description="Translate the given statement into english language"
        format="is-profanity-free"
        on-fail-is-profanity-free="fix" 
    />
</output>


<prompt>

Translate the given statement into english language:

{{statement_to_be_translated}}

@complete_json_suffix
</prompt>

</rail>
"""

guard = gd.Guard.from_rail_string(rail_str)

def main():
    st.title("LLM Translator with Guardrails ")

    text_area = st.text_area("Enter your Text that you want to translate!")

    if st.button("Translate"):
        if len(text_area) > 0:
            st.info(text_area)

            st.warning("Translation Response Without Guardrails")       
            wo_guardrails_res = without_guardrails(text_area)
            st.success(wo_guardrails_res)
            
            st.warning("Translation With Guardrails")

            raw_llm_response, validated_response = guard(
                OpenAI().chat.completions.create,
                prompt_params={"statement_to_be_translated": text_area},
                engine="gpt-4o",
                max_tokens=2048,
                temperature=0)

            st.success(f"Validated Output: {validated_response}")

if __name__ == "__main__":
    main()