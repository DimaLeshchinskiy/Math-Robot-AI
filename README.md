# 🤖 Math Robot AI

**Intelligent Mathematical Problem Solving Pipeline**
From whiteboard image → OCR → AI normalization → Wolfram evaluation → spoken result (Pepper robot)

---

## 📌 Overview

Math Robot AI is a distributed system that:

1. Captures a whiteboard image (Pepper robot or API upload)
2. Detects mathematical expressions
3. Converts them to LaTeX (Pix2Text OCR)
4. Cleans and normalizes LaTeX using LLM (Ollama – Qwen2.5 3B )
5. Converts to Wolfram syntax
6. Evaluates using Wolfram Kernel (via proxy)
7. Returns structured results
8. Generates HTML output
9. Speaks the result via Pepper robot

---

# 📦 Repository Structure

```
.
├── math-robot-api/         # Main FastAPI backend
│   ├── app/
│   │   ├── controllers/    # API endpoints
│   │   ├── services/       # Core business logic
│   │   ├── schemas/        # Pydantic models
│   │   ├── models/         # Internal domain models
│   │   ├── middlewares/    # Logging middleware
│   │   ├── config.py
│   │   └── main.py
│   ├── Dockerfile
│   └── requirements.txt
│
├── math-robot-client/      # Pepper robot client
│   ├── main.py
│   └── config.py
│
├── wolfram-proxy/          # Wolfram evaluation service
│   ├── main.py
│   └── requirments.txt
│
├── infrastructure/
│   ├── docker-compose.yml
│   ├── docker-compose-school.yml
│   └── example.env
│
└── yolo_data/
    └── best.pt             # YOLO model for problem detection
```
---

# 🚀 Quick Start

---

## 0️⃣ Pull AI model into Ollama

```bash
ollama list
ollama pull qwen2.5:3b
```

*This downloads the Qwen2.5 3B model.
Run this before first use or if the model is missing.*

---

## 1️⃣ Clone repository

```bash
git clone <repository-url>
cd math-robot-api
```

---

## 2️⃣ Configure environment

```bash
cd infrastructure
cp example.env .env
```

Edit `.env` if needed.

---

## 3️⃣ Start Backend Services (Docker)

### 🧑‍💻 Normal development mode

```bash
docker-compose up -d
```

---

### 🎓 School mode (REQUIRED for school demo)

```bash
docker-compose -f docker-compose-school.yml up -d
```

School mode includes:

* Full pipeline services
* Preconfigured classroom setup

---

## 4️⃣ Start Wolfram Proxy (Required)

⚠ The Wolfram Proxy must be started manually in a **separate terminal**.

### Open a new terminal:

```bash
cd wolfram-proxy
```

### Create virtual environment

```bash
python3 -m venv venv
```

### Activate virtual environment

**Linux / macOS**

```bash
source venv/bin/activate
```

### Install dependencies

```bash
pip install -r requirements.txt
```

### Start Wolfram Proxy

```bash
python main.py
```

If successful, you should see:

```
Running on http://0.0.0.0:8010
```

⚠ Make sure Wolfram Engine is installed and the path matches:

```python
WolframLanguageSession("/usr/local/bin/WolframKernel")
```

---

## ⏳ First Startup Notice

First startup may take several minutes because:

* Pix2Text model initializes
* Ollama model (Qwen2.5 3B) loads
* YOLO weights are loaded
* Wolfram session initializes

---

# 🌐 Services

| Service            | Port       | Description                |
| ------------------ | ---------- | -------------------------- |
| math-robot-api     | 8000       | Main FastAPI backend       |
| wolfram-proxy      | 8010       | Wolfram evaluation service |

API docs available at:

```
http://localhost:8000/docs
```

---

# 🔐 Authentication

API uses **Basic Authentication**.

Default (example):

```
username: test
password: test
```

⚠ Change credentials in production.

Pepper client sends:

```python
Authorization: Basic base64("test:test")
```

---

# 🧠 Processing Pipeline

The `PipelineService` orchestrates:

### Step 1 — Whiteboard Processing

* YOLO model detects problem regions
* Extracts individual problem images

### Step 2 — OCR

* Pix2Text converts image → LaTeX

### Step 3 — LaTeX Filtering

* Ollama (Qwen2.5 3B)
* Fixes syntax
* Normalizes structure
* Converts to Wolfram syntax

### Step 4 — Wolfram Evaluation

* Sends to `wolfram-proxy`
* Evaluates via Wolfram Kernel

### Step 5 — Result Filtering

* LLM cleans output
* Removes unnecessary formatting

---

# 📄 HTML File Generator

After pipeline execution:

```python
HtmlService.save_problem(...)
```

Generates:

* Structured HTML file
* Saved in public directory
* Accessible via:

```
/public/index.html
```

This allows:

* Viewing results on tablet
* Shows last solved problem
* Prints helpful info for debug

---

# 🤖 Pepper Robot Client

Located in:

```
math-robot-client/
```

### What it does:

* Waits for head touch
* Captures camera image
* Sends image via multipart/form-data
* Receives result
* Speaks solution
* Displays HTML on tablet
---

# 🔬 Wolfram Proxy

Located in:

```
wolfram-proxy/
```

Lightweight Flask service that:

* Maintains persistent `WolframLanguageSession`
* Evaluates Wolfram code
* Exposes:

```
GET /eval?code=...
GET /health
```

Required for full pipeline functionality.

---

# 🛠 Technology Stack

#### Backend
![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)

#### AI & Machine Learning
![Pix2Text](https://img.shields.io/badge/Pix2Text-FF6B6B?style=for-the-badge&logo=book&logoColor=white)
![Ollama](https://img.shields.io/badge/Ollama-7C3AED?style=for-the-badge&logo=ollama&logoColor=white)
![OpenCV](https://img.shields.io/badge/OpenCV-5C3EE8?style=for-the-badge&logo=opencv&logoColor=white)
![Qwen2.5](https://img.shields.io/badge/Qwen2.5_3B-10B981?style=for-the-badge&logo=ai&logoColor=white)

#### Mathematical Processing
![Wolfram](https://img.shields.io/badge/Wolfram-DD1100?style=for-the-badge&logo=wolfram&logoColor=white)
![LaTeX](https://img.shields.io/badge/LaTeX-008080?style=for-the-badge&logo=latex&logoColor=white)
![Mathematica](https://img.shields.io/badge/Mathematica-DD1100?style=for-the-badge&logo=wolframmathematica&logoColor=white)

#### Infrastructure & Tools
![Git](https://img.shields.io/badge/Git-F05033?style=for-the-badge&logo=git&logoColor=white)
![Docker Compose](https://img.shields.io/badge/Docker_Compose-2CA5E0?style=for-the-badge&logo=docker&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2CA5E0?style=for-the-badge&logo=docker&logoColor=white)
![REST API](https://img.shields.io/badge/REST_API-FF6B6B?style=for-the-badge&logo=api&logoColor=white)

---

# 🧪 Main Endpoint

## POST `/pipeline/{target_regions}`

### Parameters:

* `target_regions` — expected number of expressions (1–20)
* `file` — whiteboard image (multipart/form-data)

### Returns:

```json
{
  "total_problems": 1,
  "successful": 1,
  "failed": 0,
  "results": [
    {
      "problem_id": 1,
      "latex_raw": "...",
      "latex_filtered": "...",
      "result_wolfram": "...",
      "result_filtered": "...",
      "success": true
    }
  ],
  "processing_time": 3.42
}
```

---

# ⚠ Important Notes

* YOLO model file must exist:

```
yolo_data/best.pt
```

* Wolfram Kernel path must match:

```python
WolframLanguageSession("/usr/local/bin/WolframKernel")
```

* For school demo → always use `docker-compose-school.yml`

---
