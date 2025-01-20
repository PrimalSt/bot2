async function fetchShopItems() {
  try {
    const response = await fetch("/api/shop");
    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.error || "Не удалось загрузить магазин.");
    }

    const shopItemsElement = document.getElementById("shop-items");
    shopItemsElement.innerHTML = data.items
      .map(item => `
              <li>
                  <strong>${item.name}</strong> - ${item.price} монет
                  <p>${item.description}</p>
                  <button onclick="buyItem(${item.id})">Купить</button>
              </li>
          `)
      .join("");
  } catch (error) {
    console.error("Ошибка загрузки магазина:", error);
  }
}

async function buyItem(itemId) {
  try {
    const telegramId = Telegram.WebApp.initDataUnsafe.user.id;

    const response = await fetch("/api/shop/buy", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ telegram_id: telegramId, item_id: itemId }),
    });

    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.error || "Не удалось совершить покупку.");
    }

    alert(data.message);
  } catch (error) {
    console.error("Ошибка при покупке:", error);
    alert(error.message);
  }
}

document.addEventListener("DOMContentLoaded", fetchShopItems);