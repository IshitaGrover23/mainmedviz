import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn import svm
from django.shortcuts import render
from .forms import PredictionForm
from .models import Prediction

# Initialize model and scaler once
scaler = None
classifier = None

def initialize_model():
    global scaler, classifier
    diabetes_dataset = pd.read_csv('diabetes.csv')  # Update with correct path
    X = diabetes_dataset.drop(columns='Outcome', axis=1)
    Y = diabetes_dataset['Outcome']
    
    scaler = StandardScaler()
    scaler.fit(X)
    
    classifier = svm.SVC(kernel='linear')
    classifier.fit(scaler.transform(X), Y)

# Initialize model and scaler
initialize_model()

def predict_diabetes(request):
    result = None
    if request.method == 'POST':
        form = PredictionForm(request.POST)
        if form.is_valid():
            data = [
                form.cleaned_data['pregnancies'],
                form.cleaned_data['glucose'],
                form.cleaned_data['blood_pressure'],
                form.cleaned_data['skin_thickness'],
                form.cleaned_data['insulin'],
                form.cleaned_data['bmi'],
                form.cleaned_data['diabetes_pedigree_function'],
                form.cleaned_data['age']
            ]
            input_data_as_numpy_array = np.asarray(data).reshape(1, -1)
            std_data = scaler.transform(input_data_as_numpy_array)
            prediction = classifier.predict(std_data)
            result = 'Diabetic' if prediction[0] == 1 else 'Not Diabetic'

            # Save the prediction
            Prediction.objects.create(
                input_data=data,
                result=result
            )
            return render(request, 'diabetes/predict.html', {'form': form, 'result': result})
    else:
        form = PredictionForm()
    return render(request, 'diabetes/predict.html', {'form': form, 'result': result})
    