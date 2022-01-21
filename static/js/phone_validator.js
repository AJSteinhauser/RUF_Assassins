const input = document.getElementById('phonenumber');
var error = document.createTextNode("No symbols, numbers only please");
var created = false;


input.addEventListener('input', function(e){
    if (input.value != parseInt(input.value).toString()){
        if (!created){
            input.insertAdjacentHTML('afterend', 
                "<small id='phonewrong' class='form-text text-danger'>Numbers 0-9 only, no other symbols!</small><br>"
            );
            created = true;
        }
    }
    else{ 
        if (created){
            var errormsg = document.getElementById("phonewrong");
            errormsg.nextElementSibling.remove();
            errormsg.remove();
            created = false;
        }
    }
});
