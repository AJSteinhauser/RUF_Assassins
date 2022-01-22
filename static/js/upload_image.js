const button = document.getElementById('submit_image');
var shown = false;

function showSpinner(){
    if (!shown){
        shown = true;
        var spinner = document.createElement('span');
        spinner.className = 'spinner-border spinner-border-sm'
        button.appendChild(spinner);
        document.getElementById("overlay").style.display = "block";
    }
}
