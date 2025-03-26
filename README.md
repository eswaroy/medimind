# MediMind - AI-Powered Medical Assistant

MediMind is an AI-powered medical assistant that provides chatbot-based patient interactions and a voice-enabled prescription system. It integrates **Streamlit**, **MongoDB**, **Speech Recognition**, and **Machine Learning** for an interactive experience.

## Features

- **Doctor Chatbot:** Answer patient queries using NLP and predefined question sets.
- **Voice Assistant:** Recognize speech commands and add prescribed medicines.
- **Medicine Recommendation:** Suggest medicines using **TF-IDF** and **Fuzzy Matching**.
- **Prescription Generation:** Create PDFs of prescriptions and store them in MongoDB.
- **MongoDB Integration:** Save and retrieve patient data securely.

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/medimind.git
   cd medimind
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   streamlit run app.py
   ```

## Dependencies

The project requires the following Python libraries:
- `streamlit`
- `pandas`
- `requests`
- `scikit-learn`
- `speechrecognition`
- `pyttsx3`
- `fpdf`
- `joblib`
- `numpy`
- `pymongo`
- `rapidfuzz`
- `metaphone`

Install all dependencies using:
```bash
pip install -r requirements.txt
```

## Usage

1. **Start the Streamlit App:** Run `streamlit run app.py` and open the browser.
2. **Doctor Chatbot:** Enter patient data and ask health-related queries.
3. **Voice Assistant:** Speak medicine names and dosages for AI recognition.
4. **Generate Prescriptions:** Download a structured PDF for prescriptions.

## File Structure

```
medimind/
│── app.py                  # Main application script
│── dataset.csv              # Medicine dataset
│── requirements.txt         # Required dependencies
│── README.md                # Project documentation
│── prescriptions/           # Folder for generated PDFs
```

## API Integration

MediMind uses **Novita AI API** for NLP-based responses. Ensure you have an API key:
```python
API_KEY = "your-api-key"
API_URL = "https://api.novita.ai/v3/openai/chat/completions"
```

## Database Setup

Ensure MongoDB is running and configured properly:
```python
client = MongoClient("mongodb://localhost:27017/")
db = client['hackathon']
collection = db['mm']
```

## Contributing

Contributions are welcome! Feel free to fork the repository and submit a pull request.

## License

This project is licensed under the MIT License.
# Note the above info is completely only for app.py ( only is file with dataset.csv is enough for medimind ) all the other files are not needed. 

# Doctor’s Assistant

A web-based interface designed to assist physicians by providing real-time information about incoming patients. The application integrates with hospital management systems via APIs or databases, allowing doctors to access patient history, conditions, medications, and recent test results seamlessly.

## Features
- Interactive UI for physicians to view and query patient data
- Real-time connection to hospital management systems via API or database
- Answers questions about patient history, current conditions, medications, and test results
- AI-powered natural language processing to interpret physician queries
- Secure and scalable architecture for handling sensitive medical data

## Tech Stack

### Frontend
- *React*: JavaScript library for building a dynamic and responsive user interface
- *Tailwind CSS*: Utility-first CSS framework for rapid styling and design consistency

### Backend
- *Express*: Lightweight Node.js framework for building RESTful APIs and handling server-side logic
- *PyTorch*: Machine learning framework for powering AI-driven features (e.g., natural language processing)
- *Transformers (Hugging Face)*: Pre-trained models and tools like AutoTokenizer for processing physician queries and patient data
- *Faker*: Library for generating mock patient data during development and testing

### Database
- *MongoDB Cloud (Atlas)*: NoSQL database for storing patient records, histories, and metadata, hosted on the cloud for scalability and accessibility

### Integrations
- Hospital Management System (HMS) API or direct database connection for retrieving real-time patient data

## Prerequisites
- *Node.js*: v16.x or higher
- *Python*: v3.8 or higher (for PyTorch and Transformers)
- *MongoDB Atlas Account*: For cloud database setup
- *API Access*: Credentials or documentation for the hospital management system API (if applicable)
