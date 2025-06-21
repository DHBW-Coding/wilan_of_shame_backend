const socket = new WebSocket("ws://localhost:3000"); // URL anpassen

const screens = document.querySelectorAll(".screen");
let current = 0;

function showNextScreen() {
  screens[current].classList.add("hidden");
  current = (current + 1) % screens.length;
  screens[current].classList.remove("hidden");
}

// Alle 10 Sekunden zum nächsten Screen wechseln
setInterval(showNextScreen, 10000);

// Initial: ersten Screen anzeigen
screens[current].classList.remove("hidden");

const jsonData = [
  {
    mac_address: "3C:5A:B4:1F:8C:22",
    vendor: "Apple",
    device_name: "Anna's iPhone",
  },
  {
    mac_address: "DC:23:B4:1G:6C:42",
    vendor: "Samsung",
    device_name: "GMT-1837",
  },
  {
    mac_address: "AC:2A:F4:B2:8C:12",
    vendor: "Huawei",
    device_name: "My P60 Pro",
  },
  {
    mac_address: "3C:5A:B3:1F:8C:22",
    vendor: "Apple",
    device_name: "Max’s iPhone 14",
  },
];

const tbody = document.querySelector("#deviceTable tbody");
const countText = document.getElementById("deviceCount");

jsonData.forEach((device) => {
  const row = document.createElement("tr");
  row.innerHTML = `
        <td>${device.mac_address}</td>
        <td>${device.vendor || "Unknown"}</td>
        <td>${device.device_name || "Unknown"}</td>
      `;
  tbody.appendChild(row);
});

countText.textContent = `${jsonData.length} CONNECTED DEVICE${
  jsonData.length !== 1 ? "S" : ""
}`;
