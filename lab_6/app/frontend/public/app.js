(function () {
  const config = window.APP_CONFIG || {};
  const fallbackUrl =
    window.location.port === "3000"
      ? "http://localhost:8000"
      : window.location.origin;

  const apiBaseUrl = config.API_BASE_URL || fallbackUrl;
  const appTitle = config.APP_TITLE || "Лабораторная работа 6";

  const titleNode = document.getElementById("app-title");
  const urlNode = document.getElementById("api-url");
  const buttonNode = document.getElementById("load-button");
  const badgeNode = document.getElementById("status-badge");
  const responseNode = document.getElementById("response-box");

  titleNode.textContent = appTitle;
  urlNode.textContent = `${apiBaseUrl}/api/info`;

  async function loadBackendInfo() {
    badgeNode.textContent = "Запрос...";
    badgeNode.classList.remove("ok");

    try {
      const response = await fetch(`${apiBaseUrl}/api/info`);

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const data = await response.json();
      responseNode.textContent = JSON.stringify(data, null, 2);
      badgeNode.textContent = "Сервер доступен";
      badgeNode.classList.add("ok");
    } catch (error) {
      responseNode.textContent = [
        "Не удалось получить ответ от сервера.",
        `Ошибка: ${error.message}`,
        "",
        "Проверь:",
        "1. Запущен ли FastAPI на порту 8000/30801.",
        "2. Верный ли API_BASE_URL в config.js или ConfigMap.",
        "3. Настроен ли proxy на frontend или доступ к backend-service в Kubernetes.",
        "4. Совпадает ли DATABASE_URL приложения с контрактом PostgreSQL."
      ].join("\n");
      badgeNode.textContent = "Ошибка запроса";
      badgeNode.classList.remove("ok");
    }
  }

  buttonNode.addEventListener("click", loadBackendInfo);
})();
