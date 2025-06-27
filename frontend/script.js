const socket = new WebSocket("ws://localhost:3000");

const screens = document.querySelectorAll(".screen");
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
];

const devicesPerPage = 12;
let currentDevicePage = -1;
const totalPages = Math.ceil(jsonData.length / devicesPerPage);

function updateDeviceTable() {
  currentDevicePage = (currentDevicePage + 1) % totalPages;

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

const backendData = {
  dns_queries: [
    "https://www.dartconnect.com/",
    "http://httpforever.com/",
    "https://www.wetteronline.de/",
    "https://github.com/langflow-ai",
    "01752544762@s.whatsapp.org/",
    "https://icloud.com/myAccount",
    "https://www.dartconnect.com/",
    "http://httpforever.com/",
    "https://www.wetteronline.de/",
    "https://github.com/langflow-ai",
    "01752544762@s.whatsapp.org/",
    "https://icloud.com/myAccount",
    "https://www.dartconnect.com/",
    "http://httpforever.com/",
    "https://www.wetteronline.de/",
    "https://github.com/langflow-ai",
    "01752544762@s.whatsapp.org/",
    "https://icloud.com/myAccount",
    "https://www.dartconnect.com/",
    "http://httpforever.com/",
    "https://www.wetteronline.de/",
    "https://github.com/langflow-ai",
    "01752544762@s.whatsapp.org/",
    "https://icloud.com/myAccount",
    "https://www.dartconnect.com/",
    "http://httpforever.com/",
    "https://www.wetteronline.de/",
    "https://github.com/langflow-ai",
    "01752544762@s.whatsapp.org/",
    "https://icloud.com/myAccount",
  ],
};

function renderDNSFeed(data) {
  const container = document.getElementById("dns-feed");
  container.innerHTML = "";

  const now = new Date();
  let time = now;

  const recentQueries = data.dns_queries.slice(-19);

  recentQueries.forEach((url, index) => {
    const timeStr = new Date(time.getTime() - index * 60000)
      .toTimeString()
      .slice(0, 5);

    const line = document.createElement("div");
    line.className = "dns-line";

    const timeEl = document.createElement("div");
    timeEl.className = "time";
    timeEl.textContent = timeStr;

    const urlEl = document.createElement("div");
    urlEl.className = "url";
    urlEl.textContent = url;

    if (url.startsWith("http://")) {
      urlEl.classList.add("insecure");
    }

    line.appendChild(timeEl);
    line.appendChild(urlEl);
    container.appendChild(line);
  });
}

renderDNSFeed(backendData);

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
