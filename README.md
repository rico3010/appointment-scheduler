#   AI-Powered Appointment Scheduler

A robust backend service built with **FastAPI** that transforms natural language text and images into structured appointment data. This project is optimized for real-world usage with built-in typo correction and OCR capabilities.

##   Key Features
- **Smart Typo Correction:** Uses Fuzzy Matching (`RapidFuzz`) to understand abbreviations like "nxt" for "next" or "tmrw" for "tomorrow."
- **OCR Integration:** Extracts appointment details directly from images using Tesseract OCR.
- **Natural Language Parsing:** Converts relative dates (e.g., "next Friday") into standard ISO format.
- **API Documentation:** Built-in interactive Swagger UI for instant testing.

---

##   Technical Architecture

The system processes data through a specialized pipeline:

1.  **Ingestion:** Accepts raw text or image files via a multipart POST request.
2.  **Normalization (Smart Fix):** Pre-processes text using fuzzy string matching to fix user typos and symbols (e.g., `@` → `at`).
3.  **Extraction:** Isolates time using Regex and calculates dates using the `parsedatetime` library.
4.  **Formatting:** Returns a structured JSON response ready for frontend or database integration.



---

##   Setup & Installation

### 1. System Requirements (Linux Mint)
Ensure Tesseract OCR is installed on your system:
```bash
sudo apt update
sudo apt install tesseract-ocr libtesseract-dev -y

2. Project Setup
Bash

# Clone the repository
git clone [https://github.com/rico3010/appointment-scheduler.git](https://github.com/rico3010/appointment-scheduler.git)
cd appointment-scheduler

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

3. Run the Server
Bash

uvicorn main:app --reload

Access the dashboard at: http://127.0.0.1:8000/docs
  API Usage Examples
Text Input (with Typos)

Endpoint: POST /parse-appointment

Payload: text_input="Book doctor nxt Friday @ 3pm"

Response:
JSON

{
  "status": "success",
  "data": {
    "original_text": "Book doctor nxt Friday @ 3pm",
    "cleaned_text": "book doctor next friday at 3pm",
    "extracted_date": "2026-01-30",
    "extracted_time": "3pm",
    "department": "Doctor"
  }
}

Image Input

Upload a .png or .jpg containing text like "Dentist tomorrow 10am" to the same endpoint using the file field.
  Core Dependencies

    FastAPI: Modern web framework.

    RapidFuzz: Fuzzy string matching for typo tolerance.

    pytesseract: OCR engine interface.

    parsedatetime: NLP date/time parsing.

    Pillow: Image processing.

  Live Demo

API URL: https://spriest-immensely-suzy.ngrok-free.dev

Interactive Docs: https://spriest-immensely-suzy.ngrok-free.dev/docs

