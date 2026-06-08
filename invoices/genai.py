from google import genai
from google.genai import types
from google.genai.errors import APIError
import os
from dotenv import load_dotenv
import json
import time

load_dotenv()

def Invoice_Analyse(invoice, retries=1):

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

            try:
                response_dict = json.loads(json_output_str)
                return response_dict
            except json.JSONDecodeError as e:
                print(e)

        
        except APIError as e:
            print(f'Σφάλμα!! - {e}')
            i += 1
            # if i > retries:
            #     print(f'Σφάλμα!! - {e}')
            #     return {'status':'error' , 'message':f'Σφάλμα! - {str(e)}'}

            # time.sleep(5)
            # print(f'Αυτόματη επανάληψη σε 5 δευτερόλεπτα. Προσπάθεια {i} απο {retries}')
           
            
            

