import re
from datetime import datetime
import parsedatetime
from fastapi import FastAPI, Form, UploadFile, File
import pytesseract
from PIL import Image
import io

app = FastAPI()
# Initialize the Calendar parser
cal = parsedatetime.Calendar()

@app.post("/parse-appointment")
async def parse_appointment(text_input: str = Form(None), file: UploadFile = File(None)):
    # 1. OCR / Text Input
    raw_text = ""
    if file:
        image = Image.open(io.BytesIO(await file.read()))
        raw_text = pytesseract.image_to_string(image).strip()
    else:
        raw_text = text_input if text_input else ""

    if not raw_text:
        return {"status": "error", "message": "No input"}

    # 2. Extract Department
    dept = None
    for word in ["dentist", "doctor", "physician", "cardiology", "clinic"]:
        if word in raw_text.lower():
            dept = word
            break

    # 3. Extract Time using Regex
    time_match = re.search(r'(\d{1,2}(?::\d{2})?\s?(?:am|pm|AM|PM))', raw_text)
    time_str = time_match.group(1) if time_match else "9:00 AM" # Default time if missing

    # 4. Extract Date Phrase (next friday, tomorrow, etc.)
    # We strip out the department and "book" to leave the date words
    date_phrase = raw_text.lower().replace("book", "").replace("appointment", "")
    if dept:
        date_phrase = date_phrase.replace(dept, "")
    date_phrase = date_phrase.replace(time_str, "").replace("at", "").strip()

    # 5. The "Magic" Parsing Step
    # parsedatetime returns (datetime_struct, status)
    # 1=date, 2=time, 3=datetime
    time_struct, parse_status = cal.parse(date_phrase)
    dt = datetime(*time_struct[:6])

    # 6. Parse Time specifically
    time_struct_final, _ = cal.parse(time_str)
    dt_time = datetime(*time_struct_final[:6])

    # 7. Guardrails
    if not dept:
        return {"status": "needs_clarification", "message": "Department missing"}
    if parse_status == 0:
        return {"status": "needs_clarification", "message": f"Could not understand date: {date_phrase}"}

    # 8. Success Output
    return {
        "step_1_ocr": {
            "raw_text": raw_text,
            "confidence": 0.90 # Mock confidence for Tesseract
        },
        "step_2_extraction": {
            "entities": {
                "date_phrase": date_phrase,
                "time_phrase": time_str,
                "department": dept
            },
            "entities_confidence": 0.85
        },
        "step_3_normalization": {
            "normalized": {
                "date": dt.strftime("%Y-%m-%d"),
                "time": dt_time.strftime("%H:%M"),
                "tz": "Asia/Kolkata"
            },
            "normalization_confidence": 0.90
        },
        "appointment": {
            "department": dept.capitalize() if dept else "Unknown",
            "date": dt.strftime("%Y-%m-%d"),
            "time": dt_time.strftime("%H:%M"),
            "tz": "Asia/Kolkata"
        },
        "status": "ok"
    }