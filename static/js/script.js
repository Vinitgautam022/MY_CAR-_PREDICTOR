// ===========================
// ADVANCED CAR PREDICTOR APP
// ===========================

// Load car models when company is selected
function load_car_models() {
    const company = document.getElementById('company').value;
    const carModelSelect = document.getElementById('car_models');
    
    if (company === 'Select Company' || company === '') {
        carModelSelect.innerHTML = '<option value="">Select a model first</option>';
        return;
    }
    
    // Fetch models for selected company
    fetch('/api/models-by-company', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ company: company })
    })
    .then(response => response.json())
    .then(data => {
        if (data.models) {
            carModelSelect.innerHTML = '<option value="">Select Model</option>';
            data.models.forEach(model => {
                const option = document.createElement('option');
                option.value = model;
                option.textContent = model;
                carModelSelect.appendChild(option);
            });
        }
    })
    .catch(error => console.error('Error:', error));
}

// Clear error messages
function clearErrors() {
    document.getElementById('error-company').textContent = '';
    document.getElementById('error-model').textContent = '';
    document.getElementById('error-year').textContent = '';
    document.getElementById('error-fuel').textContent = '';
    document.getElementById('error-km').textContent = '';
    document.getElementById('alert-container').innerHTML = '';
}

// Show alert message
function showAlert(message, type = 'danger') {
    const alertContainer = document.getElementById('alert-container');
    const alertHtml = `
        <div class="alert alert-${type} alert-dismissible fade show" role="alert">
            <i class="fas fa-exclamation-circle"></i> ${message}
            <button type="button" class="close" data-dismiss="alert" aria-label="Close">
                <span aria-hidden="true">&times;</span>
            </button>
        </div>
    `;
    alertContainer.innerHTML = alertHtml;
}

// Validate inputs
function validateInputs() {
    clearErrors();
    let isValid = true;

    const company = document.getElementById('company').value;
    const carModel = document.getElementById('car_models').value;
    const year = document.getElementById('year').value;
    const fuelType = document.getElementById('fuel_type').value;
    const kmDriven = document.getElementById('kilo_driven').value;

    if (!company || company === 'Select Company') {
        document.getElementById('error-company').textContent = 'Please select a company';
        isValid = false;
    }

    if (!carModel) {
        document.getElementById('error-model').textContent = 'Please select a model';
        isValid = false;
    }

    if (!year) {
        document.getElementById('error-year').textContent = 'Please select year';
        isValid = false;
    }

    if (!fuelType) {
        document.getElementById('error-fuel').textContent = 'Please select fuel type';
        isValid = false;
    }

    if (!kmDriven || parseFloat(kmDriven) < 0) {
        document.getElementById('error-km').textContent = 'Please enter valid kilometers';
        isValid = false;
    }

    return isValid;
}

// Main prediction function
function send_data() {
    if (!validateInputs()) {
        return;
    }

    const fd = new FormData(document.getElementById('predictionForm'));
    const resultContainer = document.getElementById('result-container');
    const loader = document.getElementById('loader');
    const priceDisplay = document.getElementById('price-display');

    // Show loading state
    resultContainer.style.display = 'block';
    loader.style.display = 'block';
    priceDisplay.style.display = 'none';

    // Send prediction request
    const xhr = new XMLHttpRequest();
    xhr.open('POST', '/predict', true);
    xhr.onreadystatechange = function () {
        if (xhr.readyState === XMLHttpRequest.DONE) {
            loader.style.display = 'none';
            
            if (xhr.status === 200) {
                try {
                    const response = JSON.parse(xhr.responseText);
                    if (response.success) {
                        displayPredictionResult(response);
                        priceDisplay.style.display = 'block';
                    } else {
                        showAlert('Prediction failed: ' + (response.error || 'Unknown error'), 'danger');
                    }
                } catch (e) {
                    showAlert('Error parsing response', 'danger');
                }
            } else {
                try {
                    const errorResponse = JSON.parse(xhr.responseText);
                    if (errorResponse.errors) {
                        showAlert('Validation Error: ' + errorResponse.errors.join(', '), 'danger');
                    } else {
                        showAlert(errorResponse.error || 'Prediction failed', 'danger');
                    }
                } catch (e) {
                    showAlert('Server error: ' + xhr.status, 'danger');
                }
            }
        }
    };
    xhr.onerror = function() {
        loader.style.display = 'none';
        showAlert('Network error. Please try again.', 'danger');
    };
    xhr.send(fd);
}

// Display prediction result
function displayPredictionResult(data) {
    // Animate AI predicted price
    const prediction = data.predicted_price;
    animatePrice(prediction);

    // Animate showroom price
    const showroomPrice = data.showroom_price;
    animateShowroomPrice(showroomPrice);

    // Update confidence range
    document.getElementById('confidence-low').textContent = 
        '₹' + formatCurrency(data.confidence_low);
    document.getElementById('confidence-high').textContent = 
        '₹' + formatCurrency(data.confidence_high);

    // Update accuracy
    const accuracy = Math.round(data.model_accuracy * 100);
    document.getElementById('accuracy-text').textContent = accuracy + '% Accurate';
    document.getElementById('accuracy-bar').style.width = accuracy + '%';

    // Display similar cars
    if (data.similar_cars && data.similar_cars.length > 0) {
        displaySimilarCars(data.similar_cars);
    }
}

// Display similar cars
function displaySimilarCars(cars) {
    const similarCarsBox = document.getElementById('similar-cars-box');
    const similarCarsList = document.getElementById('similar-cars-list');
    
    if (cars.length === 0) {
        similarCarsBox.style.display = 'none';
        return;
    }

    let html = '';
    cars.forEach(car => {
        html += `
            <div class="car-item">
                <div class="car-name"><i class="fas fa-car-side"></i> ${car.name}</div>
                <div class="car-details">
                    <span>Year: ${car.year}</span> | 
                    <span>Price: ₹${formatCurrency(car.Price)}</span> | 
                    <span>KM: ${formatCurrency(car.kms_driven)}</span>
                </div>
            </div>
        `;
    });

    similarCarsList.innerHTML = html;
    similarCarsBox.style.display = 'block';
}

// Animate price counter
function animatePrice(finalValue) {
    const predictionElement = document.getElementById('prediction');
    let current = 0;
    const increment = finalValue / 100;
    const interval = setInterval(() => {
        current += increment;
        if (current >= finalValue) {
            clearInterval(interval);
            predictionElement.textContent = '₹' + formatCurrency(finalValue);
        } else {
            predictionElement.textContent = '₹' + formatCurrency(current);
        }
    }, 15);
}

// Animate showroom price counter
function animateShowroomPrice(finalValue) {
    const showroomElement = document.getElementById('showroom-price');
    let current = 0;
    const increment = finalValue / 100;
    const interval = setInterval(() => {
        current += increment;
        if (current >= finalValue) {
            clearInterval(interval);
            showroomElement.textContent = '₹' + formatCurrency(finalValue);
        } else {
            showroomElement.textContent = '₹' + formatCurrency(current);
        }
    }, 15);
}

// Format number as currency
function formatCurrency(value) {
    return Math.round(value).toLocaleString('en-IN');
}

// Load statistics on page load
document.addEventListener('DOMContentLoaded', function() {
    // Load dataset stats
    fetch('/api/stats')
        .then(response => response.json())
        .then(data => {
            document.getElementById('stat-total').textContent = data.total_cars;
            document.getElementById('stat-companies').textContent = data.companies;
            document.getElementById('stat-cars').textContent = data.total_cars;
            document.getElementById('stat-avg').textContent = '₹' + formatCurrency(data.avg_price);
            document.getElementById('stat-accuracy').textContent = '85%';
        })
        .catch(error => console.error('Error loading stats:', error));
});

// Prevent form submission on Enter
document.getElementById('predictionForm').addEventListener('keypress', function(e) {
    if (e.key === 'Enter') {
        e.preventDefault();
        send_data();
    }
});
