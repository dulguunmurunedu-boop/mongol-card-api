from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# FlutterFlow-oос дуудагдах тул CORS нээж өгнө
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
    return {
        "success": True,
        "ocrText": "FORCE TEST",
        "imageCandidateId": "NM-001",
        "ocrCandidateId": "NM-001",
        "finalMatchedId": "NM-001",
        "confidence": 1.0,
        "reason": "force_test"
    }