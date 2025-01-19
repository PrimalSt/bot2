// Инициализация Telegram Web App
//Telegram.WebApp.ready();
document.addEventListener("DOMContentLoaded", () => {
  const slotsButton = document.getElementById("slots");
  const slotsContainer = document.getElementById("slots-container");
  const slots = document.querySelectorAll(".slot");
  const resultElement = document.getElementById("game-result");

  if (!slotsButton || !slotsContainer || !slots.length) {
    console.error("Не найдены необходимые элементы для слотов.");
    return;
  }

  slotsButton.addEventListener("click", async () => {
    const betInput = document.getElementById("bet-amount");
    const bet = parseInt(betInput.value);
    const balanceElement = document.getElementById("balance");
    const telegramId = Telegram.WebApp.initDataUnsafe?.user?.id;

    if (!telegramId) {
      alert("Ошибка: Telegram ID не найден.");
      return;
    }

    if (!bet || bet <= 0) {
      alert("Введите корректную ставку.");
      return;
    }

    // Очистить прошлый результат
    resultElement.textContent = "";

    // Начать анимацию
    slotsContainer.classList.add("spinning");
    slots.forEach((slot) => slot.textContent = "🎰"); // Визуальный эффект

    try {
      // Запрос на сервер для игры в слоты
      const response = await fetch("/api/slots", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ telegram_id: telegramId, bet }),
      });

      const result = await response.json();
      if (!response.ok) {
        throw new Error(result.error || "Ошибка при игре в слоты.");
      }

      // Остановить анимацию и показать результат
      setTimeout(() => {
        slotsContainer.classList.remove("spinning");

        // Обновить значения слотов
        const slotValues = result.slots || ["🍒", "🍋", "🍉"]; // Если сервер возвращает значения слотов
        slots.forEach((slot, index) => {
          slot.textContent = slotValues[index];
          slot.classList.add("stopped");
        });

        // Обновить баланс и отобразить сообщение
        balanceElement.textContent = `Ваш новый баланс: ${result.new_balance} монет`;
        resultElement.textContent = result.message;
      }, 3000); // Имитация времени вращения
    } catch (error) {
      console.error("Ошибка:", error);
      alert("Произошла ошибка. Попробуйте позже.");
    }
  });
});
// Автоматически обновляем баланс при загрузке страницы
