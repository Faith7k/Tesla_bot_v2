import requests
import json
import sys

def test_tesla_api():
    """Tesla inventory API'sini test eder ve çıktıyı gösterir"""
    
    INVENTORY_URL = "https://www.tesla.com/inventory/api/v1/inventory-results?query=%7B%22query%22%3A%7B%22model%22%3A%22my%22%2C%22condition%22%3A%22new%22%2C%22options%22%3A%7B%7D%2C%22arrangeby%22%3A%22Price%22%2C%22order%22%3A%22asc%22%2C%22market%22%3A%22TR%22%2C%22language%22%3A%22tr%22%2C%22super_region%22%3A%22north%20america%22%2C%22lng%22%3A29.0132752%2C%22lat%22%3A41.0052592%2C%22zip%22%3A%2234010%22%2C%22range%22%3A0%2C%22region%22%3A%22TR%22%7D%2C%22offset%22%3A0%2C%22count%22%3A50%2C%22outsideOffset%22%3A0%2C%22outsideSearch%22%3Atrue%7D"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept-Language": "tr-TR,tr;q=0.9",
        "Referer": "https://www.tesla.com/tr_TR/inventory/new/my",
    }
    
    try:
        print("Tesla API'sine bağlanılıyor...")
        response = requests.get(INVENTORY_URL, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        # Yanıt yapısını kontrol et
        if "results" not in data:
            print("Hata: Yanıtta 'results' alanı bulunamadı.")
            print(f"Yanıt içeriği: {json.dumps(data, indent=2, ensure_ascii=False)}")
            return False
        
        # Araç sayısını göster
        vehicles_count = len(data["results"])
        print(f"\nToplam {vehicles_count} araç bulundu.\n")
        
        # İlk araç detaylarını göster (varsa)
        if vehicles_count > 0:
            print("İlk aracın detayları:")
            vehicle = data["results"][0]
            print(f"  Model: {vehicle.get('TRIM', 'Bilinmiyor')} {vehicle.get('TrimName', 'Bilinmiyor')}")
            print(f"  Fiyat: {vehicle.get('Price', 'Belirtilmemiş')}")
            print(f"  Menzil: {vehicle.get('Range', 'Belirtilmemiş')} km")
            print(f"  VIN: {vehicle.get('VIN', 'Belirtilmemiş')}")
            
            # Tam yanıtın yapısını göster
            print("\nTam API yapısı:")
            for key in vehicle.keys():
                print(f"  {key}: {vehicle[key]}")
                
        return True
        
    except requests.RequestException as e:
        print(f"Hata: Tesla API'ye erişirken sorun oluştu: {e}")
        return False
    except json.JSONDecodeError:
        print(f"Hata: Yanıt JSON formatında değil: {response.text[:200]}...")
        return False
    except Exception as e:
        print(f"Beklenmeyen hata: {e}")
        return False

if __name__ == "__main__":
    success = test_tesla_api()
    sys.exit(0 if success else 1) 