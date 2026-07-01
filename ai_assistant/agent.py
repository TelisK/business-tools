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
    tools = [get_totals, last_years_income_comparison, income_totals_calculation]

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
        if name == get_totals:
            result = get_totals(store=store)
        if name == last_years_income_comparison:
            result = last_years_income_comparison(store=store)
        if name == income_totals_calculation:
            result = income_totals_calculation(store=store)

    # CONTINUE HERE

    return final_result.text