import datetime
from database import init_db, SessionLocal, Flight, Hotel, Activity, User
from services.security import get_password_hash

# Lista di 43 destinazioni mondiali con attrazioni reali stile GetYourGuide e cibi tipici
DESTINATIONS = [
    {"city": "Rome", "country": "Italy", "airport": "FCO", "highlights": "Colosseo, Musei Vaticani e Fontana di Trevi", "cuisine": "Pasta Carbonara, Cacio e Pepe e Supplì croccanti"},
    {"city": "Milan", "country": "Italy", "airport": "MXP", "highlights": "Duomo di Milano, Galleria Vittorio Emanuele e Navigli", "cuisine": "Risotto alla Milanese e Cotoletta d'oro"},
    {"city": "Tokyo", "country": "Japan", "airport": "HND", "highlights": "Quartiere Shibuya, Tempio Asakusa e Santuario Meiji", "cuisine": "Sushi fresco, Ramen artigianale e Takoyaki"},
    {"city": "Paris", "country": "France", "airport": "CDG", "highlights": "Tour Eiffel, Museo del Louvre e Montmartre", "cuisine": "Macarons parigini, Croissants sfogliati ed Escargots"},
    {"city": "New York", "country": "United States", "airport": "JFK", "highlights": "Central Park, Empire State Building e Statua della Libertà", "cuisine": "Pizza stile NY, Cheesecake e Hot Dog gourmet"},
    {"city": "London", "country": "United Kingdom", "airport": "LHR", "highlights": "Big Ben, London Eye e Warner Bros Studio Harry Potter", "cuisine": "Fish and Chips croccante e Afternoon Tea inglese"},
    {"city": "Reykjavik", "country": "Iceland", "airport": "KEF", "highlights": "Laguna Blu, Circolo d'Oro e Aurora Boreale", "cuisine": "Skyr artigianale e Zuppa d'agnello islandese"},
    {"city": "Sydney", "country": "Australia", "airport": "SYD", "highlights": "Opera House, Harbour Bridge e Bondi Beach", "cuisine": "Torta di carne tradizionale e Frutti di mare freschi"},
    {"city": "Barcelona", "country": "Spain", "airport": "BCN", "highlights": "Sagrada Familia, Park Güell e Barrio Gotico", "cuisine": "Paella de marisco, Tapas varie e Crema Catalana"},
    {"city": "Madrid", "country": "Spain", "airport": "MAD", "highlights": "Palazzo Reale, Museo del Prado e Parco del Retiro", "cuisine": "Bocadillo de Calamares, Jamón Ibérico e Churros"},
    {"city": "Berlin", "country": "Germany", "airport": "BER", "highlights": "Porta di Brandeburgo, Muro di Berlino e Reichstag", "cuisine": "Currywurst originale e Brezel caldi"},
    {"city": "Munich", "country": "Germany", "airport": "MUC", "highlights": "Marienplatz, Castello di Neuschwanstein ed Englischer Garten", "cuisine": "Weisswurst con senape dolce e Knödel"},
    {"city": "Amsterdam", "country": "Netherlands", "airport": "AMS", "highlights": "Museo Van Gogh, Canali storici e Rijksmuseum", "cuisine": "Stroopwafel caldi e Bitterballen croccanti"},
    {"city": "Vienna", "country": "Austria", "airport": "VIE", "highlights": "Castello di Schönbrunn, Cattedrale di Santo Stefano e Belvedere", "cuisine": "Sachertorte originale e Wiener Schnitzel"},
    {"city": "Athens", "country": "Greece", "airport": "ATH", "highlights": "Acropoli di Atene, Partenone e Quartiere Plaka", "cuisine": "Moussaka tradizionali, Souvlaki e Tzatziki"},
    {"city": "Lisbon", "country": "Portugal", "airport": "LIS", "highlights": "Torre di Belém, Monastero dei Jerónimos e Quartiere Alfama", "cuisine": "Pastel de Nata caldo e Bacalhau a Brás"},
    {"city": "Prague", "country": "Czech Republic", "airport": "PRG", "highlights": "Ponte Carlo, Castello di Praga e Piazza della Città Vecchia", "cuisine": "Goulash boemo e Trdelník alla cannella"},
    {"city": "Budapest", "country": "Hungary", "airport": "BUD", "highlights": "Parlamento di Budapest, Castello di Buda e Terme Széchenyi", "cuisine": "Goulash ungherese e Lángos al formaggio"},
    {"city": "Copenhagen", "country": "Denmark", "airport": "CPH", "highlights": "Giardini di Tivoli, Sirenetta e Porto Nyhavn", "cuisine": "Smørrebrød tradizionali e Danish Pastry caldi"},
    {"city": "Stockholm", "country": "Sweden", "airport": "ARN", "highlights": "Centro storico Gamla Stan, Museo Vasa e Palazzo Reale", "cuisine": "Polpette svedesi con mirtilli e Cinnamon Buns"},
    {"city": "Oslo", "country": "Norway", "airport": "OSL", "highlights": "Parco Vigeland, Museo Fram ed Opera House sul Fjord", "cuisine": "Formaggio Brunost e Salmone norvegese affumicato"},
    {"city": "Helsinki", "country": "Finland", "airport": "HEL", "highlights": "Cattedrale di Helsinki, Fortezza di Suomenlinna e Sauna di Kauppatori", "cuisine": "Karjalanpiirakka e Stufato di renna"},
    {"city": "Cairo", "country": "Egypt", "airport": "CAI", "highlights": "Piramidi di Giza, Grande Sfinge e Bazar Khan el-Khalili", "cuisine": "Koshary egiziano, Falafel e Ful Medames"},
    {"city": "Cape Town", "country": "South Africa", "airport": "CPT", "highlights": "Table Mountain, Robben Island e Capo di Buona Speranza", "cuisine": "Biltong essiccato, Bobotie e Vini di Stellenbosch"},
    {"city": "Dubai", "country": "United Arab Emirates", "airport": "DXB", "highlights": "Burj Khalifa, Safari nel deserto 4x4 e Palm Jumeirah", "cuisine": "Shawarma gourmet, datteri ripieni e Kabsa"},
    {"city": "Bangkok", "country": "Thailand", "airport": "BKK", "highlights": "Grande Palazzo Reale, Tempio Wat Arun e Mercato Galleggiante", "cuisine": "Pad Thai espresso, Tom Yum Goong e Mango Sticky Rice"},
    {"city": "Singapore", "country": "Singapore", "airport": "SIN", "highlights": "Gardens by the Bay, Marina Bay Sands ed Isola di Sentosa", "cuisine": "Chilli Crab speziato e Hainanese Chicken Rice"},
    {"city": "Bali", "country": "Indonesia", "airport": "DPS", "highlights": "Foresta delle Scimmie di Ubud, Tempio Uluwatu e Terrazze di Riso", "cuisine": "Nasi Goreng, Sate Lilit e Babi Guling"},
    {"city": "Seoul", "country": "South Korea", "airport": "ICN", "highlights": "Palazzo Gyeongbokgung, N Seoul Tower e Mercato Myeongdong", "cuisine": "Kimchi fermentato, Korean BBQ e Bibimbap caldissimo"},
    {"city": "Beijing", "country": "China", "airport": "PEK", "highlights": "Grande Muraglia Cinese, Città Proibita e Tempio del Cielo", "cuisine": "Anatra alla Pechinese croccante e Dumplings vapore"},
    {"city": "Delhi", "country": "India", "airport": "DEL", "highlights": "Forte Rosso, Minareto Qutub Minar ed India Gate", "cuisine": "Butter Chicken cremoso e Biryani profumato"},
    {"city": "Mumbai", "country": "India", "airport": "BOM", "highlights": "Gateway of India, Passeggiata Marine Drive e Grotte di Elephanta", "cuisine": "Vada Pav speziato e Pav Bhaji caldo"},
    {"city": "Toronto", "country": "Canada", "airport": "YYZ", "highlights": "Torre CN Tower, Museo Royal Ontario ed Acquario Ripley", "cuisine": "Poutine originale e Peameal Bacon Sandwich"},
    {"city": "Vancouver", "country": "Canada", "airport": "YVR", "highlights": "Parco Stanley, Ponte Sospeso Capilano ed Isola Granville", "cuisine": "Salmone selvaggio grigliato e Japadog gourmet"},
    {"city": "Los Angeles", "country": "United States", "airport": "LAX", "highlights": "Hollywood Walk of Fame, Molo di Santa Monica e Getty Center", "cuisine": "Tacos californiani e Smash Burgers"},
    {"city": "San Francisco", "country": "United States", "airport": "SFO", "highlights": "Ponte Golden Gate, Isola di Alcatraz e Fisherman's Wharf", "cuisine": "Clam Chowder nella pagnotta di pane di pasta madre"},
    {"city": "Miami", "country": "United States", "airport": "MIA", "highlights": "Spiaggia South Beach, Quartiere Little Havana e Murals Wynwood", "cuisine": "Sandwich cubano originale e Torta Key Lime"},
    {"city": "Rio de Janeiro", "country": "Brazil", "airport": "GIG", "highlights": "Statua del Cristo Redentore, Pan di Zucchero e Copacabana", "cuisine": "Feijoada brasiliana, Pão de Queijo e Caipirinha"},
    {"city": "Buenos Aires", "country": "Argentina", "airport": "EZE", "highlights": "Quartiere La Boca, Cimitero Recoleta e Spettacolo di Tango", "cuisine": "Asado argentino alla griglia ed Empanadas fatte a mano"},
    {"city": "Mexico City", "country": "Mexico", "airport": "MEX", "highlights": "Piramidi di Teotihuacan, Museo Frida Kahlo e Piazza Zocalo", "cuisine": "Tacos al Pastor con ananas, Quesadillas e Guacamole fresco"},
    {"city": "Marrakech", "country": "Morocco", "airport": "RAK", "highlights": "Piazza Jemaa el-Fnaa, Palazzo Bahia e Giardini Majorelle", "cuisine": "Tagine speziato, Couscous e Tè alla menta fresco"},
    {"city": "Venice", "country": "Italy", "airport": "VCE", "highlights": "Piazza San Marco, Canal Grande e Ponte di Rialto", "cuisine": "Risi e Bisi, Cicchetti veneziani con Spritz e Sarde in Saor"},
    {"city": "Florence", "country": "Italy", "airport": "FLR", "highlights": "Galleria degli Uffizi, Duomo del Brunelleschi e Ponte Vecchio", "cuisine": "Bistecca alla Fiorentina, Cantucci con Vin Santo e Lampredotto"},
]

# 20 Template GetYourGuide-style ad alta fedeltà e ricchezza di dettagli
ACTIVITY_TEMPLATES = [
    # 1. Tour monumentale con ingresso salta-fila (Cultura)
    {
        "title": "GetYourGuide Original: Tour salta-fila guidato a {highlights}",
        "description": "Evita le lunghe code all'ingresso e accedi prioritariamente a {highlights} a {city}. Accompagnato da una guida esperta locale che ti svelerà segreti, aneddoti storici e dettagli architettonici unici.",
        "price": 55.00,
        "target_audience": "cultura, famiglie, coppie",
        "available_months": "1,2,3,4,5,6,7,8,9,10,11,12"
    },
    # 2. Corso di cucina autentico (Gastronomia)
    {
        "title": "Corso di cucina locale ed assaggio di {cuisine} a {city}",
        "description": "Metti le mani in pasta in un atelier culinario nel cuore di {city}! Impara a preparare da zero le ricette iconiche della tradizione come {cuisine} guidato da uno chef locale. Segue pranzo o cena gourmet con bevande.",
        "price": 75.00,
        "target_audience": "buongustai, coppie, famiglie",
        "available_months": "1,2,3,4,5,6,7,8,9,10,11,12"
    },
    # 3. Street Food Tour nei mercati storici (Gastronomia)
    {
        "title": "Street Food Tour gourmet e degustazione di {cuisine} a {city}",
        "description": "Una passeggiata gastronomica tra i banchi colorati dei mercati tradizionali di {city}. Assaggia oltre 6 specialità autentiche tra cui {cuisine}, raccontate da una guida locale appassionata di cibo.",
        "price": 42.00,
        "target_audience": "giovani, buongustai, solitari",
        "available_months": "1,2,3,4,5,6,7,8,9,10,11,12"
    },
    # 4. Crociera panoramica / Gita in barca (Avventura & Natura)
    {
        "title": "Crociera panoramica e vista su {highlights} a {city}",
        "description": "Sali a bordo di una confortevole imbarcazione e naviga sulle acque di {city} per ammirare le attrazioni leggendarie come {highlights} da un punto di vista spettacolare. Aperitivo di benvenuto e audioguida inclusi.",
        "price": 48.00,
        "target_audience": "coppie, famiglie, relax",
        "available_months": "4,5,6,7,8,9,10"
    },
    # 5. Escursione guidata di un giorno in natura o fuori porta (Avventura & Natura)
    {
        "title": "Escursione guidata di un giorno tra {highlights} nei dintorni di {city}",
        "description": "Lasciati la città alle spalle per un'avventura indimenticabile immersa nella natura o tra le meraviglie monumentali vicine a {city}. Include trasporto in bus gran turismo con aria condizionata e guida dal vivo.",
        "price": 85.00,
        "target_audience": "avventura, natura, famiglie",
        "available_months": "3,4,5,6,7,8,9,10,11"
    },
    # 6. Spettacolo culturale dal vivo serale (Cultura & Intrattenimento)
    {
        "title": "Spettacolo culturale dal vivo e cena tradizionale a {city}",
        "description": "Goditi una serata indimenticabile a {city} assistendo a un autentico spettacolo culturale dal vivo in un teatro d'epoca, accompagnato da una deliziosa cena a base di specialità locali tra cui {cuisine}.",
        "price": 68.00,
        "target_audience": "coppie, cultura, relax",
        "available_months": "1,2,3,4,5,6,7,8,9,10,11,12"
    },
    # 7. Tour in e-bike o bicicletta panoramica (Sport & Natura)
    {
        "title": "Tour panoramico guidato in E-Bike tra i parchi e {highlights} di {city}",
        "description": "Pedala senza sforzo in sella a una bicicletta elettrica moderna ed esplora i parchi verdeggianti e le piazze storiche di {city}. Il percorso tocca i monumenti più celebri come {highlights} con soste fotografiche.",
        "price": 38.00,
        "target_audience": "sportivi, famiglie, natura",
        "available_months": "3,4,5,6,7,8,9,10,11"
    },
    # 8. Esperienza Spa e Terme Benessere (Relax & Benessere)
    {
        "title": "Ingresso Spa, bagno termale e massaggio benessere a {city}",
        "description": "Regalati una pausa di puro relax e benessere in uno storico centro termale o Spa di lusso a {city}. L'esperienza include l'accesso completo a saune, idromassaggi e un trattamenti rilassante personalizzato.",
        "price": 95.00,
        "target_audience": "coppie, relax",
        "available_months": "1,2,3,4,5,6,7,8,9,10,11,12"
    },
    # 9. Visita Esclusiva VIP all'alba prima dell'apertura (Cultura)
    {
        "title": "Ingresso VIP prioritario all'alba a {highlights} senza folle",
        "description": "Accedi a {highlights} a {city} prima dell'orario di apertura ufficiale al pubblico. Ammira la maestosità delle collezioni d'arte e dei monumenti in totale tranquillità e silenzio con una guida d'eccezione.",
        "price": 110.00,
        "target_audience": "cultura, coppie, relax",
        "available_months": "1,2,3,4,5,6,7,8,9,10,11,12"
    },
    # 10. Tour dei Pub storici e vita notturna (Nightlife)
    {
        "title": "Pub Crawl guidato e tour della vita notturna a {city}",
        "description": "Scopri la vivace atmosfera notturna di {city}! Unisciti a un gruppo internazionale per visitare 4 locali e pub storici selezionati, con shot di benvenuto inclusi e ingresso prioritario nei migliori club.",
        "price": 28.00,
        "target_audience": "giovani, nightlife, solitari",
        "available_months": "1,2,3,4,5,6,7,8,9,10,11,12"
    },
    # 11. Trekking ed escursione avventura (Sport & Avventura)
    {
        "title": "Trekking avventura e sentieri panoramici vicino a {city}",
        "description": "Attraversa sentieri mozzafiato e scorci naturali incontaminati nei dintorni di {city}. Una camminata guidata adatta ad amanti dell'aria aperta che culmina in un punto di osservazione panoramico spettacolare.",
        "price": 45.00,
        "target_audience": "sportivi, avventura, natura",
        "available_months": "4,5,6,7,8,9,10"
    },
    # 12. Tour fotografico notturno (Nightlife & Cultura)
    {
        "title": "Tour fotografico notturno tra i monumenti illuminati di {city}",
        "description": "Scatta fotografie da copertina a {city} quando i monumenti storici come {highlights} si accendono di luci suggestive. Guidato da un fotografo professionista che ti insegnerà tecniche di scatto in notturna.",
        "price": 40.00,
        "target_audience": "giovani, coppie, cultura",
        "available_months": "1,2,3,4,5,6,7,8,9,10,11,12"
    },
    # 13. Attività acquatica sportiva (Sport & Azione)
    {
        "title": "Attività acquatica (Kayak, Surf o Paddleboard) a {city}",
        "description": "Sperimenta un'emozionante attività acquatica lungo le coste o i corsi d'acqua di {city}. Include la lezione introduttiva con istruttore qualificato e tutto l'equipaggiamento tecnico necessario.",
        "price": 52.00,
        "target_audience": "sportivi, giovani, avventura",
        "available_months": "6,7,8,9"
    },
    # 14. Yoga e meditazione all'aperto (Relax & Benessere)
    {
        "title": "Sessione di Yoga e Mindfulness al tramonto nei parchi di {city}",
        "description": "Rigenera lo spirito con una sessione di yoga e meditazione guidata al tramonto immerso nei parchi o spiagge panoramiche di {city}. Tappetino e bevanda purificante naturale inclusi.",
        "price": 22.00,
        "target_audience": "relax, sportivi, solitari",
        "available_months": "5,6,7,8,9"
    },
    # 15. Tour del quartiere artistico ed alternativo (Cultura)
    {
        "title": "Esplorazione guidata dei quartieri creativi e Street Art a {city}",
        "description": "Scopri il volto contemporaneo ed alternativo di {city}. Cammina tra gallerie d'arte indipendenti, imponenti murales di street art e mercatini vintage insoliti lontano dalle classiche rotte turistiche.",
        "price": 24.00,
        "target_audience": "giovani, cultura, solitari",
        "available_months": "1,2,3,4,5,6,7,8,9,10,11,12"
    },
    # 16. Cena gourmet di lusso con degustazione vini (Gastronomia)
    {
        "title": "Cena gourmet in ristorante panoramico ed assaggio di {cuisine} a {city}",
        "description": "Una serata gastronomica d'alto livello con vista sulle luci di {city}. Menu degustazione a 4 portate basato sulle migliori ricette tradizionali come {cuisine}, abbinato a vini pregiati selezionati.",
        "price": 125.00,
        "target_audience": "coppie, buongustai, relax",
        "available_months": "1,2,3,4,5,6,7,8,9,10,11,12"
    },
    # 17. Urban Escape Game e Caccia al Tesoro (Avventura & Intrattenimento)
    {
        "title": "Caccia al tesoro urbana ed Escape Game interattivo a {city}",
        "description": "Metti alla prova la tua astuzia risolvendo indovinelli storici e codici segreti mentre cammini per il centro storico di {city}. Un'avventura divertente da fare in squadra o in famiglia guidata da un'app.",
        "price": 19.00,
        "target_audience": "giovani, famiglie, avventura",
        "available_months": "1,2,3,4,5,6,7,8,9,10,11,12"
    },
    # 18. Passeggiata nei Giardini Botanici o Parchi Reali (Relax & Natura)
    {
        "title": "Visita rilassante ai Giardini Botanici Reali ed oasi verdi di {city}",
        "description": "Una camminata rigenerante tra piante secolari, serre monumentali e specchi d'acqua nei giardini storici di {city}. Ideale per chi cerca relax, silenzio ed ispirazione naturale.",
        "price": 16.00,
        "target_audience": "relax, famiglie, cultura",
        "available_months": "3,4,5,6,7,8,9,10"
    },
    # 19. Percorso avventura e arrampicata nei boschi (Sport & Avventura)
    {
        "title": "Parco Avventura, ponti tibetani e zipline nei boschi di {city}",
        "description": "Vivi un'esperienza adrenalinica sospeso tra gli alberi in un parco avventura immerso nei boschi vicino a {city}. Supera ponti di corda, tirolesi e carrucole in totale sicurezza.",
        "price": 36.00,
        "target_audience": "sportivi, avventura, giovani",
        "available_months": "4,5,6,7,8,9,10"
    },
    # 20. Running tour guidato all'alba (Sport & Cultura)
    {
        "title": "Running tour all'alba tra i monumenti deserti ed {highlights} a {city}",
        "description": "Unisci sport e turismo con una corsa panoramica mattutina di 5-8 km. Attraversa le vie deserte di {city} ammirando in solitudine la maestosità di {highlights} guidato da un running coach locale.",
        "price": 25.00,
        "target_audience": "sportivi, giovani, solitari",
        "available_months": "1,2,3,4,5,6,7,8,9,10,11,12"
    }
]

def generate_flights():
    flights = []
    hubs = ["FCO", "MXP"]
    
    flight_dates = [
        (datetime.date(2026, 8, 10), datetime.date(2026, 8, 17)),
        (datetime.date(2026, 9, 15), datetime.date(2026, 9, 22)),
        (datetime.date(2026, 10, 5), datetime.date(2026, 10, 12)),
        (datetime.date(2026, 12, 23), datetime.date(2026, 12, 30)),
        (datetime.date(2027, 4, 10), datetime.date(2027, 4, 17))
    ]
    
    for dest in DESTINATIONS:
        dest_airport = dest["airport"]
        
        if dest_airport in ["FCO", "MXP", "VCE", "FLR"]:
            base_price = 80.00
        elif dest_airport in ["CDG", "LHR", "BCN", "MAD", "BER", "MUC", "AMS", "VIE", "ATH", "LIS", "PRG", "BUD", "CPH", "ARN", "OSL", "HEL"]:
            base_price = 150.00
        elif dest_airport in ["KEF", "CAI", "DXB", "RAK"]:
            base_price = 350.00
        elif dest_airport in ["JFK", "LAX", "SFO", "MIA", "YYZ", "YVR", "GIG", "EZE", "MEX"]:
            base_price = 750.00
        else:
            base_price = 980.00
            
        for i, (dep_date, ret_date) in enumerate(flight_dates):
            if i == 0: multiplier = 1.2
            elif i == 1: multiplier = 1.0
            elif i == 2: multiplier = 0.9
            elif i == 3: multiplier = 1.3
            else: multiplier = 1.1
            
            price = round(base_price * multiplier, 2)
            availability = 10 + (i * 3) % 15
            
            if dest_airport == "FCO":
                departures = ["MXP", "CDG", "JFK", "LHR"]
                dep = departures[i % len(departures)]
                flight_price = price * 2.0 if dep == "JFK" else price
                flights.append(Flight(departure_airport=dep, arrival_airport="FCO", departure_date=dep_date, return_date=ret_date, price=round(flight_price, 2), availability=availability))
            elif dest_airport == "MXP":
                departures = ["FCO", "CDG", "JFK", "LHR"]
                dep = departures[i % len(departures)]
                flight_price = price * 2.0 if dep == "JFK" else price
                flights.append(Flight(departure_airport=dep, arrival_airport="MXP", departure_date=dep_date, return_date=ret_date, price=round(flight_price, 2), availability=availability))
            else:
                dep = hubs[i % len(hubs)]
                flights.append(Flight(departure_airport=dep, arrival_airport=dest_airport, departure_date=dep_date, return_date=ret_date, price=price, availability=availability))
                
    return flights

def generate_hotels():
    hotels = []
    start_date = datetime.date(2026, 1, 1)
    end_date = datetime.date(2027, 12, 31)
    
    for dest in DESTINATIONS:
        city = dest["city"]
        
        hotel_configs = [
            {"name": f"{city} Cozy Hostel", "price": 45.00},
            {"name": f"Budget Stay {city}", "price": 55.00},
            {"name": f"{city} Central Guesthouse", "price": 70.00},
            {"name": f"The {city} Inn", "price": 95.00},
            {"name": f"{city} Park Hotel", "price": 115.00},
            {"name": f"Green Garden Hotel {city}", "price": 130.00},
            {"name": f"{city} Central Suites", "price": 150.00},
            {"name": f"Grand Hotel {city}", "price": 240.00},
            {"name": f"The {city} Palace & Spa", "price": 360.00},
            {"name": f"Royal Resort {city}", "price": 490.00}
        ]
        
        for config in hotel_configs:
            hotels.append(Hotel(
                name=config["name"],
                city=city,
                price_per_night=config["price"],
                available_start_date=start_date,
                available_end_date=end_date
            ))
            
    return hotels

def generate_activities():
    activities = []
    for dest in DESTINATIONS:
        city = dest["city"]
        country = dest["country"]
        highlights = dest["highlights"]
        cuisine = dest["cuisine"]
        
        for tpl in ACTIVITY_TEMPLATES:
            title = tpl["title"].format(city=city, country=country, highlights=highlights, cuisine=cuisine)
            description = tpl["description"].format(city=city, country=country, highlights=highlights, cuisine=cuisine)
            price = tpl["price"]
            
            activities.append(Activity(
                title=title,
                city=city,
                country=country,
                price=price,
                description=description,
                target_audience=tpl["target_audience"],
                available_months=tpl["available_months"]
            ))
            
    return activities

def seed_database():
    print("Inizializzazione del database...")
    init_db()
    
    db = SessionLocal()
    
    try:
        db.query(Flight).delete()
        db.query(Hotel).delete()
        db.query(Activity).delete()
        db.query(User).delete()
        db.commit()
        
        print("Inserimento Utenti di test...")
        users = [
            User(username="viaggiatore", hashed_password=get_password_hash("password123")),
            User(username="alice", hashed_password=get_password_hash("password_alice_456")),
            User(username="bob", hashed_password=get_password_hash("password_bob_789"))
        ]
        db.add_all(users)
        
        print("Generazione procedurale dei Voli...")
        flights = generate_flights()
        db.add_all(flights)
        
        print("Generazione procedurale degli Hotel...")
        hotels = generate_hotels()
        db.add_all(hotels)
        
        print("Generazione procedurale delle Attività Stile GetYourGuide...")
        activities = generate_activities()
        db.add_all(activities)
        
        db.commit()
        print(f"Database popolato con successo! Aggiunti {len(users)} utenti, {len(flights)} voli, {len(hotels)} hotel e {len(activities)} attività.")
        
    except Exception as e:
        db.rollback()
        print(f"Errore durante il seeding: {e}")
        raise e
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
