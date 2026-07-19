# PavePro Vision: Predictive Road Maintenance Intelligence

<div align="center">
  <h3>Advanced AI-Powered Road Degradation Prediction & Digital Twin Dashboard</h3>
  <br />
  <strong>🟢 Live Demo:</strong> <a href="https://predictive-project-beryl.vercel.app">https://predictive-project-beryl.vercel.app</a>
</div>

---

## 📖 Overview

**Live Demo**: [https://predictive-project-beryl.vercel.app](https://predictive-project-beryl.vercel.app)
**GitHub Repository**: [Road-Pavement-Damage-Prediction](https://github.com/anshumanvatsa/Road-Pavement-Damage-Prediction)

**PavePro Vision** is a comprehensive, full-stack predictive maintenance platform designed to monitor, analyze, and forecast road degradation. By leveraging state-of-the-art machine learning, computer vision, and interactive digital twins, the system enables transportation agencies and civil engineers to transition from reactive repairs to proactive infrastructure management.

## 🚀 Core Features

- **Hybrid Predictive Modeling:** Integrates localized weather patterns (via ERA5 datasets) and historical traffic volume data to accurately forecast road severity and wear-and-tear progression over time.
- **Computer Vision Pipeline:** Utilizes custom-trained YOLOv8 and PyTorch CNN models to detect and classify specific types of surface damage directly from images or video feeds (Road Damage Detection).
- **Interactive Digital Twins:** A modern React web dashboard that provides a virtual representation of physical road assets, allowing stakeholders to visualize current and predicted degradation states in real-time.
- **Robust REST API:** A production-ready FastAPI backend that serves on-the-fly ML inferences, manages road metadata, and powers the dashboard analytics.

## 🛠️ Technology Stack

| Component | Technologies |
| --- | --- |
| **Frontend** | React, TypeScript, Vite, Tailwind CSS, shadcn-ui |
| **Backend** | Python, FastAPI, SQLAlchemy, SQLite/PostgreSQL |
| **Machine Learning** | PyTorch, Ultralytics (YOLOv8), Scikit-Learn, XGBoost, Pandas |
| **Data Processing** | Python scripts for PDF extraction, GRIB weather parsing, and CSV manipulation |

## 📁 Project Structure

```text
├── backend/                # FastAPI application, database models, and API routes
├── pave-pro-vision-main/   # React/Vite frontend source code and UI components
├── data/                   # Raw datasets, CV training scripts, and data extraction pipelines
├── hybrid/                 # Hybrid predictive modeling scripts (traffic + weather)
```

## 🚦 Getting Started

### Prerequisites
- Node.js (v18+)
- Python (v3.10+)

### 1. Start the Backend
Navigate to the `backend` directory, set up your virtual environment, install dependencies, and run the FastAPI server:
```bash
cd backend
python -m venv venv
# Activate venv (Windows: venv\Scripts\activate | Mac/Linux: source venv/bin/activate)
pip install -r requirements.txt
cp .env.example .env  # Configure your env variables
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```
*The API will be available at `http://localhost:8000/docs`.*

### 2. Start the Frontend
Open a new terminal, navigate to the frontend directory, install packages, and start the Vite dev server:
```bash
cd pave-pro-vision-main
npm install
npm run dev
```
*The frontend will be available at `http://localhost:5173`.*

---
*Built to ensure safer, longer-lasting roads through data intelligence.*
