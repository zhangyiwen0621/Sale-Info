var map;
var service;
var pos;
var infoWindow;
var brand;
var zipCode;

function initMap() {
  var locationInput = $("#location");
  brand = locationInput.text();
  var zipCodeInput = $("#zipcode");
  zipCode = zipCodeInput.val();
  if (!zipCode) {
    zipCode = "15217";
  }
  var pitts = {lat: 40, lng: -80};
  map = new google.maps.Map(document.getElementById('map'), {
    zoom: 12,
    center: pitts
  });

  infoWindow = new google.maps.InfoWindow();

  var currlat;
  var currlng;
  var geocoder = new google.maps.Geocoder();
  geocoder.geocode( { 'address': zipCode}, function(results, status) {
    if (status == google.maps.GeocoderStatus.OK) {
      currlat = results[0].geometry.location.lat();
      currlng = results[0].geometry.location.lng();
    } else {
      alert("Geocode was not successful for the following reason: " + status);
      currlat = 40;
      currlng = -80;
    }

    pos = {
      lat: currlat,
      lng: currlng
    };

    var marker = new google.maps.Marker({
      position: pos,
      map: map
    });

    map.setCenter(pos);
    map.addListener('idle', performSearch);

  });
}

function performSearch() {
  var request = {
    location: pos,
    radius: '50000',
    name: brand
  }
  service = new google.maps.places.PlacesService(map);
  service.nearbySearch(request, handleSearchResults);
}

function handleSearchResults(results, status) {
  for (var i = 0; i < results.length; i++) {
    addMarker(results[i]);
  }
}

function addMarker(place) {
  var marker = new google.maps.Marker({
    map: map,
    position: place.geometry.location,
    icon: {
      url: 'https://developers.google.com/maps/documentation/javascript/images/circle.png',
      anchor: new google.maps.Point(10, 10),
      scaledSize: new google.maps.Size(10, 17)
    }
  });

  google.maps.event.addListener(marker, 'click', function() {
    service.getDetails(place, function(result, status) {
      if (status !== google.maps.places.PlacesServiceStatus.OK) {
        console.error(status);
        return;
      }
      infoWindow.setContent('<div>' + result.name + '</div>' + '<div>' + result.formatted_address + '</div>');
      infoWindow.open(map, marker);
    });
  });
}
