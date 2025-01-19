// Инициализация Telegram Web App
//Telegram.WebApp.ready();
document.addEventListener("DOMContentLoaded", () => {

  const slotsButton = document.getElementById("slots");
  const slotElements = [
    document.getElementById("slot1"),
    document.getElementById("slot2"),
    document.getElementById("slot3")
  ];
  const resultText = document.getElementById("result");
  if (!slotsButton) {
    console.error("Элемент с ID 'slots' не найден в DOM.");
  } else {
    console.log("Элемент с ID 'slots' найден.");
  }

  if (typeof Telegram !== "undefined" && Telegram.WebApp) {
    const tg = Telegram.WebApp;
    const initData = tg.initDataUnsafe;
    console.log("Init Data:", initData);

    if (initData.user) {
      const telegramId = initData.user.id;
      const firstName = initData.user.first_name || "Гость";

      document.getElementById("username").innerText = `Привет, ${firstName}!`;
      document.getElementById("balance").innerText = "Загружаем баланс...";

      fetchBalance(telegramId).then((balance) => {
        document.getElementById("balance").innerText = `Ваш баланс: ${balance} монет`;
      });

      // Автоматическое обновление баланса каждые 10 секунд
      setInterval(() => {
        fetchBalance(telegramId).then((balance) => {
          document.getElementById("balance").innerText = `Ваш баланс: ${balance} монет`;
        });
      }, 10000);

    } else {
      alert("Ошибка: не удалось получить данные пользователя. Убедитесь, что приложение открыто через Telegram.");
    }
  } else {
    alert("Telegram Web App API недоступен. Убедитесь, что вы открыли приложение через Telegram.");
  }

  document.getElementById("slots").addEventListener("click", async () => {
    const betInput = document.getElementById("bet-amount");
    const bet = parseInt(betInput.value);
    const balanceElement = document.getElementById("balance");
    const telegramId = Telegram.WebApp.initDataUnsafe.user.id;

    if (!telegramId) {
      alert("Ошибка: Telegram ID не найден.");
      return;
    }

    if (!bet || bet <= 0) {
      alert("Пожалуйста, введите корректную ставку.");
      return;
    }

    // Запуск анимации крутки слотов
    slotElements.forEach(slot => {
      slot.classList.add("spinning");
      slot.classList.remove("winning", "losing");
      // slot.textContent = "🍒"; // Устанавливаем дефолтный символ
    });

    try {
      const result = await playSlots(telegramId, bet);
      setTimeout(() => {
        fetchBalance(telegramId).then((balance) => {
          document.getElementById("balance").innerText = `Ваш баланс: ${balance} монет`;
        });
      }, 3000);
      // Останавливаем анимацию слотов и показываем результат
      result.slots.forEach((symbol, index) => {
        setTimeout(() => {
          const slot = slotElements[index];
          slot.classList.remove("spinning");
          slot.textContent = symbol;

          // Добавление эффекта выигрыша/проигрыша
          if (symbol === result.slots[0] && result.slots.every(s => s === symbol)) {
            setTimeout(() => {
              slot.classList.add("winning");
            }, 2500);
          } else {
            slot.classList.add("losing");
          }
        }, index * 1000); // Останавливаем каждый слот с задержкой
      });

      // Показ сообщения о выигрыше
      setTimeout(() => {
        resultText.textContent = result.win_amount > 0
          ? `Поздравляем! Вы выиграли ${result.win_amount} монет! 🎉`
          : "Увы, вы ничего не выиграли. Попробуйте снова!";
        resultText.style.color = result.win_amount > 0 ? "green" : "red";
      }, 2500);
    } catch (error) {
      console.error("Ошибка в игре слоты:", error);
      alert("Произошла ошибка при запуске игры. Попробуйте позже.");
    }
  });
});

async function fetchBalance() {
  try {
    const telegramId = Telegram.WebApp.initDataUnsafe?.user?.id;

    if (!telegramId) {
      throw new Error("Telegram ID не найден. Проверьте, запущено ли приложение через Telegram.");
    }

    const response = await fetch("/api/balance", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ telegram_id: telegramId }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || "Ошибка сервера.");
    }

    const data = await response.json();
    return data.balance;
  } catch (error) {
    console.error("Ошибка при запросе баланса:", error);
    alert("Не удалось получить баланс: " + error.message);
    return null;
  }
}

async function playSlots(telegramId, bet) {
  try {
    const response = await fetch("/api/slots", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        telegram_id: telegramId,
        bet: bet,
      }),
    });
    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.error || "Не удалось сыграть в слоты.");
    }
    return data;
  } catch (error) {
    console.error("Ошибка при игре в слоты:", error);
    throw error;
  }
}
// Автоматически обновляем баланс при загрузке страницы