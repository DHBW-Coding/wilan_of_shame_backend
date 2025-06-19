const socket = new WebSocket('ws://localhost:3000'); // URL anpassen

const screens = document.querySelectorAll('.screen');
let current = 0;

function showNextScreen() {
  screens[current].classList.add('hidden');
  current = (current + 1) % screens.length;
  screens[current].classList.remove('hidden');
}

// Alle 10 Sekunden zum nächsten Screen wechseln
setInterval(showNextScreen, 10000);

// Initial: ersten Screen anzeigen
screens[current].classList.remove('hidden');