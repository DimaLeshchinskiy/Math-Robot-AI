🤖 Math Robot AI
================

Intelligent Mathematical Problem Solving Pipeline

From whiteboard images to Wolfram solutions - Automated mathematical problem processing

🚀 Quick Start
--------------

### Get Started in 3 Steps

1. **Clone and setup environment**
   ```bash
   git clone [repository-url]
   cd math-robot-api/infrastructure
   ```
2. **Copy environment file**
    ```bash
   cp example.env .env 
   ```
3. **Start services** docker-compose up -d
    ```bash
   docker-compose up -d
   ```

**Note:** First startup may take several minutes as ML models are downloaded and initialized. If services don't start properly, run `docker-compose up -d` multiple times.

**Important:** Update default credentials in production! The first startup may require multiple `docker-compose up -d` attempts due to ML model initialization.

API will be available at: **http://math-robot-api.localhost/docs**

📋 Project Overview
-------------------

Math Robot AI is a comprehensive pipeline that processes mathematical problems from whiteboard images through multiple AI-powered stages to generate computable solutions.

### System Architecture

**Image Input → Problem Detection → LaTeX OCR → AI Filtering → Wolfram Syntax → Solution**

### Core Pipeline Stages

*   **Stage 1:** Whiteboard image processing and problem segmentation
*   **Stage 2:** Mathematical formula OCR using Pix2Text
*   **Stage 3:** AI-powered LaTeX filtering and validation with Ollama (Qwen2.5 3B)
*   **Stage 4:** Translation to Wolfram Mathematica syntax
*   **Stage 5:** Mathematical solving (external Wolfram kernel)

🛠️ Technology Stack
--------------------

#### Backend & AI Services
![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2CA5E0?style=for-the-badge&logo=docker&logoColor=white)

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
![REST API](https://img.shields.io/badge/REST_API-FF6B6B?style=for-the-badge&logo=api&logoColor=white)

📁 Project Structure
--------------------

**Key Directories:**

- **`controllers/`** - FastAPI route handlers and endpoint definitions
- **`services/`** - Core business logic and processing pipelines
- **`schemas/`** - Pydantic models for request/response validation
- **`models/`** - Internal data models and domain objects
- **`middlewares/`** - FastAPI middleware for logging, auth, etc.
- **`infrastructure/`** - Docker and deployment configuration

```
math-robot-api/
├── app/
│ ├── controllers/
│ │ ├── pipeline_controller.py
│ │ ├── pix2text_controller.py
│ │ ├── whiteboard_processor_controller.py
│ │ └── status_controller.py
│ ├── services/
│ │ ├── pipeline_service.py
│ │ ├── pix2text_service.py
│ │ ├── whiteboard_processor_service.py
│ │ ├── ollama_service.py
│ │ ├── file_service.py
│ │ └── auth_service.py
│ ├── schemas/
│ │ ├── pipeline_schema.py
│ │ ├── latex_schema.py
│ │ └── whiteboard_schema.py
│ ├── models/
│ │ └── file_model.py
│ └── middlewares/
│ └── log_middleware.py
├── infrastructure/
│ ├── docker-compose.yml
│ ├── .env
│ └── example.env
└── requirements.txt
```

🔮 Future Components
--------------------

### Planned Features

*   Real-time mathematical solution execution
*   Physical robot integration for solution demonstration
*   Detailed PDF documentation and presentation materials explaining the mathematical processing pipeline and robot integration.