from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# FlutterFlow-оос дуудагдахын тулд CORS нээж өгнө
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
    # Түр test response
    return {
        "success": True,
        "ocrText": "тохтоа бэхи мэргид",
        "imageCandidateId": "MR-001",
        "ocrCandidateId": "MR-001",
        "finalMatchedId": "MR-001",
        "confidence": 0.93,
        "reason": "image_ocr_agree"
    }