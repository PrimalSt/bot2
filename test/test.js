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


document.getElementById("spinButton").addEventListener("click", async () => {
  if (isSpinning) {
    showNotification(`Игра идет, подождите окончания`, "success");
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

