// Проверяем, доступен ли Telegram.WebApp
if (typeof Telegram !== "undefined" && Telegram.WebApp.initDataUnsafe) {
  const telegram_id = Telegram.WebApp.initDataUnsafe.user?.id;
  const username = Telegram.WebApp.initDataUnsafe.user?.username || "Unknown";
  console.log("Telegram ID:", telegram_id);
} else {
  alert("Telegram Web App API недоступен. Запустите приложение через Telegram.");
}

// Инициализация Telegram Web App
Telegram.WebApp.ready();

// Получение данных пользователя из Telegram Web App
const user = Telegram.WebApp.initDataUnsafe;
const telegram_id = user.user?.id; // Получаем telegram_id пользователя
const username = user.user?.username || "Unknown";

if (!telegram_id) {
  alert("Не удалось получить Telegram ID. Убедитесь, что Web App запущен через Telegram.");
}

// Функция для обновления баланса
function updateBalance() {
  fetch(`/api/balance?telegram_id=${telegram_id}`)
    .then(response => response.json())
    .then(data => {
      if (data.error) {
        alert(data.error);
        return;
      }
      document.getElementById("balance").textContent = `Баланс: ${data.balance}`;
    })
    .catch(err => {
      alert("Ошибка получения баланса.");
    });
}

// Функция для игры в слоты
function playSlots() {
  const telegram_id = Telegram.WebApp.initDataUnsafe.user?.id; // Получаем Telegram ID
  const bet = 100; // Ставка

  fetch("/api/slots", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ telegram_id, bet })
  })
    .then(response => response.json())
    .then(data => {
      if (data.error) {
        alert(data.error);
        return;
      }
      const result = data.slots.join(" | ");
      const winMessage = data.win_amount > 0
        ? `Вы выиграли ${data.win_amount}!`
        : "Вы ничего не выиграли.";
      document.getElementById("result").textContent = `${result}\n${winMessage}`;
      updateBalance(); // Обновляем баланс
    })
    .catch(err => {
      alert("Ошибка игры.");
    });
}

document.querySelector("button").addEventListener("click", playSlots);

// Автоматически обновляем баланс при загрузке страницы
updateBalance();
