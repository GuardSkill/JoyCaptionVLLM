from openai import OpenAI
import time



# Write a list of Booru tags for this image.
# Write a descriptive caption for this image in a formal tone.

ip_algo='192.168.5.212'
# ip_test='192.168.5.73'

#client = OpenAI(api_key='YOUR_API_KEY', base_url='http://192.168.5.212:8000/v1')

client = OpenAI(api_key='sk-2x1zj2w6q7jQ8q6Y5q6Y5q6Y', base_url=f'http://{ip_algo}:8000/v1')
prompt="what's your name"
T0=time.time()
model_name = client.models.list().data[0].id
print(model_name)
response = client.chat.completions.create(
    model=model_name,
    messages=[
        {
        'role':'system',
        'content': 'You are a helpful chat helper.',
        },
        {
        'role':'user',
        'content': [{
            'type': 'text',
            'text': prompt,
        }, ],
    }],
    temperature=0.9,
    top_p=0.7,
    max_tokens=256,
    # frequency_penalty=1.3
    )
print("====================================================")
print(response)
print(f"Time taken: {time.time() - T0} seconds")
print("====================================================")
