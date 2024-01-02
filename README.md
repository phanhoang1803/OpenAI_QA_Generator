# OpenAI_QA_Generator

## Demo:
<img src="https://github.com/phanhoang1803/OpenAI_QA_Generator/blob/main/MCQ_Generator_Demo.gif" width="800" height="600">

## To run demo:
  - Install requirements: pip install -r requirements. txt
  - Set OPENAI_API_KEY in app.py file.
  - Run app.py: py app.py
  - Then run demo_call_api.py: py demo_call_api.py

## Run website:
  - Run file index.js in templates: node index.js

## To call api:
  - Call by POST method: 
  	+ url : http://localhost:5000/mcq
  	+ json: {'text': material_text}

  - Response as json type:
    + response_data = {"en_res": en_res, "vi_res": vi_res}
