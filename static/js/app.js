
// Инициализация Telegram Web App
//Telegram.WebApp.ready();

document.addEventListener("DOMContentLoaded", () => {
  // Проверяем, доступен ли Telegram Web App API
  if (typeof Telegram !== "undefined" && Telegram.WebApp) {
    const tg = Telegram.WebApp;
    const initData = tg.initDataUnsafe; // Получаем данные пользователя
    console.log("Init Data:", initData); // Логируем для отладки

    if (initData.user) {
      const telegramId = initData.user.id; // Telegram ID пользователя
      const firstName = initData.user.first_name || "Гость";

      // Обновляем интерфейс
      document.getElementById("username").innerText = `Привет, ${firstName}!`;
      document.getElementById("balance").innerText = "Загружаем баланс...";

      // Запрашиваем баланс пользователя с сервера
      fetchBalance(telegramId).then((balance) => {
        document.getElementById("balance").innerText = `Ваш баланс: ${balance} монет`;
      });
    } else {
      alert("Ошибка: не удалось получить данные пользователя. Убедитесь, что приложение открыто через Telegram.");
    }
  } else {
    alert("Telegram Web App API недоступен. Убедитесь, что вы открыли приложение через Telegram.");
  }

  // Обработчик кнопки "Играть в слоты"
  document.getElementById("slots").addEventListener("click", async () => {
    const balanceElement = document.getElementById("balance");
    const telegramId = Telegram.WebApp.initDataUnsafe.user.id;

    if (!telegramId) {
      alert("Ошибка: Telegram ID не найден.");
      return;
    }

    try {
      // Запрос на запуск игры в слоты
      const result = await playSlots(telegramId);
      balanceElement.innerText = `Ваш новый баланс: ${result.new_balance} монет`;
      alert(`Результат игры: ${result.message}`);
    } catch (error) {
      console.error("Ошибка в игре слоты:", error);
      alert("Произошла ошибка при запуске игры. Попробуйте позже.");
    }
  });
});

// Функция для запроса баланса пользователя
async function fetchBalance(telegramId) {
  try {
    const response = await fetch("/api/balance", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ telegram_id: telegramId }),
    });
    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.error || "Не удалось получить баланс.");
    }
    return data.balance;
  } catch (error) {
    console.error("Ошибка при запросе баланса:", error);
    alert("Не удалось загрузить баланс.");
    return "Ошибка";
  }
}

// Функция для игры в слоты
async function playSlots(telegramId) {
  try {
    const response = await fetch("/api/slots", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ telegram_id: telegramId }),
    });
    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.error || "Не удалось сыграть в слоты.");
    }
    return data;
  } catch (error) {
    console.error("Ошибка при игре в слоты:", error);
    alert("Не удалось сыграть в слоты.");
    return { new_balance: "Ошибка", message: "Попробуйте позже." };
  }
}
document.querySelector("button").addEventListener("click", playSlots);

// Автоматически обновляем баланс при загрузке страницы
updateBalance();
