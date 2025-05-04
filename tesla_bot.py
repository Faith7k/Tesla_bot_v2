import requests
import json
import time
import os
import logging
from datetime import datetime, timedelta
import telebot
import random
from dotenv import load_dotenv

# Loglama ayarları
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("tesla_bot.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# .env dosyasından çevre değişkenlerini yükle
load_dotenv()

# Telegram bot token ve chat ID
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Kontrol aralığı (dakika)
MIN_CHECK_INTERVAL = 8   # Minimum bekleme süresi (dakika)
MAX_CHECK_INTERVAL = 13  # Maksimum bekleme süresi (dakika)

# Hata durumunda bekleme süresi (dakika)
ERROR_WAIT_TIME = 30  # Hata durumunda 30 dakika bekle

# Tesla web sitesi URL'i (Stok sayfası)
TESLA_INVENTORY_WEB_URL = "https://www.tesla.com/tr_TR/inventory/new/my?arrangeby=plh&zip=34010&range=0"

# User-Agent listesi
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_7_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Mobile/15E148 Safari/604.1"
]

# Telegram bot oluştur
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

# Servis durumu için global değişken
service_running = True

@bot.message_handler(commands=['calisiyor_musun'])
def handle_calisiyor_musun(message):
    if service_running:
        bot.reply_to(message, "Evet, çalışıyorum ✅")
    else:
        bot.reply_to(message, "Hayır, çalışmıyorum ❌")

def get_tesla_inventory_web():
    """Tesla web sitesinden envanter bilgisi almaya çalışır"""
    user_agent = random.choice(USER_AGENTS)
    headers = {
        "User-Agent": user_agent,
        "Accept-Language": "tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Cache-Control": "no-cache",
        "Pragma": "no-cache",
        "DNT": "1"
    }
    try:
        logger.info("Tesla web sitesine istek gönderiliyor...")
        time.sleep(random.uniform(0, 2))
        response = requests.get(TESLA_INVENTORY_WEB_URL, headers=headers, timeout=30)
        response.raise_for_status()
        if "Aradığınız Tesla'yı göremiyor musunuz?" in response.text:
            logger.info("Tesla sitesinde araç bulunmuyor (boş envanter).")
            return {"results": []}
        if "Model Y" in response.text and "TL" in response.text:
            logger.info("Tesla web sitesinde araç olduğu tespit edildi!")
            return {"results": [{"dummy": True}]}
        logger.info("Tesla web sitesinde araç durumu belirlenemedi.")
        return {"results": []}
    except requests.RequestException as e:
        logger.error(f"Tesla web sitesine erişirken hata oluştu: {e}")
        # Hata mesajını fonksiyonla birlikte döndür
        return None, str(e)
    except Exception as e:
        logger.error(f"Tesla web sitesine erişirken beklenmeyen hata oluştu: {e}")
        return None, str(e)

def format_inventory_message(results):
    """Envanter sonuçlarını okunabilir bir mesaja dönüştürür"""
    if not results or not results.get("results"):
        return "Şu anda stokta Tesla Model Y bulunmamaktadır."
    
    vehicles = results["results"]
    if not vehicles:
        return "Şu anda stokta Tesla Model Y bulunmamaktadır."
    
    # Eğer dummy veri varsa, basit bir mesaj dön
    if len(vehicles) == 1 and vehicles[0].get("dummy"):
        return (
            "🚨 *TESLA STOK UYARISI* 🚨\n"
            "Tesla Model Y stokta bulundu!\n\n"
            "⚠️ Detaylar için web sitesini ziyaret edin.\n\n"
            "[🔗 Tesla Stok Sayfası](https://www.tesla.com/tr_TR/inventory/new/my?arrangeby=plh&zip=34010&range=0)"
        )
    
    message = f"🚨 *TESLA STOK UYARISI* 🚨\n{len(vehicles)} adet Tesla Model Y stokta!\n\n"
    
    for i, vehicle in enumerate(vehicles[:5], 1):  # İlk 5 aracı göster
        price = vehicle.get("Price", "Belirtilmemiş")
        trim = vehicle.get("TRIM", "Bilinmiyor")
        variant = vehicle.get("TrimName", "Bilinmiyor")
        range_info = vehicle.get("Range", "Belirtilmemiş")
        vin = vehicle.get("VIN", "Belirtilmemiş")
        detail_url = vehicle.get("DetailUrl")
        # Eğer detay linki yoksa genel linki kullan
        if not detail_url:
            detail_url = "https://www.tesla.com/tr_TR/inventory/new/my?arrangeby=plh&zip=34010&range=0"
        
        message += f"*{i}. {trim} {variant}*\n"
        message += f"🏷️ Fiyat: {price} TL\n"
        message += f"🔋 Menzil: {range_info} km\n"
        message += f"🆔 VIN: {vin}\n"
        message += f"[🔗 Detaylı Bilgi]({detail_url})\n\n"
    
    message += "[🔗 Tüm araçlar için tıkla](https://www.tesla.com/tr_TR/inventory/new/my?arrangeby=plh&zip=34010&range=0)\n"
    return message

def send_telegram_notification(message):
    """Telegram üzerinden bildirim gönderir"""
    try:
        bot.send_message(
            chat_id=TELEGRAM_CHAT_ID,
            text=message,
            parse_mode="Markdown"
        )
        logger.info("Telegram bildirimi başarıyla gönderildi.")
        return True
    except Exception as e:
        logger.error(f"Telegram API hatası: {e}")
        return False

def get_random_wait_time(error_occurred=False):
    """Rastgele bir bekleme süresi döndürür (saniye cinsinden)"""
    if error_occurred:
        wait_minutes = ERROR_WAIT_TIME
        logger.warning(f"Hata nedeniyle daha uzun bekleme: {wait_minutes} dakika")
    else:
        # Dakika olarak minimum ve maksimum arasında rastgele bir değer
        wait_minutes = random.randint(MIN_CHECK_INTERVAL, MAX_CHECK_INTERVAL)
        # Tam dakikalardan kaçınmak için birkaç saniye ekle
        wait_seconds = wait_minutes * 60 + random.randint(0, 59)
        return wait_seconds, wait_minutes
    
    wait_seconds = wait_minutes * 60
    return wait_seconds, wait_minutes

def main():
    global service_running
    logger.info("Tesla Bot başlatıldı")
    logger.info(f"Kontrol aralığı: {MIN_CHECK_INTERVAL}-{MAX_CHECK_INTERVAL} dakika")
    
    # Telegram botu ayrı thread'de başlat
    import threading
    bot_thread = threading.Thread(target=bot.polling, kwargs={"none_stop": True, "interval": 0.5})
    bot_thread.daemon = True
    bot_thread.start()

    # Önceki envanter durumunu saklamak için değişken
    previous_count = 0
    # Başarısız sorgu sayacı
    consecutive_errors = 0
    last_error_type = None
    last_error_detail = None
    
    while True:
        error_occurred = False
        logger.info("Envanter kontrol ediliyor...")
        # Web sitesinden kontrol et
        try:
            inventory_data, tesla_error = get_tesla_inventory_web()
        except Exception as e:
            inventory_data = None
            tesla_error = str(e)
        if inventory_data is not None:
            consecutive_errors = 0
            current_count = len(inventory_data.get("results", []))
            # Envanter durumunu loglama
            if current_count == 0:
                logger.info("Şu anda envanterde araç bulunmuyor.")
            else:
                logger.info(f"Envanterde {current_count} araç bulundu.")
            # Yeni araç varsa veya ilk kez çalıştırılıyorsa ve araç varsa bildirim gönder
            if (previous_count == 0 and current_count > 0) or (previous_count > 0 and current_count > previous_count):
                message = format_inventory_message(inventory_data)
                send_telegram_notification(message)
                logger.info(f"Yeni araçlar bulundu! Toplam: {current_count}")
            elif previous_count > current_count and current_count > 0:
                message = f"📉 Tesla envanterinde azalma: {previous_count} -> {current_count} araç"
                send_telegram_notification(message)
                logger.info(message)
            # Güncel sayıyı sakla
            previous_count = current_count
            last_error_type = None
            last_error_detail = None
        else:
            error_occurred = True
            consecutive_errors += 1
            last_error_type = "Tesla API"
            last_error_detail = tesla_error
            logger.warning(f"Tesla API sorgusu başarısız oldu. Ardışık hata sayısı: {consecutive_errors}. Hata: {tesla_error}")
            if consecutive_errors >= 3:
                error_occurred = True
                message = f"⚠️ Bot ardışık {consecutive_errors} kez *{last_error_type}* hatasıyla karşılaştı.\nHata Detayı: {last_error_detail}\nDaha uzun süre beklenecek."
                send_telegram_notification(message)
        # Rastgele bekleme süresi belirle
        wait_seconds, wait_minutes = get_random_wait_time(error_occurred)
        # Başlangıç zamanını kaydet
        start_wait_time = datetime.now()
        end_wait_time = start_wait_time + timedelta(seconds=wait_seconds)
        logger.info(f"Bir sonraki kontrol için {wait_minutes} dakika ({wait_seconds} saniye) bekleniyor...")
        logger.info(f"Sonraki kontrol zamanı: {end_wait_time.strftime('%H:%M:%S')}")
        time.sleep(wait_seconds)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Bot kullanıcı tarafından durduruldu.")
    except Exception as e:
        logger.error(f"Beklenmeyen hata: {e}", exc_info=True) 