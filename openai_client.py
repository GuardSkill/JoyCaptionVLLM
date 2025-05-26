from openai import OpenAI
import time


# test Speed
# 8k http://192.168.5.202:8188/api/view?filename=8k.png&type=input&subfolder=&rand=0.8733174155693815
# 4k http://192.168.5.202:8188/api/view?filename=4K_style.png&type=input&subfolder=&rand=0.6650523105541957
# 1M http://192.168.5.202:8188/api/view?filename=1723684603510.jpg&type=input&subfolder=&rand=0.19313660479423955


# Write a list of Booru tags for this image.
# Write a descriptive caption for this image in a formal tone.

ip_algo='192.168.5.212'
# ip_test='192.168.5.73'

#client = OpenAI(api_key='YOUR_API_KEY', base_url='http://192.168.5.212:8000/v1')

client = OpenAI(api_key='sk-2x1zj2w6q7jQ8q6Y5q6Y5q6Y', base_url=f'http://{ip_algo}:8000/v1')
prompt_types={
            # "Tag":"Write a list of Booru tags for this image.",
            # "Tag":"Write a medium-length list of Booru tags for this image.",
            "Des":"Write a descriptive caption for this image in a casual tone."
             }
image_types ={
    '8k':'http://192.168.5.202:8188/api/view?filename=8k.png&type=input&subfolder=&rand=0.8733174155693815',
             '4k':'http://192.168.5.202:8188/api/view?filename=4K_style.png&type=input&subfolder=&rand=0.6650523105541957',
             '1M':'http://192.168.5.202:8188/api/view?filename=1723684603510.jpg&type=input&subfolder=&rand=0.19313660479423955',
             "other":'http://192.168.5.202:8188/api/view?filename=node100_img_piclumen-1730464298039_batch_3.png&type=input&subfolder=&rand=0.37784726838166005',
             'o':'http://192.168.5.202:8188/api/view?filename=node100_img_objectremoval0914-12_batch_3.png&type=input&subfolder=&rand=0.4006107006928965',
             'o':'http://192.168.5.202:8188/api/view?filename=ComfyUI_10137_.png&type=input&subfolder=&rand=0.6432082526743816',
             'o':'http://192.168.5.202:8188/api/view?filename=ComfyUI_10134_.png&type=input&subfolder=&rand=0.5533343923745246',
             'o':'http://192.168.5.202:8188/api/view?filename=ComfyUI_29994_.png&type=input&subfolder=&rand=0.43000343772787253',
             'o':'http://192.168.5.202:8188/api/view?filename=ComfyUI_10898_.png&type=input&subfolder=&rand=0.5196052075904098'
             }
            

while(1):
    for img_type, img_url in image_types.items():
        for prompt_type, prompt in prompt_types.items():
            T0=time.time()
            model_name = client.models.list().data[0].id
            response = client.chat.completions.create(
                model=model_name,
                messages=[
                    {
                    'role':'system',
                    'content': 'You are a helpful image captioner.',
                    },
                    {
                    'role':'user',
                    'content': [{
                        'type': 'text',
                        'text': prompt,
                    }, {
                        'type': 'image_url',
                        'image_url': {
                            'url':img_url,
                        },
                    }],
                }],
                temperature=0.9,
                top_p=0.7,
                max_tokens=256,
                # frequency_penalty=1.3
                )
            print("====================================================")
            print(response)
            print(f"Prompt: {prompt_type}",f"Image: {img_type}")
            print(f"Time taken: {time.time() - T0} seconds")
            print("====================================================")
