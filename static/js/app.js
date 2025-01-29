// Инициализация Telegram Web App
//Telegram.WebApp.ready();
const showNotification = (message, type = "info") => {
  const notification = document.createElement("div");
  notification.textContent = message;
  notification.className = `notification ${type}`;
  document.body.appendChild(notification);
  setTimeout(() => notification.remove(), 2200);
};

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
async function updateBalanceDisplay() {
  const balanceElement = document.getElementById("balance");
  const balance = await fetchBalance();
  if (balance !== null) {
    balanceElement.textContent = `Ваш баланс: ${balance} монет`;
  }
}
document.addEventListener("DOMContentLoaded", () => {

  const slotsButton = document.getElementById("slots");
  const slotElements = [
    document.getElementById("slot1"),
    document.getElementById("slot2"),
    document.getElementById("slot3")
  ];
  const resultText = document.getElementById("result");
  let isSpinning = false;
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
      // setInterval(() => {
      //   fetchBalance(telegramId).then((balance) => {
      //    document.getElementById("balance").innerText = `Ваш баланс: ${balance} монет`;
      //});
      //  }, 10000);

    } else {
      alert("Ошибка: не удалось получить данные пользователя. Убедитесь, что приложение открыто через Telegram.");
    }
  } else {
    alert("Telegram Web App API недоступен. Убедитесь, что вы открыли приложение через Telegram.");
  }

  document.getElementById("slots").addEventListener("click", async () => {

    if (isSpinning) {
      alert("Игра уже началась! Дождитесь окончания текущей игры.");
      return;
    }

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
    isSpinning = true;
    slotsButton.disabled = true;

    // Запуск анимации крутки слотов
    slotElements.forEach(slot => {
      slot.classList.add("spinning");
      slot.classList.remove("winning", "losing", "winning-star");
      // slot.textContent = "🍒"; // Устанавливаем дефолтный символ
    });

    try {
      const result = await playSlots(telegramId, bet);
      setTimeout(() => {
        fetchBalance(telegramId).then((balance) => {
          document.getElementById("balance").innerText = `Ваш баланс: ${balance} монет`;
        });
      }, 2200);
      // Останавливаем анимацию слотов и показываем результат
      result.slots.forEach((symbol, index) => {
        setTimeout(() => {
          const slot = slotElements[index];
          slot.classList.remove("spinning");
          slot.textContent = symbol;
        }, index * 1000); // Останавливаем каждый слот с задержкой

        // Добавление эффекта выигрыша/проигрыша
        setTimeout(() => {
          const slot = slotElements[index]; // Получаем элемент слота
          if (symbol === result.slots[0] && result.slots.every(s => s === symbol)) {
            if (symbol === "⭐") {
              slot.classList.add("winning-star"); // Анимация вспышек для звёздочек
            } else if (result.slots.every(s => s === symbol)) {
              createFireworks(); // Фейерверки для других совпадений
            }
            slot.classList.add("winning");
          } else {
            slot.classList.add("losing");
          }
        }, 2200);
      });



      // Показ сообщения о выигрыше
      setTimeout(() => {
        if (result.win_amount > 0) {
          showNotification(`Поздравляем! Вы выиграли ${result.win_amount} монет!`, "success");
        } else {
          showNotification("Увы, вы проиграли. Попробуйте снова!", "error");
        }

        isSpinning = false;
        slotsButton.disabled = false;
      }, 2200);
    } catch (error) {
      console.error("Ошибка в игре слоты:", error);
      alert("Произошла ошибка при запуске игры. Попробуйте позже.");
    }
  });
});



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

document.getElementById("daily-bonus").addEventListener("click", async () => {
  const telegramId = Telegram.WebApp.initDataUnsafe.user.id;
  const bonusMessage = document.getElementById("bonus-message");

  try {
    const response = await fetch("/api/daily_bonus", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ telegram_id: telegramId }),
    });

    const result = await response.json();
    if (!response.ok) {
      throw new Error(result.error || "Не удалось получить бонус.");
    }
    showNotification(`Ежедневный бонус успешно зачислен!`, "success");
    fetchBalance(telegramId).then((balance) => {
      document.getElementById("balance").innerText = `Ваш баланс: ${balance} монет`;
    })
  } catch (error) {
    showNotification(`Вы получали уже бонус (`, "error");
  }
});

function createFireworks() {
  const container = document.getElementById("fireworks-container");

  for (let i = 0; i < 10; i++) {
    const firework = document.createElement("div");
    firework.classList.add("firework");

    // Генерация случайной позиции и цвета
    const randomX = Math.random() * 100 + "%";
    const randomY = Math.random() * 100 + "%";
    const colors = ["red", "blue", "green", "yellow", "purple"];
    const randomColor = colors[Math.floor(Math.random() * colors.length)];

    firework.style.left = randomX;
    firework.style.top = randomY;
    firework.style.backgroundColor = randomColor;

    container.appendChild(firework);

    // Удаление фейерверка после завершения анимации
    setTimeout(() => {
      firework.remove();
    }, 800);
  }
}

async function fetchLeaderboard() {
  try {
    const response = await fetch("/api/leaderboard");
    const result = await response.json();

    if (!response.ok) {
      throw new Error(result.error || "Не удалось загрузить таблицу лидеров.");
    }

    const leaderboardElement = document.getElementById("leaderboard");
    leaderboardElement.innerHTML = result.leaderboard
      .map((player) => `<li>${player[0]}: ${player[1]} монет</li>`)
      .join("");
  } catch (error) {
    console.error("Ошибка при загрузке таблицы лидеров:", error);
  }
}


// Загружаем таблицу лидеров при старте
document.addEventListener("DOMContentLoaded", fetchLeaderboard);