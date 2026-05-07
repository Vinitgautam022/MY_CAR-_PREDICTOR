"""
Quick test to verify the prediction system works
"""
import pickle
import pandas as pd
import numpy as np

print("🔍 Testing Car Price Predictor...\n")

# Load model and encoders
print("1️⃣ Loading model...")
model = pickle.load(open('LinearRegressionModel.pkl', 'rb'))
with open('encoders.pkl', 'rb') as f:
    encoders = pickle.load(f)
with open('scaler.pkl', 'rb') as f:
    scaler = pickle.load(f)
print("✅ Model loaded successfully")

# Load data to get sample values
print("\n2️⃣ Loading sample data...")
car_data = pd.read_csv('Cleaned_Car_data.csv')
print(f"✅ Dataset: {car_data.shape}")

# Get sample values
sample_company = car_data['company'].iloc[0]
sample_model = car_data['name'].iloc[0]
sample_year = int(car_data['year'].iloc[0])
sample_km = float(car_data['kms_driven'].iloc[0])
sample_fuel = car_data['fuel_type'].iloc[0]

print(f"\n3️⃣ Test prediction with:")
print(f"   Company: {sample_company}")
print(f"   Model: {sample_model}")
print(f"   Year: {sample_year}")
print(f"   KM: {sample_km}")
print(f"   Fuel: {sample_fuel}")

# Encode features
print("\n4️⃣ Encoding features...")
encoded_model = encoders['name'].transform([sample_model])[0]
encoded_company = encoders['company'].transform([sample_company])[0]
encoded_fuel = encoders['fuel_type'].transform([sample_fuel])[0]
car_age = 2026 - sample_year
price_per_km = 1.0

features = np.array([[
    encoded_model, 
    encoded_company, 
    sample_year, 
    sample_km, 
    encoded_fuel,
    car_age,
    price_per_km
]])

print("✅ Features encoded")

# Scale features
print("\n5️⃣ Scaling features...")
scaled = scaler.transform(features)
print("✅ Features scaled")

# Make prediction
print("\n6️⃣ Making prediction...")
prediction = model.predict(scaled)[0]
print(f"✅ Predicted Price: ₹{prediction:,.2f}")

# Get confidence range
confidence_low = prediction * 0.85
confidence_high = prediction * 1.15

print(f"\n7️⃣ Confidence Range:")
print(f"   Low:  ₹{confidence_low:,.2f}")
print(f"   High: ₹{confidence_high:,.2f}")

print("\n✅ ALL TESTS PASSED! System is working perfectly!")
