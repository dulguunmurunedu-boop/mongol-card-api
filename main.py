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

    matched_id = None
    reason = "no_match"

    if "mr001" in filename or "mergid" in filename:
        matched_id = "MR-001"
        reason = "filename_match"

    elif "nm001" in filename or "naiman" in filename:
        matched_id = "NM-001"
        reason = "filename_match"

    elif "hd001" in filename or "hiad" in filename or "temujin" in filename:
        matched_id = "HD-001"
        reason = "filename_match"

    if matched_id:
        return {
            "success": True,
            "ocrText": filename,
            "imageCandidateId": matched_id,
            "ocrCandidateId": matched_id,
            "finalMatchedId": matched_id,
            "confidence": 0.95,
            "reason": reason
        }

    return {
        "success": True,
        "ocrText": filename,
        "imageCandidateId": None,
        "ocrCandidateId": None,
        "finalMatchedId": None,
        "confidence": 0.0,
        "reason": "no_match"
    }