import os
import numpy as np
import cv2
from django.conf import settings
from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
from django.http import JsonResponse
from tensorflow.keras.models import load_model



# Load the model
model = load_model('media/models/braintumor.h5')
labels = ['glioma_tumor', 'meningioma_tumor', 'no_tumor', 'pituitary_tumor']

def braintumor(request):
    if request.method == 'POST' and request.FILES['image']:
        # Get the uploaded file
        image_file = request.FILES['image']
        fs = FileSystemStorage()
        filename = fs.save(image_file.name, image_file)
        file_url = fs.url(filename)

        # Preprocess the image
        img = cv2.imread(f'.{file_url}')
        img = cv2.resize(img, (150, 150))
        img_array = np.expand_dims(img, axis=0)

        # Make prediction
        prediction = model.predict(img_array)
        predicted_label = labels[np.argmax(prediction)]

        return render(request, 'result.html', {'prediction': predicted_label, 'file_url': file_url})

    return render(request, 'braintumor.html')

