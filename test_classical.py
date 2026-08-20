import joblib
import pandas as pd
from quallki_agentic.feature_schema import FEATURE_NAMES

try:
    model = joblib.load("best_regularized_model.joblib")
    print("Model loaded type:", type(model))
    
    # Try a dummy prediction
    df = pd.read_csv("MasterDatasetProcessed_Clean.csv", nrows=1)
    values = df[list(FEATURE_NAMES)].values
    # In lightgbm, you can just do model.predict
    pred = model.predict(values)
    print("Prediction:", pred)
except Exception as e:
    print("Error:", e)
