from google import genai
from google.genai import types
from google.genai.errors import APIError
import os
from dotenv import load_dotenv
import json
import time


def Invoice_Analyse(invoice, retries=3):
    print('started THE ANALYSIS .......')

    api_key_str = os.getenv("gemini_api")


    if not api_key_str:
        print("❌ ΣΦΑΛΜΑ: Το αρχείο .env δεν διαβάστηκε σωστά ή λείπει το API")
    else:
        print(f"✅ Το κλειδί βρέθηκε και ξεκινάει με: {api_key_str[:7]}...")  # I've got None...

    i = 0
    while i <= retries:
        try:
            client = genai.Client(api_key=api_key_str)
            #client = genai.Client(api_key=os.getenv("gemini_api"))

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
                        "Μονάδα μέτρησης": "..."
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
            break
        except APIError as e:
            print(f'Σφάλμα! - {e}')
            print(f'Αυτόματη επανάληψη σε 5 δευτερόλεπτα. Προσπάθεια {i} απο {retries}')
            time.sleep(5)
            i += 1
            

