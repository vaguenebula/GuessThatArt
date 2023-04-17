function chooseGenre(button) {
    var genre = button.value;
    document.getElementById('overlay').style.display = 'flex'
    fetch('/endpoint', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({"request": "choose-genre", "genre": genre})
    }).then(res => {
        return res.json()
    }).then(data => { 
        document.getElementById('overlay').style.display = 'none'
        document.getElementById('choose-genre').style.display = 'none'
        document.getElementById('result').innerHTML = data.html
    })
}