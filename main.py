import io
import os
import re
from typing import Optional, Tuple

import requests
from PIL import Image
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware

from cards_catalog import CARDS


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

OCR_SPACE_API_KEY = os.getenv("OCR_SPACE_API_KEY", "")


def normalize_text(text: str) -> str:
    """Текстийг match хийхэд бэлэн болгоно."""
    text = (text or "").lower()
    text = text.replace("\n", " ")
    text = re.sub(r"[^а-яөүёa-z0-9\+\-\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def pil_to_bytes(img: Image.Image) -> bytes:
    """PIL image-г bytes болгоно."""
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    return buffer.getvalue()


def crop_regions(image_bytes: bytes) -> dict:
    """
    Картын тогтмол layout дээр үндэслээд 3 хэсэг crop хийнэ:
    - title
    - faction
    - body
    """
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    w, h = image.size

    # Title banner
    title_box = (
        int(w * 0.20),
        int(h * 0.03),
        int(w * 0.88),
        int(h * 0.17),
    )

    # Faction logo + faction text
    faction_box = (
        int(w * 0.02),
        int(h * 0.02),
        int(w * 0.28),
        int(h * 0.18),
    )

    # Skill / body text
    body_box = (
        int(w * 0.15),
        int(h * 0.56),
        int(w * 0.88),
        int(h * 0.92),
    )

    return {
        "title": image.crop(title_box),
        "faction": image.crop(faction_box),
        "body": image.crop(body_box),
    }


def ocr_space_extract(image_bytes: bytes, filename: str = "crop.png") -> str:
    """OCR.Space API-р text гаргаж авна."""
    if not OCR_SPACE_API_KEY:
        print("DEBUG: OCR_SPACE_API_KEY is missing")
        return ""

    url = "https://api.ocr.space/parse/image"

    files = {
        "filename": (filename, image_bytes)
    }

    data = {
        "apikey": OCR_SPACE_API_KEY,
        "language": "eng",
        "isOverlayRequired": "false",
        "OCREngine": "2",
        "scale": "true",
    }

    try:
        response = requests.post(url, files=files, data=data, timeout=60)
        print(f"\nDEBUG OCR REQUEST: {filename}")
        print("DEBUG OCR STATUS:", response.status_code)
        print("DEBUG OCR RAW RESPONSE:", response.text[:1000])

        response.raise_for_status()
        result = response.json()
    except Exception as e:
        print(f"DEBUG OCR REQUEST FAILED ({filename}):", str(e))
        return ""

    if result.get("IsErroredOnProcessing"):
        print("DEBUG OCR ERROR:", result)
        return ""

    parsed_results = result.get("ParsedResults", [])
    if not parsed_results:
        print("DEBUG OCR: No ParsedResults")
        return ""

    extracted_text = "\n".join(
        item.get("ParsedText", "") for item in parsed_results
    ).strip()

    print("DEBUG OCR EXTRACTED TEXT:", extracted_text)
    return extracted_text


def score_card(
    card: dict,
    title_text: str,
    faction_text: str,
    body_text: str,
) -> Tuple[int, list]:
    """
    Карт бүрт оноо өгнө.
    Priority:
    1. title
    2. faction
    3. body text
    """
    score = 0
    reasons = []

    norm_title = normalize_text(title_text)
    norm_faction = normalize_text(faction_text)
    norm_body = normalize_text(body_text)

    # 1) Title keywords
    for kw in card.get("title_keywords", []):
        norm_kw = normalize_text(kw)
        if norm_kw and norm_kw in norm_title:
            score += 50
            reasons.append(f"title:{kw}")

    # 2) Faction keywords
    for kw in card.get("faction_keywords", []):
        norm_kw = normalize_text(kw)
        if norm_kw and norm_kw in norm_faction:
            score += 30
            reasons.append(f"faction:{kw}")

    # 3) Body keywords
    for kw in card.get("body_keywords", []):
        norm_kw = normalize_text(kw)
        if norm_kw and norm_kw in norm_body:
            score += 20
            reasons.append(f"body:{kw}")

    return score, reasons


def pick_best_match(
    title_text: str,
    faction_text: str,
    body_text: str,
) -> Tuple[Optional[str], float, str]:
    """Хамгийн өндөр оноотой картыг сонгоно."""
    best_card = None
    best_score = 0
    best_reasons = []

    for card in CARDS:
        score, reasons = score_card(card, title_text, faction_text, body_text)

        print(f"DEBUG SCORE {card['id']}: {score} | {reasons}")

        if score > best_score:
            best_score = score
            best_card = card
            best_reasons = reasons

    # Босго
    if not best_card or best_score < 20:
        return None, 0.0, "no_match"

    confidence = min(best_score / 100.0, 0.99)
    return best_card["id"], round(confidence, 2), ",".join(best_reasons)


@app.get("/")
def root():
    return {"message": "Mongol Card OCR API live"}


@app.post("/recognize-card")
async def recognize_card(image: UploadFile = File(...)):
    image_bytes = await image.read()

    print("\n====================")
    print("DEBUG: New request received")
    print("DEBUG: Uploaded filename:", image.filename)
    print("DEBUG: Image size (bytes):", len(image_bytes))

    try:
        regions = crop_regions(image_bytes)
    except Exception as e:
        print("DEBUG: crop_regions failed:", str(e))
        return {
            "success": False,
            "ocrText": "",
            "imageCandidateId": None,
            "ocrCandidateId": None,
            "finalMatchedId": None,
            "confidence": 0.0,
            "reason": f"crop_error: {str(e)}",
        }

    title_bytes = pil_to_bytes(regions["title"])
    faction_bytes = pil_to_bytes(regions["faction"])
    body_bytes = pil_to_bytes(regions["body"])

    print("DEBUG: Title crop bytes:", len(title_bytes))
    print("DEBUG: Faction crop bytes:", len(faction_bytes))
    print("DEBUG: Body crop bytes:", len(body_bytes))

    title_text = ocr_space_extract(title_bytes, "title.png")
    faction_text = ocr_space_extract(faction_bytes, "faction.png")
    body_text = ocr_space_extract(body_bytes, "body.png")

    print("\nDEBUG FINAL OCR TEXTS")
    print("TITLE TEXT:", repr(title_text))
    print("FACTION TEXT:", repr(faction_text))
    print("BODY TEXT:", repr(body_text))

    final_matched_id, confidence, reason = pick_best_match(
        title_text=title_text,
        faction_text=faction_text,
        body_text=body_text,
    )

    print("\nDEBUG MATCH RESULT")
    print("MATCHED ID:", final_matched_id)
    print("CONFIDENCE:", confidence)
    print("REASON:", reason)
    print("====================\n")
    print(f"TRACK: user scanned {final_matched_id}")
    print(f"TRACK: confidence = {confidence}")
    print(f"TRACK: reason = {reason}")

    full_ocr_text = (
        f"[TITLE]\n{title_text}\n\n"
        f"[FACTION]\n{faction_text}\n\n"
        f"[BODY]\n{body_text}"
    )

    return {
        "success": True,
        "ocrText": full_ocr_text,
        "imageCandidateId": final_matched_id,
        "ocrCandidateId": final_matched_id,
        "finalMatchedId": final_matched_id,
        "confidence": confidence,
        "reason": reason,
    }