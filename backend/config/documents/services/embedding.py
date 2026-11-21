import torch
from transformers import AutoTokenizer, AutoModel
from torch.nn import functional as F






class EmbeddingService:
    
    __model_name = "intfloat/multilingual-e5-small"
    __device = "cpu"
    
    def __init__(self):
        self.tokenizer = AutoTokenizer.from_pretrained(self.__model_name)
        self.model = AutoModel.from_pretrained(self.__model_name).to(self.__device)
        self.model.eval()
        
        
    def tokenize(self, text: str):
        return self.tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
    
    def get_embedding(self, text: str, prefix: str = "passage: "):
        if not text or not text.strip():
            raise ValueError("Error value, Text cannot be empty field.")
        
        text = prefix + text
        token = self.tokenize(text)
        with torch.inference_mode():
            outputs = self.model(**token)
            
        token_embedding = outputs.last_hidden_state
        mask = token["attention_mask"].unsqueeze(-1).float()
        
        summed = (token_embedding * mask).sum(dim=1)
        counts = mask.sum(dim=1).clamp(min=1e-9)
        
        embedding = summed / counts
        return F.normalize(embedding, p=2, dim=1)