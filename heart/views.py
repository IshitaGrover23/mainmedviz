from django.shortcuts import render
from .model import predict_heart_disease  

def heart_view(request):
    if request.method == 'POST':
        input_data = [
            request.POST['age'],
            request.POST['sex'],
            request.POST['cp'],
            request.POST['trestbps'],
            request.POST['chol'],
            request.POST['fbs'],
            request.POST['restecg'],
            request.POST['thalach'],
            request.POST['exang'],
            request.POST['oldpeak'],
            request.POST['slope'],
            request.POST['ca'],
            request.POST['thal'],
        ]
        input_data = list(map(float, input_data))
        prediction = predict_heart_disease(input_data)
        result = 'The Person has Heart Disease' if prediction == 1 else 'The Person does not have Heart Disease'
        return render(request, 'heart/result.html', {'result': result})

    return render(request, 'heart/index.html')