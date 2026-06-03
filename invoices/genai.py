import google.generativeai as genai
from dotenv import load_dotenv

def Invoice_Analyse(invoice):

    genai.configure(api_key=load_dotenv('gemini_api'))
    model = genai.GenerativeModel("gemini-1.5-flash")

    # if invoice