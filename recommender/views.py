from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import logging
import speech_recognition as sr

logger = logging.getLogger(__name__)

symptom_prediction_mapping = {
    "headache": {
        "disease": "Tension Headache",
        "description": "A common type of headache that feels like a constant ache or pressure around the head, particularly at the temples or back of the head and neck.",
        "precaution": "Rest, stay hydrated, and practice stress-reduction techniques.",
        "medications": "Over-the-counter pain relievers like acetaminophen or ibuprofen.",
        "workouts": "Light stretching, yoga, or walking may help relieve tension.",
        "diets": "Stay hydrated and avoid known trigger foods like caffeine or alcohol."
    },
    "migraine": {
        "disease": "Migraine",
        "description": "A neurological condition characterized by intense, debilitating headaches often accompanied by nausea, vomiting, and sensitivity to light and sound.",
        "precaution": "Identify and avoid triggers, maintain a regular sleep schedule, and manage stress.",
        "medications": "Triptans, ergotamines, or preventive medications as prescribed by a doctor.",
        "workouts": "Regular moderate exercise can help prevent migraines, but avoid vigorous activity during an attack.",
        "diets": "Avoid known dietary triggers and stay hydrated. Some find magnesium-rich foods helpful."
    },
    "fever": {
        "disease": "Viral Infection",
        "description": "An elevated body temperature, often a sign that your body is fighting off an infection.",
        "precaution": "Rest, stay hydrated, and monitor your temperature.",
        "medications": "Acetaminophen or ibuprofen can help reduce fever.",
        "workouts": "Rest is recommended until the fever subsides.",
        "diets": "Light, easily digestible foods and plenty of fluids."
    },
    "cough": {
        "disease": "Upper Respiratory Infection",
        "description": "An infection affecting the upper respiratory tract, often causing cough, congestion, and sore throat.",
        "precaution": "Rest, stay hydrated, and avoid irritants like smoke.",
        "medications": "Over-the-counter cough suppressants or expectorants may help.",
        "workouts": "Light exercise is okay if you feel up to it, but avoid strenuous activity.",
        "diets": "Warm liquids like herbal tea or soup can be soothing."
    },
    "shortness of breath": {
        "disease": "Asthma",
        "description": "A condition in which your airways narrow and swell, producing extra mucus, which can make breathing difficult.",
        "precaution": "Avoid known triggers, use an inhaler if prescribed, and monitor your breathing.",
        "medications": "Inhaled corticosteroids, bronchodilators.",
        "workouts": "Breathing exercises and light aerobic exercise may help.",
        "diets": "Avoid foods that can trigger allergic reactions."
    },
    "chest pain": {
        "disease": "Angina",
        "description": "Chest pain caused by reduced blood flow to the heart muscles, often triggered by physical exertion or stress.",
        "precaution": "Rest, avoid heavy physical activity, and manage stress.",
        "medications": "Nitrates, beta-blockers, or calcium channel blockers as prescribed by a doctor.",
        "workouts": "Light exercise under medical supervision.",
        "diets": "Heart-healthy diet low in saturated fats and rich in fruits, vegetables, and whole grains."
    },
    "joint pain": {
        "disease": "Osteoarthritis",
        "description": "A degenerative joint disease characterized by the breakdown of cartilage, leading to pain and stiffness.",
        "precaution": "Maintain a healthy weight, exercise regularly, and avoid joint overuse.",
        "medications": "Pain relievers like acetaminophen, nonsteroidal anti-inflammatory drugs (NSAIDs).",
        "workouts": "Low-impact exercises like swimming or cycling can help maintain joint function.",
        "diets": "A balanced diet with anti-inflammatory foods such as fish, nuts, and leafy greens."
    },
    "rash": {
        "disease": "Contact Dermatitis",
        "description": "A red, itchy rash caused by direct contact with a substance or an allergic reaction.",
        "precaution": "Identify and avoid the trigger. Keep the affected area clean and dry.",
        "medications": "Topical corticosteroids or oral antihistamines may provide relief.",
        "workouts": "Regular exercise is fine, but avoid sweating on affected areas.",
        "diets": "No specific dietary changes, but staying hydrated is important."
    },
    "nausea": {
        "disease": "Gastroenteritis",
        "description": "Inflammation of the stomach and intestines, often due to viral or bacterial infection.",
        "precaution": "Stay hydrated and rest. Avoid solid foods until nausea subsides.",
        "medications": "Anti-nausea medications may be recommended by a doctor.",
        "workouts": "Rest until symptoms improve.",
        "diets": "Clear liquids, then gradually introduce bland, easy-to-digest foods."
    },
    "fatigue": {
        "disease": "Chronic Fatigue Syndrome",
        "description": "A complex disorder characterized by extreme fatigue that can't be explained by any underlying medical condition.",
        "precaution": "Pace activities, practice good sleep hygiene, and manage stress.",
        "medications": "Consult a doctor for personalized treatment options.",
        "workouts": "Gradual, supervised exercise program may be beneficial.",
        "diets": "Balanced diet with emphasis on whole foods and proper hydration."
    },
    "dizziness": {
        "disease": "Vertigo",
        "description": "A sensation of feeling off balance or that the environment around you is spinning.",
        "precaution": "Move slowly and carefully. Avoid sudden head movements.",
        "medications": "Antihistamines or anti-nausea medications may help.",
        "workouts": "Balance exercises under supervision may be beneficial.",
        "diets": "Stay hydrated and avoid caffeine and alcohol."
    },
    "sore throat": {
        "disease": "Strep Throat",
        "description": "A bacterial infection causing inflammation and pain in the throat.",
        "precaution": "Rest, gargle with warm salt water, and avoid irritants.",
        "medications": "Antibiotics as prescribed by a doctor, pain relievers.",
        "workouts": "Rest until symptoms improve and fever subsides.",
        "diets": "Soft, cool foods and warm liquids can be soothing."
    },
    "runny nose": {
        "disease": "Common Cold",
        "description": "A viral infection of the upper respiratory tract, causing nasal congestion, sneezing, and sore throat.",
        "precaution": "Rest, stay hydrated, and practice good hygiene to prevent spread.",
        "medications": "Over-the-counter decongestants, antihistamines, and pain relievers.",
        "workouts": "Light exercise if you feel up to it, but rest if tired.",
        "diets": "Chicken soup, warm liquids, and foods rich in vitamin C."
    },
    "stomach pain": {
        "disease": "Gastritis",
        "description": "Inflammation of the stomach lining, causing pain, nausea, and sometimes vomiting.",
        "precaution": "Avoid spicy, fatty foods and alcohol. Eat smaller, more frequent meals.",
        "medications": "Antacids, proton pump inhibitors, or H2 blockers as recommended by a doctor.",
        "workouts": "Light exercise like walking can aid digestion.",
        "diets": "Bland, easily digestible foods. Avoid irritants like caffeine and alcohol."
    },
    "back pain": {
        "disease": "Lumbar Strain",
        "description": "Stretching or tearing of muscles or tendons in the lower back.",
        "precaution": "Use proper lifting techniques, maintain good posture, and strengthen core muscles.",
        "medications": "Over-the-counter pain relievers, muscle relaxants if prescribed.",
        "workouts": "Gentle stretching and strengthening exercises for the back and core.",
        "diets": "Anti-inflammatory foods like leafy greens, fatty fish, and nuts."
    },
    "difficulty sleeping": {
        "disease": "Insomnia",
        "description": "Persistent problems falling and staying asleep, despite adequate opportunity for sleep.",
        "precaution": "Maintain a regular sleep schedule, create a relaxing bedtime routine, and limit screen time before bed.",
        "medications": "Sleep aids may be prescribed by a doctor for short-term use.",
        "workouts": "Regular exercise, particularly aerobic activities, can improve sleep quality.",
        "diets": "Avoid caffeine, large meals, and alcohol close to bedtime. Consider foods rich in melatonin like cherries or kiwi."
    },
    "blurred vision": {
        "disease": "Myopia",
        "description": "Nearsightedness, where close objects look clear but distant objects appear blurry.",
        "precaution": "Regular eye check-ups, proper lighting when reading or working, and taking breaks from screens.",
        "medications": "Not applicable, but corrective lenses or surgery may be recommended.",
        "workouts": "Eye exercises as recommended by an optometrist.",
        "diets": "Foods rich in vitamins A, C, E, and omega-3 fatty acids for eye health."
    },
    "high blood pressure": {
        "disease": "Hypertension",
        "description": "A chronic condition where the force of blood against artery walls is too high.",
        "precaution": "Monitor blood pressure regularly, reduce sodium intake, and manage stress.",
        "medications": "ACE inhibitors, ARBs, diuretics, or beta-blockers as prescribed by a doctor.",
        "workouts": "Regular aerobic exercise and strength training can help lower blood pressure.",
        "diets": "DASH diet: rich in fruits, vegetables, whole grains, and low-fat dairy. Limit sodium and alcohol."
    },
    "abdominal pain": {
        "disease": "Appendicitis",
        "description": "Inflammation of the appendix, causing severe pain in the lower right abdomen.",
        "precaution": "Seek immediate medical attention if suspected. Do not eat or drink anything.",
        "medications": "Antibiotics and pain relievers may be given. Surgery is often necessary.",
        "workouts": "Avoid exercise until fully recovered post-surgery.",
        "diets": "Follow doctor's instructions post-surgery, usually starting with clear liquids."
    },
    "frequent urination": {
        "disease": "Urinary Tract Infection (UTI)",
        "description": "An infection in any part of the urinary system, most commonly in the bladder and urethra.",
        "precaution": "Stay hydrated, urinate frequently, and practice good hygiene.",
        "medications": "Antibiotics as prescribed by a doctor.",
        "workouts": "Light exercise is generally okay, but avoid activities that may irritate the bladder.",
        "diets": "Drink plenty of water, and consider cranberry juice or supplements."
    },
    "anxiety": {
        "disease": "Generalized Anxiety Disorder",
        "description": "Persistent and excessive worry about various aspects of life.",
        "precaution": "Practice relaxation techniques, maintain a regular sleep schedule, and seek support.",
        "medications": "Anti-anxiety medications or antidepressants may be prescribed by a doctor.",
        "workouts": "Regular exercise, particularly aerobic activities, can help reduce anxiety.",
        "diets": "Limit caffeine and alcohol. Consider foods rich in omega-3 fatty acids and complex carbohydrates."
    },
    "depression": {
        "disease": "Major Depressive Disorder",
        "description": "A mood disorder causing persistent feelings of sadness and loss of interest.",
        "precaution": "Seek professional help, maintain social connections, and establish a routine.",
        "medications": "Antidepressants may be prescribed by a doctor.",
        "workouts": "Regular exercise can help improve mood and reduce symptoms of depression.",
        "diets": "A balanced diet rich in fruits, vegetables, and omega-3 fatty acids may help support mental health."
    },
    "memory loss": {
        "disease": "Alzheimer's Disease",
        "description": "A progressive brain disorder that slowly destroys memory and thinking skills.",
        "precaution": "Engage in mentally stimulating activities, maintain social connections, and manage cardiovascular risk factors.",
        "medications": "Cholinesterase inhibitors or memantine may be prescribed by a doctor.",
        "workouts": "Regular physical exercise may help slow the progression of cognitive decline.",
        "diets": "Mediterranean diet rich in fruits, vegetables, whole grains, and lean proteins."
    },
    "tremors": {
        "disease": "Parkinson's Disease",
        "description": "A neurodegenerative disorder affecting movement, often including tremors.",
        "precaution": "Work with a healthcare team to manage symptoms and maintain independence.",
        "medications": "Carbidopa-levodopa, dopamine agonists, or other medications as prescribed.",
        "workouts": "Regular exercise, including balance and flexibility training, can help manage symptoms.",
        "diets": "A balanced diet rich in fiber and omega-3 fatty acids. Some may benefit from a low-protein diet."
    },
    "chest tightness": {
        "disease": "Chronic Obstructive Pulmonary Disease (COPD)",
        "description": "A group of lung diseases that block airflow and make it difficult to breathe.",
        "precaution": "Quit smoking, avoid air pollutants, and get vaccinated against flu and pneumonia.",
        "medications": "Bronchodilators, inhaled steroids, or other medications as prescribed.",
        "workouts": "Pulmonary rehabilitation exercises can help improve breathing and quality of life.",
        "diets": "A balanced diet with adequate calories. Some may need to limit salt intake."
    },
    "excessive thirst": {
        "disease": "Diabetes Mellitus",
        "description": "A group of diseases that result in too much sugar in the blood.",
        "precaution": "Monitor blood sugar levels regularly, maintain a healthy weight, and exercise regularly.",
        "medications": "Insulin, metformin, or other diabetes medications as prescribed by a doctor.",
        "workouts": "Regular aerobic exercise and strength training can help manage blood sugar levels.",
        "diets": "A balanced diet with controlled portions of carbohydrates, focusing on low glycemic index foods."
    },
    "skin lesions": {
        "disease": "Psoriasis",
        "description": "A condition causing red, itchy, scaly patches on the skin.",
        "precaution": "Avoid triggers like stress and skin injuries, keep skin moisturized.",
        "medications": "Topical corticosteroids, vitamin D analogues, or systemic medications as prescribed.",
        "workouts": "Regular exercise can help reduce stress and inflammation.",
        "diets": "Anti-inflammatory foods may help. Some find gluten-free or dairy-free diets beneficial."
    },
    "joint swelling": {
        "disease": "Rheumatoid Arthritis",
        "description": "An autoimmune disorder causing inflammation in the joints.",
        "precaution": "Protect joints, maintain a healthy weight, and manage stress.",
        "medications": "Disease-modifying antirheumatic drugs (DMARDs), NSAIDs, or corticosteroids as prescribed.",
        "workouts": "Low-impact exercises like swimming or cycling can help maintain joint function.",
        "diets": "Mediterranean diet or other anti-inflammatory diets may help reduce symptoms."
    },
    "diarrhea": {
        "disease": "Gastroenteritis",
        "description": "An inflammation of the stomach and intestines that causes symptoms like diarrhea, stomach pain, and vomiting.",
        "precaution": "Stay hydrated, avoid fatty foods, and maintain good hand hygiene.",
        "medications": "Anti-diarrheal medications or antibiotics (if bacterial infection) may be prescribed by a doctor.",
        "workouts": "Rest until symptoms improve.",
        "diets": "BRAT diet (Bananas, Rice, Applesauce, Toast) is recommended until symptoms subside."
    },
    "vomiting": {
        "disease": "Food Poisoning",
        "description": "An illness caused by eating contaminated food, leading to symptoms like vomiting, diarrhea, and abdominal cramps.",
        "precaution": "Avoid risky foods like raw or undercooked meats, and maintain proper food hygiene.",
        "medications": "Anti-nausea or anti-diarrheal medications as recommended by a doctor.",
        "workouts": "Rest until symptoms improve.",
        "diets": "Clear fluids at first, followed by bland, easily digestible foods."
    },
    "frequent urination": {
        "disease": "Diabetes",
        "description": "A chronic condition that affects how your body turns food into energy, often leading to high blood sugar levels.",
        "precaution": "Monitor blood sugar levels regularly, maintain a healthy diet, and exercise.",
        "medications": "Insulin or oral diabetes medications as prescribed by a doctor.",
        "workouts": "Regular aerobic and strength-training exercises can help regulate blood sugar.",
        "diets": "A balanced diet low in sugars and refined carbohydrates, high in fiber and healthy fats."
    },
    "swollen ankles": {
        "disease": "Congestive Heart Failure",
        "description": "A condition where the heart doesn't pump blood as well as it should, leading to fluid retention and swelling in the legs and ankles.",
        "precaution": "Monitor weight, reduce salt intake, and take medications as prescribed.",
        "medications": "Diuretics, ACE inhibitors, beta-blockers, or other heart medications as recommended by a doctor.",
        "workouts": "Low-impact exercises like walking or swimming, under medical supervision.",
        "diets": "Low-sodium, heart-healthy diet, rich in vegetables, fruits, and whole grains."
    },
    "sudden weight loss": {
        "disease": "Hyperthyroidism",
        "description": "A condition where the thyroid gland produces too much thyroid hormone, leading to an increased metabolism and rapid weight loss.",
        "precaution": "Follow your doctor's treatment plan, including medications and regular monitoring.",
        "medications": "Anti-thyroid medications or beta-blockers as prescribed by a doctor.",
        "workouts": "Moderate exercise to maintain muscle mass, but avoid over-exertion.",
        "diets": "Balanced diet with adequate calorie intake, focusing on nutrient-dense foods."
    },
    "hair loss": {
        "disease": "Alopecia",
        "description": "An autoimmune disorder that causes hair to fall out, often in patches.",
        "precaution": "Avoid harsh hair treatments, reduce stress, and consult a dermatologist.",
        "medications": "Topical treatments like minoxidil or corticosteroids as recommended by a doctor.",
        "workouts": "Regular exercise to reduce stress and improve overall health.",
        "diets": "A diet rich in proteins, vitamins (especially vitamin D), and minerals like zinc."
    },
    "itchy skin": {
        "disease": "Eczema",
        "description": "A condition that causes the skin to become inflamed, itchy, and cracked.",
        "precaution": "Moisturize regularly, avoid known triggers, and use gentle skincare products.",
        "medications": "Topical corticosteroids or antihistamines as prescribed by a doctor.",
        "workouts": "Regular exercise is fine, but avoid sweating excessively if it worsens symptoms.",
        "diets": "Some find relief by avoiding foods that trigger inflammation, such as dairy or gluten."
    },
    "cold hands and feet": {
        "disease": "Raynaud's Disease",
        "description": "A condition where cold temperatures or stress cause the blood vessels to narrow, leading to cold hands and feet.",
        "precaution": "Keep hands and feet warm, avoid stress, and avoid smoking.",
        "medications": "Calcium channel blockers may help improve circulation.",
        "workouts": "Regular aerobic exercise to improve circulation.",
        "diets": "A balanced diet rich in omega-3 fatty acids and antioxidants."
    },
    "dry mouth": {
        "disease": "Sjogren's Syndrome",
        "description": "An autoimmune disorder that affects the glands that produce moisture, leading to dry mouth and dry eyes.",
        "precaution": "Stay hydrated, use saliva substitutes, and maintain good oral hygiene.",
        "medications": "Prescription medications that stimulate saliva production may be recommended.",
        "workouts": "Regular exercise to improve overall health.",
        "diets": "Avoid salty or dry foods, and drink plenty of fluids."
    },
    "persistent cough": {
        "disease": "Chronic Bronchitis",
        "description": "A form of chronic obstructive pulmonary disease (COPD) that causes inflammation of the bronchial tubes, leading to a persistent cough.",
        "precaution": "Avoid smoking, reduce exposure to irritants, and take medications as prescribed.",
        "medications": "Bronchodilators, inhaled corticosteroids, or oxygen therapy as needed.",
        "workouts": "Breathing exercises and light aerobic activity can help improve lung function.",
        "diets": "A balanced diet with anti-inflammatory foods like fruits, vegetables, and omega-3-rich foods."
    },
    "loss of appetite": {
        "disease": "Anorexia Nervosa",
        "description": "An eating disorder characterized by an abnormally low body weight, intense fear of gaining weight, and a distorted perception of weight.",
        "precaution": "Seek professional help, monitor eating habits, and support emotional well-being.",
        "medications": "Antidepressants or antipsychotic medications may be prescribed in some cases.",
        "workouts": "Light exercise under professional guidance, focusing on body recovery and mental health.",
        "diets": "Nutritionally balanced meals, with professional guidance to restore healthy eating patterns.",
    },
    "swollen glands": {
        "disease": "Lymphadenitis",
        "description": "Swollen lymph nodes, often due to infection, inflammation, or certain diseases.",
        "precaution": "Monitor symptoms, rest, and seek medical advice if swelling persists or is painful.",
        "medications": "Antibiotics or anti-inflammatory medications may be prescribed, depending on the cause.",
        "workouts": "Rest is recommended until swelling subsides.",
        "diets": "No specific dietary changes, but maintaining hydration and a healthy immune-boosting diet is beneficial."
    },
    "burning sensation": {
        "disease": "Gastroesophageal Reflux Disease (GERD)",
        "description": "A condition where stomach acid frequently flows back into the tube connecting your mouth and stomach, causing heartburn and a burning sensation.",
        "precaution": "Avoid spicy and fatty foods, eat smaller meals, and avoid lying down after eating.",
        "medications": "Antacids, H2 blockers, or proton pump inhibitors as prescribed by a doctor.",
        "workouts": "Moderate, low-impact exercise like walking or cycling may help reduce symptoms.",
        "diets": "Avoid trigger foods such as spicy foods, caffeine, and alcohol. Eat smaller, more frequent meals.",
    },
    "numbness": {
        "disease": "Peripheral Neuropathy",
        "description": "Damage to the peripheral nerves, often causing weakness, numbness, and pain, typically in the hands and feet.",
        "precaution": "Manage underlying conditions like diabetes, avoid repetitive movements, and take breaks during physical activity.",
        "medications": "Pain relievers, anticonvulsants, or antidepressants may be prescribed.",
        "workouts": "Low-impact exercises like swimming, cycling, or walking to maintain circulation and mobility.",
        "diets": "A diet rich in vitamins B6 and B12, and folate can support nerve health.",
    },
    "swelling in legs": {
        "disease": "Deep Vein Thrombosis (DVT)",
        "description": "A blood clot that forms in a deep vein, usually in the legs, leading to swelling and discomfort.",
        "precaution": "Avoid prolonged periods of sitting or standing, stay active, and wear compression stockings if prescribed.",
        "medications": "Anticoagulants (blood thinners) may be prescribed to prevent clot growth.",
        "workouts": "Light walking or gentle stretching to improve circulation, but avoid vigorous exercise until cleared by a doctor.",
        "diets": "Stay hydrated and follow a heart-healthy diet, including foods low in sodium.",
    },
    "itching": {
        "disease": "Eczema (Atopic Dermatitis)",
        "description": "A condition that makes your skin red and itchy, commonly in children but also seen in adults.",
        "precaution": "Keep the skin moisturized, avoid harsh soaps, and wear breathable fabrics.",
        "medications": "Topical corticosteroids, antihistamines, or immune-modulating creams may be recommended.",
        "workouts": "Avoid activities that cause excessive sweating or skin irritation.",
        "diets": "A balanced diet; some individuals may find relief by avoiding specific allergens.",
    },
    "yellowing of skin": {
        "disease": "Jaundice",
        "description": "A condition characterized by yellowing of the skin and eyes due to high bilirubin levels, often related to liver issues.",
        "precaution": "Monitor liver health, avoid alcohol, and manage any underlying conditions.",
        "medications": "Depends on the underlying cause, which may include antibiotics, antiviral medications, or other treatments.",
        "workouts": "Rest and avoid strenuous activity until the underlying condition is treated.",
        "diets": "A liver-friendly diet, including low-fat foods, fruits, vegetables, and lean proteins.",
    },
    "frequent infections": {
        "disease": "Immunodeficiency Disorder",
        "description": "A condition where the immune system's ability to fight infectious diseases is compromised or entirely absent.",
        "precaution": "Take preventive measures against infections, stay vaccinated, and practice good hygiene.",
        "medications": "Immunoglobulin therapy or other treatments based on the specific type of immunodeficiency.",
        "workouts": "Light exercises to maintain overall health, but avoid exposure to pathogens.",
        "diets": "A balanced diet rich in vitamins and minerals to support immune function.",
    },
    "loss of coordination": {
        "disease": "Multiple Sclerosis (MS)",
        "description": "A disease in which the immune system eats away at the protective covering of nerves, disrupting communication between the brain and body.",
        "precaution": "Manage stress, stay active within limits, and follow medical advice.",
        "medications": "Disease-modifying therapies, corticosteroids, or muscle relaxants as prescribed by a doctor.",
        "workouts": "Low-impact activities such as swimming or yoga can help maintain mobility and strength.",
        "diets": "A diet rich in omega-3s, fruits, and vegetables to help reduce inflammation.",
    },
}

@csrf_exempt
def recommender(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body.decode('utf-8'))
            text_input = data.get('text_input', '').lower()
            predictions = []
            for symptom, info in symptom_prediction_mapping.items():
                if symptom in text_input:
                    predictions.append(info)
            
            if not predictions:
                predictions.append({
                    "disease": "Unknown",
                    "description": "The symptoms provided do not match any specific condition in our database.",
                    "precaution": "Please consult a healthcare professional for proper diagnosis and treatment.",
                    "medications": "Do not self-medicate. Consult a doctor.",
                    "workouts": "Maintain regular, moderate exercise unless advised otherwise by a doctor.",
                    "diets": "Maintain a balanced diet rich in fruits and vegetables."
                })
            
            return JsonResponse({'predictions': predictions})
        except json.JSONDecodeError:
            logger.error("Invalid JSON received")
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            logger.error(f"Error processing request: {e}")
            return JsonResponse({'error': 'An error occurred while processing your request'}, status=500)
    else:
        return render(request, 'recommender/recommender_home.html')

@csrf_exempt
def speech_to_text(request):
    if request.method == 'POST':
        recognizer = sr.Recognizer()
        audio_file = request.FILES.get('audio')

        if audio_file:
            try:
                with sr.AudioFile(audio_file) as source:
                    audio_data = recognizer.record(source)
                text = recognizer.recognize_google(audio_data)
                
                # Process the recognized text through the recommender
                predictions = []
                for symptom, info in symptom_prediction_mapping.items():
                    if symptom in text.lower():
                        predictions.append(info)
                
                if not predictions:
                    predictions.append({
                        "disease": "Unknown",
                        "description": "The symptoms provided do not match any specific condition in our database.",
                        "precaution": "Please consult a healthcare professional for proper diagnosis and treatment.",
                        "medications": "Do not self-medicate. Consult a doctor.",
                        "workouts": "Maintain regular, moderate exercise unless advised otherwise by a doctor.",
                        "diets": "Maintain a balanced diet rich in fruits and vegetables."
                    })
                
                return JsonResponse({'text': text, 'predictions': predictions})
            except sr.UnknownValueError:
                logger.error("Speech recognition could not understand audio")
                return JsonResponse({'error': 'Speech recognition could not understand audio'})
            except sr.RequestError:
                logger.error("Could not request results from speech recognition service")
                return JsonResponse({'error': 'Could not request results from speech recognition service'})
        else:
            return JsonResponse({'error': 'No audio file uploaded'}, status=400)

    return render(request, 'recommender/speech.html')