from google import genai
from google.genai import types
import os
from dotenv import load_dotenv
import json

load_dotenv()

def Invoice_Analyse(invoice):
    print('started THE ANALYSIS .......')
    client = genai.Client(api_key=os.getenv('gemini_api'))

    prompt = """Ανέλυσε το παρακάτω τιμολόγιο και παρουσίασε μου τα στοιχεία σε μορφή JSON.
    Η δομή του JSON θα πρέπει να είναι ακριβώς η εξής:
    {
        "Αριθμός Τιμολογίου": "...",
        "ΑΦΜ προμηθευτή": "...",
        "Προμηθευτής": "...",
        "Ημερομηνία": "...",
        "Προϊόντα": [
            {
                "Κωδικός προϊόντος": "...",
                "Όνομα προϊόντος": "...",
                "Τιμή προϊόντος": 0.0,
                "Ποσότητα": 0.0
            }
        ],
        "Ποσά": {
            "ΚΑΘΑΡΗ ΑΞΙΑ": 0.0, 
            "ΦΠΑ": 0.0,
            "Σύνολο πληρωτέο": 0.0
        }
    }
    Στα πεδία των ποσών, της τιμής και της ποσότητας χρησιμοποίησε αποκλειστικά FLOAT αριθμούς (π.χ. 12.34), ποτέ με κόμμα."""


    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[invoice, prompt],
        # This gives to gemini strict instructions for JSON file.
        config=types.GenerateContentConfig(
            response_mime_type="application/json"
        ),
    )


    json_output_str = response.text

    print(json_output_str)