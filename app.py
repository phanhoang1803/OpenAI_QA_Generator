# app.py
import utils
import data
import json

from langchain.prompts import PromptTemplate
from langchain import OpenAI, LLMChain
from langchain.chat_models import ChatOpenAI
from langchain.document_loaders import PyPDFLoader, DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Set env
import os
os.environ["OPENAI_API_KEY"] = "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"

from flask import Flask, request, jsonify

app = Flask(__name__)

def get_set_of_question(qtype):
    assert qtype=="mcq" or qtype=="qa"
    
    en_path = "temp_en_result.json"
    vi_path = "temp_vi_result.json"
    
    # Delete existing files
    if os.path.exists(en_path):
        os.remove(en_path)
    if os.path.exists(vi_path):
        os.remove(vi_path)
        
    format_instructions = utils.get_format_instructions(qtype=qtype)
    
    if qtype=="mcq":
        prompt = PromptTemplate.from_template(utils.MCQ_PROMPT_TEMPLATE)
    elif qtype=="qa":
        prompt = PromptTemplate.from_template(utils.QA_PROMPT_TEMPLATE)
    
    llm_chain = LLMChain(
        llm=ChatOpenAI(model="gpt-3.5-turbo-16k", temperature=0),
        prompt=prompt
    )
    
    corrector = LLMChain(
        llm=ChatOpenAI(model="gpt-3.5-turbo", temperature=0),
        prompt=prompt.from_template(utils.CORRECT_PROMPT_TEMPLATE)
    )
    
    if request.is_json:
        text = request.get_json()['text']
        
        # Splitting data into chunks
        text_splitter = RecursiveCharacterTextSplitter(chunk_size = 7000, chunk_overlap = 100)
        all_splits = text_splitter.split_text(text)
        
        n = len(all_splits)
        
        print(f"Number of splitted text: ", n)
        for i in range(n):
            print(f'\n###--------------------------------- CHUNK {i} ---------------------------------###')
            context = all_splits[i]
            print("\nGenerating.......................................\n")
            
            result1 = llm_chain({"context": context, "format_instructions": format_instructions})

            result2 = corrector({"set": result1['text']})

            data.save_to_json(result1['text'], en_path)
            data.save_to_json(result2['text'], vi_path)
            # input("Enter to continue")
    else:
        return jsonify({"error": "Internal Server Error"}), 500
    
    if qtype=="mcq":
        # Remove duplicating questions, error question...
        data.format_questions(en_path)
        data.format_questions(vi_path)
        
    # Load existing JSON data
    with open(en_path, 'r') as json_file:
        en_res = json.load(json_file)
    
    with open(vi_path, 'r') as json_file:
        vi_res = json.load(json_file)    
    
    response_data = {
        "en_res" : en_res,
        "vi_res" : vi_res
    }    
        
    return jsonify(response_data)

@app.post("/mcq")
def get_mcq():
    return get_set_of_question(qtype="mcq")

@app.post("/qa")
def get_qa():
    return get_set_of_question(qtype="qa")
    
if __name__ == '__main__':
   app.run()