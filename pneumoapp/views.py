import os
import numpy as np
from django.shortcuts import render, redirect
from .models import ChestXRay
from .forms import ChestXRayForm
from tensorflow.keras.models import model_from_json
from tensorflow.keras.preprocessing.image import load_img, img_to_array
import tempfile
import logging
import json
from django.conf import settings

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Construct the full path using BASE_DIR
config_path = os.path.join(settings.BASE_DIR, 'config.json')
weights_path = os.path.join(settings.BASE_DIR, 'model.weights.h5')

# Load the model once when the server starts
model = None
try:
    # Load the model architecture from config.json
    with open('config.json', 'r') as config_file:
        model_config = json.load(config_file)
        model = model_from_json(json.dumps(model_config))
        logger.info("Model architecture loaded successfully")
    
    # Load the model weights from model.weights.h5
    model.load_weights('model.weights.h5')
    logger.info("Model weights loaded successfully")
    
    # Optionally, compile the model if needed
    model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
    logger.info("Model compiled successfully")

except Exception as e:
    logger.error(f"Error loading model: {e}")

# Preprocess the uploaded image for prediction
def preprocess_image(image_file):
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as temp_file:
            temp_file.write(image_file.read())
            temp_file_path = temp_file.name

        logger.debug(f"Temporary file created: {temp_file_path}")
        
        # Resize image to 224x224 to match the model's input size
        img = load_img(temp_file_path, target_size=(224, 224))  # Change to (224, 224)
        img_array = img_to_array(img)
        img_array = np.expand_dims(img_array, axis=0)
        img_array = img_array / 255.0  # Normalize the image

        logger.debug(f"Image preprocessed successfully. Shape: {img_array.shape}")
        return img_array

    except Exception as e:
        logger.error(f"Error preprocessing image: {e}")
        raise

    finally:
        if 'temp_file_path' in locals():
            os.unlink(temp_file_path)
            logger.debug(f"Temporary file deleted: {temp_file_path}")

# View to handle image uploads and make predictions
def index(request):
    global model
    if request.method == 'POST':
        form = ChestXRayForm(request.POST, request.FILES)
        
        # Validate the form
        if form.is_valid():
            logger.debug("Form is valid")
            xray = form.save(commit=False)  
            
            # Check if the image file is present in request.FILES
            if 'image' not in request.FILES:
                logger.warning("No image file provided")
                xray.result = "No image file provided. Unable to predict."
                xray.save()
                return redirect('result', xray_id=xray.id)

            # Ensure a model is loaded and an image is provided
            if model is not None and 'image' in request.FILES:
                logger.debug(f"Image received: {request.FILES['image'].name}")
                try:
                    # Preprocess the image
                    img_array = preprocess_image(request.FILES['image'])
                    
                    # Make the prediction
                    prediction = model.predict(img_array)
                    probability = prediction[0][0]  # Assuming a binary classification
                    result = "PNEUMONIA" if probability > 0.5 else "NORMAL"
                    
                    logger.info(f"Prediction: {result}, Probability: {probability}")
                    
                    # Store the result and probability
                    xray.result = result
                    xray.probability = float(probability)
                
                except Exception as e:
                    logger.error(f"Error during prediction: {e}")
                    xray.result = f"Error during prediction: {str(e)}"
                    xray.probability = None
            else:
                logger.warning("Model not loaded or no image provided")
                xray.result = "Model not loaded or no image provided. Unable to predict."
                xray.probability = None
            
            # Save the ChestXRay instance with the prediction result
            xray.save()
            
            # Redirect to the result view to display the prediction
            return redirect('result', xray_id=xray.id)
        else:
            logger.warning("Form is not valid")
    else:
        form = ChestXRayForm()
    
    # Render the index.html template with the form
    return render(request, 'pneumoapp/index.html', {'form': form})

# View to display the prediction result
def result(request, xray_id):
    try:
        xray = ChestXRay.objects.get(id=xray_id)  # Fetch the ChestXRay instance by id
    except ChestXRay.DoesNotExist:
        logger.warning(f"X-ray with id {xray_id} not found")
        return render(request, 'pneumoapp/error.html', {'message': 'X-ray not found'})
    
    # Render the result.html template with the X-ray object
    return render(request, 'pneumoapp/result.html', {'xray': xray})
