from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from plagiat import check_similarity, reformulate_text
import os
import io
import docx2txt
import pypdf
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("SERPAPI_KEY")

app = FastAPI(
    title="Plagiat Detection API",
    description="API pour la détection de plagiat et la reformulation de texte",
    version="1.0.0"
)

# Configuration CORS plus sécurisée pour la production
allowed_origins = [
    "http://localhost:5173",  # Dev local
    "http://localhost:4173",  # Preview local
    "https://plagiat-frontend.onrender.com",  # Production frontend
    "https://*.onrender.com",  # Autres domaines Render
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins if os.getenv("ENVIRONMENT") == "production" else ["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

class TextRequest(BaseModel):
    text: str

class ReformulateRequest(BaseModel):
    text: str
    use_ai: bool = True  # Paramètre pour choisir le niveau de reformulation

@app.get("/")
def read_root():
    """Endpoint de base pour vérifier que l'API fonctionne"""
    return {"message": "Plagiat Detection API", "status": "running", "version": "1.0.0"}

@app.get("/health")
def health_check():
    """Endpoint de santé pour les vérifications de déploiement"""
    return {"status": "healthy", "service": "plagiat-api"}

@app.post("/check")
def check_text(data: TextRequest):
    print(f"Received text analysis request. Text length: {len(data.text)}")
    score, sources = check_similarity(data.text, API_KEY)
    print(f"Returning score: {score}, sources: {len(sources)}")
    return {"plagiarism_score": score, "sources": sources}

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    print(f"Received file upload: {file.filename}")
    contents = await file.read()
    
    if file.filename.endswith(".pdf"):
        try:
            reader = pypdf.PdfReader(io.BytesIO(contents))
            text = "".join(page.extract_text() or "" for page in reader.pages)
            print(f"Extracted PDF text length: {len(text)}")
        except Exception as e:
            raise HTTPException(status_code=400, detail="Erreur PDF : " + str(e))

    elif file.filename.endswith(".docx"):
        try:
            temp_file = f"temp_{file.filename}"
            with open(temp_file, "wb") as f:
                f.write(contents)
            text = docx2txt.process(temp_file)
            os.remove(temp_file)  # Nettoyer le fichier temporaire
        except Exception as e:
            raise HTTPException(status_code=400, detail="Erreur DOCX : " + str(e))
    else:
        raise HTTPException(status_code=400, detail="Format non supporté")

    score, sources = check_similarity(text, API_KEY)
    return {"plagiarism_score": score, "sources": sources}

@app.post("/reformulate")
def reformulate_text_endpoint(data: ReformulateRequest):
    print(f"Received reformulation request. Text length: {len(data.text)}, AI: {data.use_ai}")
    reformulated = reformulate_text(data.text, use_ai=data.use_ai)
    print(f"Reformulated text length: {len(reformulated)}")
    return {"original": data.text, "reformulated": reformulated, "method": "AI" if data.use_ai else "Basic"}
