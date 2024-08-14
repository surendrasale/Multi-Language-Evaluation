from nltk.translate.bleu_score import sentence_bleu
import pandas as pd
import requests
import json
import asyncio
import aiohttp

async def calculate_bleu_score(reference, candidate):
    return sentence_bleu([reference], candidate)

# Function to translate the given text to the given language
def translate_text(text, target_language):
    translator = Translator()
    try:
        translated_text = translator.translate(text, dest=target_language)
        return translated_text.text
    except Exception as e:
        print(f"Translation failed: {e}")
        return None

# Function to get the token
async def get_ai_api_access_token():
    access_token = None
    base_app_link = "http://localhost:9999/ai/api/v1/copilot/admin/ask"
    client_id = "a9e13fc9fb47e706140833ccde2760d3"
    client_secret = "hahsgygwabaabsjajkuhegmgb"
    scope = "ai.integrations.api"

    async with aiohttp.ClientSession() as session:
        token_data = {
            "grant_type": "client_credentials",
            "client_id": client_id,
            "client_secret": client_secret,
            "scope": scope
        }

        async with session.post(base_app_link, data=token_data) as response:
            token_response = await response.json()

            if "error" in token_response:
                raise Exception(token_response["error_description"])

            access_token = token_response.get("access_token")

    return access_token 
# Function to make API request and translate the response
def get_response(question,access_token,language):
    url = "https://dev-bolddesksupport.bolddesk.com/ai/api/v1/copilot/ticket/ask"
    header = {"Authorization": f"Bearer {access_token}"}
    data = {
    "ticketId": 544846,
   "message" : question,
   "GenerateTicketConversationReply" : False
    }
    response = requests.post(url,headers=header, json = data)
    if(response.status_code == 400):
        access_token = get_ai_api_access_token()
        header = {"Authorization": f"Bearer {access_token}"}
        response = requests.post(url,headers=header, json=data)
    if(response.status_code == 400) :
       access_token = get_ai_api_access_token()
       get_response(question=question,access_token = access_token) 
    print(response.text)
    print(language)
    #Translating response to English
    translated_response = translate_text(response.text, 'en')  
    return response.text
    #return response.text
# Function to process the CSV file having the questions
def process_excel(input_file, output_file, access_token):
    df = pd.read_excel(input_file)
    #languages = ['en','es','de','fr','it','pt','cs','ja','no','fi','ko', 'pl', 'sv', 'uk', 'ru', 'ro', 'nl', 'el', 'hu', 'fil','id', 'vi', 'ms', 'th', 'zh-CN', 'tr', 'bg', 'da', 'zh-TW']
    languages =['es','no']
    # Create a DataFrame to store the translated data
    translated_data = []   
    
    for index in range(len(df)):
        row = df.iloc[index] 
        question = row['Question']       
        # Translate the question to English (assuming English is the source language)
        for target_language in languages:
            translated_question = translate_text(question, target_language)
            response = get_response(translated_question, access_token, target_language)    
            json_data = json.loads(response)
            generated_message = json_data.get("generatedMessage", "")
            translated_message = translate_text(generated_message, 'en-US')
            if(target_language == 'en-US'):
                original_answer = translated_message
            comparison_report = original_answer
            # Append translated data to list
            translated_data.append([question,target_language,translated_question, generated_message,generated_message])
    
    # Create a DataFrame from the translated data
    translated_df = pd.DataFrame(translated_data, columns=['Question', 'Language','Translated Question','Generated Answer','Translated Answer'])
    
    # Write the translated data to a new Excel file
    translated_df.to_excel(output_file, index=False)
    print(f"Translated data has been written to {output_file}")

async def main():
    input_file = 'questions.xlsx'  
    output_file = 'GoogleTransNormal.xlsx'
    # Calling the process_csv method
    access_token = await get_ai_api_access_token()
    process_excel(input_file, output_file,access_token)

if __name__ == "__main__":
    asyncio.run(main())
