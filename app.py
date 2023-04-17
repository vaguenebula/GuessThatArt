import base64
from flask import Flask, render_template, jsonify, request, session
import openai 
import os
import re
import requests
import random

with open('stop_words.txt', 'r') as f:
    stop_words = f.readlines()

stop_words = [word.rstrip() for word in stop_words]

def find_words(string):
    re.findall(r'\b\w+\b', string)

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
    
    words = re.findall(r'\b\w+\b', string)
    # find all words (not including symbols) in the paragraph using regex

    for word in words:
        if word.lower() not in stop_words:
            string = string.replace(word, '*' * len(word))
        # replace each word with asterisks of the same length
    return string

app = Flask(__name__)
app.secret_key = 'QYLMFqwci9HXf4ZPoG8Jgm4AWZphaMAB'

openai.api_key = "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"

genres = [
    'Landscape',
    'Fantasy',
    'Anime',
    'Cyberpunk'
]

@app.route("/")
@app.route("/home")
def home():
    random.shuffle(genres)
    return render_template('home.html', genres=genres)

@app.route("/about")
def about():
    return render_template('about.html', title='About')

@app.route('/endpoint', methods=['GET', 'POST'])
def endpoint():
    request_type = request.get_json()['request']
    
    if request_type == 'choose-genre':
        genre = request.get_json()['genre']
        my_data = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                    {"role": "system", "content": """
You write a prompt to generate art with the provided genre
Example:
landscapes
Prompt:
An oil painting of a cathedral in nature, stained glass, trees, mountains in the distance
                    """},
                    {"role": "user", "content": f"""
{genre}
Prompt:"""},
                ]
            )
        unknown_string = convert_to_asterisk(my_data['choices'][0]['message']['content'])

        session['prompt'] = my_data['choices'][0]['message']['content']
        session['unknowns'] = unknown_string
        session['guesses_left'] = 10
        print(session.get('prompt'))
        # temp_prompt = "a landscape, with a beautiful river"
        # unknown_string = convert_to_asterisk(temp_prompt)
        # session['prompt'] = temp_prompt
        # session['unknowns'] = unknown_string
        # session['guesses_left'] = 10
        session['correct'] = 0
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

        data = response.json()['artifacts'][0]['base64']
                
        html = render_template('guess.html', prompt=unknown_string, image=f"data:image/png;base64,{data}", guesses=10)
        
        return jsonify({'html':html})


    if request_type == "guess":
        html = None
        session['guesses_left'] -= 1
        word = request.get_json()['word']
        prompt = session.get('prompt')
        guesses_left = session.get('guesses_left')
        print(f'{guesses_left} guesses left')
        unknown_prompt = session.get('unknowns')
        prompt_words = string_to_array(prompt)
        indices = []
        
        if word in prompt_words:
            session['correct'] += 1
            index = prompt.find(word)
            while index != -1:
                indices.append(index)
                index = prompt.find(word, index + 1)
            for eachIndex in indices:
                unknown_prompt = unknown_prompt[:eachIndex] + word + unknown_prompt[eachIndex + len(word):]
            print(unknown_prompt)
            session['unknowns'] = unknown_prompt
            if guesses_left < 1:
                html = render_template("gameover.html", correct=4, total=len(prompt_words), prompt=session.get('prompt'))
            return {'value': True, 'new_prompt':unknown_prompt, 'html': html, 'guesses':session.get('guesses_left')}
        else:
            if guesses_left < 1:
                html = render_template("gameover.html", correct=session.get('correct'), total=len(prompt_words), prompt=session.get('prompt'))
            return {'value': False, 'html': html, 'guesses':session.get('guesses_left')}

    else:
        return None
    
if __name__ == '__main__':
    app.run(debug=True)