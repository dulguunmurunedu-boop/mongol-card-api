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
    filename = image.filename.lower()

    # Түр demo/test match
    if "temujin" in filename or "hiad" in filename:
        return {
            "success": True,
            "ocrText": "Тэмүжин Хиад",
            "imageCandidateId": "HD-001",
            "ocrCandidateId": "HD-001",
            "finalMatchedId": "HD-001",
            "confidence": 0.95,
            "reason": "filename_match"
        }

    elif "naiman" in filename:
        return {
            "success": True,
            "ocrText": "Найман",
            "imageCandidateId": "NM-001",
            "ocrCandidateId": "NM-001",
            "finalMatchedId": "NM-001",
            "confidence": 0.95,
            "reason": "filename_match"
        }

    elif "mergid" in filename or "tohtoa" in filename:
        return {
            "success": True,
            "ocrText": "Тохтоа бэхи Мэргид",
            "imageCandidateId": "MR-001",
            "ocrCandidateId": "MR-001",
            "finalMatchedId": "MR-001",
            "confidence": 0.95,
            "reason": "filename_match"
        }

    elif "kereid" in filename or "wang" in filename:
        return {
            "success": True,
            "ocrText": "Ван хан Хэрэйд",
            "imageCandidateId": "KR-001",
            "ocrCandidateId": "KR-001",
            "finalMatchedId": "KR-001",
            "confidence": 0.95,
            "reason": "filename_match"
        }

    return {
        "success": False,
        "ocrText": "Танигдсангүй",
        "imageCandidateId": None,
        "ocrCandidateId": None,
        "finalMatchedId": None,
        "confidence": 0.0,
        "reason": "no_match"
    }