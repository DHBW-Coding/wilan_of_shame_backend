const socket = new WebSocket("ws://192.168.4.1:8083/ws");

const screens = document.querySelectorAll(".screen");
const screenDurations = [10000, 20000, 30000];
let current = 0;
updateIndicators();

function showNextScreen() {
  screens[current].classList.add("hidden");
  current = (current + 1) % screens.length;
  screens[current].classList.remove("hidden");
  showRandomTip();
  updateIndicators();

  if (screens[current].id === "screen-2") {
    currentDevicePage = 0;
    updateDeviceTable();
  }
  
  setTimeout(showNextScreen, screenDurations[current]);
}

setTimeout(showNextScreen, screenDurations[current]);

// Initial: ersten Screen anzeigen
screens[current].classList.remove("hidden");

let jsonData = [];

let backendData = {
  dns_queries: [
  ],
};

const devicesPerPage = 11;
let currentDevicePage = -1;
let totalPages = Math.ceil(jsonData.length / devicesPerPage);

function updateDeviceTable() {
  if (totalPages === 0) {
    currentDevicePage = 0;
  } else {
    currentDevicePage = (currentDevicePage + 1) % totalPages;
  }

  const tbody = document.querySelector("#deviceTable tbody");
  tbody.innerHTML = "";

  const startIndex = currentDevicePage * devicesPerPage;
  const endIndex = startIndex + devicesPerPage;
  const devicesToShow = jsonData.slice(startIndex, endIndex);

  devicesToShow.forEach((device) => {
    const row = document.createElement("tr");
    row.innerHTML = `
      <td>${device.mac_address}</td>
      <td>${device.vendor || "Unknown"}</td>
      <td>${device.device_name || "Unknown"}</td>
    `;
    tbody.appendChild(row);
  });

  const countText = document.getElementById("deviceCount");
  countText.textContent = `${jsonData.length} CONNECTED DEVICE${
    jsonData.length !== 1 ? "S" : ""
  }`;
}

setInterval(() => {
  const screen2 = document.getElementById("screen-2");
  if (!screen2.classList.contains("hidden")) {
    updateDeviceTable();
  }
}, 5000);

function renderDNSFeed(data) {
  const container = document.getElementById("dns-feed");
  container.innerHTML = "";

  const now = new Date();
  let time = now;

  const recentQueries = data.dns_queries.slice(-17);

  recentQueries.forEach((request, index) => {
    let timeStr;

    if (!request.time) {
      timeStr = new Date(time.getTime() - index * 60000)
      .toTimeString()
      .slice(0, 8); // HH:MM:SS
    } else {
      timeStr = new Date(request.time).toTimeString().slice(0, 8); // HH:MM:SS
    }

    const line = document.createElement("div");
    line.className = "dns-line";

    const timeEl = document.createElement("div");
    timeEl.className = "time";
    timeEl.textContent = timeStr;

    const urlEl = document.createElement("div");
    urlEl.className = "url";
    urlEl.textContent = request.url;

    const deviceEl = document.createElement("div");
    deviceEl.className = "device";
    deviceEl.textContent = request.requester || "Unknown Device";

    line.appendChild(timeEl);
    line.appendChild(urlEl);
    line.appendChild(deviceEl);
    container.appendChild(line);
  });
}

function showRandomTip() {
  const randomTip = tips[Math.floor(Math.random() * tips.length)];

  const activeScreen = document.querySelector(".screen:not(.hidden)");

  if (activeScreen) {
    const tipEl = activeScreen.querySelector(".footer-headline");
    const descEl = activeScreen.querySelector("footer p");

    if (tipEl && descEl) {
      tipEl.innerHTML = randomTip.headline;
      descEl.textContent = randomTip.text;
    }
  }
}

function updateIndicators() {
  const visibleScreen = document.querySelector(".screen:not(.hidden)");

  const indicators = visibleScreen.querySelectorAll(
    ".screen-indicators, .screen-indicators_qr"
  );

  indicators.forEach((group) => {
    const dots = group.querySelectorAll(".dot");
    dots.forEach((dot, index) => {
      dot.classList.toggle("active", index === current);
    });
  });
}

socket.addEventListener("message", (event) => {
  try {
    const device = JSON.parse(event.data);

    if (device.mac_address) {
      // Prüfe, ob das Gerät schon in der Liste ist
      const idx = jsonData.findIndex(d => d.mac_address === device.mac_address);

        if (idx === -1) {
          // Neues Gerät hinzufügen
          jsonData.push(device);
          console.log("New device added:", device.mac_address);
        } else {
          // Gerät ggf. updaten (optional)
          jsonData[idx] = device;
          backendData.dns_queries.push({
            time:device.timestamp,
            url: device.dns_query,
            requester: device.device_name || device.mac_address,
          });
          console.log("Device updated:", device.mac_address);
        }

        renderDNSFeed(backendData);

    }
  } catch (e) {
    console.error("Invalid JSON from backend:", event.data);
  }
});


const tips = [
  {
    headline: "💡 <strong>Use a VPN before surfing freely!</strong>",
    text: "A VPN encrypts your connection and keeps snoopers away.",
  },
  {
    headline: "💡 <strong>Look for https:// and a padlock!</strong>",
    text: "Only enter personal info on secure websites.",
  },
  {
    headline:
      "💡 <strong>Don't access banking sites over public Wi-Fi!</strong>",
    text: "Save it for a trusted, private connection.",
  },
  {
    headline: "💡 <strong>Turn off automatic Wi-Fi connections!</strong>",
    text: "Prevent your device from joining risky networks.",
  },
  {
    headline: "💡 <strong>Enable your firewall!</strong>",
    text: "It helps block unwanted access attempts.",
  },
  {
    headline: "💡 <strong>Don’t share passwords!</strong>",
    text: "Even friends can be a risk in shared networks.",
  },
  {
    headline: "💡 <strong>Avoid file sharing in public Wi-Fi!</strong>",
    text: "Turn off AirDrop, Nearby Share, or similar features to stay private.",
  },
  {
    headline: "💡 <strong>Use two-factor authentication!</strong>",
    text: "It adds an extra layer of security if your password gets stolen.",
  },
  {
    headline: "💡 <strong>Forget the network after use!</strong>",
    text: "Remove public Wi-Fi entries to avoid auto-reconnection later.",
  },
  {
    headline: "💡 <strong>Keep your software up to date!</strong>",
    text: "Security patches protect you from known vulnerabilities.",
  },
  {
    headline: "💡 <strong>Disable Wi-Fi when not in use!</strong>",
    text: "This keeps your device from being discovered by attackers.",
  },
  {
    headline: "💡 <strong>Use privacy screens in public!</strong>",
    text: "Prevent shoulder surfers from reading your screen.",
  },
  {
    headline: "💡 <strong>Don’t log into sensitive accounts!</strong>",
    text: "Avoid online banking or shopping over public connections.",
  },
  {
    headline: "💡 <strong>Use strong, unique passwords!</strong>",
    text: "Don’t reuse the same password across websites.",
  },
  {
    headline: "💡 <strong>Check network names carefully!</strong>",
    text: "Avoid fake hotspots with names like 'Free_WiFi_Public'.",
  },
  {
    headline: "💡 <strong>Beware of pop-ups and fake login pages!</strong>",
    text: "They might be phishing attempts to steal your data.",
  },
];