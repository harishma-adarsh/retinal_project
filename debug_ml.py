import os
import joblib
import numpy as np

MODEL_DIR = r'c:\Harishma\Maitexa\A_project\Retinal_image\retinal_project\retina_app\ml_models'
MODEL_PATH = os.path.join(MODEL_DIR, 'heart_disease_model.pkl')

model = joblib.load(MODEL_PATH)

# Healthy: Low age, high thalach, low restbps, etc.
healthy = np.array([[25, 0, 0, 110, 170, 0, 0, 180, 0, 0.0, 1, 0, 3]])
# Unhealthy: High age, low thalach, high restbps, etc.
unhealthy = np.array([[75, 1, 3, 170, 300, 1, 2, 80, 1, 4.0, 3, 3, 7]])

p_h = model.predict(healthy)[0]
p_u = model.predict(unhealthy)[0]

print(f"H_Result: {p_h}")
print(f"U_Result: {p_u}")
