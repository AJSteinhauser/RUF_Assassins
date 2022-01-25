// Note: This example requires that you consent to location sharing when
// prompted by your browser. If you see the error "The Geolocation service
// failed.", it means you probably did not give permission for the browser to
// locate you.
//map.js

//Set up some of our variables.
var map; //Will contain map object.
var marker = false; ////Has the user plotted their location marker? 


        
//Function called to initialize / create the map.
//This is called when the page has loaded.
function initMap() {

    //The center location of our map.
    var centerOfMap = new google.maps.LatLng(33.95156072962477, -83.37603784190308);

    //Map options.
    var options = {
      center: centerOfMap, //Set center.
      zoom: 16, //The zoom value.
      disableDefaultUI: true,
      zoomControl: true
    };

    //Create the map object.
    map = new google.maps.Map(document.getElementById('map'), options);

    const locationButton = document.createElement("button");
    locationButton.classList.add("btn")
    locationButton.classList.add("btn-primary")
    locationButton.style.cssText += "margin-top: 5px"

    locationButton.textContent = "Pan to Current Location";
    //locationButton.classList.add("custom-map-control-button");
    map.controls[google.maps.ControlPosition.TOP_CENTER].push(locationButton);
    locationButton.addEventListener("click", () => {
        // Try HTML5 geolocation.
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(
                (position) => {
                const pos = {
                    lat: position.coords.latitude,
                    lng: position.coords.longitude,
                };
                if(marker === false){
                    //Create the marker.
                    marker = new google.maps.Marker({
                        position: pos,
                        map: map,
                        draggable: true //make it draggable
                    });
                    //Listen for drag events!
                    google.maps.event.addListener(marker, 'dragend', function(event){
                        markerLocation();
                    });
                } else{
                    //Marker has already been added, so just change its location.
                    marker.setPosition(pos);
                }
                map.panTo(pos);
                },
                () => {
                handleLocationError(true, infoWindow, map.getCenter());
                }
            );
        }
    });

    //Listen for any clicks on the map.
    google.maps.event.addListener(map, 'click', function(event) {                
        //Get the location that the user clicked.
        var clickedLocation = event.latLng;
        //If the marker hasn't been added.
        if(marker === false){
            //Create the marker.
            marker = new google.maps.Marker({
                position: clickedLocation,
                map: map,
                draggable: true //make it draggable
            });
            //Listen for drag events!
            google.maps.event.addListener(marker, 'dragend', function(event){
                markerLocation();
            });
        } else{
            //Marker has already been added, so just change its location.
            marker.setPosition(clickedLocation);
        }
        //Get the marker's location.
        markerLocation();
    });
}
        
//This function will get the marker's current location and then add the lat/long
//values to our textfields so that we can save the location.
function markerLocation(){
    //Get location.
    var currentLocation = marker.getPosition();
    //Add lat and lng values to a field that we can save.
    //document.getElementById('lat').value = currentLocation.lat(); //latitude
    //document.getElementById('lng').value = currentLocation.lng(); //longitude
}


        
//Load the map when the page has finished loading.