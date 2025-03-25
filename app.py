import streamlit as st
import pandas as pd
import requests
import json
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import speech_recognition as sr
import pyttsx3
from datetime import datetime
from fpdf import FPDF
import os
import numpy as np
import re
import joblib
from rapidfuzz import fuzz, process
from metaphone import doublemetaphone
import threading
import queue
import warnings
from pymongo import MongoClient
import uuid
import io

warnings.filterwarnings("ignore")

# --- MongoDB Setup ---
client = MongoClient("mongodb://localhost:27017/")
db = client['hackathon']
collection = db['mm']

# --- Local Folder Setup ---
PRESCRIPTION_FOLDER = "C:/persnol ai/prescriptions"
if not os.path.exists(PRESCRIPTION_FOLDER):
    os.makedirs(PRESCRIPTION_FOLDER)

# --- Styling ---
st.set_page_config(page_title="MediMind", layout="wide")
st.markdown("""
    <style>
    .main-title {text-align: center; font-size: 40px; color: #2ecc71; margin-bottom: 20px;}
    .section-header {font-size: 24px; color: #3498db; margin-top: 20px;}
    .stButton>button {background-color: #2ecc71; color: white; border-radius: 5px;}
    .stTextInput>input {border-radius: 5px;}
    .popup-box {border: 2px solid #3498db; padding: 20px; background-color: #f0f8ff; border-radius: 10px;}
    .column-container {border: 1px solid #ddd; padding: 15px; border-radius: 10px; background-color: #f9f9f9;}
    </style>
""", unsafe_allow_html=True)

# --- Load Dataset ---
medicine_df = pd.read_csv("dataset.csv")
medicine_names = medicine_df['medicine_name'].str.lower().unique()

# --- Doctor Chatbot Functions ---
API_KEY = "sk_wBUOekKZIdo-mwY2IB9-Jtx5pvsaxT4QMMGsiveTK6Y"
API_URL = "https://api.novita.ai/v3/openai/chat/completions"

if "patient_data" not in st.session_state:
    st.session_state.patient_data = {"history": "", "conditions": "", "medications": "", "test_results": ""}

predefined_questions = {
    "history": [
        "What is your past medical history?", "Have you had any surgeries?",
        "Do you have a family history of diseases?", "When were you last hospitalized?",
        "Any previous allergic reactions?", "What chronic illnesses have you had?",
        "Have you ever smoked or used alcohol?", "What injuries have you had in the past?",
        "Any history of mental health issues?", "When did you last see a doctor?"
    ],
    "conditions": [
        "What conditions do you currently have?", "Are you experiencing any symptoms now?",
        "How long have you had this condition?", "Is your condition worsening?",
        "Do you have any pain related to your condition?", "Are your conditions managed well?",
        "Any recent changes in your symptoms?", "Do you have diabetes or hypertension?",
        "Are you feeling fatigued due to your condition?", "What triggers your condition?"
    ],
    "medications": [
        "What medications are you taking?", "When did you start your current meds?",
        "Any side effects from your medications?", "Are you taking your meds as prescribed?",
        "What dosage are you on?", "Have you missed any doses recently?",
        "Are you on any over-the-counter drugs?", "Any recent changes to your medications?",
        "Do you take vitamins or supplements?", "Are your medications helping?"
    ],
    "test_results": [
        "What were your latest test results?", "When was your last blood test?",
        "Any abnormal results recently?", "What did your last scan show?",
        "Have your test_results improved?", "When was your last cholesterol check?",
        "What were your blood sugar levels?", "Any recent urine test results?",
        "Did your doctor explain your last results?", "What was your last ECG like?"
    ]
}

def call_novita_api(prompt):
    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
    payload = {"model": "meta-llama/llama-3.1-8b-instruct", "messages": [{"role": "user", "content": prompt}], "max_tokens": 150}
    try:
        response = requests.post(API_URL, headers=headers, data=json.dumps(payload))
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"Error calling API: {str(e)}"

def match_question(user_question, category_questions, threshold=0.7):
    if not user_question or not category_questions:
        return None
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform([user_question] + category_questions)
    similarity_scores = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:])[0]
    max_score_idx = similarity_scores.argmax()
    return category_questions[max_score_idx] if similarity_scores[max_score_idx] >= threshold else None

def get_response(matched_question, category):
    data = st.session_state.patient_data[category]
    if not data:
        return "No data provided for this category yet."
    prompt = f"Based on the following {category} data: '{data}', answer this question: '{matched_question}'"
    return call_novita_api(prompt)

# --- Voice Assistant Functions ---
class MediMindVoiceAssistant:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 210)
        self.engine.setProperty('volume', 1)
        self.medicines = []
        self.specialties = {
            'cardiology': [], 'neurology': [], 'respiratory': [], 'gastroenterology': [],
            'endocrinology': [], 'antibiotics': [], 'analgesics': [], 'other': []
        }
        self.model = joblib.load("medicine_model.pkl") if os.path.exists("medicine_model.pkl") else None
        self.medicine_df = medicine_df
        self.listening = False
        self.command_queue = queue.Queue()

    def speak(self, text):
        self.engine.say(text)
        self.engine.runAndWait()

    def preprocess_command(self, command):
        if not command:
            return None
        command = command.lower()
        fillers = ['um', 'uh', 'like', 'so', 'and', 'then', 'please', 'add', 'prescribe']
        for filler in fillers:
            command = re.sub(r'\b' + filler + r'\b', ' ', command)
        command = re.sub(r'\s+', ' ', command).strip()
        return command if command else None

    def classify_medicine(self, command):
        processed = self.preprocess_command(command)
        if not processed:
            return None
        if not self.model:
            best_match = process.extractOne(processed, medicine_names, scorer=fuzz.ratio)
            return best_match[0].capitalize() if best_match and best_match[1] > 80 else None
        try:
            prediction = self.model.predict([processed])[0]
            confidence = np.max(self.model.predict_proba([processed]))
            if confidence > 0.7:
                return prediction
        except Exception as e:
            self.command_queue.put(f"Model error: {e}. Using fuzzy matching.")
        best_match = process.extractOne(processed, medicine_names, scorer=fuzz.ratio)
        return best_match[0].capitalize() if best_match and best_match[1] > 80 else None

    def extract_dosage_info(self, command):
        dosage_patterns = [r'(\d+\.?\d*\s*(mg|mcg|ml|g))']
        frequency_patterns = [
            r'once daily', r'twice daily', r'three times daily',
            r'(\d+) times daily', r'every (\d+) hours', r'as needed'
        ]
        dosage = next((re.search(p, command).group(0) for p in dosage_patterns if re.search(p, command)), None)
        frequency = next((re.search(p, command).group(0) for p in frequency_patterns if re.search(p, command)), None)
        return dosage, frequency

    def add_medicine_with_details(self, medicine_name, dosage=None, frequency=None):
        medicine_row = self.medicine_df[self.medicine_df['medicine_name'].str.lower() == medicine_name.lower()]
        if not medicine_row.empty:
            default_dosage = medicine_row.iloc[0]['common_dosage']
            category = medicine_row.iloc[0]['category']
            self.specialties[category].append(medicine_name)
        else:
            self.specialties['other'].append(medicine_name)
            default_dosage = "As directed"
        medicine_info = {'name': medicine_name, 'dosage': dosage or default_dosage, 'frequency': frequency or 'As directed'}
        self.medicines.append(medicine_info)
        return medicine_info

    def take_command(self):
        try:
            with sr.Microphone() as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                audio = self.recognizer.listen(source, timeout=None, phrase_time_limit=10)
                command = self.recognizer.recognize_google(audio).lower()
                self.command_queue.put(f"Recognized: {command}")
                return command
        except sr.UnknownValueError:
            self.command_queue.put("Could not understand audio.")
            return None
        except sr.RequestError as e:
            self.command_queue.put(f"Speech recognition error: {e}")
            return None
        except Exception as e:
            self.command_queue.put(f"Error in speech recognition: {e}")
            return None

    def listen_continuously(self):
        self.listening = True
        self.command_queue.put("Listening continuously... Say 'stop' to end")
        while self.listening:
            command = self.take_command()
            if command:
                if 'stop' in command:
                    self.listening = False
                    self.command_queue.put("Stopped listening")
                    self.speak("Stopped listening")
                    break
                medicine_name = self.classify_medicine(command)
                if medicine_name:
                    dosage, frequency = self.extract_dosage_info(command)
                    med_info = self.add_medicine_with_details(medicine_name, dosage, frequency)
                    self.command_queue.put(f"Added: {med_info['name']}")
                    self.speak(f"Added {med_info['name']}")
                else:
                    self.command_queue.put(f"Medicine not recognized: {command}")
                    self.speak("Medicine not recognized")

    def generate_prescription_pdf(self):
        patient_id = str(uuid.uuid4())
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, "MediMind Prescription", ln=True, align="C")
        pdf.set_font("Arial", "", 12)
        pdf.cell(0, 10, f"Patient ID: {patient_id}", ln=True)
        pdf.cell(0, 10, f"Date: {datetime.now().strftime('%B %d, %Y')}", ln=True)
        pdf.ln(10)
        for specialty, medicines_list in self.specialties.items():
            if medicines_list:
                pdf.set_font("Arial", "B", 14)
                pdf.cell(0, 10, f"{specialty.capitalize()} Medicines", ln=True)
                pdf.set_font("Arial", "", 12)
                for med in self.medicines:
                    if med['name'] in medicines_list:
                        pdf.multi_cell(0, 10, f"* {med['name']} - {med['dosage']} - {med['frequency']}")
                pdf.ln(5)
        pdf.line(20, pdf.get_y(), 90, pdf.get_y())
        pdf.cell(0, 10, "Doctor's Signature", ln=True)
        
        pdf_path = os.path.join(PRESCRIPTION_FOLDER, f"MediMind_Prescription_{patient_id}.pdf")
        pdf.output(pdf_path)
        
        with open(pdf_path, "rb") as f:
            pdf_data = f.read()
        collection.insert_one({"patient_id": patient_id, "pdf": pdf_data})
        
        return pdf_path, patient_id

# --- Helper Function for Patient Records ---
def retrieve_patient_pdf(patient_id):
    record = collection.find_one({"patient_id": patient_id})
    if record and "pdf" in record:
        return record["pdf"]
    return None

# --- Main UI ---
st.markdown("<h1 class='main-title'>MediMind</h1>", unsafe_allow_html=True)

# Three-column layout
col1, col2, col3 = st.columns([1, 1, 1])

# --- Doctor Chatbot Section ---
with col1:
    st.markdown("<div class='column-container'>", unsafe_allow_html=True)
    st.markdown("<h2 class='section-header'>Doctor Chatbot</h2>", unsafe_allow_html=True)
    
    if "patient_data_collected" not in st.session_state:
        st.session_state.patient_data_collected = False
    if "show_query_popup" not in st.session_state:
        st.session_state.show_query_popup = False

    if not st.session_state.patient_data_collected:
        st.subheader("Collect Patient Data")
        with st.form(key="patient_data_form"):
            st.session_state.patient_data["history"] = st.text_area("Medical History", value=st.session_state.patient_data["history"], key="history")
            st.session_state.patient_data["conditions"] = st.text_area("Current Conditions", value=st.session_state.patient_data["conditions"], key="conditions")
            st.session_state.patient_data["medications"] = st.text_area("Current Medications", value=st.session_state.patient_data["medications"], key="medications")
            st.session_state.patient_data["test_results"] = st.text_area("Recent Test Results", value=st.session_state.patient_data["test_results"], key="test_results")
            submit_button = st.form_submit_button(label="Submit Patient Data")
            if submit_button:
                st.session_state.patient_data_collected = True
                st.session_state.show_query_popup = True
                st.success("Patient data collected successfully!")
                st.rerun()
    else:
        if st.session_state.show_query_popup:
            with st.container():
                st.markdown("<div class='popup-box'>", unsafe_allow_html=True)
                st.subheader("Ask a Question")
                with st.form(key="query_form"):
                    question = st.text_input("Enter your question:", key="question_input")
                    submit_query = st.form_submit_button(label="Submit Question")
                    if submit_query and question:
                        category = None
                        for cat, keywords in {
                            "history": ["history", "past", "surgeries", "family"],
                            "conditions": ["condition", "symptoms", "pain", "disease"],
                            "medications": ["medication", "meds", "dose", "side effects"],
                            "test_results": ["test", "results", "blood", "scan"]
                        }.items():
                            if any(kw in question.lower() for kw in keywords):
                                category = cat
                                break
                        if category:
                            matched_question = match_question(question, predefined_questions[category])
                            if matched_question:
                                response = get_response(matched_question, category)
                                st.write(f"**Response:** {response}")
                            else:
                                st.write("Question not recognized. Please rephrase.")
                        else:
                            st.write("Could not determine category. Specify history, conditions, medications, or test results.")
                    if st.form_submit_button(label="Close"):
                        st.session_state.show_query_popup = False
                        st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# --- Voice Assistant Section ---
with col2:
    st.markdown("<div class='column-container'>", unsafe_allow_html=True)
    st.markdown("<h2 class='section-header'>Voice Assistant</h2>", unsafe_allow_html=True)
    
    if "assistant" not in st.session_state:
        st.session_state.assistant = MediMindVoiceAssistant()
    if "status" not in st.session_state:
        st.session_state.status = "Ready"

    assistant = st.session_state.assistant
    
    if st.button("Start Continuous Listening"):
        assistant.listening = False
        threading.Thread(target=assistant.listen_continuously, daemon=True).start()
    
    while not assistant.command_queue.empty():
        message = assistant.command_queue.get()
        st.session_state.status = message
        st.rerun()

    st.write(f"Status: {st.session_state.status}")
    
    st.subheader("Prescribed Medicines")
    if not assistant.medicines:
        st.write("No medicines added yet.")
    else:
        for specialty, medicines_list in assistant.specialties.items():
            if medicines_list:
                st.markdown(f"**{specialty.upper()}**")
                for med in assistant.medicines:
                    if med['name'] in medicines_list:
                        st.write(f"• {med['name']} - {med['dosage']} - {med['frequency']}")
    
    if st.button("Generate PDF"):
        if assistant.medicines:
            pdf_path, patient_id = assistant.generate_prescription_pdf()
            st.write(f"PDF generated for Patient ID: {patient_id} at {pdf_path}")
            assistant.speak("Prescription PDF generated")
            with open(pdf_path, "rb") as f:
                st.download_button("Download PDF", f, file_name=os.path.basename(pdf_path))
        else:
            st.write("No medicines to generate PDF.")
    
    if st.button("Clear All"):
        assistant.medicines = []
        assistant.specialties = {key: [] for key in assistant.specialties}
        st.session_state.status = "All medicines cleared"
        assistant.speak("All medicines cleared")
    st.markdown("</div>", unsafe_allow_html=True)

# --- Patient Records Section ---
with col3:
    st.markdown("<div class='column-container'>", unsafe_allow_html=True)
    st.markdown("<h2 class='section-header'>Patient Records</h2>", unsafe_allow_html=True)
    
    st.subheader("Retrieve Patient Prescription")
    patient_id_input = st.text_input("Enter Patient ID:", key="patient_id_input")
    if st.button("Retrieve PDF"):
        if patient_id_input:
            pdf_data = retrieve_patient_pdf(patient_id_input)
            if pdf_data:
                st.write(f"PDF found for Patient ID: {patient_id_input}")
                
                # Provide download option
                pdf_buffer = io.BytesIO(pdf_data)
                st.download_button(
                    label="Download Patient PDF",
                    data=pdf_buffer,
                    file_name=f"MediMind_Prescription_{patient_id_input}.pdf",
                    mime="application/pdf"
                )
                
                # Save to local folder
                pdf_path = os.path.join(PRESCRIPTION_FOLDER, f"MediMind_Prescription_{patient_id_input}.pdf")
                with open(pdf_path, "wb") as f:
                    f.write(pdf_data)
                st.write(f"PDF saved locally at: {pdf_path}")
            else:
                st.error("No record found for this Patient ID.")
        else:
            st.warning("Please enter a Patient ID.")
    st.markdown("</div>", unsafe_allow_html=True)