from fastapi import FastAPI, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from transformers import pipeline
from PyPDF2 import PdfReader
import nltk

nltk.download("punkt")
nltk.download("punkt_tab")
nltk.download("stopwords")
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

app = FastAPI()

# Habilitar CORS para conectar com o frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # em produção coloque apenas o domínio do frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Carregar modelo Hugging Face
classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

# Pré-processamento
def preprocess(text):
    tokens = word_tokenize(text.lower())
    stop_words = set(stopwords.words("portuguese"))
    tokens = [t for t in tokens if t.isalpha() and t not in stop_words]
    return " ".join(tokens)

# Classificação
def classify_email(text):
    labels = ["Produtivo", "Improdutivo"]
    result = classifier(text, candidate_labels=labels)
    classification = result["labels"][0]
    score = float(result["scores"][0])
    return classification, score

# Resposta automática
def generate_response(classification):
    if classification == "Produtivo":
        return "Obrigado pelo contato. Sua solicitação será analisada e retornaremos em breve."
    else:
        return "Este email não parece relevante para nossas operações, portanto não será necessário responder."

@app.post("/classify-text")
async def classify_text(text: str = Form(...)):
    processed = preprocess(text)
    classification, score = classify_email(processed)
    response = generate_response(classification)
    return {"classification": classification, "confidence": score, "response": response}

@app.post("/classify-file")
async def classify_file(file: UploadFile):
    content = ""
    if file.filename.endswith(".txt"):
        content = (await file.read()).decode("utf-8")
    elif file.filename.endswith(".pdf"):
        reader = PdfReader(file.file)
        for page in reader.pages:
            content += page.extract_text() + "\n"

    processed = preprocess(content)
    classification, score = classify_email(processed)
    response = generate_response(classification)
    return {"classification": classification, "confidence": score, "response": response}