
import instrumentation.langfuse
from openai import OpenAI
 
openai_client = OpenAI()
chat_completion = openai_client.chat.completions.create(
    messages=[
        {
          "role": "user",
          "content": "Finish this sentence: 'Roses are red, violets are blue, I like purple shoes, and so should...",
        }
    ],
    model="gpt-4o-mini",
)
 
print(chat_completion)