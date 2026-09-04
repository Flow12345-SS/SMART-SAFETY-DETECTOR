# Smart Safety Detector

Real-Time Workplace Safety Detection & Monitoring System using YOLOv8, FastAPI, and HTML/CSS/JS.

## Features
- **AI**: YOLOv8 object detection, object tracking, and confidence scoring.
- **Safety Engine**: Rules for detecting No Helmet, No Vest, Fire, Smoke, and Mobile Phones.
- **Backend**: FastAPI with SQLite for logging detections and alerts.
- **Frontend**: Responsive dashboard showing real-time metrics, live camera feeds, and uploaded image detections.

## Architecture
```text
                 DATASET
                    ↓
          DATA PREPROCESSING
                    ↓
             JUPYTER TRAINING
                    ↓
              YOLO MODEL (best.pt)
                    ↓
   IMAGE/VIDEO/WEBCAM INFERENCE (YOLO)
                    ↓
             OBJECT TRACKING
                    ↓
             SAFETY RULE ENGINE
                    ↓
          ALERTS & SQLITE DB
                    ↓
              FASTAPI REST
                    ↓
             FRONTEND DASHBOARD
```

## Dataset
Use standard YOLO annotations for the following classes:
0. person
1. helmet
2. vest
3. no-helmet
4. no-vest
5. fire
6. smoke
7. mobile-phone

Place dataset in `data/images/` and `data/labels/` according to `config/dataset.yaml`.

## Installation (Windows)

```bash
# 1. Create venv
python -m venv venv
.\venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Train Model (or run Jupyter Notebooks in notebooks/)
python scripts/train.py

# 4. Start API & Frontend
uvicorn app.main:app --reload
```

## Usage

**Webcam**: `python run.py --source webcam`
**Image**: `python run.py --source image --path data/test.jpg`
**Video**: `python run.py --source video --path data/test.mp4`

## Vercel Deployment
Vercel is serverless and cannot natively run heavy YOLO inference (PyTorch) due to file size and memory limits. The provided `vercel.json` deploys the FastAPI REST endpoints and the static HTML dashboard. You must host the inference module (FastAPI with YOLO) via Docker on a standard VPS (e.g. AWS EC2, DigitalOcean) for the AI components to function.
