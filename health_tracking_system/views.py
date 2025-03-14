import os
import numpy as np
import pandas as pd
import pickle
from django.shortcuts import render,redirect
from django.contrib import messages
from django.conf import settings

from django.contrib.auth.decorators import login_required


from django.contrib.auth import login, authenticate,logout

from .forms import CustomUserCreationForm, CustomLoginForm

# Load the training dataset dynamically
dataset_path = os.path.join(settings.BASE_DIR, 'health_tracking_system', 'datasets', 'Training.csv')
df = pd.read_csv(dataset_path)

# Extract symptom names from the first 132 columns
symptoms = df.columns[:-1].tolist()
diseases = sorted(df['prognosis'].unique())  

# Create mappings for symptoms and diseases
symptom_index = {symptom: idx for idx, symptom in enumerate(symptoms)}
disease_mapping = {idx: disease for idx, disease in enumerate(diseases)}

# Load the trained model
model_path = os.path.join(settings.BASE_DIR, 'health_tracking_system', 'models', 'svc.pkl')
svc = pickle.load(open(model_path, 'rb'))

# Load additional datasets
sym_des = pd.read_csv(os.path.join(settings.BASE_DIR, "health_tracking_system", "datasets", "symtoms_df.csv"))
precautions = pd.read_csv(os.path.join(settings.BASE_DIR, "health_tracking_system", "datasets", "precautions_df.csv"))
workout = pd.read_csv(os.path.join(settings.BASE_DIR, "health_tracking_system", "datasets", "workout_df.csv"))
description = pd.read_csv(os.path.join(settings.BASE_DIR, "health_tracking_system", "datasets", "description.csv"))
medications = pd.read_csv(os.path.join(settings.BASE_DIR, "health_tracking_system", "datasets", "medications.csv"))
diets = pd.read_csv(os.path.join(settings.BASE_DIR, "health_tracking_system", "datasets", "diets.csv"))


# Helper function to fetch details about the disease
def helper(disease_name):
    desc = " ".join(description[description['Disease'] == disease_name]['Description'])

    pre = precautions[precautions['Disease'] == disease_name][['Precaution_1', 'Precaution_2', 'Precaution_3', 'Precaution_4']]
    pre = [col for col in pre.values] if not pre.empty else []

    med = medications[medications['Disease'] == disease_name]['Medication']
    med = [med for med in med.values] if not med.empty else []

    die = diets[diets['Disease'] == disease_name]['Diet']
    die = [die for die in die.values] if not die.empty else []

    wrkout = workout[workout['disease'] == disease_name]['workout']
    wrkout = [wrkout for wrkout in wrkout.values] if not wrkout.empty else []

    return desc, pre, med, die, wrkout


# Normalize user input symptom names
def normalize_symptom(symptom):
    return symptom.strip().lower().replace(" ", "_")


# Prediction function
def get_predicted_value(patient_symptoms):
    # Initialize an empty feature vector of length 132 (or the number of symptoms in Training.csv)
    input_vector = np.zeros(len(symptoms))

    # Set 1 for symptoms that the user enters
    for symptom in patient_symptoms:
        normalized_symptom = normalize_symptom(symptom)
        if normalized_symptom in symptom_index:
            input_vector[symptom_index[normalized_symptom]] = 1 

    # Reshape for prediction
    input_vector = input_vector.reshape(1, -1)

    # Predict disease (returns an index)
    predicted_index = svc.predict(input_vector)[0]

    # Convert the index back to a disease name
    predicted_disease = disease_mapping.get(predicted_index, "Unknown Disease")

    return predicted_disease


@login_required(login_url='signup/')
def home(request):
    if request.method == "POST":
        symptoms = request.POST.get("symptoms")

        if symptoms == "Symptoms" or not symptoms:
            return render(request, "home.html", {"message": "Please enter correct symptoms."})

        # Convert user symptoms input to a 
        user_symptoms = [s.strip("[]' ") for s in symptoms.split(",")]

        # Get the predicted disease
        predicted_disease = get_predicted_value(user_symptoms)

    
        dis_des, precautions, medications, rec_diet, workout = helper(predicted_disease)

        return render(request, "home.html", {
            "predicted_disease": predicted_disease,
            "dis_des": dis_des,
            "my_precautions": precautions[0] if precautions else [],
            "medications": medications,
            "my_diet": rec_diet,
            "workout": workout,
        })

    return render(request, "home.html")


def signup(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('login-url')
    else:
        form = CustomUserCreationForm()
        
    return render(request,'account/signup.html',{'form': form})


def login_user(request):
    if request.method == 'POST':
        form = CustomLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            
            if user is not None:

                login(request, user)  
                messages.success(request, f'Welcome, {username} ')
                return redirect('home-url')
            else:
                pass
        else:
            pass
    else:
        form = CustomLoginForm()
        
    return render(request, 'account/login.html', {'form': form})
    
def logout_user(request):
    logout(request)
    return redirect('login-url')
