
# 🚗 Car Price Predictor – ML Web App

This project is a **Machine Learning-powered web application** that predicts the price of a car based on input features like company, model, year, fuel type, kilometers driven, etc. It is built using `scikit-learn`, `Flask`, and `HTML`.

## 📸 Demo

> 👉 [Live Demo Link](https://your-deployment-url.com) *(Replace with your actual link after deployment)*

## 📁 Project Structure

```
car-price-predictor/
│
├── app.py                 # Flask backend server
├── car_price_model.pkl    # Trained ML model
├── Cleaned_Car_data.csv   # Dataset used for training
├── requirements.txt       # All Python dependencies
├── Procfile               # For deployment (Render/Heroku)
│
├── templates/
│   └── index.html         # Frontend page (form to get inputs)
│
└── static/                # Optional folder for CSS/JS/images
```

## ⚙️ Technologies Used

- Python
- Pandas / NumPy
- Scikit-learn
- Flask
- HTML/CSS (Jinja2 for templating)
- Render (for deployment)

## 🔮 How It Works

1. User selects:
   - Company, car model, fuel type, year, kilometers driven
2. Data is passed to a trained regression model
3. Model returns the predicted price
4. Output is displayed on the web page

## 🚀 How to Run Locally

1. **Clone the repo**
   ```bash
   git clone https://github.com/your_username/car-price-predictor.git
   cd car-price-predictor
   ```

2. **Create virtual environment (optional)**
   ```bash
   python -m venv venv
   source venv/bin/activate  # for Linux/Mac
   venv\Scripts\activate     # for Windows
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the Flask app**
   ```bash
   python app.py
   ```


   ```

## 🌐 Deploy to Render (Free Hosting)

1. Push your code to GitHub
2. Go to [https://render.com](https://render.com)
3. Connect your repo
4. Add:
   - **Start Command**: `gunicorn app:app`
   - **Build Command**: leave blank
5. Deploy & get your public URL

## 📌 Sample Screenshot

> *(You can add a screenshot of your running app here)*

## 🧠 ML Model Details

- Algorithm: Linear Regression
- Target: Car Selling Price
- Features: Year, Fuel Type, Company, Model, KMs Driven

## 📜 License

This project is for educational use only.
