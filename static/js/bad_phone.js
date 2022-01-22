

function startTimer(duration, display, start_text) {
    var timer = duration, minutes, seconds;
    setInterval(function () {
        minutes = parseInt(timer / 60, 10);
        seconds = parseInt(timer % 60, 10);

        minutes = minutes < 10 ? "0" + minutes : minutes;
        seconds = seconds < 10 ? "0" + seconds : seconds;

        display.textContent = start_text + minutes + ":" + seconds;

        console.log(display.textContent)
        console.log(display)

        if (--timer < 0) {
            timer = duration;
            location.reload()
        }
    }, 1000);
}

async function bad_phone(){
    const node = document.getElementById("errormsg")
    const start_text = "There has been a problem, reloading page in "
    node.textContent = start_text + "00:05"
    startTimer(5,node,start_text)
}