# 🚀 AI-Powered Isometric MTO Extractor

An AI-powered web application that automatically extracts **Material Take-Off (MTO)** information from industrial piping isometric drawings using **Google Gemini 2.5 Flash**.

Instead of manually reading piping drawings and preparing MTO sheets, users can simply upload a PDF or image and receive a structured, validated Material Take-Off along with downloadable CSV output.

---

# ✨ Features

- 📄 Upload PDF or Image (PNG/JPG/JPEG)
- 🤖 AI-powered extraction using Gemini 2.5 Flash
- 📑 Automatic Material Take-Off generation
- 🎯 Confidence score for every extracted item
- 📥 Export results as CSV
- ⚡ FastAPI backend
- 🎨 Modern Next.js + Tailwind frontend
- 📱 Responsive UI
- 🛡 Structured validation using Pydantic
- 🚫 Hallucination reduction through prompt engineering

---

# 🏗 Architecture

```text
                    +-----------------------+
                    |   User uploads PDF    |
                    +----------+------------+
                               |
                               v
                 +---------------------------+
                 |     Next.js Frontend      |
                 +-------------+-------------+
                               |
                      HTTP Multipart Upload
                               |
                               v
                  +--------------------------+
                  |      FastAPI Backend     |
                  +------------+-------------+
                               |
               Detect file type (PDF/Image)
                               |
               +---------------+---------------+
               |                               |
               v                               v
      PDF → Images                    Image directly
      (pdf2image)                          used
               \_______________________________/
                               |
                               v
                  Prompt + Image Construction
                               |
                               v
              Google Gemini 2.5 Flash API
                               |
                               v
                 Structured JSON Response
                               |
                               v
                               API Key Available?
                              |
                        +--------+--------+
                        |                 |
                        Yes                No
                        |                 |
                        v                 v
                  Gemini Vision      Mock Pipeline
                        |                 |
                        +--------+--------+
                              |
                              v
                Pydantic Schema Validation
                               |
                               v
                  ExtractionResponse Model
                               |
                  +------------+-------------+
                  |                          |
                  v                          v
            JSON Response             CSV Export
                               |
                               v
                      Next.js Result UI
```

---

# ⚙ Technology Stack

## Frontend

- Next.js 15
- React
- TypeScript
- Tailwind CSS

## Backend

- FastAPI
- Python 3.11+
- Pydantic
- pdf2image
- Pillow
- Uvicorn

## AI

- Google Gemini 2.5 Flash
- Google GenAI SDK

---

# 📂 Project Structure

```
Isometric-MTO-extractor/

│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── services/
│   │   │      gemini_service.py
│   │   │      csv_service.py
│   │   ├── schemas/
│   │   ├── utils/
│   │   └── main.py
│   │
│   ├── uploads/
│   ├── outputs/
│   ├── requirements.txt
│   └── .env
│
├── frontend/
│   ├── app/
│   ├── components/
│   ├── lib/
│   ├── public/
│   └── package.json
│
└── README.md
```

---

# 🚀 Setup

## Requirements

### Backend

- Python **3.11 or newer**

Verify:

```bash
python --version
```

### Frontend

- Node.js **20+**
- npm **10+**

Verify:

```bash
node -v
npm -v
```

---

# Backend Setup

Clone repository

```bash
git clone https://github.com/USERNAME/Isometric-MTO-extractor.git

cd Isometric-MTO-extractor/backend
```

Create virtual environment

Windows

```bash
python -m venv venv

venv\Scripts\activate
```

Linux/macOS

```bash
python3 -m venv venv

source venv/bin/activate
```

Install dependencies

```bash
pip install -r requirements.txt
copy .env.example .env
```

Run backend

```bash
uvicorn app.main:app --reload
```

Backend runs on

```
http://localhost:8000
```

---

# Frontend Setup

Open another terminal

```bash
cd frontend
```

Install dependencies

```bash
npm install
```

Run development server

```bash
npm run dev
```

Frontend runs on

```
http://localhost:3000
```

---

# 🔑 Environment Variables

Backend requires a `.env` file.

Example:

```env
# Backend
GEMINI_API_KEY=
GEMINI_MODEL=gemini-2.5-flash

# Frontend
NEXT_PUBLIC_API_URL=http://localhost:8000
```

Frontend

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

# 🤖 AI Pipeline

## 1. File Upload

The user uploads either:

- PDF
- PNG
- JPG
- JPEG

---

## 2. Pre-processing

If the input is a PDF:

- PDF pages are converted into high-resolution images using **pdf2image**.

If the input is already an image:

- It is directly passed to the AI pipeline.

---

## 3. Prompt Construction

A carefully engineered prompt instructs Gemini to:

- Read only visible information
- Never hallucinate components
- Return "N/A" when values are missing
- Return structured JSON only
- Include confidence scores

Temperature is kept low (`0.1`) to improve consistency.

---

## 4. AI Extraction

Images are sent to:

**Google Gemini 2.5 Flash**

using the official Google GenAI SDK.

Gemini extracts:

- Drawing Number
- Line Number
- Item Code
- Description
- Size
- Schedule
- Quantity
- Unit
- Confidence

---

## 5. Validation

The raw Gemini response is validated using **Pydantic models**.

Benefits:

- Prevent malformed JSON
- Type safety
- Required fields
- Schema consistency

---

## 6. Mock Mode Check

Before calling Gemini, the backend checks whether a valid API key is available.

- If available → Gemini Vision pipeline
- Otherwise → predefined sample MTO response
---

## 7. Response Generation

Validated data is returned as:

- JSON API response
- Downloadable CSV report

---

# 🧠 Prompt Strategy

The prompt follows several rules to reduce hallucinations.

Key instructions include:

- Read only visible information.
- Do not invent components.
- Return "N/A" if unavailable.
- Return valid JSON only.
- Extract every visible MTO item.
- Confidence must be between 0.0 and 1.0.

This significantly improves extraction reliability.

---

# 🛡 Validation Layer

After Gemini responds:

- JSON parsing
- Schema validation
- Confidence normalization
- Metadata validation

Invalid responses are rejected before reaching the frontend.

---

# 🔄 Mock Mode (Graceful Fallback)

If `GEMINI_API_KEY` is not configured, the backend automatically switches to **Mock Mode**.

In Mock Mode:

- A predefined sample MTO response is returned.
- The complete upload → extraction → result → CSV workflow remains functional.
- The frontend clearly displays a **"Mock Mode"** badge so users know the output is simulated.
- This allows evaluators to run the application without creating an API key.

If a Gemini API key is provided, the backend automatically uses the live AI extraction pipeline instead.

---

# 📄 CSV Export

Generated CSV includes:

```
Drawing Number
Line Number
Generated At
Model
Source File

Item Code
Description
Size
Schedule
Quantity
Unit
Confidence
```

---

# 📸 Screenshots

## Upload Page

```
/screenshots/upload.png
```

## Loading State

```
/screenshots/loading.png
```

## Extraction Result

```
/screenshots/result.png
```

## CSV Export

```
/screenshots/csv.png
```

---

# ⚠ Assumptions

- Drawings are reasonably clear.
- Text is readable by Gemini.
- MTO information is visible.
- Single drawing per upload.
- When running in Mock Mode, extraction results are simulated and do not reflect the uploaded drawing.
- The application supports both Live AI mode and Mock Mode.

---

# 🚧 Known Limitations

- Very low-resolution scans reduce extraction accuracy.
- Multi-page PDFs are processed sequentially.
- Handwritten annotations are not guaranteed.
- No OCR fallback if Gemini cannot interpret text.
- CSV export only (Excel not yet supported).

---

# 🔮 Future Improvements

- OCR fallback using PaddleOCR/Tesseract
- Multi-page drawing aggregation
- Excel (.xlsx) export
- DXF/DWG support
- User authentication
- Extraction history
- Batch processing
- Streaming progress updates
- AI-assisted correction mode
- Human-in-the-loop review workflow
- Asynchronous background job processing
- Confidence visualization overlay on drawing
- Automatic symbol detection using Computer Vision

---
# ⚖ Design Decisions

The backend uses a synchronous extraction endpoint instead of an asynchronous job queue.

Reasons:

- Simpler architecture
- Easier local setup
- Suitable for processing one drawing at a time
- Lower implementation complexity for the scope of this assessment

With more time, an asynchronous queue (Celery/RQ) could improve scalability for large batch uploads.
---
# 📜 License

This project was developed for technical assessment and educational purposes.