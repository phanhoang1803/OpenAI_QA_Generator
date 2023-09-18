import torch
from torch import cuda, bfloat16
import transformers
from transformers import StoppingCriteria, StoppingCriteriaList
from langchain.llms import HuggingFacePipeline
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS       

import data

class Embeddings:
    def load_embeddings():
        model_name = "sentence-transformers/all-mpnet-base-v2"
        model_kwargs = {"device": "cuda"}

        embeddings = HuggingFaceEmbeddings(model_name=model_name, model_kwargs=model_kwargs)

        return embeddings

class LLAMAModel:
    def __init__(self, model_id, hf_auth):
        self.model_id = model_id
        self.hf_auth = hf_auth
        
    def load_model(self):
        device = f'cuda:{cuda.current_device()}' if cuda.is_available() else 'cpu'

        # set quantization configuration to load large model with less GPU memory
        # this requires the `bitsandbytes` library
        bnb_config = transformers.BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type='nf4',
            bnb_4bit_use_double_quant=True,
            bnb_4bit_compute_dtype=bfloat16
        )

        # begin initializing HF items, you need an access token
        model_config = transformers.AutoConfig.from_pretrained(
            pretrained_model_name_or_path=self.model_id,
            use_auth_token=self.hf_auth
        )

        model = transformers.AutoModelForCausalLM.from_pretrained(
            pretrained_model_name_or_path=self.model_id,
            trust_remote_code=True,
            config=model_config,
            quantization_config=bnb_config,
            device_map='auto',
            use_auth_token=self.hf_auth
        )

        # enable evaluation mode to allow model inference
        model.eval()

        print(f"Model loaded on {device}")
        return model

    def load_stopping_criteria(self):
        device = f'cuda:{cuda.current_device()}' if cuda.is_available() else 'cpu'

        tokenizer = transformers.AutoTokenizer.from_pretrained(
            pretrained_model_name_or_path=self.model_id,
            use_auth_token=self.hf_auth
        )
        stop_list = ['\nHuman:', '\n```\n']
        stop_token_ids = [tokenizer(x)['input_ids'] for x in stop_list]
        stop_token_ids = [torch.LongTensor(x).to(device) for x in stop_token_ids]

        # define custom stopping criteria object
        class StopOnTokens(StoppingCriteria):
            def __call__(self, input_ids: torch.LongTensor, scores: torch.FloatTensor, **kwargs) -> bool:
                for stop_ids in stop_token_ids:
                    if torch.eq(input_ids[0][-len(stop_ids):], stop_ids).all():
                        return True
                return False

        stopping_criteria = StoppingCriteriaList([StopOnTokens()])

        return stopping_criteria

    def load_llm(self, temperature=0.5, max_new_tokens=512, repetition_penalty=1.1):
        model = self.load_model()

        tokenizer = transformers.AutoTokenizer.from_pretrained(
            pretrained_model_name_or_path=self.model_id,
            use_auth_token=self.hf_auth
        )

        stopping_criteria = self.load_stopping_criteria()

        generate_text = transformers.pipeline(
            model=model,
            tokenizer=tokenizer,
            return_full_text=True,  # langchain expects the full text
            task='text-generation',
            # we pass model parameters here too
            stopping_criteria=stopping_criteria,  # without this model rambles during chat
            temperature=temperature,  # 'randomness' of outputs, 0.0 is the min and 1.0 the max
            max_new_tokens=max_new_tokens,  # max number of tokens to generate in the output
            repetition_penalty=repetition_penalty  # without this output begins repeating
        )

        llm = HuggingFacePipeline(pipeline=generate_text)

        return llm