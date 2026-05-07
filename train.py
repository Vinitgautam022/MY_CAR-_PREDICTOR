"""
Advanced Car Price Predictor - Model Training Script
Trains multiple algorithms with FIXED feature engineering
"""

import pandas as pd
import numpy as np
import pickle
import json
from sklearn.model_selection import train_test_split, cross_val_score, KFold
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor, AdaBoostRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score, mean_absolute_percentage_error
import warnings
warnings.filterwarnings('ignore')

# ============================================
# 1. LOAD & PREPARE DATA
# ============================================
print("🔄 Loading data...")
df = pd.read_csv('Cleaned_Car_data.csv')

# Drop unnecessary columns
cols_to_drop = []
for col in ['Unnamed: 0.2', 'Unnamed: 0.1', 'Unnamed: 0']:
    if col in df.columns:
        cols_to_drop.append(col)
if cols_to_drop:
    df = df.drop(cols_to_drop, axis=1)

print(f"✅ Dataset shape: {df.shape}")
print(f"Columns: {df.columns.tolist()}")

# ============================================
# 2. DATA CLEANING
# ============================================
print("\n🧹 Data Cleaning...")

# Remove outliers - reasonable car price range
df = df[(df['Price'] >= 100000) & (df['Price'] <= 10000000)].copy()

# Handle kms_driven - remove unrealistic values
df = df[df['kms_driven'] >= 0].copy()
df = df[df['kms_driven'] <= 2500000].copy()  # Max 2.5M km

print(f"✅ Dataset after cleaning: {df.shape}")

# ============================================
# 3. FEATURE ENGINEERING (NO CIRCULAR FEATURES!)
# ============================================
print("\n🔨 Feature Engineering...")

df['car_age'] = 2026 - df['year']
df['log_kms'] = np.log1p(df['kms_driven'])  # Log transform for skewed data
df['log_price'] = np.log1p(df['Price'])

print(f"✅ Features created successfully")

# ============================================
# 4. CATEGORICAL ENCODING
# ============================================
print("\n🔀 Encoding categorical features...")

encoders = {}

# Encode company
le_company = LabelEncoder()
company_encoded = le_company.fit_transform(df['company'])
encoders['company'] = le_company

# Encode fuel type
le_fuel = LabelEncoder()
fuel_encoded = le_fuel.fit_transform(df['fuel_type'])
encoders['fuel_type'] = le_fuel

# Encode car name/model
le_name = LabelEncoder()
name_encoded = le_name.fit_transform(df['name'])
encoders['name'] = le_name

# Save encoders
with open('encoders.pkl', 'wb') as f:
    pickle.dump(encoders, f)

print("✅ Encoders saved")

# ============================================
# 5. PREPARE FEATURES FOR TRAINING
# ============================================
print("\n📊 Preparing training features...")

# Use only these features (NO price_per_km which is circular!)
X = pd.DataFrame({
    'name': name_encoded,
    'company': company_encoded,
    'year': df['year'].values,
    'kms_driven': df['kms_driven'].values,
    'fuel_type': fuel_encoded,
    'car_age': df['car_age'].values,
    'log_kms': df['log_kms'].values
})

y = df['Price'].values

print(f"Feature shape: {X.shape}")
print(f"Features: {X.columns.tolist()}")

# ============================================
# 6. SCALE FEATURES
# ============================================
print("\n📈 Scaling features...")

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

with open('scaler.pkl', 'wb') as f:
    pickle.dump(scaler, f)

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(
    X_scaled, y, test_size=0.2, random_state=42
)

print(f"✅ Training set: {X_train.shape}")
print(f"✅ Test set: {X_test.shape}")

# ============================================
# 7. TRAIN MODELS
# ============================================
print("\n" + "="*60)
print("🚀 TRAINING MODELS")
print("="*60)

models = {
    'Gradient Boosting': GradientBoostingRegressor(
        n_estimators=300, 
        learning_rate=0.05, 
        max_depth=6, 
        subsample=0.8,
        random_state=42
    ),
    'Random Forest': RandomForestRegressor(
        n_estimators=300, 
        max_depth=15, 
        random_state=42, 
        n_jobs=-1
    ),
    'AdaBoost': AdaBoostRegressor(
        n_estimators=200,
        learning_rate=0.05,
        random_state=42
    ),
}

results = {}
kfold = KFold(n_splits=5, shuffle=True, random_state=42)

for model_name, model in models.items():
    print(f"\n📊 Training {model_name}...")
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    
    mae = mean_absolute_error(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    r2 = r2_score(y_test, y_pred)
    mape = mean_absolute_percentage_error(y_test, y_pred)
    cv_score = cross_val_score(model, X_train, y_train, cv=kfold, scoring='r2').mean()
    
    results[model_name] = {
        'MAE': round(mae, 2),
        'RMSE': round(rmse, 2),
        'R2': round(r2, 4),
        'MAPE': round(mape, 4),
        'CV': round(cv_score, 4),
        'model': model
    }
    
    print(f"   MAE: ₹{mae:,.0f} | MAPE: {mape:.2%} | R²: {r2:.4f} | CV: {cv_score:.4f}")

# ============================================
# 8. SELECT BEST MODEL (by MAE - most important for price prediction)
# ============================================
print("\n" + "="*60)
print("📈 BEST MODEL SELECTED")
print("="*60)

# Select by lowest MAE (most important metric for price prediction accuracy)
best_name = min(results.keys(), key=lambda x: results[x]['MAE'])
best_model = results[best_name]['model']

print(f"\n🏆 {best_name} (Selected by lowest MAE)")
print(f"   MAE: ₹{results[best_name]['MAE']:,.0f}")
print(f"   MAPE: {results[best_name]['MAPE']:.2%}")
print(f"   R² Score: {results[best_name]['R2']}")
print(f"   CV Score: {results[best_name]['CV']:.4f}")

# Save metrics
with open('model_metrics.json', 'w') as f:
    metrics = {k: {
        'MAE': v['MAE'],
        'RMSE': v['RMSE'],
        'R2': v['R2'],
        'MAPE': v['MAPE'],
        'CV': v['CV']
    } for k, v in results.items()}
    json.dump(metrics, f, indent=2)

print("\n" + "="*60)
print("💾 SAVING MODELS")
print("="*60)

# Save model
with open('LinearRegressionModel.pkl', 'wb') as f:
    pickle.dump(best_model, f)

with open('BestRegressionModel.pkl', 'wb') as f:
    pickle.dump(best_model, f)

print("✅ Best model saved as 'LinearRegressionModel.pkl'")
print("="*60)
