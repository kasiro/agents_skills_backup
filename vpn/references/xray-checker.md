# Xray Checker (Docker)

- **Репозиторий:** github.com/kutovoys/xray-checker
- **Образ:** kutovoys/xray-checker
- **Документация:** xray-checker.kutovoy.dev
- **Версия:** v1.3.1
- **Порт:** 2112
- **Статус:** Up (контейнер xray-checker)
- **Команда запуска:** 
  ```bash
  docker run -d --name xray-checker --restart unless-stopped \
    -v /home/kasiro/xray-checker-configs:/configs:ro \
    -e SUBSCRIPTION_URL="folder:///configs" \
    -e PROXY_CHECK_INTERVAL=300 -e PROXY_TIMEOUT=20 \
    -e SUBSCRIPTION_UPDATE=false \
    -e WEB_PUBLIC=true \
    -e METRICS_PROTECTED=true -e METRICS_USERNAME=xray -e METRICS_PASSWORD=xray2024 \
    -p 2112:2112 kutovoys/xray-checker
  ```
- **Файлы конфигов:** /home/kasiro/xray-checker-configs/ (4 текстовых файла с vless:// строками)
- **Поддерживаемые протоколы:** VLESS, VMess, Trojan, Shadowsocks, Hysteria2, SOCKS, HTTP, WireGuard
- **Методы проверки:** ip (по умолчанию), status, download
- **Формат подписок:** URL, base64, file://, folder://, JSON
