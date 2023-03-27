import openai
import os

openai.api_key = os.getenv("OPENAI_API_KEY")
if os.getenv("HTTP_PROXY"):
    openai.proxy = os.getenv("HTTP_PROXY")
else:
    raise ValueError('HTTP_PROXY environment variable is not set')

embedding = openai.Embedding.create(
    input="The University of Science and Technology of China (USTC) is a public research university in Hefei, Anhui, China.", model="text-embedding-ada-002"
)
print(len(embedding["data"][0]["embedding"]))
print(embedding["usage"]["total_tokens"])
