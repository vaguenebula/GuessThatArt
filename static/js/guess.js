function guessPrompt() {
    var word = document.getElementById('guess-input').value
    console.log(word)
    if (word !== ""){
        fetch('/endpoint', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({"request": "guess", "word": word})
        }).then(res => {
            return res.json()
        }).then(data => {
            if (data.value) {
                document.getElementById('prompt_text').innerHTML = data.new_prompt
                document.getElementById('guesses').innerHTML = 'Guesses left: ' + data.guesses
                document.getElementById('guess-input').value = ''
            }
            else {
                document.getElementById('guesses').innerHTML = 'Guesses left: ' + data.guesses
                document.getElementById('guess-input').value = ''
            }
            if (data.html !== null) {
                document.getElementById('result').innerHTML = data.html
            }
        })
    }
}