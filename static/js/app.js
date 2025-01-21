// Инициализация Telegram Web App
//Telegram.WebApp.ready();
const showNotification = (message, type = "info") => {
  const notification = document.createElement("div");
  notification.textContent = message;
  notification.className = `notification ${type}`;
  document.body.appendChild(notification);
  setTimeout(() => notification.remove(), 2200);
};
const symbolImages = {
  "🍒": "/static/images/cherry.png",
  "🍋": "/static/images/lemon.png",
  "🔔": "/static/images/daimond.png",
  "⭐": "/static/images/seven.png",
  "🍉": "/static/images/watermelon.png",
  "🍇": "/static/images/grape.png",
  "🥝": "/static/images/plum.png"
};


// Элементы интерфейса
const spinButton = document.getElementById("spinButton");
const balanceElement = document.getElementById("balance");
const resultElement = document.getElementById("result");
const reelsContainer = document.getElementById("reels");

function updateReels(reels) {
  const reelContainers = document.querySelectorAll('.reel');
  reels.forEach((reel, index) => {
    reelContainers[index].innerHTML = reel
      .map(symbol => `<img src="${symbolImages[symbol]}" alt="${symbol}" class="symbol">`)
      .join('');
  });
}

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

  const slotsButton = document.getElementById("spinButton");
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
});




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

    showNotification(`Вы получили ежедневный бонус: 100 монет!`, "success");
    fetchBalance(telegramId).then((balance) => {
      document.getElementById("balance").innerText = `Ваш баланс: ${balance} монет`;
    })
  } catch (error) {
    showNotification(`Вы получали уже сегодня свой бонус`, "error");
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

// Улучшение таблицы лидеров с современным оформлением
async function fetchLeaderboard() {
  try {
    const response = await fetch("/api/leaderboard");
    const result = await response.json();

    if (!response.ok) {
      throw new Error(result.error || "Не удалось загрузить таблицу лидеров.");
    }

    const leaderboardElement = document.getElementById("leaderboard");
    leaderboardElement.innerHTML = '';

    const table = document.createElement('table');
    const headerRow = document.createElement('tr');

    ['Место', 'Игрок', 'Баланс'].forEach(text => {
      const th = document.createElement('th');
      th.textContent = text;
      headerRow.appendChild(th);
    });

    table.appendChild(headerRow);

    result.leaderboard.forEach((player, index) => {
      const row = document.createElement('tr');
      [index + 1, player[0], player[1]].forEach(text => {
        const td = document.createElement('td');
        td.textContent = text;
        row.appendChild(td);
      });
      table.appendChild(row);
    });

    leaderboardElement.appendChild(table);
  } catch (error) {
    console.error("Ошибка при загрузке таблицы лидеров:", error);
    showNotification("Не удалось загрузить таблицу лидеров", "error");
  }
}
// Вращение барабанов
async function spinSlots() {
  const bet = parseInt(document.getElementById("bet").value);
  if (isNaN(bet) || bet <= 0) {
    alert("Введите корректную ставку.");
    return;
  }

  // Блокируем кнопку во время вращения
  spinButton.disabled = true;

  // Отображаем анимацию вращения
  startSpinning();

  try {
    // Отправляем запрос на сервер
    const response = await fetch("/api/slots", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        telegram_id: Telegram.WebApp.initDataUnsafe.user.id,
        bet: bet,
      }),
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.error || "Ошибка при обработке игры.");
    }

    // Останавливаем анимацию и обновляем результат
    setTimeout(() => {
      stopSpinning(data.reels);
      updateBalance(data.new_balance);
      showResult(data.win_amount);
      spinButton.disabled = false;
    }, 2000); // Останавливаем через 2 секунды
  } catch (error) {
    console.error("Ошибка при запуске спинов:", error);
    alert("Произошла ошибка. Попробуйте позже.");
    spinButton.disabled = false;
  }
}

// Запуск анимации вращения
function startSpinning() {
  reelsContainer.innerHTML = "";

  for (let i = 0; i < 5; i++) {
    const reel = document.createElement("div");
    reel.className = "reel";

    // Добавляем 10 случайных символов
    for (let j = 0; j < 10; j++) {
      const img = document.createElement("img");
      img.src = getRandomSymbolImage();
      img.className = "symbol";
      reel.appendChild(img);
    }

    reelsContainer.appendChild(reel);

    // Анимация вращения с GSAP
    gsap.to(reel, {
      y: -1000, // Сдвиг вверх (зависит от количества символов)
      duration: 1 + i * 0.2, // Разная скорость для каждого барабана
      ease: "power2.inOut",
      repeat: -1,
    });
  }
}

// Остановка анимации с результатами
function stopSpinning(reels) {
  const reelElements = Array.from(reelsContainer.children);

  reelElements.forEach((reelElement, index) => {
    // Проверяем, что массив reels содержит данные
    if (!Array.isArray(reels) || !Array.isArray(reels[index])) {
      console.error(`Данные для барабана ${index} отсутствуют или некорректны. reels:`, reels);
      return;
    }

    // Останавливаем анимацию GSAP
    gsap.killTweensOf(reelElement);

    // Заменяем содержимое на итоговые символы
    reelElement.innerHTML = reels[index]
      .map(symbol => {
        const decodedSymbol = String.fromCodePoint(symbol.codePointAt(0));
        return `<img src="${symbolImages[decodedSymbol]}" class="symbol">`;
      })
      .join("");
  });
}
// Обновление баланса
function updateBalance(newBalance) {
  balanceElement.textContent = `Баланс: ${newBalance} монет`;
}

// Отображение результата игры
function showResult(winAmount) {
  if (winAmount > 0) {
    showNotification(`Поздравляем! Вы выиграли ${result.win_amount} монет!`, "success");
  } else {
    showNotification("Увы, вы проиграли. Попробуйте снова!", "error");
  }
}

// Получение случайного символа для анимации
function getRandomSymbolImage() {
  const symbols = Object.keys(symbolImages);
  const randomSymbol = symbols[Math.floor(Math.random() * symbols.length)];
  return symbolImages[randomSymbol];
}

// Привязываем обработчик к кнопке
spinButton.addEventListener("click", spinSlots);

// Загружаем таблицу лидеров при старте
document.addEventListener("DOMContentLoaded", fetchLeaderboard);
