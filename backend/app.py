from fastapi import FastAPI, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from transformers import pipeline
from PyPDF2 import PdfReader
import nltk
import re
from typing import Dict, List
import numpy as np
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

nltk.download("punkt")
nltk.download("stopwords")
nltk.download("punkt_tab")
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

classifier = pipeline("zero-shot-classification", 
                     model="facebook/bart-large-mnli",
                     device=-1)

PRODUCTIVE_KEYWORDS = [
    "projeto", "reunião", "relatório", "prazo", "entrega", "cliente",
    "solicitação", "orcamento", "proposta", "contrato", "desenvolvimento",
    "implementação", "análise", "relatório", "resultado", "metas",
    "objetivo", "tarefa", "atividade", "processo", "melhoria", "solução"
]

UNPRODUCTIVE_KEYWORDS = [
    "spam", "promoção", "oferta", "desconto", "marketing", "newsletter",
    "divulgação", "publicidade", "sorteio", "concurso", "assine", "compre",
    "venda", "oportunidade", "exclusivo", "limitado", "grátis", "gratuito"
]

def preprocess(text: str) -> str:
    if not text or len(text.strip()) == 0:
        return ""
    
    text = re.sub(r'\s+', ' ', text) 
    text = re.sub(r'[^\w\s]', ' ', text)
    text = text.lower().strip()
    
    tokens = word_tokenize(text, language='portuguese')
    
    stop_words = set(stopwords.words("portuguese"))
    

    filtered_tokens = []
    for token in tokens:
        if (token.isalpha() and 
            token not in stop_words and 
            len(token) > 2 and
            not token.isdigit()):
            filtered_tokens.append(token)
    
    return " ".join(filtered_tokens)

def keyword_score(text: str) -> float:
    productive_count = sum(1 for keyword in PRODUCTIVE_KEYWORDS if keyword in text)
    unproductive_count = sum(1 for keyword in UNPRODUCTIVE_KEYWORDS if keyword in text)
    
    total_keywords = productive_count + unproductive_count
    if total_keywords == 0:
        return 0.5
    
    return productive_count / total_keywords

def classify_email(text: str) -> Dict:
    if not text or len(text) < 10: 
        return {"classification": "Improdutivo", "confidence": 0.9}
    
    processed_text = preprocess(text)
    
    if len(processed_text.split()) < 3:
        return {"classification": "Improdutivo", "confidence": 0.85}
    
    kw_score = keyword_score(processed_text)
    
    labels = [
        "email profissional relacionado a trabalho ou projetos",  # Produtivo
        "email promocional, spam ou não relacionado a trabalho"   # Improdutivo
    ]
    
    try:
        result = classifier(processed_text, candidate_labels=labels)
        
        model_prod_score = result["scores"][0] if result["labels"][0] == labels[0] else result["scores"][1]
        
        final_score = 0.7 * model_prod_score + 0.3 * kw_score
        
        threshold = 0.6 if len(text) > 50 else 0.7
        
        if final_score >= threshold:
            classification = "Produtivo"
            confidence = final_score
        else:
            classification = "Improdutivo"
            confidence = 1 - final_score
            
        return {
            "classification": classification, 
            "confidence": round(float(confidence), 3),
            "keyword_score": round(kw_score, 3),
            "model_score": round(model_prod_score, 3)
        }
        
    except Exception as e:
        fallback_class = "Produtivo" if kw_score > 0.6 else "Improdutivo"
        return {
            "classification": fallback_class, 
            "confidence": 0.7,
            "error": str(e),
            "fallback": True
        }

def generate_response(classification: str, confidence: float) -> str:
    if classification == "Produtivo":
        if confidence > 0.8:
            return "Obrigado pelo contato. Sua solicitação será analisada e retornaremos em breve."
        else:
            return "Agradecemos seu email. Estamos analisando o conteúdo e retornaremos em breve."
    else:
        if confidence > 0.8:
            return "Este email não parece relevante para nossas operações, portanto não será necessário responder."
        else:
            return "Obrigado pelo contato. Vamos analisar seu email e retornaremos se necessário."

@app.post("/classify-text")
async def classify_text(text: str = Form(...)):
    if not text or len(text.strip()) == 0:
        return {
            "classification": "Improdutivo", 
            "confidence": 0.9,
            "response": "Texto vazio ou inválido.",
            "error": "Empty text"
        }
    
    result = classify_email(text)
    response = generate_response(result["classification"], result["confidence"])
    
    return {
        "classification": result["classification"],
        "confidence": result["confidence"],
        "response": response,
        "keyword_score": result.get("keyword_score"),
        "model_score": result.get("model_score")
    }

@app.post("/classify-file")
async def classify_file(file: UploadFile):
    content = ""
    try:
        if file.filename.endswith(".txt"):
            content = (await file.read()).decode("utf-8", errors='ignore')
        elif file.filename.endswith(".pdf"):
            reader = PdfReader(file.file)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    content += page_text + "\n"
        else:
            return {"error": "Formato de arquivo não suportado"}
            
    except Exception as e:
        return {"error": f"Erro ao processar arquivo: {str(e)}"}
    
    result = classify_email(content)
    response = generate_response(result["classification"], result["confidence"])
    
    return {
        "classification": result["classification"],
        "confidence": result["confidence"],
        "response": response,
        "keyword_score": result.get("keyword_score"),
        "model_score": result.get("model_score")
    }

@app.post("/debug-preprocess")
async def debug_preprocess(text: str = Form(...)):
    processed = preprocess(text)
    kw_score = keyword_score(processed)
    
    return {
        "original": text,
        "processed": processed,
        "keyword_score": kw_score,
        "productive_keywords_found": [kw for kw in PRODUCTIVE_KEYWORDS if kw in processed],
        "unproductive_keywords_found": [kw for kw in UNPRODUCTIVE_KEYWORDS if kw in processed]
    }

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def read_index():
    return FileResponse('index.html')

@app.get("/{path:path}")
async def serve_spa(path: str):
    if os.path.exists(path):
        return FileResponse(path)
    return FileResponse('index.html')