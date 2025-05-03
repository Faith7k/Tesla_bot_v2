# Tesla Stok Takip Botu

Bu bot, Tesla Türkiye'nin envanter sayfasını düzenli olarak kontrol ederek, stoğa yeni Model Y araçlar eklendiğinde Telegram üzerinden otomatik bildirim gönderir.

## Özellikler

- Tesla Türkiye envanter sayfasını belirli aralıklarla kontrol eder
- Yeni araç eklendiğinde anında Telegram bildirimi gönderir
- Model, fiyat ve diğer araç detaylarını bildirimde gösterir
- Docker ile kolay kurulum ve çalıştırma

## Kurulum

### Gereksinimler

- Python 3.8+
- Telegram Bot Token ([@BotFather](https://t.me/botfather) üzerinden alabilirsiniz)
- Telegram Chat ID

### Kurulum Adımları

1. Repoyu klonlayın:
   ```
   git clone https://github.com/KULLANICI_ADINIZ/tesla-bot.git
   cd tesla-bot
   ```

2. `.env` dosyasını oluşturun:
   ```
   cp env.example .env
   ```

3. `.env` dosyasını düzenleyin ve Telegram bot token ve chat ID'nizi ekleyin.

### Doğrudan Python ile Çalıştırma

1. Gerekli paketleri yükleyin:
   ```
   pip install -r requirements.txt
   ```

2. Botu çalıştırın:
   ```
   python tesla_bot.py
   ```

### Docker ile Çalıştırma

1. Docker imajını oluşturun:
   ```
   docker build -t tesla-bot .
   ```

2. Docker konteynerini çalıştırın:
   ```
   docker run -d --name tesla-bot --restart unless-stopped tesla-bot
   ```

## Telegram Bot Kurulumu

1. Telegram'da [@BotFather](https://t.me/botfather) ile konuşun ve `/newbot` komutunu kullanarak yeni bir bot oluşturun.
2. Bot token'ınızı .env dosyasına kaydedin.
3. Chat ID'nizi almak için, botunuzu başlatın ve [@userinfobot](https://t.me/userinfobot) ile konuşun.

## Katkıda Bulunma

Katkılarınız her zaman memnuniyetle karşılanır! Lütfen bir pull request göndermekten çekinmeyin.

## Lisans

MIT Lisansı altında lisanslanmıştır. 