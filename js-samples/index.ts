/**
 * @license
 * Copyright 2019 Google LLC. All Rights Reserved.
 * SPDX-License-Identifier: Apache-2.0
 */

import { create } from "domain";

const created_markers = {}
async function initMap() {
    // Request needed libraries.
    const { Map } = await google.maps.importLibrary("maps") as google.maps.MapsLibrary;
    const { AdvancedMarkerElement } = await google.maps.importLibrary("marker") as google.maps.MarkerLibrary;
    const myLatlng = { lat: -25.363, lng: 131.044 };

    const map = new Map(document.getElementById('map') as HTMLElement, {
        center: myLatlng,
        zoom: 14,
        mapId: '4504f8b37365c3d0',
    });

    map.addListener("rightclick", (e) => {
        addMarker(e.latLng, map)
    });

    const bounds: google.maps.LatLngBoundsLiteral = {
        north: -25.363882,
        south: -31.203405,
        east: 131.044922,
        west: 125.244141,
    };

    // Display the area between the location southWest and northEast.
    map.fitBounds(bounds);

    const marker = new AdvancedMarkerElement({
        map,
        position: myLatlng,
        title: "Ciao Tony",
    });
}

const submitLocation = (latLng: string): void => {
    const nameElement = document.getElementById('location-name') as HTMLInputElement;
    const descriptionElement = document.getElementById('location-description') as HTMLTextAreaElement;
    const marker = created_markers[latLng];
    const name = nameElement.value;
    const description = descriptionElement.value;
    marker["title"] = name + ',' + description;
    marker.infowindow.close();

    google.maps.event.clearListeners(marker, "click");

    const infowindow = new google.maps.InfoWindow({
        content: createInfoWindowEvent(name, description),
    });

    marker.infowindow = infowindow;
    marker.addListener("click", () => {
        infowindow.open(marker.map, marker);
    });

    console.log('Location submitted:', { name, description });
};

const createInfoWindowEvent = (name: string, descr: string): string => {
  return `
    <div style="padding: 10px; font-family: Arial, sans-serif;">
      <h3 style="margin-bottom: 10px;">Event Information</h3>
      <div type="text" id="location-name" style="width: 100%; padding: 5px; margin-bottom: 10px;">${name}</div>
      <div id="location-description" style="width: 100%; height: 100px; padding: 5px; margin-bottom: 10px;">${descr}</div>
      <button onclick='buyTicket()' style="background-color: #4CAF50; color: white; padding: 10px 15px; border: none; cursor: pointer;">Buy Ticket</button>
    </div>
  `;

};

const createInfoWindowContent = (latLng: string): string => {
  const latLngStr = JSON.stringify(latLng);
  return `
    <div style="padding: 10px; font-family: Arial, sans-serif;">
      <h3 style="margin-bottom: 10px;">Enter Location Details</h3>
      <input type="text" id="location-name" placeholder="Location Name" style="width: 100%; padding: 5px; margin-bottom: 10px;">
      <textarea id="location-description" placeholder="Description" style="width: 100%; height: 100px; padding: 5px; margin-bottom: 10px;"></textarea>
      <button onclick='submitLocation(${latLngStr})' style="background-color: #4CAF50; color: white; padding: 10px 15px; border: none; cursor: pointer;">Submit</button>
    </div>
  `;
};

(window as any).submitLocation = submitLocation;

async function addMarker(latLng: google.maps.LatLng, map: google.maps.Map){
    
    var marker = new google.maps.marker.AdvancedMarkerElement({
        position: latLng,
        map: map,
    });
    const latLngStr = JSON.stringify(latLng.lat() + ';' + latLng.lng());

    const infowindow = new google.maps.InfoWindow({
        content: createInfoWindowContent(latLngStr),
    });

    marker.infowindow = infowindow;

    marker.addListener("click", () => {
        infowindow.open(marker.map, marker);
    });

    created_markers[latLngStr] = marker;

    // map.panTo(latLng);
};


initMap();
export { };