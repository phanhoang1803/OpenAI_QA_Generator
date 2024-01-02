from langchain.document_loaders import PyPDFLoader
from langchain.document_loaders import DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import FAISS
# from langchain.document_loaders import PyPDFLoader
import pickle
import models

def embed(courseID):
    # loader = PyPDFLoader("/content/data/course1/VietAI_system_research.pdf")
    # docs = loader.load_and_split()

    # Load data from directory
    loader = DirectoryLoader('data/course' + str(courseID), glob="**/*.pdf", loader_cls=PyPDFLoader)
    docs = loader.load()

    # Splitting data into chunks
    text_splitter = RecursiveCharacterTextSplitter(chunk_size = 1000, chunk_overlap = 20)
    all_splits = text_splitter.split_documents(docs)

    # Embedding
    vectorstore = FAISS.from_documents(documents=all_splits, embedding=models.Embeddings.load_embeddings())

    # Storing
    with open(f"vectorstores/course{str(courseID)}.pkl", "wb") as f:
        pickle.dump(vectorstore, f)

def load_vectorstore(courseID):
    # Load vectorstore from disk
    with open(f"vectorstores/course{str(courseID)}.pkl", "rb") as f:
        vectorstore = pickle.load(f)

    return vectorstore
    
def embed_and_get_vectorstore(courseID, pdf_path = None):
    # Load data from directory
    if pdf_path == None:
        loader = DirectoryLoader('data/course' + str(courseID), glob="**/*.pdf")
    else:
        loader = PyPDFLoader(file_path=pdf_path)
    docs = loader.load()
    
    # Splitting data into chunks
    text_splitter = RecursiveCharacterTextSplitter(chunk_size = 2000, chunk_overlap = 50)
    all_splits = text_splitter.split_documents(docs)
    
    # Embedding
    vectorstore = FAISS.from_documents(documents=all_splits, embedding=models.Embeddings.load_embeddings())
    
    return vectorstore

def save_to_json(markdown_text, path):
    import re
    import json
    import os
    
    # Extract JSON content from Markdown text
    json_strings = re.findall(r'```json\n(.*?)```', markdown_text, re.DOTALL)
    
    for json_string in json_strings:
        try:        
            # Add comma to separate each group
            json_string = json_string.replace('}\n{', '},\n{')
            
            # Convert JSON string to Python list
            python_list = json.loads(f'[{json_string}]')
            
            # Convert MCQ choices into lists
            try:
                for i in python_list:
                    # i['options'] = i['options'].split('\n' or '|')
                    i['options'] = re.split(r'\n|\| |\||. ', i['options'])
                    
                    # Process answer
                    # if len(i['answer']) > 1:
                        
            except:
                pass
                
            # Check if the JSON file already exists
            if os.path.exists(path):
                # Load existing JSON data
                with open(path, 'r') as json_file: 
                    existing_data = json.load(json_file)
                
                # Extend the existing data with the new data
                existing_data.extend(python_list)
                
                # Save the extended data back to the file
                with open(path, 'w') as json_file:
                    json.dump(existing_data, json_file, indent=2)
            else:
                # Save as new json file
                with open(path, 'w') as json_file:
                    json.dump(python_list, json_file, indent=2)        

            print("Saved.") 
        except:
            print("An exception occurred")
            # raise
            pass

def format_questions(path):
    # levels = ["None", "remember", "understand", "apply", "analyze", "evaluate", "create"]
    # level_mapping = {level: index for index, level in enumerate(levels)}
    
    import json
    # Load existing JSON data
    try:
        with open(path, 'r') as json_file:
            data = json.load(json_file)
    except Exception as e:
        return
    
    # Create a dictionary to store unique questions
    unique_questions = {}

    # Iterate through the data list and keep only the first occurrence of each question
    filtered_data = []
    for item in data:
        if len(item["options"]) < 4:
            continue
        
        question = item["question"]
        if question not in unique_questions:
            unique_questions[question] = True
            
            #### Process levels
            # level_words = item["level"].split()  # Split the level string into words
            # mapped_levels = [level_mapping[word] for word in level_words if word in level_mapping]
            
            # if mapped_levels:
            #     item["level"] = str(max(mapped_levels))  # Use the highest level index found
            #     # processed_data.append(item)
            
            ### Fixing the issue of the answer not being A, B, C, D characters
            if len(item['answer']) > 1:
                # Create a list of letters to use for the answer
                answer_letters = ["A", "B", "C", "D"]

                # Find the position of the answer in the options list
                answer_index = item["options"].index(item["answer"])

                # Change the answer section to the corresponding letter
                item["answer"] = answer_letters[answer_index]
            
            filtered_data.append(item)
        
    # Save json file
    with open(path, 'w') as json_file:
        json.dump(filtered_data, json_file, indent=2)
        
    print(f"Length before deduplicating: {len(data)}")
    print(f"Length after deduplicating: {len(filtered_data)}\n")
    
            
    