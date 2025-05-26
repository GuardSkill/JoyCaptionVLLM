curl -X POST 'http://192.168.5.212:8000/v1/chat/completions' \
-H 'Content-Type: application/json' \
-H 'Authorization: Bearer YOUR_API_KEY' \
-d '{
  "model": "llama-joycaption-alpha-two-hf-llava",
  "messages": [
    {
      "role": "user",
      "content": [
        {
          "type": "text",
          "text": "Write a descriptive caption for this image in a formal tone."
        },
        {
          "type": "image_url",
          "image_url": {
            "url": "http://192.168.5.202:8188/api/view?filename=8k.png&type=input&subfolder=&rand=0.8733174155693815"
          }
        }
      ]
    }
  ],
  "temperature": 0.8,
  "top_p": 0.8
}'
