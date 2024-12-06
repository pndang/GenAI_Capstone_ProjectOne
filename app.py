import openai 
import os
from dotenv import load_dotenv
import streamlit as st

from privateai import *

from nemoguardrails import RailsConfig, LLMRails

load_dotenv()

# API Configuration
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
openai.api_key = os.getenv("OPENAI_API_KEY")

# load NeMo Guardrails configurations
config = RailsConfig.from_path("./config")
rails = LLMRails(config)

def call_nemo(prompt):

    response = rails.generate(messages=[{
        "role": "user",
        "content": prompt
        }])

    return {
        'input prompt': prompt,
        'response': response['content']
    }

def main():

    st.title("LLM Translator with Guardrails")

    text_area = st.text_area("Please enter your inquiry below")

    if st.button("Translate"):
        
        if len(text_area)>0:

            st.info(text_area)

            # st.warning("Translation Without Guardrails")

            nemo_output = call_nemo(text_area)

            st.success("Input moderation guardrail response:")

            st.success(nemo_output['response'])

            if 'yes' in nemo_output['response'].lower():

                privateai_output = private_ai_pipeline(text_area)

                st.success("Prompt sent to LLM:")

                st.success(privateai_output['redacted prompt'])
                
                st.success("LLM response:")

                st.success(privateai_output['llm output'])

                st.success("Final response:")

                st.success(privateai_output['re-identified'])

            # st.warning("Translation With Guardrails")
       
if __name__ == "__main__":
    main()