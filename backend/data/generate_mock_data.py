import pandas as pd
import numpy as np

# Set random seed for reproducibility
np.random.seed(42)

n_samples = 1000

data = {
    'id': np.arange(1, n_samples + 1),
    'gender': np.random.choice(['Male', 'Female'], n_samples),
    'age': np.random.uniform(1, 85, n_samples),
    'hypertension': np.random.choice([0, 1], n_samples, p=[0.9, 0.1]),
    'heart_disease': np.random.choice([0, 1], n_samples, p=[0.95, 0.05]),
    'ever_married': np.random.choice(['Yes', 'No'], n_samples),
    'work_type': np.random.choice(['Private', 'Self-employed', 'Govt_job', 'children', 'Never_worked'], n_samples),
    'Residence_type': np.random.choice(['Urban', 'Rural'], n_samples),
    'avg_glucose_level': np.random.uniform(50, 250, n_samples),
    'bmi': np.random.uniform(15, 45, n_samples),
    'smoking_status': np.random.choice(['never smoked', 'Unknown', 'formerly smoked', 'smokes'], n_samples),
}

# Generate target 'stroke' based on some risk factors
risk = (
    (data['age'] > 55).astype(int) * 0.2 +
    data['hypertension'] * 0.3 +
    data['heart_disease'] * 0.3 +
    (data['avg_glucose_level'] > 150).astype(int) * 0.1
)

# Convert risk to probability using a simple logistic-like curve, then sample
stroke_prob = 1 / (1 + np.exp(- (risk - 0.5) * 5))
data['stroke'] = np.random.binomial(1, stroke_prob)

df = pd.DataFrame(data)
df.to_csv(r'c:\Users\Axioo Hype 7\Documents\Matkul\Macine Learning\projects\SanaAI\backend\data\healthcare-dataset-stroke-data.csv', index=False)
print("Synthetic dataset created successfully!")

