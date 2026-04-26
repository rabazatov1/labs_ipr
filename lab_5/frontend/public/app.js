(function () {
  const config = window.APP_CONFIG || {};
  const apiBase = (config.API_BASE_URL ?? "").replace(/\/$/, "");

  const titleNode = document.getElementById("app-title");
  const urlNode = document.getElementById("api-url");
  const buttonNode = document.getElementById("load-button");
  const badgeNode = document.getElementById("status-badge");
  const responseNode = document.getElementById("response-box");

  const appTitle = config.APP_TITLE || "Лабораторная работа 5: Kubernetes";
  const infoPath = `${apiBase}/api/info`;

  titleNode.textContent = appTitle;
  urlNode.textContent = infoPath;

  async function loadBackendInfo() {
    badgeNode.textContent = "Запрос...";
    badgeNode.classList.remove("ok");

    try {
      const response = await fetch(infoPath);

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
        "1. В Kubernetes: применены ли манифесты, работает ли backend.",
        "2. Nginx должен проксировать /api на backend-service (см. nginx.conf).",
        "3. Локально без k8s: подними backend (uvicorn :8000) и открой статику с порта, где задан API_BASE_URL в config.js."
      ].join("\n");
      badgeNode.textContent = "Ошибка запроса";
      badgeNode.classList.remove("ok");
    }
  }

  buttonNode.addEventListener("click", loadBackendInfo);
})();
