# AutoU - Classifier

O **AutoU - Classifier** é uma aplicação web que utiliza o *Zero-Shot Classification* da biblioteca Hugging Face, implementado com **FastAPI** para o backend e **HTML/CSS/JavaScript** para o frontend. A ferramenta permite que você classifique o conteúdo de e-mails (texto puro ou anexos `.txt` e `.pdf`) como **"Produtivo"** ou **"Improdutivo"**, gerando uma resposta automática com base na classificação.   

A escolha de usar Zero-Shot Classification se da pelo fato do custo financeiro de utilizar uma NLP de larga escala (OpenAI) e também do custo computacional para fazer o deploy de uma aplicação como esta. Em diversos casos foi possível observar estouro de memória antes mesmo da aplicação entrar em operação, evidenciando necessidade de recursos de hardware potentes.

## Funcionalidades

* **Classificação por Texto:** Cole o corpo do e-mail em uma caixa de texto e obtenha uma classificação imediata.
* **Classificação por Arquivo:** Envie e-mails como anexos nos formatos `.txt` ou `.pdf`.
* **Inteligência Artificial:** Utiliza o modelo `facebook/bart-large-mnli` para classificação *zero-shot* em português, rotulando o conteúdo como "Produtivo" ou "Improdutivo".
* **Resposta Automática:** Gera uma resposta sugerida com base na categoria
* **Pré-processamento:** O backend realiza a tokenização do texto, remove *stopwords* em português e converte para minúsculas antes da classificação, garantindo maior precisão.

## Tecnologias Utilizadas

* **Backend:** Python com **FastAPI**
* **AI/NLP:** `transformers` (Hugging Face) e `nltk` para processamento de linguagem natural.
* **PDF Handling:** `PyPDF2`
* **Frontend:** HTML, CSS e JavaScript puro

---

## Como Rodar Localmente

Para rodar localmente é necessário seguir os passos:

### 1. Pré-requisitos

Certifique-se de ter o Python (versão 3.8+) e o `pip` (gerenciador de pacotes) instalados.

### 2. Clonar o Repositório

Abra o CMD no diretório desejado e execute os comandos:

```bash
git clone <https://github.com/Louiz0/email-classifier.git>
cd email-classifier
cd backend
```
### 3. Criar o ambiente virtual do Python

```bash
python -m venv venv
```

### 4. Iniciar o ambiente virtual do Python

```bash
venv\Scripts\activate
```

### 5. Instalar as dependências

```bash
pip install -r requirements.txt
```

### 6. Executar o servidor FastAPI

```bash
uvicorn app:app --reload --port 8000
```

### 7. Executar o frontend

Abra outro CMD dentro da pasta raiz do projeto que foi clonado do Github. Mantenha o do backend em execução
```bash
cd frontend
python -m http.server 3000
```
---