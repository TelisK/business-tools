from google import genai
from google.genai import types
from income_expenses.views import get_totals, last_years_income_comparison, income_totals_calculation
import os
from dotenv import load_dotenv

client = genai.Client()

INSTRUCTION = '''
Είσαι ο ΑΙ Βοηθός για ένα site που αναλύει οικονομικά δεδομένα. Μιλάς μόνο ελληνικά.
Απαντάς μόνο σε ότι αφορά τα οικομικά δεδομένα του καταστήματος, και τίποτα άλλο.
Σε άσχετο prompt αρνήσου ευγενικά λέγοντας 'Η ερώτηση δέν σχετίζεται με την εργασία μου στην εφαρμογή'.
Έχεις στη διάθεσή σου συγκεκριμένα εργαλεία για να τραβάς δεδομένα από τη βάση.
'''

api_key_str = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key_str)

def gemini_agent(store, question):
    tools = [get_totals, last_years_income_comparison]

    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=question,
        config=types.GenerateContentConfig(
            system_instruction=INSTRUCTION,
            tools=tools,
        ),
    )

    if response.function_calls:
        for f_call in response.function_calls:
            # Gives the name of the tool and the arguments.
            name = f_call.name
            args = f_call.args

            print(f"[DEBUG] Το Gemini αποφάσισε να καλέσει το εργαλείο: {name} με ορίσματα {args}")
            if name == 'get_totals':
                result = get_totals(store=store.id)
            elif name == 'last_years_income_comparison':
                result = last_years_income_comparison(store=store.id)
            elif name == 'income_totals_calculation':
                result = income_totals_calculation(store=store.id)

        # We have to create a chat history, so at the next response, ai will
        # be able to see the previous conversation.
        chat_history = [
                types.Content(role="user", parts=[types.Part.from_text(text=question)]),
                response.candidates[0].content,  # Gemini calls function call
                types.Content(
                    role="tool", 
                    parts=[
                        types.Part.from_function_response(
                            name=name,
                            response={"result": result}  # result of Django ORM
                        )
                    ]
                )
        ]

        second_response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=chat_history,
        config=types.GenerateContentConfig(
            system_instruction=INSTRUCTION,
            tools=tools,
        ),
        )
        
        return second_response.text

    return response.text

'''
AΠΟΤΕΛΕΣΜΑΤΑ ΜΕΣΩ ΤΟΥ SHELL.
>>> result_1 = gemini_agent(store=store_obj, question="Ποια είναι τα συνολικά έσοδα του καταστήματος απο 1 ιανουαρίου 2026 μέχρι σήμερα;")
INFO 2026-07-07 01:02:59,677 models: AFC is enabled with max remote calls: 10.
INFO 2026-07-07 01:03:02,374 _client: HTTP Request: POST https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent "HTTP/1.1 200 OK"
>>> print(f"Απάντηση Agent: {result_1}")
Απάντηση Agent: Παρακαλώ δώστε μου το αναγνωριστικό του καταστήματος (store ID) για να σας εμφανίσω τα συνολικά έσοδα από 1 Ιανουαρίου 2026 έως και σήμερα.
>>> result_1 = gemini_agent(store=store_obj, question=f"Ποια είναι τα συνολικά έσοδα του καταστήματος με id {store_obj.i
d} απο 1 ιανουαρίου 2026 μέχρι σήμερα;")
INFO 2026-07-07 01:03:59,737 models: AFC is enabled with max remote calls: 10.
INFO 2026-07-07 01:04:08,869 _client: HTTP Request: POST https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent "HTTP/1.1 200 OK"
INFO 2026-07-07 01:04:08,893 models: AFC remote call 1 is done.
Traceback (most recent call last):
'''