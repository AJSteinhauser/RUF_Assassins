var map;
var marker = false; 
var pos,locationButton, spinner;

const DEBUG_MODE = false;

function success(position){
    pos = {
        lat: position.coords.latitude,
        lng: position.coords.longitude,
    };
    spinner.remove();
    locationButton.textContent = "Pan To Current Location";
    locationButton.disabled = false;

}

function failure(err){
    console.warn(`ERROR(${err.code}): ${err.message}`);
    if (DEBUG_MODE)
        document.getElementById("alttext").textContent = err.code.toString() + "\n" +err.message.toString()
}
        

function initMap() {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(success,failure);
    }
    var centerOfMap = new google.maps.LatLng(33.95156072962477, -83.37603784190308);
    

    var options = {
      center: centerOfMap,
      zoom: 16,
      disableDefaultUI: true,
      zoomControl: true,
    };

    map = new google.maps.Map(document.getElementById('map'), options);

    locationButton = document.createElement("button");
    locationButton.classList.add("btn")
    locationButton.classList.add("btn-primary")
    locationButton.style.cssText += "margin-top: 10px"

    locationButton.textContent = "Loading Current Location ";
    locationButton.disabled = true;
    map.controls[google.maps.ControlPosition.TOP_CENTER].push(locationButton);
    spinner = document.createElement('span');
    spinner.className = 'spinner-border spinner-border-sm'
    locationButton.appendChild(spinner);
    locationButton.addEventListener("click", () => {
        if(marker === false){
            marker = new google.maps.Marker({
                position: pos,
                map: map,
                draggable: true 
            });
            google.maps.event.addListener(marker, 'dragend', function(event){
                markerLocation();
            });
        } else{
            marker.setPosition(pos);
        }
        markerLocation();
        map.panTo(pos);
    });

    google.maps.event.addListener(map, 'click', function(event) {                
        var clickedLocation = event.latLng;
        if(marker === false){
            marker = new google.maps.Marker({
                position: clickedLocation,
                map: map,
                draggable: true
            });
            google.maps.event.addListener(marker, 'dragend', function(event){
                markerLocation();
            });
        } else{
            marker.setPosition(clickedLocation);
        }
        markerLocation();
    });
}
        
function markerLocation(){
    var currentLocation = marker.getPosition();
    document.getElementById('lat_send').value = currentLocation.lat(); //latitude
    document.getElementById('long_send').value = currentLocation.lng(); //longitude
}
