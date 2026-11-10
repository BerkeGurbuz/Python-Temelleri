"""Overture Maps "places" verisi: indirme ve Türkçe sınıflandırma.

Overture Maps Foundation'ın açık işletme veri seti (Meta, Microsoft, Foursquare vb. kaynaklı)
OpenStreetMap'e göre çok daha fazla işletme içerir. Veri AWS S3 üzerinde GeoParquet olarak
yayımlanır; okumak için `pyarrow` gerekir:  pip install pyarrow
"""
from __future__ import annotations

import json
import os
import struct
from pathlib import Path
from urllib.parse import urlparse

KOVA = "overturemaps-us-west-2"

# --------------------------------------------------------------------------- sınıflandırma
# Üst düzey Overture kategorisi -> haritadaki kategori (None: işletme değil, atla)
UST = {
    "food_and_drink": "yeme-icme",
    "shopping": "alisveris",
    "services_and_business": "hizmet",
    "community_and_government": "kamu",
    "cultural_and_historic": None,
    "education": "egitim",
    "geographic_entities": None,
    "arts_and_entertainment": "spor-eglence",
    "lodging": "konaklama",
    "sports_and_recreation": "spor-eglence",
    "travel_and_transportation": None,
    "health_care": "saglik",
    "lifestyle_services": "guzellik",
}

# basic_category / primary düzeyinde istisnalar (üst düzey eşlemeyi ezer)
OZEL = {
    # market & gıda
    "food_and_beverage_store": "market-gida", "convenience_store": "market-gida", "farmers_market": "market-gida",
    "grocery_store": "market-gida", "butcher_shop": "market-gida", "organic_grocery_store": "market-gida",
    "produce_store": "market-gida", "health_food_store": "market-gida", "liquor_store": "market-gida",
    "superstore": "market-gida", "warehouse_club_store": "market-gida", "candy_store": "market-gida",
    "chocolatier": "market-gida", "delicatessen": "market-gida", "market": "market-gida",
    # sağlık
    "pharmacy_and_drug_store": "saglik", "pharmacy": "saglik", "eyewear_store": "saglik",
    "veterinarian": "saglik", "nutrition_service": "saglik", "senior_living_facility": "saglik",
    "retirement_home": "saglik",
    # araç
    "auto_dealer": "arac", "vehicle_dealer": "arac", "vehicle_parts_store": "arac", "automotive_service": "arac",
    "gas_station": "arac", "vehicle_service": "arac", "taxi_or_ride_share_service": "arac",
    # güzellik
    "personal_care_and_beauty_store": "guzellik",
    # finans
    "atm": "finans", "bank_or_credit_union": "finans", "financial_service": "finans",
    # hizmet
    "travel_service": "hizmet", "animal_or_pet_service": "hizmet", "event_or_party_service": "hizmet",
    "cultural_center": "spor-eglence", "library": "kamu",
    # işletme olmayanlar
    "park": None, "recreational_trail_or_path": None, "national_park": None, "public_plaza": None,
    "military_site": None, "parking": None, "public_transit_facility_or_service": None, "train_station": None,
    "sport_field": None, "condominium": None, "hiking_trail": None,
}

TEMEL_ADI = {
    # yeme-içme
    "restaurant": "Restoran", "cafe": "Kafe", "coffee_shop": "Kahve dükkânı", "casual_eatery": "Lokanta / Büfe",
    "fast_food_restaurant": "Fast food", "bar": "Bar", "non_alcoholic_beverage_venue": "İçecek mekânı",
    "smoothie_juice_bar": "Meyve suyu / Smoothie", "lounge": "Lounge", "food_court": "Yemek alanı",
    "food_and_drink": "Yeme içme", "brewery": "Bira imalathanesi", "winery": "Şarap evi",
    # alışveriş
    "hardware_home_and_garden_store": "Ev, yapı ve bahçe mağazası", "food_and_beverage_store": "Gıda mağazası",
    "fashion_and_apparel_store": "Giyim mağazası", "shopping": "Mağaza", "electronics_store": "Elektronik mağazası",
    "flowers_and_gifts_store": "Çiçek ve hediyelik", "shopping_mall": "Alışveriş merkezi",
    "convenience_store": "Market / Bakkal", "pharmacy_and_drug_store": "Eczane", "auto_dealer": "Oto galeri",
    "sporting_goods_store": "Spor malzemeleri", "personal_care_and_beauty_store": "Kozmetik / Kişisel bakım",
    "arts_crafts_and_hobby_store": "Hobi ve el işi mağazası", "vehicle_dealer": "Araç satıcısı",
    "books_music_and_video_store": "Kitap / Müzik mağazası", "animal_and_pet_store": "Pet shop",
    "department_store": "Mağaza", "warehouse_club_store": "Toptan market", "office_supply_store": "Kırtasiye / Ofis malzemeleri",
    "farmers_market": "Pazar", "vehicle_parts_store": "Oto yedek parça", "toys_and_games_store": "Oyuncak mağazası",
    "discount_store": "İndirim mağazası", "superstore": "Hipermarket", "specialty_store": "Özel ürün mağazası",
    "market": "Pazar yeri", "second_hand_store": "İkinci el mağazası",
    # hizmet
    "real_estate_service": "Emlak", "building_or_construction_service": "İnşaat / Yapı hizmetleri",
    "event_or_party_service": "Organizasyon / Etkinlik", "professional_service": "Profesyonel hizmet",
    "home_service": "Ev hizmetleri", "atm": "ATM", "manufacturer": "Üretici / İmalat",
    "corporate_or_business_office": "Şirket ofisi", "attorney_or_law_firm": "Avukatlık bürosu",
    "financial_service": "Finansal hizmet", "technical_service": "Teknik servis", "bank_or_credit_union": "Banka",
    "printing_service": "Matbaa / Baskı", "farm": "Çiftlik", "design_service": "Tasarım hizmetleri",
    "media_service": "Medya", "storage_facility": "Depo", "b2b_service": "Kurumsal hizmet",
    "b2b_transportation_and_storage_service": "Nakliye ve depolama", "senior_living_facility": "Huzurevi / Bakımevi",
    "supplier_or_distributor": "Tedarikçi / Dağıtıcı", "b2b_industrial_and_machine_service": "Endüstriyel hizmet",
    "legal_service": "Hukuk hizmetleri", "agricultural_service": "Tarım hizmetleri", "laundry_service": "Çamaşırhane / Kuru temizleme",
    "rental_service": "Kiralama", "shipping_or_delivery_service": "Kargo / Teslimat", "family_service": "Aile hizmetleri",
    "radio_station": "Radyo", "environmental_or_ecological_service": "Çevre hizmetleri",
    "b2b_office_and_professional_service": "Ofis hizmetleri", "b2b_science_and_technology_service": "Teknoloji hizmetleri",
    "travel_service": "Seyahat acentesi", "animal_or_pet_service": "Evcil hayvan hizmetleri",
    # kamu
    "social_or_community_service": "Sosyal hizmet / Dernek", "government_office": "Kamu kurumu",
    "community_and_government": "Kamu / Topluluk", "community_center": "Toplum merkezi", "youth_organization": "Gençlik kuruluşu",
    "civic_organization": "Sivil toplum kuruluşu", "police_station": "Polis / Karakol", "courthouse": "Adliye",
    "political_organization": "Siyasi parti", "electric_utility_provider": "Elektrik idaresi", "public_utility": "Kamu hizmeti",
    "library": "Kütüphane",
    # eğitim
    "college_university": "Üniversite", "campus_building": "Kampüs binası", "elementary_school": "İlkokul",
    "place_of_learning": "Eğitim kurumu", "preschool": "Anaokulu / Kreş", "specialty_school": "Kurs / Özel eğitim",
    "education": "Eğitim", "high_school": "Lise", "middle_school": "Ortaokul", "educational_service": "Eğitim hizmetleri",
    "research_institute": "Araştırma enstitüsü",
    # eğlence / spor
    "arts_and_entertainment": "Sanat ve eğlence", "dance_club": "Gece kulübü", "art_gallery": "Sanat galerisi",
    "music_venue": "Müzik mekânı", "arcade": "Oyun salonu", "stadium_arena": "Stadyum / Salon", "movie_theater": "Sinema",
    "event_venue": "Etkinlik mekânı", "theatre_venue": "Tiyatro", "comedy_club": "Komedi kulübü",
    "amusement_attraction": "Eğlence merkezi", "social_club": "Sosyal kulüp", "amusement_park": "Lunapark",
    "adult_entertainment_venue": "Eğlence mekânı", "gym": "Spor salonu", "sport_or_fitness_facility": "Spor tesisi",
    "fitness_studio": "Fitness stüdyosu", "sport_league": "Spor ligi / kulübü", "swimming_pool": "Yüzme havuzu",
    "sport_court": "Spor sahası", "sports_and_recreation": "Spor ve rekreasyon", "sport_team": "Spor takımı",
    "sport_or_recreation_club": "Spor kulübü", "cultural_center": "Kültür merkezi",
    # konaklama
    "lodging": "Konaklama", "hotel": "Otel", "campground": "Kamp alanı", "bed_and_breakfast": "Pansiyon",
    "private_lodging": "Kiralık konut",
    # araç
    "automotive_service": "Oto servis", "gas_station": "Akaryakıt istasyonu", "vehicle_service": "Araç servisi",
    "taxi_or_ride_share_service": "Taksi",
    # sağlık
    "diagnostics_imaging_or_lab_service": "Tahlil / Görüntüleme merkezi", "behavioral_or_mental_health_clinic": "Psikolog / Psikiyatri",
    "dental_clinic": "Diş kliniği", "hospital": "Hastane", "outpatient_care_facility": "Poliklinik",
    "specialized_health_care": "Uzman hekim", "physical_medicine_and_rehabilitation": "Fizik tedavi",
    "reproductive_perinatal_and_womens_care": "Kadın sağlığı", "vision_or_eye_care_clinic": "Göz kliniği",
    "health_care": "Sağlık hizmeti", "medical_service": "Sağlık hizmeti", "surgery": "Cerrahi", "pediatric_clinic": "Çocuk doktoru",
    "specialized_medical_facility": "Sağlık merkezi",
    # güzellik
    "wellness_service": "Sağlıklı yaşam / Spa", "personal_or_beauty_service": "Güzellik hizmetleri",
}

BIRINCIL_ADI = {
    "furniture_store": "Mobilya mağazası", "home_developer": "İnşaat firması", "grocery_store": "Market",
    "real_estate_agent": "Emlakçı", "spa": "Spa / Güzellik merkezi", "party_and_event_planning": "Organizasyon",
    "bakery": "Fırın / Pastane", "doctors_office": "Muayenehane", "turkish_restaurant": "Türk mutfağı restoranı",
    "advertising_agency": "Reklam ajansı", "beauty_salon": "Güzellik salonu", "steakhouse": "Et lokantası / Steakhouse",
    "pharmacy": "Eczane", "veterinarian": "Veteriner", "school": "Okul", "dessert_shop": "Tatlıcı",
    "psychology": "Psikolog", "clothing_store": "Giyim mağazası", "eyewear_store": "Gözlükçü",
    "auto_detailing": "Oto kuaför", "nutrition_service": "Diyetisyen", "womens_clothing_store": "Kadın giyim",
    "doner_kebab_restaurant": "Dönerci / Kebapçı", "barber": "Berber", "beauty_supply_store": "Kozmetik mağazası",
    "pizza_restaurant": "Pizzacı", "building_supply_store": "Yapı malzemeleri", "engineering_service": "Mühendislik",
    "breakfast_and_brunch_restaurant": "Kahvaltı salonu", "ice_cream_shop": "Dondurmacı", "butcher_shop": "Kasap",
    "automotive_repair": "Oto tamir", "hair_salon": "Kuaför", "chicken_restaurant": "Tavuk restoranı",
    "burger_restaurant": "Burgerci", "mens_clothing_store": "Erkek giyim", "shoe_store": "Ayakkabı mağazası",
    "interior_design": "İç mimarlık", "barbecue_restaurant": "Mangal / Izgara", "mobile_phone_store": "Cep telefonu mağazası",
    "delicatessen": "Şarküteri", "language_school": "Dil kursu", "jewelry_store": "Kuyumcu",
    "motorcycle_dealer": "Motosiklet satıcısı", "appraisal_service": "Ekspertiz", "bookstore": "Kitabevi",
    "chocolatier": "Çikolatacı", "architectural_designer": "Mimarlık ofisi", "counseling": "Danışmanlık",
    "home_goods_store": "Ev eşyaları", "tea_room": "Çay bahçesi / Çay evi", "carpet_cleaning": "Halı yıkama",
    "software_development": "Yazılım şirketi", "retirement_home": "Huzurevi", "home_cleaning": "Ev temizliği",
    "pet_store": "Pet shop", "bagel_shop": "Simitçi", "pilates_studio": "Pilates stüdyosu",
    "lighting_store": "Aydınlatma mağazası", "hardware_store": "Hırdavat / Nalbur", "freight_and_cargo_service": "Kargo / Nakliye",
    "it_service_and_computer_repair": "Bilgisayar servisi", "appliance_store": "Beyaz eşya mağazası",
    "private_school": "Özel okul", "insurance_agency": "Sigorta acentesi", "obstetrics_and_gynecology": "Kadın doğum uzmanı",
    "bank": "Banka", "car_wash": "Oto yıkama", "commercial_industrial": "Sanayi işletmesi", "machine_shop": "Torna / Makine atölyesi",
    "information_technology_company": "Bilişim şirketi", "industrial_company": "Sanayi şirketi",
    "automation_service": "Otomasyon", "glass_and_mirror_sales_service": "Cam ve ayna", "childrens_clothing_store": "Çocuk giyim",
    "public_school": "Devlet okulu", "nursery_and_gardening_store": "Fidanlık / Bahçe market",
    "auto_parts_store": "Oto yedek parça", "industrial_equipment_manufacturer": "Endüstriyel ekipman üreticisi",
    "auditorium": "Konferans salonu", "media_agency": "Medya ajansı", "yoga_studio": "Yoga stüdyosu",
    "buffet_restaurant": "Açık büfe restoran", "bridal_shop": "Gelinlik mağazası", "physical_therapy": "Fizyoterapi",
    "optometry": "Göz muayenesi", "toy_store": "Oyuncakçı", "taxi_service": "Taksi durağı", "wedding_planning": "Düğün organizasyonu",
    "driving_school": "Sürücü kursu", "italian_restaurant": "İtalyan restoranı", "dry_cleaning": "Kuru temizleme",
    "mattress_store": "Yatak mağazası", "home_improvement_store": "Yapı market", "seafood_restaurant": "Balık restoranı",
    "bus_station": "Otobüs terminali", "plastics_company": "Plastik firması", "car_rental_service": "Araç kiralama",
    "asian_restaurant": "Asya mutfağı", "fabric_store": "Kumaşçı", "horse_boarding": "At çiftliği",
    "property_management": "Mülk yönetimi", "organic_grocery_store": "Organik market", "financial_advising": "Finans danışmanlığı",
    "nail_salon": "Tırnak salonu", "plastic_and_reconstructive_surgery": "Estetik cerrahi", "carpet_store": "Halı mağazası",
    "hvac_service": "Klima / Isıtma servisi", "medical_service_organization": "Sağlık kuruluşu",
    "fish_and_chips_restaurant": "Balık restoranı", "comfort_food_restaurant": "Ev yemekleri",
    "vocational_and_technical_school": "Meslek okulu", "tennis_court": "Tenis kortu",
    "cosmetics_and_fragrance_store": "Kozmetik / Parfümeri", "watch_store": "Saatçi", "contractor": "Müteahhit",
    "makeup_artist": "Makyaj uzmanı", "appliance_manufacturer": "Beyaz eşya üreticisi", "psychotherapy": "Psikoterapi",
    "podiatry": "Ayak sağlığı", "mover": "Evden eve nakliyat", "outdoor_store": "Outdoor mağazası",
    "web_designer": "Web tasarım", "diving_center": "Dalış merkezi", "produce_store": "Manav",
    "pool_cleaning": "Havuz bakımı", "mediterranean_restaurant": "Akdeniz mutfağı", "diner": "Lokanta",
    "metal_fabricator": "Metal işleme", "publisher": "Yayınevi", "bowling_alley": "Bowling salonu",
    "granite_supplier": "Mermer / Granit", "soccer_stadium": "Futbol stadyumu", "medical_school": "Tıp fakültesi",
    "post_office": "Postane", "home_security": "Güvenlik sistemleri", "american_restaurant": "Amerikan mutfağı",
    "beauty_product_supplier": "Güzellik ürünleri tedarikçisi", "hostel": "Hostel", "dermatology": "Cildiye",
    "fitness_trainer": "Spor eğitmeni", "money_transfer_service": "Para transferi", "candy_store": "Şekerci",
    "speech_therapy": "Dil ve konuşma terapisi", "non_governmental_association": "Dernek", "dance_studio": "Dans stüdyosu",
    "funeral_service": "Cenaze hizmetleri", "tattoo_and_piercing": "Dövme / Piercing", "theatrical_production": "Tiyatro topluluğu",
    "telecommunications_company": "Telekomünikasyon", "health_food_store": "Sağlıklı gıda", "tobacco_shop": "Tütün ürünleri",
    "town_hall": "Belediye", "damage_restoration": "Onarım / Restorasyon", "abuse_and_addiction_treatment_center": "Bağımlılık tedavi merkezi",
    "linen_store": "Ev tekstili", "ear_nose_and_throat": "Kulak burun boğaz", "cardiology": "Kardiyoloji",
    "political_party_office": "Parti binası", "tour_operator": "Tur operatörü", "pest_control_service": "İlaçlama",
    "countertop_installation": "Tezgâh montajı", "tire_dealer_and_repair": "Lastikçi", "accountant": "Mali müşavir",
    "hunting_and_fishing_store": "Av ve balıkçılık malzemeleri", "furniture_assembly": "Mobilya montaj",
    "florist": "Çiçekçi", "pub": "Pub", "paintball": "Paintball", "holiday_rental_home": "Kiralık tatil evi",
    "elevator_service": "Asansör servisi", "water_park": "Su parkı", "internet_marketing_service": "Dijital pazarlama",
    "shooting_range": "Atış poligonu", "boxing_class": "Boks salonu", "hookah_bar": "Nargile kafe",
    "charity_organization": "Yardım kuruluşu", "music_school": "Müzik kursu", "sewing_and_alterations": "Terzi",
    "martial_arts_club": "Dövüş sanatları kulübü", "newspaper_and_magazines_store": "Gazete bayii", "truck_repair": "Kamyon tamir",
    "general_dentistry": "Diş hekimi", "laboratory_testing": "Laboratuvar", "urology": "Üroloji",
    "car_window_tinting": "Cam filmi", "sandwich_shop": "Sandviççi", "mexican_restaurant": "Meksika mutfağı",
    "pool_billiards": "Bilardo salonu", "gymnastics_center": "Jimnastik salonu", "flight_school": "Uçuş okulu",
    "hair_replacement": "Saç ekimi", "pet_groomer": "Pet kuaför", "dairy_farm": "Süt çiftliği",
    "test_preparation": "Sınav hazırlık kursu", "bags_luggage_company": "Çanta / Bavul", "cupcake_shop": "Pastane",
    "fashion_boutique": "Butik", "laser_hair_removal": "Lazer epilasyon", "textile_manufacturer": "Tekstil üreticisi",
    "weight_loss_center": "Zayıflama merkezi", "costume_store": "Kostüm mağazası", "skin_care_and_makeup": "Cilt bakımı",
    "emissions_inspection": "Egzoz muayene", "lumber_store": "Keresteci", "shipping_center": "Kargo şubesi",
    "plastic_manufacturer": "Plastik üreticisi", "public_relations": "Halkla ilişkiler", "divorce_and_family_law": "Aile hukuku",
    "outlet_store": "Outlet mağaza", "french_restaurant": "Fransız mutfağı", "translating_and_interpreting_service": "Tercüme bürosu",
    "notary_public": "Noter", "european_restaurant": "Avrupa mutfağı", "roofing": "Çatı ustası",
    "chinese_restaurant": "Çin mutfağı", "sushi_restaurant": "Suşi restoranı", "service_apartment": "Apart otel",
    "soup_restaurant": "Çorbacı", "media_news_company": "Haber kuruluşu", "swimming_instructor": "Yüzme kursu",
    "auto_customization": "Oto aksesuar / Modifiye", "energy_company": "Enerji şirketi",
    "audio_visual_equipment_store": "Ses ve görüntü sistemleri", "family_counseling": "Aile danışmanlığı",
    "appliance_repair_service": "Beyaz eşya servisi", "lebanese_restaurant": "Lübnan mutfağı", "metal_supplier": "Metal tedarikçisi",
    "pharmaceutical_company": "İlaç firması", "motorcycle_repair": "Motosiklet tamir", "emergency_roadside_service": "Yol yardım",
    "bike_store": "Bisikletçi", "blood_and_plasma_donation_center": "Kan bağış merkezi", "hobby_shop": "Hobi mağazası",
    "food_beverage_distributor": "Gıda toptancısı", "lodge": "Dağ evi", "liquor_store": "Tekel bayii",
    "packing_supply_store": "Ambalaj malzemeleri", "animal_shelter": "Hayvan barınağı", "pet_breeder": "Evcil hayvan üreticisi",
    "religious_school": "Kur'an kursu / Dinî okul", "livestock_breeder": "Hayvancılık", "child_care_and_day_care": "Kreş / Gündüz bakımevi",
    "glass_manufacturer": "Cam üreticisi", "t_shirt_printing_service": "Tişört baskı", "senior_citizen_service": "Yaşlı bakım hizmeti",
    "occupational_therapy": "Ergoterapi", "commercial_real_estate": "Ticari emlak", "recreational_vehicle_dealer": "Karavan satıcısı",
    "clothing_company": "Giyim firması", "windows_installation": "Pencere / PVC montaj", "structural_engineer": "İnşaat mühendisi",
    "fireplace_service": "Şömine", "tv_mounting": "TV montaj", "agriculture": "Tarım", "indonesian_restaurant": "Endonezya mutfağı",
    "eastern_european_restaurant": "Doğu Avrupa mutfağı", "night_market": "Gece pazarı", "flea_market": "Bit pazarı",
    "auto_company": "Otomotiv firması", "railroad_freight": "Demiryolu taşımacılığı", "b2b_water_treatment_service": "Su arıtma",
    "b2b_advertising_and_marketing_service": "Reklam ve pazarlama", "educational_research_institute": "Eğitim araştırma enstitüsü",
    "broadcasting_media_production": "Yayın / Prodüksiyon", "drive_in_theater": "Arabalı sinema", "wedding_chapel": "Nikâh salonu",
    "pop_up_store": "Geçici mağaza", "sky_diving": "Paraşüt", "surfing": "Sörf", "bus_tour": "Otobüs turu",
    "circus_venue": "Sirk", "proctology": "Proktoloji", "prenatal_and_perinatal_care": "Gebelik takibi",
    "professional_sport_team": "Profesyonel spor takımı", "school_sport_team": "Okul spor takımı",
    "medical_research_institute": "Tıbbi araştırma enstitüsü",
}


def siniflandir(kayit: dict) -> tuple[str, str] | None:
    """Overture kaydından (kategori, tür adı) üretir; işletme değilse None döner."""
    taks = kayit.get("taxonomy") or {}
    hiyerarsi = taks.get("hierarchy") or []
    birincil = taks.get("primary")
    temel = kayit.get("basic_category")
    ust = hiyerarsi[0] if hiyerarsi else None

    kategori: str | None
    if birincil in OZEL:
        kategori = OZEL[birincil]
    elif temel in OZEL:
        kategori = OZEL[temel]
    elif ust is None and temel is None and birincil is None:
        kategori = "diger"
    else:
        kategori = UST.get(ust, "diger")
    if kategori is None:
        return None

    tur = (BIRINCIL_ADI.get(birincil) or TEMEL_ADI.get(birincil) or TEMEL_ADI.get(temel)
           or (birincil or temel or "").replace("_", " ").capitalize() or "İşletme")
    return kategori, tur


# --------------------------------------------------------------------------- indirme
def _dosya_sistemi():
    import pyarrow.fs as pafs

    secenekler = dict(anonymous=True, region="us-west-2", request_timeout=180, connect_timeout=30)
    vekil = os.environ.get("HTTPS_PROXY") or os.environ.get("https_proxy")
    if vekil:  # kurumsal / bulut ortamlarında vekil sunucu üzerinden bağlan
        v = urlparse(vekil)
        secenekler.update(
            proxy_options={"scheme": v.scheme, "host": v.hostname, "port": v.port},
            endpoint_override="s3.amazonaws.com",
            force_virtual_addressing=True,
        )
        sertifika = os.environ.get("SSL_CERT_FILE") or os.environ.get("REQUESTS_CA_BUNDLE")
        if sertifika:
            secenekler["tls_ca_file_path"] = sertifika
    return pafs.S3FileSystem(**secenekler)


def _nokta(wkb: bytes) -> tuple[float, float] | None:
    """WKB nokta geometrisini (lon, lat) olarak çözer."""
    if not wkb or len(wkb) < 21:
        return None
    duzen = "<" if wkb[0] == 1 else ">"
    (tip,) = struct.unpack(duzen + "I", wkb[1:5])
    if tip % 1000 != 1:
        return None
    return struct.unpack(duzen + "dd", wkb[5:21])


def indir(kutu: tuple[float, float, float, float], onbellek: Path | None = None) -> dict:
    """Sınır kutusundaki (batı, güney, doğu, kuzey) Overture işletmelerini indirir.

    Dönen değer: {"surum": "2026-10-21.0", "kayitlar": [ {...}, ... ]}
    """
    dosya = onbellek / "overture.json" if onbellek else None
    if dosya and dosya.exists():
        return json.loads(dosya.read_text(encoding="utf-8"))

    import pyarrow.fs as pafs
    import pyarrow.parquet as pq

    bati, guney, dogu, kuzey = kutu
    fs = _dosya_sistemi()
    surumler = sorted(
        b.base_name for b in fs.get_file_info(pafs.FileSelector(f"{KOVA}/release"))
        if b.type == pafs.FileType.Directory
    )
    surum = surumler[-1]
    parcalar = sorted(
        b.path for b in fs.get_file_info(pafs.FileSelector(f"{KOVA}/release/{surum}/theme=places/type=place"))
        if b.path.endswith(".parquet")
    )
    print(f"  Overture sürümü {surum}: {len(parcalar)} dosya taranıyor…")

    sutunlar = ["id", "geometry", "names", "basic_category", "taxonomy", "confidence", "websites", "socials",
                "emails", "phones", "brand", "addresses", "operating_status", "sources"]
    kayitlar = []
    for yol in parcalar:
        pf = pq.ParquetFile(fs.open_input_file(yol))
        md = pf.metadata
        adlar = [md.schema.column(i).path for i in range(md.num_columns)]
        ix = {k: adlar.index(f"bbox.{k}") for k in ("xmin", "xmax", "ymin", "ymax")}
        # Dosyalar mekânsal sıralı: satır gruplarının bbox istatistikleriyle yalnızca ilgili kısmı oku.
        gruplar = []
        for g in range(md.num_row_groups):
            ist = {k: md.row_group(g).column(i).statistics for k, i in ix.items()}
            if any(s is None or not s.has_min_max for s in ist.values()) or (
                ist["xmin"].min <= dogu and ist["xmax"].max >= bati
                and ist["ymin"].min <= kuzey and ist["ymax"].max >= guney
            ):
                gruplar.append(g)
        if not gruplar:
            continue
        mevcut = [s for s in sutunlar if s in pf.schema_arrow.names]
        for satir in pf.read_row_groups(gruplar, columns=mevcut).to_pylist():
            nokta = _nokta(satir.pop("geometry", None))
            if not nokta or not (bati <= nokta[0] <= dogu and guney <= nokta[1] <= kuzey):
                continue
            satir["lon"], satir["lat"] = nokta
            kayitlar.append(satir)

    sonuc = {"surum": surum, "kayitlar": kayitlar}
    print(f"  ✓ overture: {len(kayitlar)} kayıt")
    if dosya:
        dosya.parent.mkdir(parents=True, exist_ok=True)
        dosya.write_text(json.dumps(sonuc, ensure_ascii=False, default=str), encoding="utf-8")
    return sonuc
