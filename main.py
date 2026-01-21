import re
import datetime
from typing import Optional
from fastapi import FastAPI, Form, UploadFile, File
from rapidfuzz import process, fuzz
import parsedatetime
import pytesseract
from PIL import Image
import io

app = FastAPI(title="AI Appointment Scheduler")

# Setup for Date Parsing
cal = parsedatetime.Calendar()

# 1. FUZZY MATCHING SETTINGS
# Words we want to "fix" if the user typos them
TARGET_KEYWORDS = [
    "next", "tomorrow", "today", "monday", "tuesday", "wednesday", 
    "thursday", "friday", "saturday", "sunday", "appointment", "at"
]

def fuzzy_clean_text(text: str) -> str:
    """Corrects typos like 'nxt' to 'next' and '@' to 'at'."""
    # Basic pre-cleaning
    text = text.lower().replace("@", " at ")
    words = text.split()
    fixed_words = []

    for word in words:
        # We only want to fuzzy match words that aren't already perfect
        if word in TARGET_KEYWORDS or len(word) < 3:
            fixed_words.append(word)
            continue
        
        # Check for a 'close enough' match (score > 80)
        match = process.extractOne(word, TARGET_KEYWORDS, scorer=fuzz.WRatio)
        if match and match[1] > 80:
            fixed_words.append(match[0])
        else:
            fixed_words.append(word)
            
    return " ".join(fixed_words)

# 2. EXTRACTION LOGIC
def extract_appointment_details(text: str):
    # Clean the text first!
    cleaned_text = fuzzy_clean_text(text)
    
    # Extract time using Regex (e.g., 3pm, 10:30am)
    time_match = re.search(r'(\d{1,2}(?::\d{2})?\s*(?:am|pm))', cleaned_text)
    time_str = time_match.group(1) if time_match else "Not found"

    # Extract date using parsedatetime
    # It uses the 'now' time as a reference to calculate "next Friday"
    now = datetime.datetime.now()
    time_struct, parse_status = cal.parse(cleaned_text, now)
    
    # parse_status 1 = date, 2 = time, 3 = datetime
    if parse_status > 0:
        parsed_dt = datetime.datetime(*time_struct[:6])
        date_str = parsed_dt.strftime("%Y-%m-%d")
    else:
        date_str = "Could not determine date"

    # Simple Keyword extraction for Department
    departments = ["dentist", "doctor", "cardiology", "physio", "pediatric"]
    dept_match = next((d for d in departments if d in cleaned_text), "General")

    return {
        "original_text": text,
        "cleaned_text": cleaned_text,
        "extracted_date": date_str,
        "extracted_time": time_str,
        "department": dept_match.capitalize()
    }

# 3. API ENDPOINTS
@app.post("/parse-appointment")
async def parse_appointment(
    text_input: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None)
):
    final_text = ""

    # If an image is uploaded, use OCR
    if file:
        image_data = await file.read()
        image = Image.open(io.BytesIO(image_data))
        final_text = pytesseract.image_to_string(image)
    elif text_input:
        final_text = text_input
    else:
        return {"error": "No text or image provided"}

    # Process the text
    result = extract_appointment_details(final_text)
    return {"status": "success", "data": result}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)