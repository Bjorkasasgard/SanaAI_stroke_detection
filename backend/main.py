"""
main.py — FastAPI backend untuk Sana AI Stroke Screening.
Bilingual Edition
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any, Dict, List

import joblib
import numpy as np
import feedparser
import os

from fastapi import FastAPI, HTTPException, Query, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(level=logging.INFO)
logger: logging.Logger = logging.getLogger("sana-ai")

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
BASE_DIR: Path = Path(__file__).resolve().parent
MODELS_DIR: Path = BASE_DIR / "models"

# ---------------------------------------------------------------------------
# Global state
# ---------------------------------------------------------------------------
loaded_models: Dict[str, Any] = {}
scaler: Any = None
encoding_maps: Dict[str, Dict[str, int]] = {}
feature_names: List[str] = []
models_ready: bool = False

# ---------------------------------------------------------------------------
# Translations
# ---------------------------------------------------------------------------
FEATURE_LABELS = {
    "id": {
        "gender": "Jenis Kelamin",
        "age": "Usia",
        "hypertension": "Hipertensi",
        "heart_disease": "Penyakit Jantung",
        "ever_married": "Status Pernikahan",
        "work_type": "Jenis Pekerjaan",
        "Residence_type": "Tipe Tempat Tinggal",
        "avg_glucose_level": "Rata-rata Kadar Glukosa",
        "bmi": "Indeks Massa Tubuh (BMI)",
        "smoking_status": "Status Merokok",
    },
    "en": {
        "gender": "Gender",
        "age": "Age",
        "hypertension": "Hypertension",
        "heart_disease": "Heart Disease",
        "ever_married": "Marital Status",
        "work_type": "Work Type",
        "Residence_type": "Residence Type",
        "avg_glucose_level": "Average Glucose Level",
        "bmi": "Body Mass Index (BMI)",
        "smoking_status": "Smoking Status",
    }
}

# ---------------------------------------------------------------------------
# Pydantic schemas
# ---------------------------------------------------------------------------
class PredictionRequest(BaseModel):
    model: str = Field(default="logistic_regression")
    gender: str
    age: float
    hypertension: int
    heart_disease: int
    ever_married: str
    work_type: str
    residence_type: str
    avg_glucose_level: float
    bmi: float
    smoking_status: str

class ContributingFactor(BaseModel):
    factor: str
    value: str
    impact: str
    description: str

class PredictionResponse(BaseModel):
    prediction: int
    probability: float
    risk_level: str
    risk_color: str
    model_used: str
    contributing_factors: List[ContributingFactor]
    recommendations: List[str]

# ---------------------------------------------------------------------------
# Lifespan
# ---------------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    global loaded_models, scaler, encoding_maps, feature_names, models_ready

    model_files = {
        "logistic_regression": "logistic_regression.pkl",
        "decision_tree": "decision_tree.pkl",
        "knn": "knn.pkl",
    }

    try:
        for model_id, filename in model_files.items():
            model_path = MODELS_DIR / filename
            if model_path.exists():
                loaded_models[model_id] = joblib.load(model_path)
        
        scaler_path = MODELS_DIR / "scaler.pkl"
        if scaler_path.exists():
            scaler = joblib.load(scaler_path)
            
        encoding_path = MODELS_DIR / "encoding_maps.pkl"
        if encoding_path.exists():
            encoding_maps = joblib.load(encoding_path)
            
        feature_names_path = MODELS_DIR / "feature_names.pkl"
        if feature_names_path.exists():
            feature_names = joblib.load(feature_names_path)

        if loaded_models and scaler is not None and encoding_maps and feature_names:
            models_ready = True
    except Exception as exc:
        logger.error("Gagal memuat artefak model: %s", exc)

    yield

app: FastAPI = FastAPI(title="Sana AI API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------
def _determine_risk(probability: float, lang: str) -> tuple[str, str]:
    if probability < 0.30:
        return "Rendah" if lang == "id" else "Low", "#4CAF50"
    elif probability < 0.60:
        return "Sedang" if lang == "id" else "Medium", "#FF9800"
    else:
        return "Tinggi" if lang == "id" else "High", "#E53935"

def _format_feature_value(feature: str, request: PredictionRequest, lang: str) -> str:
    y_str = "Ya" if lang == "id" else "Yes"
    n_str = "Tidak" if lang == "id" else "No"
    yr_str = "tahun" if lang == "id" else "years"
    
    human_values = {
        "gender": request.gender,
        "age": f"{request.age:.0f} {yr_str}",
        "hypertension": y_str if request.hypertension == 1 else n_str,
        "heart_disease": y_str if request.heart_disease == 1 else n_str,
        "ever_married": request.ever_married,
        "work_type": request.work_type,
        "Residence_type": request.residence_type,
        "avg_glucose_level": f"{request.avg_glucose_level:.1f} mg/dL",
        "bmi": f"{request.bmi:.1f}",
        "smoking_status": request.smoking_status,
    }
    return human_values.get(feature, "")

def _get_feature_description(feature: str, request: PredictionRequest, lang: str) -> str:
    if lang == "id":
        if feature == "age": return "Usia di atas 55 tahun meningkatkan risiko stroke" if request.age > 55 else "Usia Anda masih dalam rentang risiko rendah"
        if feature == "hypertension": return "Hipertensi adalah faktor risiko utama stroke" if request.hypertension == 1 else "Tidak memiliki hipertensi menurunkan risiko"
        if feature == "heart_disease": return "Penyakit jantung meningkatkan risiko stroke secara signifikan" if request.heart_disease == 1 else "Tidak ada riwayat penyakit jantung"
        if feature == "avg_glucose_level": return "Kadar glukosa tinggi (>200 mg/dL) berkaitan dengan risiko stroke" if request.avg_glucose_level > 200 else "Kadar glukosa sedikit tinggi" if request.avg_glucose_level > 140 else "Kadar glukosa normal"
        if feature == "bmi": return "BMI di atas 30 menunjukkan obesitas" if request.bmi > 30 else "BMI sedikit di atas normal" if request.bmi > 25 else "BMI normal"
        if feature == "smoking_status": return "Merokok meningkatkan risiko secara signifikan" if request.smoking_status == "smokes" else "Riwayat merokok sebelumnya masih meningkatkan risiko" if request.smoking_status == "formerly smoked" else "Tidak merokok menurunkan risiko"
        return "Faktor yang berpengaruh terhadap prediksi"
    else:
        if feature == "age": return "Age over 55 increases stroke risk" if request.age > 55 else "Your age is in the low-risk range"
        if feature == "hypertension": return "Hypertension is a major stroke risk factor" if request.hypertension == 1 else "No hypertension lowers the risk"
        if feature == "heart_disease": return "Heart disease significantly increases stroke risk" if request.heart_disease == 1 else "No history of heart disease"
        if feature == "avg_glucose_level": return "High glucose (>200 mg/dL) is linked to stroke risk" if request.avg_glucose_level > 200 else "Slightly elevated glucose" if request.avg_glucose_level > 140 else "Normal glucose level"
        if feature == "bmi": return "BMI over 30 indicates obesity" if request.bmi > 30 else "BMI slightly above normal" if request.bmi > 25 else "Normal BMI"
        if feature == "smoking_status": return "Smoking significantly increases risk" if request.smoking_status == "smokes" else "Former smoking still elevates risk" if request.smoking_status == "formerly smoked" else "Non-smoking helps lower risk"
        return "Factor influencing prediction"

def _impact_level(magnitude: float, threshold_high: float, threshold_med: float) -> str:
    if magnitude >= threshold_high: return "high"
    elif magnitude >= threshold_med: return "medium"
    return "low"

def _analyze_contributing_factors_lr(model: Any, feature_values: np.ndarray, request: PredictionRequest, lang: str) -> List[ContributingFactor]:
    coefficients = model.coef_[0]
    contributions = np.abs(coefficients * feature_values)
    sorted_indices = np.argsort(contributions)[::-1]
    factors = []
    max_contrib = float(contributions.max()) if contributions.max() > 0 else 1.0

    for idx in sorted_indices[:5]:
        feat = feature_names[idx]
        magnitude = float(contributions[idx]) / max_contrib
        factors.append(
            ContributingFactor(
                factor=FEATURE_LABELS[lang].get(feat, feat),
                value=_format_feature_value(feat, request, lang),
                impact=_impact_level(magnitude, 0.6, 0.3),
                description=_get_feature_description(feat, request, lang),
            )
        )
    return factors

def _analyze_contributing_factors_heuristic(request: PredictionRequest, lang: str) -> List[ContributingFactor]:
    factors = []
    if request.age > 55: factors.append(ContributingFactor(factor=FEATURE_LABELS[lang]["age"], value=f"{request.age:.0f}", impact="high", description=_get_feature_description("age", request, lang)))
    elif request.age > 40: factors.append(ContributingFactor(factor=FEATURE_LABELS[lang]["age"], value=f"{request.age:.0f}", impact="medium", description=_get_feature_description("age", request, lang)))
    else: factors.append(ContributingFactor(factor=FEATURE_LABELS[lang]["age"], value=f"{request.age:.0f}", impact="low", description=_get_feature_description("age", request, lang)))

    y_str = "Ya" if lang == "id" else "Yes"
    n_str = "Tidak" if lang == "id" else "No"

    factors.append(ContributingFactor(factor=FEATURE_LABELS[lang]["hypertension"], value=y_str if request.hypertension == 1 else n_str, impact="high" if request.hypertension == 1 else "low", description=_get_feature_description("hypertension", request, lang)))
    factors.append(ContributingFactor(factor=FEATURE_LABELS[lang]["heart_disease"], value=y_str if request.heart_disease == 1 else n_str, impact="high" if request.heart_disease == 1 else "low", description=_get_feature_description("heart_disease", request, lang)))

    impact_order = {"high": 0, "medium": 1, "low": 2}
    factors.sort(key=lambda f: impact_order.get(f.impact, 3))
    return factors[:5]

def _generate_recommendations(request: PredictionRequest, risk_level: str, lang: str) -> List[str]:
    recs = []
    if lang == "id":
        recs.append("Konsultasikan hasil ini dengan dokter Anda")
        if risk_level in ("Sedang", "Tinggi"): recs.append("Segera lakukan pemeriksaan kesehatan menyeluruh")
        if request.hypertension == 1: recs.append("Pantau tekanan darah secara rutin")
        if request.heart_disease == 1: recs.append("Lakukan kontrol rutin ke dokter spesialis jantung")
        if request.avg_glucose_level > 140: recs.append("Periksa kadar gula darah secara berkala")
        if request.bmi > 25: recs.append("Jaga berat badan ideal melalui diet seimbang")
        if request.smoking_status in ("smokes", "formerly smoked"): recs.append("Berhenti merokok")
        recs.append("Terapkan pola hidup sehat")
        recs.append("⚠️ Hasil ini bersifat prediktif dan BUKAN diagnosis medis.")
    else:
        recs.append("Consult these results with your doctor")
        if risk_level in ("Medium", "High"): recs.append("Perform a comprehensive health check-up immediately")
        if request.hypertension == 1: recs.append("Routinely monitor blood pressure")
        if request.heart_disease == 1: recs.append("Regular check-ups with a cardiologist")
        if request.avg_glucose_level > 140: recs.append("Check blood sugar regularly")
        if request.bmi > 25: recs.append("Maintain an ideal weight through balanced diet")
        if request.smoking_status in ("smokes", "formerly smoked"): recs.append("Stop smoking")
        recs.append("Adopt a healthy lifestyle")
        recs.append("⚠️ This result is predictive and NOT a medical diagnosis.")
    return recs

# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------
@app.get("/api/health")
async def health_check():
    return {"status": "ok", "models_loaded": models_ready}

@app.get("/api/models")
async def get_models(lang: str = Query("id")):
    return [
        {
            "id": "logistic_regression",
            "name": "Logistic Regression",
            "recommended": True,
            "badge": "Direkomendasikan" if lang == "id" else "Recommended",
            "description": "Model yang paling sensitif dalam mendeteksi potensi stroke. Sangat baik untuk screening awal karena mampu menangkap hingga 85% kasus stroke yang sebenarnya." if lang == "id" else "Most sensitive model for detecting potential stroke. Excellent for early screening as it captures up to 85% of actual stroke cases.",
            "pros": "Recall tinggi — meminimalkan kasus stroke yang terlewat" if lang == "id" else "High recall — minimizes missed stroke cases",
            "cons": "Mungkin memberikan beberapa peringatan berlebih (false alarm)" if lang == "id" else "May yield some false alarms",
            "best_for": "Screening awal yang mengutamakan keselamatan" if lang == "id" else "Safety-first early screening"
        },
        {
            "id": "decision_tree",
            "name": "Decision Tree",
            "recommended": False,
            "badge": "Akurasi Tinggi" if lang == "id" else "High Accuracy",
            "description": "Model dengan akurasi keseluruhan tertinggi. Menggunakan pohon keputusan untuk mengklasifikasi risiko berdasarkan pola data." if lang == "id" else "Model with the highest overall accuracy. Uses decision trees to classify risk based on data patterns.",
            "pros": "Akurasi keseluruhan tinggi" if lang == "id" else "High overall accuracy",
            "cons": "Recall rendah — beberapa kasus stroke mungkin tidak terdeteksi" if lang == "id" else "Low recall — some stroke cases might go undetected",
            "best_for": "Analisis umum dengan akurasi tinggi" if lang == "id" else "General analysis with high accuracy"
        },
        {
            "id": "knn",
            "name": "K-Nearest Neighbors",
            "recommended": False,
            "badge": "Seimbang" if lang == "id" else "Balanced",
            "description": "Model yang mengklasifikasi berdasarkan kemiripan dengan data pasien lain. Memberikan keseimbangan antara sensitivitas dan akurasi." if lang == "id" else "Model that classifies based on similarity to other patients. Provides a balance between sensitivity and accuracy.",
            "pros": "Pendekatan berbasis kemiripan yang intuitif" if lang == "id" else "Intuitive similarity-based approach",
            "cons": "Performa bergantung pada distribusi data" if lang == "id" else "Performance depends heavily on data distribution",
            "best_for": "Alternatif dengan pendekatan berbeda" if lang == "id" else "Alternative with a different approach"
        }
    ]

@app.get("/api/news")
async def get_news(lang: str = Query("id")):
    """Mengambil berita kesehatan terkini dari RSS Feed publik."""
    try:
        # Menggunakan feed CNN Indonesia Gaya Hidup/Kesehatan untuk ID, dan NYT Health untuk EN
        feed_url = "https://www.cnnindonesia.com/gaya-hidup/rss" if lang == "id" else "https://rss.nytimes.com/services/xml/rss/nyt/Health.xml"
        feed = feedparser.parse(feed_url)
        
        news_items = []
        # Ambil maksimal 4 berita
        for entry in feed.entries[:4]:
            news_items.append({
                "title": entry.title,
                "link": entry.link,
                "pubDate": entry.published if hasattr(entry, 'published') else "",
                "summary": entry.description[:150] + "..." if hasattr(entry, 'description') and entry.description else ""
            })
            
        return {"status": "ok", "news": news_items}
    except Exception as exc:
        logger.error("Gagal mengambil berita: %s", exc)
        return {"status": "error", "news": []}

@app.post("/api/predict", response_model=PredictionResponse)
async def predict(request: PredictionRequest, lang: str = Query("id")):
    if not models_ready: raise HTTPException(status_code=503, detail="Models not ready")
    if request.model not in loaded_models: raise HTTPException(status_code=400, detail="Invalid model")

    try:
        encoded_values = {
            "gender": encoding_maps["gender"][request.gender],
            "age": request.age,
            "hypertension": request.hypertension,
            "heart_disease": request.heart_disease,
            "ever_married": encoding_maps["ever_married"][request.ever_married],
            "work_type": encoding_maps["work_type"][request.work_type],
            "Residence_type": encoding_maps["Residence_type"][request.residence_type],
            "avg_glucose_level": request.avg_glucose_level,
            "bmi": request.bmi,
            "smoking_status": encoding_maps["smoking_status"][request.smoking_status],
        }
    except KeyError:
        raise HTTPException(status_code=400, detail="Invalid values")

    feature_array = np.array([encoded_values[feat] for feat in feature_names]).reshape(1, -1)
    scaled_input = scaler.transform(feature_array)
    selected_model = loaded_models[request.model]
    
    prediction = int(selected_model.predict(scaled_input)[0])
    stroke_probability = float(selected_model.predict_proba(scaled_input)[0][1])

    risk_level, risk_color = _determine_risk(stroke_probability, lang)

    if request.model == "logistic_regression":
        contributing_factors = _analyze_contributing_factors_lr(selected_model, scaled_input[0], request, lang)
    else:
        contributing_factors = _analyze_contributing_factors_heuristic(request, lang)

    recommendations = _generate_recommendations(request, risk_level, lang)

    return PredictionResponse(
        prediction=prediction,
        probability=round(stroke_probability, 4),
        risk_level=risk_level,
        risk_color=risk_color,
        model_used=request.model,
        contributing_factors=contributing_factors,
        recommendations=recommendations,
    )
