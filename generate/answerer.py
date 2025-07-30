import os
#from dotenv import load_dotenv
#from openai import OpenAI

#load_dotenv()
#client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def answer_query(query, results):
    #messages = [
       #{"role": "system", "content": "You are a helpful assistant."},
        #{"role": "user", "content": f"Use the following context to answer the question:\n\n{context}\n\nQuestion: {query}"}
    #]
    #response = client.chat.completions.create(
        #model="gpt-3.5-turbo",  # or "gpt-3.5-turbo" if needed
        #messages=messages,
        #temperature=0.7,
        #max_tokens=512,
    #)
    #return response.choices[0].message.content.strip()
    return results
