from google import genai
#from dotenv import load_dotenv
from os import getenv


def ask_question_to_gemini(prompt:str,api_key) -> str :
    #load_dotenv()
    client = genai.Client(api_key=api_key)

    response =client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
    )
    print(response)
    return(response.text)