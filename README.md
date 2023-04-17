# GuessThatArt
A web application made with flask for guessing the prompt that was used to generate an image

Install dependences
```
pip install -r requirements.txt
```

Description:
First a prompt is generated via ChatGPT with the given genre. Then, an image is generated via stability's API. The goal is to guess the most amount of words possible with 10 guesses. 

TODOS:
- Make a better system message for larger variety of prompts
- Add a feature to combine multiple genres
- Make UI more visually appealing (transitions, loading, etc.)
- Add a feature where you can buy letters, which reveals all of a certain character
