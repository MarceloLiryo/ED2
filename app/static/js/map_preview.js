document.addEventListener("DOMContentLoaded", () => {
    const mapElement = document.getElementById("map-preview");
    if (!mapElement || typeof L === "undefined") return;

    const map = L.map("map-preview").setView([20, 0], 2);

    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
        minZoom: 2,
        maxZoom: 8,
        attribution: "&copy; OpenStreetMap contributors"
    }).addTo(map);

    const countries = Array.isArray(window.countriesData) ? window.countriesData : [];

    countries.forEach((item) => {
        if (!Array.isArray(item.coordinates) || item.coordinates.length !== 2) return;
        const [lat, lng] = item.coordinates;
        if (typeof lat !== "number" || typeof lng !== "number") return;

        const marker = L.marker([lat, lng]).addTo(map);
        marker.bindPopup(
            `<strong>${item.country} (${item.code})</strong><br>` +
            `Região: ${item.region}<br>` +
            `Operadora: ${item.provider} · <b>${item.tech}</b>`
        );
    });

    // Se estiver na tela de Admin, clicar no mapa preenche os campos de Latitude e Longitude
    const latInput = document.getElementById("lat-input");
    const lngInput = document.getElementById("lng-input");

    if (latInput && lngInput) {
        let tempMarker = null;
        map.on("click", (event) => {
            const { lat, lng } = event.latlng;
            latInput.value = lat.toFixed(4);
            lngInput.value = lng.toFixed(4);

            if (tempMarker) {
                tempMarker.setLatLng([lat, lng]);
            } else {
                tempMarker = L.marker([lat, lng]).addTo(map);
            }
            tempMarker.bindPopup(`Coordenada selecionada:<br>${lat.toFixed(4)}, ${lng.toFixed(4)}`).openPopup();
        });
    }
});
