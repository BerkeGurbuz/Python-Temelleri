#!/usr/bin/env python3
"""Serdivan işletme verisini indirip haritanın okuduğu dosyalara çevirir.

İki açık veri kaynağı birleştirilir:
  * OpenStreetMap (Overpass API)   - elle girilmiş, ayrıntılı ama az sayıda kayıt
  * Overture Maps "places"         - çok daha fazla işletme (pyarrow gerekir: pip install pyarrow)

Kullanım:
    python scripts/veri_guncelle.py                 # indir + dönüştür
    python scripts/veri_guncelle.py --onbellek ham  # ham yanıtları 'ham/' klasöründe sakla / oradan oku
    python scripts/veri_guncelle.py --overture-yok  # yalnızca OpenStreetMap (ek paket gerekmez)
    python scripts/veri_guncelle.py --guven 0.7     # Overture kayıtları için en düşük güven puanı

Çıktılar:
    data/isletmeler.geojson      Serdivan sınırları içindeki işletmeler (nokta)
    data/serdivan-sinir.geojson  İlçe sınırı (çokgen)
"""
from __future__ import annotations

import argparse
import json
import math
import re
import statistics
import sys
import time
import urllib.parse
import urllib.request
from collections import Counter
from datetime import date
from pathlib import Path

KOK = Path(__file__).resolve().parent.parent
ILCE_RELATION = 6989045  # OSM: Serdivan ilçe sınırı
OVERPASS = [
    "https://overpass-api.de/api/interpreter",
    "https://maps.mail.ru/osm/tools/overpass/api/interpreter",
    "https://overpass.private.coffee/api/interpreter",
]
ANAHTARLAR = ["shop", "amenity", "office", "craft", "tourism", "leisure", "healthcare", "club"]

# --------------------------------------------------------------------------- sınıflandırma
YEME = {"restaurant", "cafe", "fast_food", "bar", "pub", "ice_cream", "food_court", "biergarten"}
GIDA = {
    "supermarket", "convenience", "bakery", "butcher", "greengrocer", "deli", "pastry",
    "confectionery", "seafood", "beverages", "alcohol", "dairy", "cheese", "nuts", "spices",
    "tea", "coffee", "water", "health_food", "farm", "frozen_food", "chocolate", "grocery",
}
GUZELLIK = {"hairdresser", "beauty", "cosmetics", "perfumery", "massage", "tattoo"}
ARAC_DUKKAN = {"car", "car_repair", "car_parts", "tyres", "motorcycle", "motorcycle_repair", "caravan", "truck"}
SAGLIK_DUKKAN = {"optician", "medical_supply", "hearing_aids", "herbalist", "dentures"}
HIZMET_DUKKAN = {
    "laundry", "dry_cleaning", "travel_agency", "estate_agent", "copyshop", "tailor",
    "funeral_directors", "locksmith", "photo", "photo_studio", "printing", "ticket",
    "money_lender", "pawnbroker", "storage_rental", "rental", "repair",
}

AMENITY = {
    **{v: "yeme-icme" for v in YEME},
    **{v: "saglik" for v in ("pharmacy", "hospital", "clinic", "doctors", "dentist", "veterinary")},
    **{v: "finans" for v in ("bank", "atm", "bureau_de_change", "money_transfer")},
    **{v: "egitim" for v in (
        "school", "kindergarten", "university", "college", "driving_school", "language_school",
        "music_school", "prep_school", "training", "childcare", "dancing_school",
    )},
    **{v: "arac" for v in (
        "fuel", "charging_station", "car_wash", "car_rental", "vehicle_inspection", "car_sharing",
        "taxi", "motorcycle_rental", "bicycle_rental",
    )},
    **{v: "spor-eglence" for v in (
        "cinema", "theatre", "nightclub", "events_venue", "internet_cafe", "arts_centre",
        "gambling", "casino", "conference_centre", "exhibition_centre",
    )},
    **{v: "kamu" for v in (
        "townhall", "police", "fire_station", "post_office", "courthouse", "library",
        "community_centre", "social_facility", "public_building",
    )},
    "marketplace": "alisveris",
    "coworking_space": "hizmet",
    "studio": "hizmet",
    "post_depot": "hizmet",
    "animal_boarding": "hizmet",
}
TOURISM = {
    **{v: "konaklama" for v in ("hotel", "motel", "guest_house", "hostel", "apartment", "chalet", "camp_site", "caravan_site")},
    **{v: "spor-eglence" for v in ("museum", "gallery", "theme_park", "zoo", "aquarium")},
}
LEISURE = {v: "spor-eglence" for v in (
    "fitness_centre", "sports_centre", "sports_hall", "bowling_alley", "amusement_arcade",
    "water_park", "dance", "escape_game", "horse_riding", "miniature_golf", "ice_rink",
    "golf_course", "adult_gaming_centre", "trampoline_park", "indoor_play", "sauna", "stadium",
)}

TUR_ADI = {
    # yeme-içme
    "restaurant": "Restoran", "cafe": "Kafe", "fast_food": "Fast food", "bar": "Bar", "pub": "Pub",
    "ice_cream": "Dondurmacı", "food_court": "Yemek alanı", "biergarten": "Bahçe bar",
    # gıda
    "supermarket": "Süpermarket", "convenience": "Market / Bakkal", "bakery": "Fırın", "butcher": "Kasap",
    "greengrocer": "Manav", "deli": "Şarküteri", "pastry": "Pastane", "confectionery": "Şekerleme",
    "seafood": "Balıkçı", "beverages": "İçecek satışı", "alcohol": "Tekel bayii", "dairy": "Süt ürünleri",
    "cheese": "Peynirci", "nuts": "Kuruyemiş", "spices": "Baharatçı", "tea": "Çay satışı",
    "coffee": "Kahve satışı", "water": "Su bayii", "health_food": "Sağlıklı gıda", "farm": "Çiftlik ürünleri",
    "frozen_food": "Dondurulmuş gıda", "chocolate": "Çikolatacı", "grocery": "Bakkal",
    # alışveriş
    "clothes": "Giyim", "shoes": "Ayakkabı", "furniture": "Mobilya", "mobile_phone": "Cep telefonu",
    "jewelry": "Kuyumcu", "mall": "Alışveriş merkezi", "electronics": "Elektronik", "hardware": "Hırdavat",
    "doityourself": "Yapı market", "florist": "Çiçekçi", "books": "Kitabevi", "stationery": "Kırtasiye",
    "toys": "Oyuncak", "gift": "Hediyelik eşya", "kiosk": "Büfe", "department_store": "Mağaza",
    "variety_store": "Züccaciye / Her şey", "houseware": "Ev gereçleri", "computer": "Bilgisayar",
    "bicycle": "Bisiklet", "sports": "Spor malzemeleri", "pet": "Pet shop", "chemist": "Kozmetik / Kişisel bakım",
    "bag": "Çanta", "fabric": "Kumaş", "carpet": "Halı", "curtain": "Perde", "bed": "Yatak",
    "kitchen": "Mutfak", "bathroom_furnishing": "Banyo / Seramik", "paint": "Boya", "electrical": "Elektrik malzemeleri",
    "lighting": "Aydınlatma", "interior_decoration": "Dekorasyon", "appliance": "Beyaz eşya", "tobacco": "Tütün ürünleri",
    "e-cigarette": "Elektronik sigara", "newsagent": "Gazete bayii", "lottery": "Şans oyunları bayii",
    "second_hand": "İkinci el", "baby_goods": "Bebek ürünleri", "watches": "Saatçi", "music": "Müzik market",
    "musical_instrument": "Müzik aletleri", "outdoor": "Outdoor", "garden_centre": "Bahçe market",
    "agrarian": "Tarım ürünleri", "gas": "Tüp bayii", "trade": "Toptan satış", "building_materials": "Yapı malzemeleri",
    "wholesale": "Toptancı", "boutique": "Butik", "tiles": "Fayans / Seramik", "glaziery": "Camcı",
    "security": "Güvenlik sistemleri", "hifi": "Ses sistemleri", "video_games": "Oyun mağazası", "art": "Sanat malzemeleri",
    "craft": "Hobi malzemeleri", "sewing": "Tuhafiye", "leather": "Deri ürünleri", "antiques": "Antikacı",
    "wedding": "Gelinlik", "party": "Parti malzemeleri", "medical_supply": "Medikal", "optician": "Gözlükçü",
    "hearing_aids": "İşitme cihazları", "herbalist": "Aktar", "marketplace": "Pazar yeri", "yes": "Dükkân",
    # güzellik
    "hairdresser": "Kuaför / Berber", "beauty": "Güzellik salonu", "cosmetics": "Kozmetik", "perfumery": "Parfümeri",
    "massage": "Masaj salonu", "tattoo": "Dövme stüdyosu",
    # araç
    "fuel": "Akaryakıt istasyonu", "charging_station": "Şarj istasyonu", "car_wash": "Oto yıkama",
    "car_rental": "Araç kiralama", "vehicle_inspection": "Araç muayene", "car": "Oto galeri",
    "car_repair": "Oto tamir", "car_parts": "Oto yedek parça", "tyres": "Lastikçi", "motorcycle": "Motosiklet",
    "motorcycle_repair": "Motosiklet tamir", "taxi": "Taksi durağı", "car_sharing": "Araç paylaşımı",
    "bicycle_rental": "Bisiklet kiralama",
    # sağlık
    "pharmacy": "Eczane", "hospital": "Hastane", "clinic": "Klinik / Poliklinik", "doctors": "Muayenehane",
    "dentist": "Diş hekimi", "veterinary": "Veteriner", "laboratory": "Laboratuvar", "physiotherapist": "Fizyoterapi",
    "psychotherapist": "Psikoterapi", "alternative": "Alternatif tıp", "centre": "Sağlık merkezi",
    "optometrist": "Optometrist", "dialysis": "Diyaliz merkezi", "rehabilitation": "Rehabilitasyon",
    "blood_donation": "Kan bağışı", "nurse": "Hemşirelik hizmeti", "midwife": "Ebe", "speech_therapist": "Dil terapisti",
    # finans
    "bank": "Banka", "atm": "ATM", "bureau_de_change": "Döviz bürosu", "money_transfer": "Para transferi",
    # eğitim
    "school": "Okul", "kindergarten": "Anaokulu / Kreş", "university": "Üniversite", "college": "Yüksekokul / Kolej",
    "driving_school": "Sürücü kursu", "language_school": "Dil kursu", "music_school": "Müzik kursu",
    "prep_school": "Dershane / Kurs", "training": "Eğitim merkezi", "childcare": "Çocuk bakımevi",
    "dancing_school": "Dans kursu", "educational_institution": "Eğitim kurumu",
    # konaklama
    "hotel": "Otel", "motel": "Motel", "guest_house": "Pansiyon", "hostel": "Hostel", "apartment": "Apart",
    "chalet": "Bungalov / Dağ evi", "camp_site": "Kamp alanı", "caravan_site": "Karavan parkı",
    # hizmet
    "laundry": "Çamaşırhane", "dry_cleaning": "Kuru temizleme", "travel_agency": "Seyahat acentesi",
    "estate_agent": "Emlakçı", "copyshop": "Fotokopi / Baskı", "tailor": "Terzi", "funeral_directors": "Cenaze hizmetleri",
    "locksmith": "Çilingir", "photo": "Fotoğrafçı", "photo_studio": "Fotoğraf stüdyosu", "printing": "Matbaa",
    "ticket": "Bilet satış", "rental": "Kiralama", "repair": "Tamirci", "storage_rental": "Depo kiralama",
    "coworking_space": "Ortak çalışma alanı", "studio": "Stüdyo", "post_depot": "Kargo deposu",
    "animal_boarding": "Hayvan oteli", "money_lender": "Kredi / Finansman", "pawnbroker": "Rehinci",
    "company": "Şirket", "insurance": "Sigorta acentesi", "lawyer": "Avukat", "accountant": "Mali müşavir",
    "architect": "Mimarlık ofisi", "engineer": "Mühendislik ofisi", "notary": "Noter", "it": "Bilişim şirketi",
    "telecommunication": "Telekomünikasyon", "ngo": "Sivil toplum kuruluşu", "association": "Dernek",
    "political_party": "Siyasi parti", "union": "Sendika", "foundation": "Vakıf", "consulting": "Danışmanlık",
    "financial": "Finans ofisi", "financial_advisor": "Finans danışmanı", "tax_advisor": "Vergi danışmanı",
    "employment_agency": "İş bulma ajansı", "advertising_agency": "Reklam ajansı", "newspaper": "Gazete",
    "logistics": "Lojistik", "courier": "Kargo şubesi", "construction_company": "İnşaat şirketi",
    "property_management": "Site / Mülk yönetimi", "research": "Araştırma kurumu", "religion": "Dinî kurum ofisi",
    "energy_supplier": "Enerji şirketi", "water_utility": "Su idaresi", "diplomatic": "Diplomatik temsilcilik",
    "carpenter": "Marangoz", "electrician": "Elektrikçi", "plumber": "Tesisatçı", "painter": "Boyacı",
    "shoemaker": "Ayakkabı tamircisi", "metal_construction": "Demir doğrama", "blacksmith": "Demirci",
    "upholsterer": "Döşemeci", "hvac": "Klima / Isıtma servisi", "electronics_repair": "Elektronik tamir",
    "key_cutter": "Anahtarcı", "glazier": "Camcı", "stonemason": "Mermerci", "gardener": "Peyzaj / Bahçıvan",
    "builder": "İnşaat ustası", "roofer": "Çatı ustası", "tiler": "Fayans ustası", "window_construction": "PVC / Doğrama",
    "photographer": "Fotoğrafçı", "caterer": "Catering", "jeweller": "Kuyum atölyesi", "watchmaker": "Saat tamircisi",
    "dressmaker": "Terzi", "sawmill": "Kereste / Hızar", "signmaker": "Tabelacı", "handicraft": "El sanatları",
    "confectionery_craft": "Şekerleme imalatı", "print_shop": "Baskı atölyesi", "cleaning": "Temizlik şirketi",
    "car_painter": "Oto boya", "agricultural_engines": "Tarım makineleri servisi", "beekeeper": "Arıcı",
    # spor-eğlence
    "fitness_centre": "Spor salonu", "sports_centre": "Spor tesisi", "sports_hall": "Kapalı spor salonu",
    "bowling_alley": "Bowling salonu", "amusement_arcade": "Oyun salonu", "water_park": "Su parkı",
    "dance": "Dans stüdyosu", "escape_game": "Kaçış oyunu", "horse_riding": "Binicilik tesisi",
    "miniature_golf": "Mini golf", "ice_rink": "Buz pisti", "golf_course": "Golf sahası",
    "trampoline_park": "Trambolin parkı", "indoor_play": "Çocuk oyun alanı", "sauna": "Sauna",
    "stadium": "Stadyum", "cinema": "Sinema", "theatre": "Tiyatro", "nightclub": "Gece kulübü",
    "events_venue": "Etkinlik / Düğün salonu", "internet_cafe": "İnternet kafe", "arts_centre": "Sanat merkezi",
    "museum": "Müze", "gallery": "Sanat galerisi", "theme_park": "Eğlence parkı", "zoo": "Hayvanat bahçesi",
    "aquarium": "Akvaryum", "conference_centre": "Kongre merkezi", "exhibition_centre": "Fuar merkezi",
    "adult_gaming_centre": "Oyun salonu", "sport": "Spor kulübü",
    # kamu
    "townhall": "Belediye / Muhtarlık", "police": "Polis / Karakol", "fire_station": "İtfaiye",
    "post_office": "Postane", "courthouse": "Adliye", "library": "Kütüphane", "community_centre": "Toplum merkezi",
    "social_facility": "Sosyal hizmet kurumu", "public_building": "Kamu binası", "government": "Kamu kurumu",
}

MUTFAK = {
    "turkish": "Türk mutfağı", "kebab": "Kebap", "pizza": "Pizza", "burger": "Burger", "coffee_shop": "Kahve",
    "doner": "Döner", "döner": "Döner", "chicken": "Tavuk", "fish": "Balık", "seafood": "Deniz ürünleri",
    "regional": "Yöresel", "dessert": "Tatlı", "pide": "Pide", "lahmacun": "Lahmacun", "breakfast": "Kahvaltı",
    "ice_cream": "Dondurma", "sandwich": "Sandviç", "italian": "İtalyan", "steak_house": "Et / Steak",
    "meatball": "Köfte", "kofte": "Köfte", "köfte": "Köfte", "barbecue": "Mangal", "grill": "Izgara",
    "pasta": "Makarna", "cake": "Pasta", "baklava": "Baklava", "tea": "Çay", "bubble_tea": "Bubble tea",
    "asian": "Asya mutfağı", "chinese": "Çin mutfağı", "sushi": "Suşi", "japanese": "Japon mutfağı",
    "mexican": "Meksika mutfağı", "international": "Dünya mutfağı", "soup": "Çorba", "pancake": "Krep / Pankek",
    "waffle": "Waffle", "donut": "Donut", "börek": "Börek", "borek": "Börek", "manti": "Mantı", "mantı": "Mantı",
    "cig_kofte": "Çiğ köfte", "çiğ_köfte": "Çiğ köfte", "kumpir": "Kumpir", "tantuni": "Tantuni",
    "kokorec": "Kokoreç", "kokoreç": "Kokoreç", "gozleme": "Gözleme", "gözleme": "Gözleme", "wings": "Kanat",
    "fried_chicken": "Kızarmış tavuk", "vegetarian": "Vejetaryen", "juice": "Meyve suyu", "bagel": "Simit",
    "friture": "Kızartma", "hot_dog": "Sosisli", "noodle": "Noodle", "salad": "Salata", "local": "Yöresel",
    "black_sea": "Karadeniz mutfağı", "ıslama_köfte": "Islama köfte", "pastry": "Hamur işi", "wrap": "Dürüm",
}

ENGELLI = {"yes": "Tekerlekli sandalye ile erişilebilir", "limited": "Kısmen erişilebilir", "no": "Tekerlekli sandalyeye uygun değil"}


def tur_adi(deger: str) -> str:
    """OSM etiket değerini okunur Türkçe bir ada çevirir."""
    return TUR_ADI.get(deger) or deger.replace("_", " ").replace(";", ", ").capitalize()


def siniflandir(t: dict) -> tuple[str, str] | None:
    """Etiketlerden (kategori, tür adı) üretir; işletme sayılmıyorsa None döner."""
    v = t.get("shop")
    if v and v not in ("vacant", "no"):
        if v in GIDA:
            return "market-gida", tur_adi(v)
        if v in GUZELLIK:
            return "guzellik", tur_adi(v)
        if v in ARAC_DUKKAN:
            return "arac", tur_adi(v)
        if v in SAGLIK_DUKKAN:
            return "saglik", tur_adi(v)
        if v in HIZMET_DUKKAN:
            return "hizmet", tur_adi(v)
        return "alisveris", tur_adi(v)

    v = t.get("amenity")
    if v in AMENITY:
        return AMENITY[v], tur_adi(v)

    v = t.get("healthcare")
    if v and v != "no":
        return "saglik", tur_adi(v.split(";")[0])

    v = t.get("office")
    if v and v != "no":
        if v == "government":
            return "kamu", tur_adi(v)
        if v == "educational_institution":
            return "egitim", tur_adi(v)
        return "hizmet", "Ofis" if v == "yes" else tur_adi(v)

    v = t.get("craft")
    if v and v != "no":
        return "hizmet", "Atölye" if v == "yes" else tur_adi(v.split(";")[0])

    v = t.get("tourism")
    if v in TOURISM:
        return TOURISM[v], tur_adi(v)

    v = t.get("leisure")
    if v in LEISURE:
        return LEISURE[v], tur_adi(v)

    v = t.get("club")
    if v and t.get("name"):
        return "spor-eglence", tur_adi(v) if v in TUR_ADI else "Kulüp / Dernek"

    return None


# --------------------------------------------------------------------------- indirme
def overpass(sorgu: str, ad: str, onbellek: Path | None) -> dict:
    """Overpass sorgusunu çalıştırır; sunucular yoğunsa sırayla ve tekrar tekrar dener."""
    dosya = onbellek / f"{ad}.json" if onbellek else None
    if dosya and dosya.exists():
        return json.loads(dosya.read_text(encoding="utf-8"))

    son_hata: Exception | None = None
    for deneme in range(6):
        for sunucu in OVERPASS:
            try:
                istek = urllib.request.Request(
                    sunucu,
                    data=urllib.parse.urlencode({"data": sorgu}).encode(),
                    headers={"User-Agent": "serdivan-3d-harita/1.0 (veri_guncelle.py)"},
                )
                with urllib.request.urlopen(istek, timeout=150) as yanit:
                    ham = yanit.read()
                veri = json.loads(ham)
                if "elements" not in veri or veri.get("remark"):
                    raise ValueError(veri.get("remark", "beklenmeyen yanıt"))
                if dosya:
                    dosya.parent.mkdir(parents=True, exist_ok=True)
                    dosya.write_bytes(ham)
                print(f"  ✓ {ad}: {len(veri['elements'])} öğe ({urllib.parse.urlparse(sunucu).netloc})")
                return veri
            except Exception as hata:  # noqa: BLE001 - her türlü ağ hatasında sıradaki sunucuya geç
                son_hata = hata
                print(f"  … {ad}: {urllib.parse.urlparse(sunucu).netloc} yanıt vermedi ({str(hata)[:60]})")
        time.sleep(10 * (deneme + 1))
    raise RuntimeError(f"Overpass'ten '{ad}' alınamadı: {son_hata}")


# --------------------------------------------------------------------------- geometri
def halkalari_birlestir(yollar: list[list[tuple[float, float]]]) -> list[list[tuple[float, float]]]:
    """Uç uca gelen yol parçalarını kapalı halkalara dönüştürür."""
    kalan = [list(y) for y in yollar if len(y) >= 2]
    halkalar = []
    while kalan:
        halka = kalan.pop()
        while halka[0] != halka[-1]:
            for i, y in enumerate(kalan):
                if y[0] == halka[-1]:
                    halka.extend(y[1:])
                elif y[-1] == halka[-1]:
                    halka.extend(reversed(y[:-1]))
                else:
                    continue
                kalan.pop(i)
                break
            else:
                raise ValueError("İlçe sınırı kapalı bir halka oluşturmuyor")
        halkalar.append(halka)
    return halkalar


def halka_icinde(nokta: tuple[float, float], halka: list[tuple[float, float]]) -> bool:
    """Işın atma (ray casting) yöntemiyle nokta-çokgen testi."""
    x, y = nokta
    icinde = False
    j = len(halka) - 1
    for i in range(len(halka)):
        xi, yi = halka[i]
        xj, yj = halka[j]
        if (yi > y) != (yj > y) and x < (xj - xi) * (y - yi) / (yj - yi) + xi:
            icinde = not icinde
        j = i
    return icinde


# --------------------------------------------------------------------------- dönüştürme
def temiz(deger: str | None) -> str:
    return " ".join((deger or "").split())


def adres(t: dict) -> str:
    if t.get("addr:full"):
        return temiz(t["addr:full"])
    parcalar = []
    mahalle = t.get("addr:neighbourhood") or t.get("addr:suburb") or t.get("addr:quarter")
    if mahalle:
        parcalar.append(mahalle if "mah" in mahalle.lower() else f"{mahalle} Mah.")
    sokak = t.get("addr:street") or t.get("addr:place")
    if sokak:
        no = t.get("addr:housenumber")
        parcalar.append(f"{sokak} No: {no}" if no else sokak)
    return temiz(", ".join(parcalar))


def web_adresi(t: dict) -> str:
    u = temiz(t.get("website") or t.get("contact:website") or t.get("url")).split(";")[0].strip()
    if not u:
        return ""
    if not u.lower().startswith(("http://", "https://")):
        u = "https://" + u
    return u


def mutfak(t: dict) -> str:
    degerler = [d.strip().lower() for d in (t.get("cuisine") or "").split(";") if d.strip()]
    return ", ".join(MUTFAK.get(d, d.replace("_", " ").capitalize()) for d in degerler)


def ozellik(ogeler: dict) -> dict:
    """Boş değerleri atarak dosyayı küçük tutar."""
    return {k: v for k, v in ogeler.items() if v not in ("", None, False)}


def osm_donustur(ham_ogeler: list[dict], dis_halkalar, ic_halkalar) -> list[dict]:
    gorulen: set[str] = set()
    sonuc = []
    for o in ham_ogeler:
        kimlik = f"{o['type'][0]}{o['id']}"
        if kimlik in gorulen:
            continue
        gorulen.add(kimlik)

        t = o.get("tags") or {}
        sinif = siniflandir(t)
        if not sinif:
            continue
        if o["type"] == "node":
            lon, lat = o["lon"], o["lat"]
        elif "center" in o:
            lon, lat = o["center"]["lon"], o["center"]["lat"]
        else:
            continue
        if not any(halka_icinde((lon, lat), h) for h in dis_halkalar):
            continue
        if any(halka_icinde((lon, lat), h) for h in ic_halkalar):
            continue

        kategori, tur = sinif
        ad = temiz(t.get("name") or t.get("name:tr") or t.get("brand") or t.get("operator"))
        sonuc.append({
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [round(lon, 6), round(lat, 6)]},
            "properties": ozellik({
                "id": kimlik,
                "ad": ad or tur,
                "adsiz": not ad,
                "kat": kategori,
                "tur": tur,
                "adres": adres(t),
                "tel": temiz(t.get("phone") or t.get("contact:phone") or t.get("contact:mobile")),
                "web": web_adresi(t),
                "eposta": temiz(t.get("email") or t.get("contact:email")),
                "saat": temiz(t.get("opening_hours")),
                "mutfak": mutfak(t),
                "marka": temiz(t.get("brand")) if temiz(t.get("brand")) != ad else "",
                "isleten": temiz(t.get("operator")) if temiz(t.get("operator")) != ad else "",
                "engelli": ENGELLI.get(t.get("wheelchair", ""), ""),
                "kaynak": "osm",
                "osm": f"{o['type']}/{o['id']}",
            }),
        })
    return sonuc


def telefon(numara: str) -> str:
    """+905321234567 -> +90 532 123 45 67"""
    rakam = re.sub(r"[^\d+]", "", numara or "")
    m = re.fullmatch(r"\+90(\d{3})(\d{3})(\d{2})(\d{2})", rakam)
    return f"+90 {m[1]} {m[2]} {m[3]} {m[4]}" if m else temiz(numara)


def overture_donustur(kayitlar: list[dict], dis_halkalar, ic_halkalar, esik: float) -> list[dict]:
    import overture

    sonuc = []
    for k in kayitlar:
        if (k.get("confidence") or 0) < esik:
            continue
        if k.get("operating_status") not in (None, "open"):
            continue
        ad = temiz((k.get("names") or {}).get("primary"))
        sinif = overture.siniflandir(k)
        if not ad or not sinif:
            continue
        lon, lat = k["lon"], k["lat"]
        if not any(halka_icinde((lon, lat), h) for h in dis_halkalar):
            continue
        if any(halka_icinde((lon, lat), h) for h in ic_halkalar):
            continue

        kategori, tur = sinif
        a = (k.get("addresses") or [{}])[0] or {}
        adr = temiz(a.get("freeform"))
        yer = temiz(a.get("locality"))
        if yer and yer.lower() not in adr.lower():
            adr = f"{adr}, {yer}" if adr else yer
        web = temiz((k.get("websites") or [""])[0])
        if web and not web.lower().startswith(("http://", "https://")):
            web = "https://" + web
        marka = temiz((((k.get("brand") or {}).get("names")) or {}).get("primary"))
        saglayici = ((k.get("sources") or [{}])[0] or {}).get("dataset") or ""
        sonuc.append({
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [round(lon, 6), round(lat, 6)]},
            "properties": ozellik({
                "id": "o" + k["id"].replace("-", "")[:14],
                "ad": ad,
                "kat": kategori,
                "tur": tur,
                "adres": adr,
                "tel": "; ".join(telefon(t) for t in (k.get("phones") or [])[:2]),
                "web": web,
                "sosyal": temiz((k.get("socials") or [""])[0]),
                "marka": marka if marka != ad else "",
                "kaynak": "overture",
                "saglayici": saglayici,
                "guven": round((k.get("confidence") or 0) * 100),
            }),
        })
    return sonuc


# --------------------------------------------------------------------------- birleştirme
_HARF = str.maketrans("çğıöşüâîû", "cgiosuaiu")
DOLGU = {"ve", "the", "serdivan", "sakarya", "adapazari", "subesi", "sube", "ltd", "sti", "as", "tic", "san"}
GENEL = {
    "eczane", "eczanesi", "market", "cafe", "kafe", "restaurant", "restoran", "kuafor", "berber", "otel",
    "hotel", "atm", "avm", "bank", "bankasi", "kafeterya",
    "pastanesi", "pastane", "firin", "firini", "lokantasi", "kasap", "kasabi", "emlak", "insaat", "mobilya",
    "oto", "petrol", "coffee", "kahve", "kebap", "doner", "pide", "bufe", "tekel", "giyim", "kuyumculuk",
}


def belirtecler(ad: str) -> set[str]:
    return {b for b in re.findall(r"[a-z0-9]+", ad.replace("İ", "i").lower().translate(_HARF)) if b not in DOLGU}


def benzer(a: set[str], b: set[str]) -> bool:
    """İki işletme adı aynı yeri anlatıyor mu? (kaba bir benzerlik ölçütü)"""
    if not a or not b:
        return False
    if a == b:
        return True
    oz_a, oz_b = a - GENEL, b - GENEL
    if not oz_a or not oz_b:  # yalnızca "Eczane", "Market" gibi genel sözcükler: birebir eşleşme şart
        return False
    ortak = len(oz_a & oz_b)
    return ortak / len(oz_a | oz_b) > 0.5 or (ortak >= 2 and (oz_a <= oz_b or oz_b <= oz_a))


def metre(a: list[float], b: list[float]) -> float:
    dx = (a[0] - b[0]) * 111_320 * math.cos(math.radians(a[1]))
    dy = (a[1] - b[1]) * 111_320
    return math.hypot(dx, dy)


class Izgara:
    """Yakındaki işletmeleri hızlı bulmak için ~110 m'lik hücrelerden oluşan basit mekânsal dizin."""

    def __init__(self) -> None:
        self.hucreler: dict[tuple[int, int], list[tuple[dict, set[str]]]] = {}

    @staticmethod
    def _anahtar(k: list[float]) -> tuple[int, int]:
        return int(k[0] / 0.0013), int(k[1] / 0.001)

    def ekle(self, f: dict) -> None:
        self.hucreler.setdefault(self._anahtar(f["geometry"]["coordinates"]), []).append(
            (f, belirtecler(f["properties"]["ad"])))

    def benzerini_bul(self, f: dict, yaricap: float) -> dict | None:
        k = f["geometry"]["coordinates"]
        ad = belirtecler(f["properties"]["ad"])
        x, y = self._anahtar(k)
        for i in (x - 1, x, x + 1):
            for j in (y - 1, y, y + 1):
                for diger, diger_ad in self.hucreler.get((i, j), ()):
                    if metre(k, diger["geometry"]["coordinates"]) <= yaricap and benzer(ad, diger_ad):
                        return diger
        return None


def birlestir(osm: list[dict], ov: list[dict]) -> tuple[list[dict], int]:
    """OSM kayıtlarını esas alır; Overture'dan yalnızca OSM'de olmayanları ekler."""
    izgara = Izgara()
    for f in osm:
        if not f["properties"].get("adsiz"):
            izgara.ekle(f)

    eklenen = []
    cift = 0
    for f in sorted(ov, key=lambda f: -f["properties"]["guven"]):
        es = izgara.benzerini_bul(f, 120)
        if es is None:
            izgara.ekle(f)
            eklenen.append(f)
            continue
        cift += 1
        if es["properties"].get("kaynak") == "osm":  # OSM kaydındaki eksik iletişim bilgilerini tamamla
            for alan in ("adres", "tel", "web", "sosyal"):
                if alan in f["properties"] and alan not in es["properties"]:
                    es["properties"][alan] = f["properties"][alan]
    return osm + eklenen, cift


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--onbellek", type=Path, help="Ham Overpass yanıtlarının saklanacağı / okunacağı klasör")
    ap.add_argument("--cikti", type=Path, default=KOK / "data", help="Çıktı klasörü (varsayılan: data/)")
    ap.add_argument("--overture-yok", action="store_true", help="Overture Maps verisini kullanma (yalnızca OSM)")
    ap.add_argument("--guven", type=float, default=0.5, help="Overture kayıtları için en düşük güven puanı (0-1)")
    a = ap.parse_args()

    print("1/4 İlçe sınırı indiriliyor…")
    sinir = overpass(f"[out:json][timeout:120];rel({ILCE_RELATION});out geom;", "sinir", a.onbellek)
    iliski = sinir["elements"][0]

    def yollar(rol: str):
        return [
            [(n["lon"], n["lat"]) for n in u["geometry"]]
            for u in iliski["members"]
            if u["type"] == "way" and u.get("role") == rol and u.get("geometry")
        ]

    dis = halkalari_birlestir(yollar("outer"))
    ic = halkalari_birlestir(yollar("inner"))
    lonlar = [x for h in dis for x, _ in h]
    latlar = [y for h in dis for _, y in h]
    kutu = f"{min(latlar)},{min(lonlar)},{max(latlar)},{max(lonlar)}"

    print("2/4 OpenStreetMap işletmeleri indiriliyor…")
    ham: list[dict] = []
    son_guncelleme = ""
    for anahtar in ANAHTARLAR:
        veri = overpass(f'[out:json][timeout:120];nwr["{anahtar}"]({kutu});out center tags;', f"poi_{anahtar}", a.onbellek)
        ham.extend(veri["elements"])
        son_guncelleme = max(son_guncelleme, veri.get("osm3s", {}).get("timestamp_osm_base", ""))

    osm = osm_donustur(ham, dis, ic)

    ov: list[dict] = []
    ov_surum = ""
    if a.overture_yok:
        print("3/4 Overture Maps atlandı (--overture-yok).")
    else:
        print("3/4 Overture Maps işletmeleri indiriliyor…")
        try:
            import overture
            ov_ham = overture.indir((min(lonlar), min(latlar), max(lonlar), max(latlar)), a.onbellek)
            ov_surum = ov_ham["surum"]
            ov = overture_donustur(ov_ham["kayitlar"], dis, ic, a.guven)
        except ImportError:
            print("  ! pyarrow kurulu değil; yalnızca OpenStreetMap verisi kullanılacak (pip install pyarrow).")

    print("4/4 Birleştiriliyor…")
    isletmeler, cift = birlestir(osm, ov)
    isletmeler.sort(key=lambda f: f["properties"]["id"])
    if not isletmeler:
        print("Hiç işletme bulunamadı; dosyalar değiştirilmedi.", file=sys.stderr)
        return 1

    sayim = Counter(f["properties"]["kat"] for f in isletmeler)
    a.cikti.mkdir(parents=True, exist_ok=True)

    cokgenler = [[[[round(x, 6), round(y, 6)] for x, y in h]] for h in dis]
    for h in ic:  # iç halkaları (varsa) kendilerini içeren dış halkaya ekle
        for c, d in zip(cokgenler, dis):
            if halka_icinde(h[0], d):
                c.append([[round(x, 6), round(y, 6)] for x, y in h])
                break
    sinir_geojson = {
        "type": "Feature",
        "properties": {"ad": "Serdivan", "osm": f"relation/{ILCE_RELATION}"},
        "geometry": {"type": "Polygon", "coordinates": cokgenler[0]} if len(cokgenler) == 1
        else {"type": "MultiPolygon", "coordinates": cokgenler},
    }
    (a.cikti / "serdivan-sinir.geojson").write_text(
        json.dumps(sinir_geojson, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")

    koleksiyon = {
        "type": "FeatureCollection",
        "meta": {
            "tarih": (son_guncelleme[:10] or date.today().isoformat()),
            "kaynak": "© OpenStreetMap katkıcıları (ODbL 1.0)" + (" · © Overture Maps Foundation (CDLA-Permissive 2.0)" if ov else ""),
            "overture_surum": ov_surum,
            "toplam": len(isletmeler),
            "kaynaklar": dict(Counter(f["properties"]["kaynak"] for f in isletmeler)),
            "kategoriler": dict(sorted(sayim.items())),
            "merkez": [
                round(statistics.median(f["geometry"]["coordinates"][0] for f in isletmeler), 5),
                round(statistics.median(f["geometry"]["coordinates"][1] for f in isletmeler), 5),
            ],
        },
        "features": isletmeler,
    }
    satirlar = ",\n".join(json.dumps(f, ensure_ascii=False, separators=(",", ":")) for f in isletmeler)
    bas = json.dumps({k: v for k, v in koleksiyon.items() if k != "features"}, ensure_ascii=False, separators=(",", ":"))
    (a.cikti / "isletmeler.geojson").write_text(
        f'{bas[:-1]},"features":[\n{satirlar}\n]}}\n', encoding="utf-8")

    print(f"\n{len(isletmeler)} işletme yazıldı → {a.cikti / 'isletmeler.geojson'}")
    for kategori, adet in sayim.most_common():
        print(f"  {kategori:14s} {adet}")
    adsiz = sum(1 for f in isletmeler if f["properties"].get("adsiz"))
    print(f"  (OSM: {len(osm)}, Overture'dan eklenen: {len(isletmeler) - len(osm)}, "
          f"yinelenen/elenen: {cift}, adı girilmemiş: {adsiz})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
