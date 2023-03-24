import os
import openai

openai.api_key = os.getenv("OPENAI_API_KEY")
if os.getenv("HTTP_PROXY"):
    openai.proxy = os.getenv("HTTPS_PROXY")
else:
    raise ValueError('HTTP_PROXY environment variable is not set')

response = openai.ChatCompletion.create(
  model="gpt-3.5-turbo",
  messages=[
    {"role": "user", "content": "What is the last human light if all humans suddenly disappear at the same time?"}
  ]
)
print(response)
