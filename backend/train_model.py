"""
train_model.py — Script pelatihan model untuk Sana AI Stroke Screening.

Melatih 3 model klasifikasi (Logistic Regression, Decision Tree, KNN)
pada dataset stroke dan menyimpan artefak ke backend/models/.
"""

import sys
from pathlib import Path
from typing import Dict, List, Tuple

import joblib
import numpy as np
import pandas as pd
from imblearn.over_sampling import SMOTE
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import classification_report


# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
BASE_DIR: Path = Path(__file__).resolve().parent
DATA_DIR: Path = BASE_DIR / "data"
MODELS_DIR: Path = BASE_DIR / "models"
DATASET_PATH: Path = DATA_DIR / "healthcare-dataset-stroke-data.csv"

# Ensure output directories exist
DATA_DIR.mkdir(parents=True, exist_ok=True)
MODELS_DIR.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# Encoding maps — saved alongside models so the API can decode user inputs
# ---------------------------------------------------------------------------
ENCODING_MAPS: Dict[str, Dict[str, int]] = {
    "gender": {"Female": 0, "Male": 1},
    "ever_married": {"No": 0, "Yes": 1},
    "work_type": {
        "Govt_job": 0,
        "Never_worked": 1,
        "Private": 2,
        "Self-employed": 3,
        "children": 4,
    },
    "Residence_type": {"Rural": 0, "Urban": 1},
    "smoking_status": {
        "Unknown": 0,
        "formerly smoked": 1,
        "never smoked": 2,
        "smokes": 3,
    },
}


def load_and_clean(path: Path) -> pd.DataFrame:
    """Memuat CSV dan melakukan pembersihan awal."""
    print(f"[1/10] Memuat dataset dari {path} ...")
    if not path.exists():
        print(f"ERROR: File dataset tidak ditemukan di {path}")
        print("       Letakkan file 'healthcare-dataset-stroke-data.csv' di folder backend/data/")
        sys.exit(1)

    df: pd.DataFrame = pd.read_csv(path)
    print(f"        Dataset dimuat: {df.shape[0]} baris, {df.shape[1]} kolom")
    return df


def preprocess(df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray, List[str]]:
    """
    Pipeline preprocessing lengkap:
    drop id, hapus gender='Other', isi BMI, label encode, scale, SMOTE.

    Returns:
        X_resampled: fitur setelah SMOTE
        y_resampled: target setelah SMOTE
        feature_names: daftar nama fitur (terurut)
    """
    # --- Drop 'id' column ---
    print("[2/10] Menghapus kolom 'id' ...")
    df = df.drop(columns=["id"], errors="ignore")

    # --- Drop invalid/missing gender ---
    print("[3/10] Menghapus baris dengan gender selain 'Female' atau 'Male' ...")
    n_before = len(df)
    df = df[df["gender"].isin(["Female", "Male"])].copy()
    n_removed = n_before - len(df)
    print(f"        {n_removed} baris dihapus")


    # --- Fill missing BMI with median ---
    print("[4/10] Mengisi nilai BMI yang kosong dengan median ...")
    bmi_median: float = df["bmi"].median()
    n_missing: int = int(df["bmi"].isna().sum())
    df["bmi"] = df["bmi"].fillna(bmi_median)
    print(f"        {n_missing} nilai kosong diisi dengan median = {bmi_median:.1f}")

    # --- Label encode categorical columns ---
    print("[5/10] Label encoding kolom kategorikal ...")
    for col, mapping in ENCODING_MAPS.items():
        if col in df.columns:
            df[col] = df[col].map(mapping)
            unmapped = df[col].isna().sum()
            if unmapped > 0:
                print(f"        PERINGATAN: {unmapped} nilai tidak ter-map di kolom '{col}'")

    # --- Separate features and target ---
    print("[6/10] Memisahkan fitur (X) dan target (y) ...")
    target_col: str = "stroke"
    feature_names: List[str] = [c for c in df.columns if c != target_col]
    X: np.ndarray = df[feature_names].values
    y: np.ndarray = df[target_col].values
    print(f"        Fitur: {feature_names}")
    print(f"        Distribusi target — 0: {(y == 0).sum()}, 1: {(y == 1).sum()}")

    # --- StandardScaler ---
    print("[7/10] Melakukan StandardScaler pada fitur ...")
    scaler: StandardScaler = StandardScaler()
    X_scaled: np.ndarray = scaler.fit_transform(X)

    # Save scaler
    scaler_path: Path = MODELS_DIR / "scaler.pkl"
    joblib.dump(scaler, scaler_path)
    print(f"        Scaler disimpan ke {scaler_path}")

    # --- SMOTE ---
    print("[8/10] Menerapkan SMOTE untuk menangani ketidakseimbangan kelas ...")
    smote: SMOTE = SMOTE(random_state=42)
    X_resampled, y_resampled = smote.fit_resample(X_scaled, y)
    print(f"        Setelah SMOTE — 0: {(y_resampled == 0).sum()}, 1: {(y_resampled == 1).sum()}")

    return X_resampled, y_resampled, feature_names


def train_and_evaluate(
    X: np.ndarray,
    y: np.ndarray,
    feature_names: List[str],
) -> None:
    """Melatih 3 model, menampilkan laporan, dan menyimpan artefak."""
    # --- Train-test split ---
    print("[9/10] Membagi data: 80% latih, 20% uji ...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    print(f"        Train: {X_train.shape[0]}, Test: {X_test.shape[0]}")

    # --- Define models ---
    models: Dict[str, object] = {
        "logistic_regression": LogisticRegression(
            random_state=42, max_iter=1000, class_weight="balanced"
        ),
        "decision_tree": DecisionTreeClassifier(random_state=42),
        "knn": KNeighborsClassifier(n_neighbors=5),
    }

    # --- Train and evaluate ---
    print("[10/10] Melatih dan mengevaluasi model ...\n")
    for name, model in models.items():
        print(f"{'=' * 60}")
        print(f"  Model: {name}")
        print(f"{'=' * 60}")

        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)

        print(classification_report(y_test, y_pred, target_names=["No Stroke", "Stroke"]))

        # Save model
        model_path: Path = MODELS_DIR / f"{name}.pkl"
        joblib.dump(model, model_path)
        print(f"  [OK] Model disimpan ke {model_path}\n")

    # --- Save encoding maps and feature names ---
    encoding_path: Path = MODELS_DIR / "encoding_maps.pkl"
    joblib.dump(ENCODING_MAPS, encoding_path)
    print(f"[OK] Encoding maps disimpan ke {encoding_path}")

    feature_names_path: Path = MODELS_DIR / "feature_names.pkl"
    joblib.dump(feature_names, feature_names_path)
    print(f"[OK] Feature names disimpan ke {feature_names_path}")


def main() -> None:
    """Entry-point utama untuk training pipeline."""
    print("=" * 60)
    print("  Sana AI - Training Pipeline")
    print("=" * 60)
    print()

    df: pd.DataFrame = load_and_clean(DATASET_PATH)
    X, y, feature_names = preprocess(df)
    train_and_evaluate(X, y, feature_names)

    print()
    print("=" * 60)
    print("  [OK] Training selesai! Semua model tersimpan di backend/models/")
    print("=" * 60)


if __name__ == "__main__":
    main()
