# core/crop_model.py
import pandas as pd
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier # More robust than Decision Tree
import joblib
import random
import os

# --- Configuration ---
DATA_FILE = os.path.join(os.path.dirname(__file__), 'data', 'Crop_recommendation.csv')
MODEL_FILE = os.path.join(os.path.dirname(__file__), 'data', 'crop_predictor_model.pkl')
LABEL_ENCODER_FILE = os.path.join(os.path.dirname(__file__), 'data', 'crop_label_encoder.pkl')
FEATURES = ['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']
CROP_PREDICTOR_MODEL = None
CROP_LABEL_ENCODER = None
ALL_CROPS = []

# --- Functions ---

def load_and_train_model():
    """Loads data, trains a model, and saves it, or loads the saved model."""
    global CROP_PREDICTOR_MODEL, CROP_LABEL_ENCODER, ALL_CROPS
    
    if os.path.exists(MODEL_FILE) and os.path.exists(LABEL_ENCODER_FILE):
        print("✅ Crop Model: Loading pre-trained model and encoder.")
        CROP_PREDICTOR_MODEL = joblib.load(MODEL_FILE)
        CROP_LABEL_ENCODER = joblib.load(LABEL_ENCODER_FILE)
        ALL_CROPS = list(CROP_LABEL_ENCODER.classes_)
        return

    # 1. Load Data
    if not os.path.exists(DATA_FILE):
        print(f"🔴 Crop Model: Error! Data file not found at {DATA_FILE}")
        return
        
    df = pd.read_csv(DATA_FILE)

    # 2. Prepare Data and Encoder
    # Use LabelEncoder to convert crop names to numeric IDs
    CROP_LABEL_ENCODER = LabelEncoder()
    df['label_id'] = CROP_LABEL_ENCODER.fit_transform(df['label'])
    ALL_CROPS = list(CROP_LABEL_ENCODER.classes_)

    X = df[FEATURES]
    y = df['label_id']

    # 3. Train Model (Random Forest is better for classification)
    print("✅ Crop Model: Training new Random Forest Classifier for suitability.")
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X, y)
    CROP_PREDICTOR_MODEL = model
    
    # 4. Save Model and Encoder
    joblib.dump(CROP_PREDICTOR_MODEL, MODEL_FILE)
    joblib.dump(CROP_LABEL_ENCODER, LABEL_ENCODER_FILE)


def get_soil_data_by_location(location):
    """Mocks/Estimates all required features based on location."""
    # (This function remains a robust mock for NPK, pH, and Rainfall)
    return {
        'N': random.randint(50, 100), 
        'P': random.randint(30, 60), 
        'K': random.randint(20, 50),
        'temperature': random.uniform(20, 35), # Real-time from OWM
        'humidity': random.uniform(50, 90),     # Real-time from OWM
        'ph': random.uniform(5.5, 7.5),
        'rainfall': random.uniform(100, 200)   # Estimated Annual Rainfall
    }


def predict_suitable_crops(input_data):
    """Predicts suitability scores for all crops and returns the top 5."""
    if not CROP_PREDICTOR_MODEL:
        return []
        
    try:
        input_df = pd.DataFrame([input_data], columns=FEATURES)
        
        # Use predict_proba to get the likelihood for every single crop type
        probabilities = CROP_PREDICTOR_MODEL.predict_proba(input_df)[0]
        
        # Create a list of (crop_name, probability) tuples
        suitability_scores = []
        for i, prob in enumerate(probabilities):
            # Only include crops with a reasonable chance (e.g., > 10%)
            if prob > 0.05: # Changed threshold to 5% to include more options
                crop_name = CROP_LABEL_ENCODER.inverse_transform([CROP_PREDICTOR_MODEL.classes_[i]])[0]
                suitability_scores.append((crop_name, prob))
        
        # Sort by probability (descending) and return the top 8
        suitability_scores.sort(key=lambda item: item[1], reverse=True)
        
        # Return a list of only the top 8 crop names
        return [item[0] for item in suitability_scores[:8]]
        
    except Exception as e:
        print(f"🔴 Prediction Error: {e}")
        return ["Prediction Failed"]

# Execute the model loading when the module is imported
load_and_train_model()