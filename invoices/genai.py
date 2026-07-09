from google import genai
from google.genai import types
from google.genai.errors import APIError
import os
from dotenv import load_dotenv
import json
import time
import logging
from django.contrib import messages

logger = logging.getLogger(__name__)

load_dotenv()

def Invoice_Analyse(invoice, retries=1):
    '''
    Use of gemini to analyse the pdf or image file of an invoice.
    Gemini gives a json based on our instructions.
    Returns a dictionary.
    '''

    api_key_str = os.getenv("GEMINI_API_KEY")

    i = 0
    while i < retries:
        try:
            client = genai.Client(api_key=api_key_str)

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
                        "Μονάδα μέτρησης": "...",
                        "Τιμή προϊόντος": 0.0,
                        "Ποσότητα": 0.0
                    }
                ],
                "Ποσά": {
                    "ΚΑΘΑΡΗ ΑΞΙΑ": 0.0, 
                    "ΦΠΑ": 0.0,
                    "Ποσοστό ΦΠΑ": 0 %,
                    "Σύνολο πληρωτέο": 0.0
                }
            }
            Στα πεδία των ποσών, της τιμής και της ποσότητας χρησιμοποίησε αποκλειστικά FLOAT αριθμούς (π.χ. 12.34),
            ποτέ με κόμμα. Επίσης η ημερομηνία πρέπει να είναι πάντα της μορφής DD/MM/YYYY.
            
            ΚΑΝΟΝΕΣ ΑΣΦΑΛΕΙΑΣ (VALIDATION):
            Εάν το έγγραφο ΔΕΝ είναι τιμολόγιο αγοράς/πώλησης (ή αν δεν αναγράφει ξεκάθαρα τη λέξη 'ΤΙΜΟΛΟΓΙΟ' ή 'INVOICE'), μην προσπαθήσεις να συμπληρώσεις την παραπάνω δομή. 
            Αντίθετα, επίστρεψε ΑΠΟΚΛΕΙΣΤΙΚΑ ΚΑΙ ΜΟΝΟ το παρακάτω JSON σφάλμα:
            {
                "error": "Το έγγραφο δέν είναι τιμολόγιο"
            }
            """


            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=[invoice, prompt],
                # This gives to gemini strict instructions for JSON file.
                config=types.GenerateContentConfig(
                    response_mime_type="application/json"
                ),
            )


            json_output_str = response.text

            try:
                response_dict = json.loads(json_output_str) # Creates a dictionary from json.
                return response_dict
            except json.JSONDecodeError as e:
                logger.error(f'The creation of dict from json on invoice analysis failed. {e}')
                messages.error(e)

        
        except APIError as e:
            logger.error(f'Failure! {e}')
            messages.error(e)
            return json

            
            

