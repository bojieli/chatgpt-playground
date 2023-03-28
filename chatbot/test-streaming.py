import os
import openai
import sys

if os.getenv("OPENAI_API_KEY"):
    openai.api_key = os.getenv("OPENAI_API_KEY")
else:
    raise ValueError('OPENAI_API_KEY environment variable is not set')

if os.getenv("HTTP_PROXY"):
    openai.proxy = os.getenv("HTTP_PROXY")
else:
    raise ValueError('HTTP_PROXY environment variable is not set')

response = openai.ChatCompletion.create(
  model="gpt-3.5-turbo",
  messages=[
    {"role": "user", "content": "Write a sample code to use OpenSSL to communicate via a TLS socket."}
  ],
  stream=True
)
for snippet in response:
    try:
        sys.stdout.write(snippet.choices[0].delta.content)
        sys.stdout.flush()
    except:
        pass
