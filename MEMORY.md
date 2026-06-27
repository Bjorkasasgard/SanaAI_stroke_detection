# Memory

## Projects & Knowledge
- **Project Name**: Sana AI Stroke Screening
- **Backend Directory**: Contains API and ML model training scripts.
- **Dataset location**: `backend/data/healthcare-dataset-stroke-data.csv`
- **Trained models**: Saved as `.pkl` files in `backend/models/`.

## Lessons Learned
- **Missing Categorical Data**: Kaggle datasets may have unexpected `NaN` values (e.g. in `gender`). When performing label encoding using pandas `.map()`, unmapped values automatically become `NaN`, which crashes algorithms like `SMOTE` during preprocessing. Ensure categoricals are filtered/cleaned of non-standard values (e.g. keeping only "Female" and "Male") before encoding.
- **Directory Execution**: Always run `train_model.py` from the `backend/` directory to ensure relative paths resolve correctly.
