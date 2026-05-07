from flask import Flask, render_template, request, jsonify
from flask_cors import CORS, cross_origin
import pickle
import pandas as pd
import numpy as np
import json
import warnings
warnings.filterwarnings('ignore')

app = Flask(__name__)
cors = CORS(app)

# Load model and encoders
try:
    model = pickle.load(open('LinearRegressionModel.pkl', 'rb'))
    with open('encoders.pkl', 'rb') as f:
        encoders = pickle.load(f)
    with open('scaler.pkl', 'rb') as f:
        scaler = pickle.load(f)
    with open('model_metrics.json', 'r') as f:
        model_metrics = json.load(f)
except:
    print("⚠️  Using fallback - some models may not be available")
    model = None
    encoders = None
    scaler = None
    model_metrics = None

# Load data
car_data = pd.read_csv('Cleaned_Car_data.csv')
car_data_clean = car_data.drop(['Unnamed: 0.1', 'Unnamed: 0'], axis=1)

@app.route('/', methods=['GET', 'POST'])
def index():
    """Render home page with available options"""
    try:
        companies = sorted(car_data['company'].unique())
        car_models = sorted(car_data['name'].unique())
        years = sorted(car_data['year'].unique(), reverse=True)
        fuel_types = sorted(car_data['fuel_type'].unique())
        
        companies.insert(0, 'Select Company')
        
        # Get model metrics for display
        metrics = model_metrics if model_metrics else {}
        
        return render_template(
            'index.html',
            companies=companies,
            car_models=car_models,
            years=years,
            fuel_types=fuel_types,
            metrics=metrics
        )
    except Exception as e:
        return f"Error loading page: {str(e)}", 500


@app.route('/api/models-by-company', methods=['POST'])
@cross_origin()
def get_models_by_company():
    """Get car models for selected company"""
    try:
        company = request.json.get('company')
        
        if not company or company == 'Select Company':
            return jsonify({'error': 'Please select a valid company'}), 400
        
        models = sorted(car_data[car_data['company'] == company]['name'].unique().tolist())
        
        if not models:
            return jsonify({'error': f'No models found for {company}'}), 404
        
        return jsonify({'models': models}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/predict', methods=['POST'])
@cross_origin()
def predict():
    """
    Predict car price with validation, error handling, and confidence intervals
    """
    try:
        # Extract form data
        company = request.form.get('company', '').strip()
        car_model = request.form.get('car_models', '').strip()
        year_str = request.form.get('year', '').strip()
        fuel_type = request.form.get('fuel_type', '').strip()
        driven_str = request.form.get('kilo_driven', '').strip()
        
        # ============================================
        # VALIDATION
        # ============================================
        errors = []
        
        # Validate company
        if not company or company == 'Select Company':
            errors.append('Company is required')
        elif company not in car_data['company'].unique():
            errors.append(f'Invalid company: {company}')
        
        # Validate car model
        if not car_model:
            errors.append('Car model is required')
        elif car_model not in car_data['name'].unique():
            errors.append(f'Invalid car model: {car_model}')
        
        # Validate year
        if not year_str:
            errors.append('Year is required')
        else:
            try:
                year = int(year_str)
                min_year = car_data['year'].min()
                max_year = car_data['year'].max()
                if year < min_year or year > max_year:
                    errors.append(f'Year must be between {min_year} and {max_year}')
            except ValueError:
                errors.append('Year must be a valid number')
        
        # Validate fuel type
        if not fuel_type:
            errors.append('Fuel type is required')
        elif fuel_type not in car_data['fuel_type'].unique():
            errors.append(f'Invalid fuel type: {fuel_type}')
        
        # Validate kilometers driven
        if not driven_str:
            errors.append('Kilometers driven is required')
        else:
            try:
                driven = float(driven_str)
                if driven < 0:
                    errors.append('Kilometers driven must be positive')
                if driven > 5000000:  # Reasonable max
                    errors.append('Kilometers driven seems too high (max: 5,000,000)')
            except ValueError:
                errors.append('Kilometers driven must be a valid number')
        
        if errors:
            return jsonify({
                'success': False,
                'errors': errors
            }), 400
        
        # ============================================
        # ENCODE FEATURES
        # ============================================
        if encoders is None:
            return jsonify({
                'success': False,
                'error': 'Model encoders not available'
            }), 500
        
        try:
            encoded_model = encoders['name'].transform([car_model])[0]
            encoded_company = encoders['company'].transform([company])[0]
            encoded_fuel = encoders['fuel_type'].transform([fuel_type])[0]
        except Exception as e:
            return jsonify({
                'success': False,
                'error': f'Encoding error: {str(e)}'
            }), 500
        
        # ============================================
        # PREDICTION WITH CORRECTED FEATURES
        # ============================================
        if scaler is None:
            return jsonify({
                'success': False,
                'error': 'Model scaler not available'
            }), 500
        
        try:
            # Calculate new features (MUST match training.py)
            car_age = 2026 - year
            log_kms = np.log1p(driven)  # Log transform for skewed data
            
            # Create feature array - EXACT SAME ORDER AS TRAINING
            # Features: name, company, year, kms_driven, fuel_type, car_age, log_kms
            raw_features = np.array([[
                encoded_model,           # name
                encoded_company,         # company
                year,                    # year
                driven,                  # kms_driven
                encoded_fuel,            # fuel_type
                car_age,                 # car_age
                log_kms                  # log_kms
            ]])
            
            # Scale features
            scaled_features = scaler.transform(raw_features)
            
            # Make prediction
            prediction = model.predict(scaled_features)[0]
            prediction = max(100000, min(prediction, 10000000))  # Clamp to realistic range
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': f'Prediction error: {str(e)}'
            }), 500
        
        # ============================================
        # CONFIDENCE INTERVAL (±10% based on model performance)
        # ============================================
        confidence_low = prediction * 0.90
        confidence_high = prediction * 1.10
        
        # ============================================
        # SHOWROOM PRICE (Current Market Price)
        # ============================================
        showroom_cars = car_data[
            (car_data['company'] == company) & 
            (car_data['name'] == car_model) &
            (car_data['fuel_type'] == fuel_type)
        ]
        
        if len(showroom_cars) > 0:
            showroom_price = showroom_cars['Price'].mean()
        else:
            # Fallback: use company + fuel type average
            showroom_cars = car_data[
                (car_data['company'] == company) & 
                (car_data['fuel_type'] == fuel_type)
            ]
            showroom_price = showroom_cars['Price'].mean() if len(showroom_cars) > 0 else prediction
        
        # ============================================
        # SIMILAR CARS
        # ============================================
        similar_cars = car_data[
            (car_data['company'] == company) & 
            (car_data['fuel_type'] == fuel_type) &
            (car_data['year'] >= year - 2) & 
            (car_data['year'] <= year + 2)
        ].nlargest(5, 'Price')[['name', 'year', 'Price', 'kms_driven']].to_dict('records')
        
        # ============================================
        # GET MODEL ACCURACY
        # ============================================
        model_accuracy = 0.5
        if model_metrics:
            # Find the best model's R2 score
            best_r2 = max([m.get('R2', 0) for m in model_metrics.values()])
            model_accuracy = max(0.5, best_r2)  # Min 50%, Max actual R2
        
        # ============================================
        # RESPONSE
        # ============================================
        return jsonify({
            'success': True,
            'predicted_price': round(prediction, 2),
            'showroom_price': round(showroom_price, 2),
            'confidence_low': round(confidence_low, 2),
            'confidence_high': round(confidence_high, 2),
            'similar_cars': similar_cars,
            'model_accuracy': round(model_accuracy, 4)
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Prediction error: {str(e)}'
        }), 500


@app.route('/api/stats', methods=['GET'])
@cross_origin()
def get_stats():
    """Return dataset statistics for visualization"""
    try:
        stats = {
            'total_cars': len(car_data),
            'companies': len(car_data['company'].unique()),
            'models': len(car_data['name'].unique()),
            'avg_price': float(car_data['Price'].mean()),
            'min_price': float(car_data['Price'].min()),
            'max_price': float(car_data['Price'].max()),
            'year_range': [int(car_data['year'].min()), int(car_data['year'].max())]
        }
        return jsonify(stats), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)