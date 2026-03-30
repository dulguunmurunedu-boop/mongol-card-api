from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "Mongol Card API ажиллаж байна"}

@app.post("/recognize-card")
async def recognize_card(image: UploadFile = File(...)):
    filename = image.filename.lower()

    return {
        "success": True,
        "ocrText": filename,
        "imageCandidateId": None,
        "ocrCandidateId": None,
        "finalMatchedId": None,
        "confidence": 0.0,
        "reason": "debug_filename"
    }