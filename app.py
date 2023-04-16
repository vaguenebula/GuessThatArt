import base64
from flask import Flask, render_template, jsonify, request, session
import openai 
import os
import re
import requests

api_host = os.getenv('API_HOST', 'https://api.stability.ai')
url = f"{api_host}/v1/user/account"

api_key = 'sk-SlOyxUzvLWnkZdBo9apyzq9y0H3nh6n3LbsXOtft3C31I9j6'
if api_key is None:
    raise Exception("Missing Stability API key.")

response = requests.get(url, headers={
    "Authorization": f"Bearer {api_key}"
})

if response.status_code != 200:
    raise Exception("Non-200 response: " + str(response.text))

def string_to_array(text):
    # Replace all non-alphanumeric characters with spaces
    text = re.sub(r'[^\w\s]', ' ', text)
    # Split the string into words
    words = text.split()
    return words

def convert_to_asterisk(string):
    # Replace all non-symbol characters with an asterisk
    return re.sub(r'[^\W_]', '*', string)

app = Flask(__name__)
app.secret_key = 'QYLMFqwci9HXf4ZPoG8Jgm4AWZphaMAB'

openai.api_key = "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"

genres = [
    'landscapes',
    'fantasy',
    'anime grill'
]

@app.route("/")
@app.route("/home")
def hello():
    return render_template('home.html', genres=genres)

@app.route("/about")
def about():
    return render_template('about.html', title='About')

@app.route('/endpoint', methods=['GET', 'POST'])
def endpoint():
    request_type = request.form['request']
    
    if request_type == 'choose-genre':
        genre = request.form['genre']
        my_data = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                    {"role": "system", "content": "You write a prompt to generate art with the provided genre"},
                    {"role": "user", "content": genre},
                ]
            )
        unknown_string = convert_to_asterisk(my_data['choices'][0]['message']['content'])

        session['prompt'] = my_data['choices'][0]['message']['content']
        session['unknowns'] = unknown_string
        session['guesses_left'] = 10

        response = requests.post(
            f"{api_host}/v1/generation/stable-diffusion-v1-5/text-to-image",
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Authorization": f"Bearer {api_key}"
            },
            json={
                "text_prompts": [
                    {
                        "text": "{%s}" % my_data['choices'][0]['message']['content']
                    }
                ],
                "cfg_scale": 7,
                "clip_guidance_preset": "FAST_BLUE",
                "height": 512,
                "width": 512,
                "samples": 1,
                "steps": 20,
            },
        )

        data = response.json()
        print(data.keys())
        print(data['message'])
        for image in data['message']:
            with open(f"./static/img/txt2img.png", "wb") as f:
                f.write(base64.b64decode(image["base64"]))
                
        html = render_template('guess.html', prompt=unknown_string)
        
        return jsonify({'html':html})


    if request_type == "guess":
        session['guesses_left'] -= session['guesses_left'] - 1
        word = request.form['word']
        prompt = session.get('prompt')
        guesses_left = session.get('guesses_left')
        print(f'{guesses_left} guesses left')
        unknown_prompt = session.get('unknowns')
        prompt_words = string_to_array(prompt)
        print(prompt_words)
        indices = []
        
        if word in prompt_words:
            index = prompt.find(word)
            while index != -1:
                indices.append(index)
                index = prompt.find(word, index + 1)
            for eachIndex in indices:

                unknown_prompt = unknown_prompt[:eachIndex] + word + unknown_prompt[eachIndex + len(word):]
            print(unknown_prompt)
            session['unknowns'] = unknown_prompt
            return {'value': True, 'new_prompt':unknown_prompt}
        else:
            return {'value': False}

    else:
        return None
    
if __name__ == '__main__':
    app.run(debug=True)