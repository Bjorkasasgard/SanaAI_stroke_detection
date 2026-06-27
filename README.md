---
title: SanaAI Backend
emoji: 🏥
colorFrom: blue
colorTo: green
sdk: docker
pinned: false
---
# SanaAI: Stroke Detection System

[English Version Below]

## Bahasa Indonesia

SanaAI adalah sistem deteksi dini risiko stroke berbasis Machine Learning. Proyek ini terdiri dari antarmuka web (Frontend), API pemrosesan model (Backend), dan Bot Telegram untuk aksesibilitas yang lebih luas.

### Arsitektur Proyek
* **Frontend:** React.js dengan Vite.
* **Backend:** FastAPI (Python) yang memuat model Scikit-Learn (Logistic Regression, Decision Tree, KNN).
* **Telegram Bot:** Python dengan `python-telegram-bot`, berjalan sebagai background worker.

### Cara Menjalankan Secara Lokal

**1. Menjalankan Backend & Machine Learning**
```bash
cd backend
python -m venv venv
source venv/Scripts/activate  # Untuk Windows
pip install -r requirements.txt
python train_model.py         # Melatih model
uvicorn main:app --reload --port 8001
```

**2. Menjalankan Frontend**
```bash
cd frontend
npm install
npm run dev
```

**3. Menjalankan Bot Telegram**
Buat file `.env` di dalam folder `backend` dan tambahkan `TELEGRAM_BOT_TOKEN=token_bot_anda`.
```bash
cd backend
python bot.py
```

---

## English

SanaAI is an early stroke risk detection system based on Machine Learning. This project consists of a web interface (Frontend), a model processing API (Backend), and a Telegram Bot for wider accessibility.

### Project Architecture
* **Frontend:** React.js with Vite.
* **Backend:** FastAPI (Python) loading Scikit-Learn models (Logistic Regression, Decision Tree, KNN).
* **Telegram Bot:** Python with `python-telegram-bot`, running as a background worker.

### How to Run Locally

**1. Running the Backend & Machine Learning**
```bash
cd backend
python -m venv venv
source venv/Scripts/activate  # For Windows
pip install -r requirements.txt
python train_model.py         # Train the models
uvicorn main:app --reload --port 8001
```

**2. Running the Frontend**
```bash
cd frontend
npm install
npm run dev
```

**3. Running the Telegram Bot**
Create a `.env` file inside the `backend` folder and add `TELEGRAM_BOT_TOKEN=your_bot_token`.
```bash
cd backend
python bot.py
```
