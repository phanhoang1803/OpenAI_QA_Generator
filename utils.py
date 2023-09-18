# To parse outputs and get structured data back
from langchain.output_parsers import StructuredOutputParser, ResponseSchema

def get_format_instructions(qtype="mcq"):
    assert qtype=="mcq" or qtype=="qa"
    
    if qtype=="mcq":
        response_schemas = [
            ResponseSchema(name="question", description="A multiple choice question generated from input text snippet."),
            # ResponseSchema(name="level", description="A number corresponding level in the 6 levels of Bloom's Taxonomy: 1. remember, 2. understand, 3. apply, 4. analyze, 5. evaluate, 6. create."),
            ResponseSchema(name="options", description="Four possible choices for the multiple choice question as a Python list."),
            ResponseSchema(name="answer", description="A or B or C or D corresponding 4 choices options.")
        ]
    elif qtype=="qa":
        response_schemas = [
            ResponseSchema(name="question", description="A question generated from input text snippet. NOT multiple choices."),
            ResponseSchema(name="answer", description="ONE correct answer for the question.")
        ]
        
    # The parser that will look for the LLM output in my schema and return it back to me
    output_parser = StructuredOutputParser.from_response_schemas(response_schemas)

    # The format instructions that LangChain makes. Let's look at them
    format_instructions = output_parser.get_format_instructions()
    
    return format_instructions

def get_vi_format_instructions():
    response_schemas = [
        ResponseSchema(name="question", description="Một câu hỏi trắc nghiệm được tạo từ đoạn văn bản đầu vào."),
        ResponseSchema(name="options", description="Bốn lựa chọn có thể có cho câu hỏi trắc nghiệm dưới dạng Python list."),
        ResponseSchema(name="answer", description="A hoặc B hoặc C hoặc D tương ứng với đáp án trong 4 lựa chọn.")
    ]
        
    # The parser that will look for the LLM output in my schema and return it back to me
    output_parser = StructuredOutputParser.from_response_schemas(response_schemas)

    # The format instructions that LangChain makes. Let's look at them
    format_instructions = output_parser.get_format_instructions()
    
    return format_instructions

# Use the following text to create a quiz of 6 multiple choice questions which corresponsfor grade students in educational tone.
MCQ_PROMPT_TEMPLATE = """
You are an expert Multi Choice Question maker.
Use the following text to create some multiple choice helpful questions test for grade students with an educational tone.
Make sure that questions are not repeated and check all the questions to be conforming to the text as well.
Do not use information unrelated to the text provided for creating questions.
NOTICE: Do not create questions that need to be answered based on certain passages provided.

{context}

{format_instructions}

Answer:"""

CORRECT_PROMPT_TEMPLATE = """
Given the set of multiple choice questions below. 
Please correct these questions to appropriate any case and context.

{set}

Answer in Vietnamese language:"""

MCQ_VI_PROMPT_TEMPLATE = """ 
Bạn là một chuyên gia đưa ra câu hỏi trắc nghiệm.
Sử dụng văn bản sau đây để tạo một số bài kiểm tra câu hỏi trắc nghiệm Phân loại tư duy của Bloom cho học sinh với giọng điệu giáo dục.
Đảm bảo rằng các câu hỏi không lặp lại và kiểm tra tất cả các câu hỏi để phù hợp với văn bản.
Không sử dụng thông tin không liên quan đến văn bản được cung cấp để tạo câu hỏi.

{context}

{format_instructions}

Câu trả lời:"""











QA_PROMPT_TEMPLATE = """
You are an expert Question & Answer maker.
Use the following text to create some questions and answers test for grade students with an educational tone.
Make sure that questions are not repeated and check all the questions to be conforming to the text as well.
Do not use information unrelated to the text provided for creating questions.

{context}

{format_instructions}

Answer:"""