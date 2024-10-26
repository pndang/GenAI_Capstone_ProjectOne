import streamlit as st 
import os
from dotenv import load_dotenv 
import openai 

GPT_MODEL = 'gpt-4o'

load_dotenv()

os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
openai.api_key = os.getenv("OPENAI_API_KEY")

def without_guardrails(text):

    prompt = [
        {"role": "user", "content": 
         "Translate the texts to English language\n"+text},
    ]

    response = openai.ChatCompletion.create(
        model=GPT_MODEL, 
        messages=prompt,
        max_tokens=2055,
        temperature=0.5
    )

    result = response['choices'][0].message.content

    return result 


def main():
    st.title("Guardrails Implementation in LLMs")

    text_area = st.text_area("Enter your Text that you want to translate!")

    if st.button("Translate"):
        if len(text_area) > 0:
            st.info(text_area)

            st.warning("Translation Response Without Guardrails")       
            wo_guardrails_res = without_guardrails(text_area)
            st.success(wo_guardrails_res)


if __name__ == "__main__":
    main()