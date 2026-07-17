import datetime
from database import init_db, SessionLocal, Flight, Hotel, Activity, User

def seed_database():
    print("Inizializzazione del database...")
    init_db()
    
    db = SessionLocal()
    
    try:
        # Pulisci tabelle esistenti per evitare duplicazioni nel seeding
        db.query(Flight).delete()
        db.query(Hotel).delete()
        db.query(Activity).delete()
        db.query(User).delete()
        db.commit()
        
        print("Inserimento Utenti di test...")
        users = [
            User(username="viaggiatore", email="viaggiatore@example.com", hashed_password="hashed_password_placeholder_123"),
            User(username="alice", email="alice@example.com", hashed_password="password_alice_456"),
            User(username="bob", email="bob@example.com", hashed_password="password_bob_789")
        ]
        db.add_all(users)
        
        print("Inserimento Voli (Espanso)...")
        flights = [
            # --- Voli da Roma FCO / Milano MXP a Tokyo HND ---
            Flight(departure_airport="FCO", arrival_airport="HND", departure_date=datetime.date(2026, 8, 1), return_date=datetime.date(2026, 8, 15), price=850.00, availability=10),
            Flight(departure_airport="FCO", arrival_airport="HND", departure_date=datetime.date(2026, 9, 5), return_date=datetime.date(2026, 9, 20), price=720.00, availability=15),
            Flight(departure_airport="MXP", arrival_airport="HND", departure_date=datetime.date(2026, 10, 10), return_date=datetime.date(2026, 10, 24), price=690.00, availability=12),
            Flight(departure_airport="FCO", arrival_airport="HND", departure_date=datetime.date(2026, 12, 20), return_date=datetime.date(2027, 1, 4), price=1150.00, availability=8),
            
            # --- Voli da Roma FCO / Milano MXP a Parigi CDG ---
            Flight(departure_airport="MXP", arrival_airport="CDG", departure_date=datetime.date(2026, 8, 10), return_date=datetime.date(2026, 8, 17), price=120.00, availability=25),
            Flight(departure_airport="MXP", arrival_airport="CDG", departure_date=datetime.date(2026, 10, 12), return_date=datetime.date(2026, 10, 19), price=85.00, availability=30),
            Flight(departure_airport="FCO", arrival_airport="CDG", departure_date=datetime.date(2026, 9, 15), return_date=datetime.date(2026, 9, 22), price=110.00, availability=20),
            Flight(departure_airport="FCO", arrival_airport="CDG", departure_date=datetime.date(2026, 12, 23), return_date=datetime.date(2026, 12, 30), price=195.00, availability=15),
            
            # --- Voli da Roma FCO / Milano MXP a New York JFK ---
            Flight(departure_airport="FCO", arrival_airport="JFK", departure_date=datetime.date(2026, 7, 20), return_date=datetime.date(2026, 8, 3), price=680.00, availability=8),
            Flight(departure_airport="MXP", arrival_airport="JFK", departure_date=datetime.date(2026, 9, 8), return_date=datetime.date(2026, 9, 22), price=590.00, availability=14),
            Flight(departure_airport="MXP", arrival_airport="JFK", departure_date=datetime.date(2026, 12, 20), return_date=datetime.date(2027, 1, 3), price=950.00, availability=12),
            Flight(departure_airport="FCO", arrival_airport="JFK", departure_date=datetime.date(2026, 10, 5), return_date=datetime.date(2026, 10, 15), price=620.00, availability=16),
            
            # --- Voli da Roma FCO / Milano MXP a Londra LHR ---
            Flight(departure_airport="FCO", arrival_airport="LHR", departure_date=datetime.date(2026, 8, 5), return_date=datetime.date(2026, 8, 12), price=135.00, availability=22),
            Flight(departure_airport="MXP", arrival_airport="LHR", departure_date=datetime.date(2026, 9, 10), return_date=datetime.date(2026, 9, 17), price=95.00, availability=28),
            Flight(departure_airport="FCO", arrival_airport="LHR", departure_date=datetime.date(2026, 11, 20), return_date=datetime.date(2026, 11, 27), price=80.00, availability=35),
            
            # --- Voli da Roma FCO / Milano MXP a Reykjavik KEF ---
            Flight(departure_airport="FCO", arrival_airport="KEF", departure_date=datetime.date(2026, 8, 10), return_date=datetime.date(2026, 8, 20), price=450.00, availability=10),
            Flight(departure_airport="MXP", arrival_airport="KEF", departure_date=datetime.date(2026, 9, 1), return_date=datetime.date(2026, 9, 10), price=320.00, availability=15),
            Flight(departure_airport="MXP", arrival_airport="KEF", departure_date=datetime.date(2026, 12, 10), return_date=datetime.date(2026, 12, 18), price=480.00, availability=8),
            
            # --- Voli da Roma FCO / Milano MXP a Sydney SYD ---
            Flight(departure_airport="FCO", arrival_airport="SYD", departure_date=datetime.date(2026, 11, 1), return_date=datetime.date(2026, 11, 20), price=1350.00, availability=6),
            Flight(departure_airport="MXP", arrival_airport="SYD", departure_date=datetime.date(2026, 12, 15), return_date=datetime.date(2027, 1, 5), price=1580.00, availability=5)
        ]
        db.add_all(flights)
        
        print("Inserimento Hotel (Espanso)...")
        hotels = [
            # --- Hotel a Tokyo ---
            Hotel(name="Shinjuku Park Hotel", city="Tokyo", price_per_night=120.00, available_start_date=datetime.date(2026, 1, 1), available_end_date=datetime.date(2026, 12, 31)),
            Hotel(name="Asakusa Traditional Ryokan", city="Tokyo", price_per_night=95.00, available_start_date=datetime.date(2026, 1, 1), available_end_date=datetime.date(2026, 12, 31)),
            Hotel(name="Palace Hotel Tokyo", city="Tokyo", price_per_night=350.00, available_start_date=datetime.date(2026, 1, 1), available_end_date=datetime.date(2026, 12, 31)),
            
            # --- Hotel a Parigi ---
            Hotel(name="Hotel de Seine", city="Paris", price_per_night=150.00, available_start_date=datetime.date(2026, 1, 1), available_end_date=datetime.date(2026, 12, 31)),
            Hotel(name="Montmartre Boutique Hostel", city="Paris", price_per_night=65.00, available_start_date=datetime.date(2026, 1, 1), available_end_date=datetime.date(2026, 12, 31)),
            Hotel(name="Ritz Paris", city="Paris", price_per_night=650.00, available_start_date=datetime.date(2026, 1, 1), available_end_date=datetime.date(2026, 12, 31)),
            
            # --- Hotel a New York ---
            Hotel(name="The Manhattan Oasis", city="New York", price_per_night=210.00, available_start_date=datetime.date(2026, 1, 1), available_end_date=datetime.date(2026, 12, 31)),
            Hotel(name="Brooklyn Loft Hostel", city="New York", price_per_night=85.00, available_start_date=datetime.date(2026, 1, 1), available_end_date=datetime.date(2026, 12, 31)),
            Hotel(name="The Plaza Hotel", city="New York", price_per_night=450.00, available_start_date=datetime.date(2026, 1, 1), available_end_date=datetime.date(2026, 12, 31)),
            
            # --- Hotel a Londra ---
            Hotel(name="Covent Garden Inn", city="London", price_per_night=160.00, available_start_date=datetime.date(2026, 1, 1), available_end_date=datetime.date(2026, 12, 31)),
            Hotel(name="SoHo Backpackers Hostel", city="London", price_per_night=75.00, available_start_date=datetime.date(2026, 1, 1), available_end_date=datetime.date(2026, 12, 31)),
            Hotel(name="The Savoy", city="London", price_per_night=480.00, available_start_date=datetime.date(2026, 1, 1), available_end_date=datetime.date(2026, 12, 31)),
            
            # --- Hotel a Reykjavik ---
            Hotel(name="Glacier View Guesthouse", city="Reykjavik", price_per_night=130.00, available_start_date=datetime.date(2026, 1, 1), available_end_date=datetime.date(2026, 12, 31)),
            Hotel(name="Reykjavik Downtown Hostel", city="Reykjavik", price_per_night=60.00, available_start_date=datetime.date(2026, 1, 1), available_end_date=datetime.date(2026, 12, 31)),
            Hotel(name="Northern Lights Luxury Lodge", city="Reykjavik", price_per_night=280.00, available_start_date=datetime.date(2026, 1, 1), available_end_date=datetime.date(2026, 12, 31)),
            
            # --- Hotel a Sydney ---
            Hotel(name="Harbour Bridge Inn", city="Sydney", price_per_night=185.00, available_start_date=datetime.date(2026, 1, 1), available_end_date=datetime.date(2026, 12, 31)),
            Hotel(name="Bondi Beach Surf Lodge", city="Sydney", price_per_night=80.00, available_start_date=datetime.date(2026, 1, 1), available_end_date=datetime.date(2026, 12, 31)),
             Hotel(name="Park Hyatt Sydney", city="Sydney", price_per_night=420.00, available_start_date=datetime.date(2026, 1, 1), available_end_date=datetime.date(2026, 12, 31)),
            
            # --- Hotel a Roma ---
            Hotel(name="Colosseum View Suite", city="Rome", price_per_night=180.00, available_start_date=datetime.date(2026, 1, 1), available_end_date=datetime.date(2026, 12, 31)),
            Hotel(name="Trastevere Cozy Apartment", city="Rome", price_per_night=110.00, available_start_date=datetime.date(2026, 1, 1), available_end_date=datetime.date(2026, 12, 31)),
            Hotel(name="Rome Luxury Spa Hotel", city="Rome", price_per_night=320.00, available_start_date=datetime.date(2026, 1, 1), available_end_date=datetime.date(2026, 12, 31))
        ]
        db.add_all(hotels)
        
        print("Inserimento Attività (Espanso)...")
        activities = [
            # ======================== TOKYO ========================
            Activity(
                title="Tasting Tour di Street Food a Shibuya",
                city="Tokyo", country="Japan", price=60.00,
                description="Esplora i vicoli nascosti di Shibuya (Nonbei Yokocho) assaggiando yakitori, takoyaki, okonomiyaki e sushi fresco. Guidato da un esperto gastronomico locale. Ideale per buongustai e amanti della nightlife.",
                target_audience="giovani, coppie, buongustai", available_months="1,2,3,4,5,6,7,8,9,10,11,12"
            ),
            Activity(
                title="Lezione di Spada Samurai e Filosofia Kenjutsu",
                city="Tokyo", country="Japan", price=85.00,
                description="Impara le antiche posture, la disciplina mentale e le tecniche di taglio con la katana da un autentico maestro samurai. Include la vestizione del costume hakama tradizionale. Ideale per chi cerca cultura, arti marziali e storia.",
                target_audience="giovani, sportivi, cultura", available_months="1,2,3,4,5,6,7,8,9,10,11,12"
            ),
            Activity(
                title="Relax e Bagno Termale Onsen a Hakone",
                city="Tokyo", country="Japan", price=110.00,
                description="Una giornata di relax assoluto in un onsen tradizionale (bagno termale vulcanico) all'aperto, con spettacolare vista sul Monte Fuji. Include pranzo Kaiseki a più portate. Esperienza rigenerante immersa nella natura.",
                target_audience="coppie, relax, natura", available_months="1,2,3,4,5,6,7,8,9,10,11,12"
            ),
            Activity(
                title="Tour Anime, Manga e Cultura Otaku ad Akihabara",
                city="Tokyo", country="Japan", price=35.00,
                description="Passeggia per il quartiere elettrico di Akihabara con una guida Otaku locale. Scopri i migliori negozi di action figures, manga rari, retro-gaming e fermati a bere una bevanda in un bizzarro Maid Café.",
                target_audience="giovani, famiglie, solitari", available_months="1,2,3,4,5,6,7,8,9,10,11,12"
            ),
            Activity(
                title="Cerimonia del Tè Matcha ad Asakusa",
                city="Tokyo", country="Japan", price=45.00,
                description="Scopri l'armonia della cerimonia del tè guidato da un maestro certificato nel quartiere storico di Asakusa. Imparerai i gesti e la filosofia zen dietro la preparazione del tè matcha e assaggerai dolci tradizionali wagashi.",
                target_audience="famiglie, cultura, relax", available_months="1,2,3,4,5,6,7,8,9,10,11,12"
            ),
            
            # ======================== PARIGI ========================
            Activity(
                title="Crociera sulla Senna con cena gourmet romantica",
                city="Paris", country="France", price=130.00,
                description="Una crociera romantica sul fiume Senna. Cena di 3 portate preparata a bordo con ingredienti stagionali, musica dal vivo in sottofondo e vista privilegiata sulla Tour Eiffel, sul Museo d'Orsay e Notre Dame illuminate.",
                target_audience="coppie, relax", available_months="4,5,6,7,8,9,10"
            ),
            Activity(
                title="Tour guidato salta-fila del Museo del Louvre",
                city="Paris", country="France", price=55.00,
                description="Scopri la Gioconda, la Venere di Milo e le spettacolari collezioni egizie con una guida esperta di storia dell'arte che ti mostrerà i capolavori principali evitando le folle. Un'immersione nella cultura mondiale.",
                target_audience="famiglie, cultura", available_months="1,2,3,4,5,6,7,8,9,10,11,12"
            ),
            Activity(
                title="Corso di pasticceria parigina: Macarons e Croissants",
                city="Paris", country="France", price=70.00,
                description="Impara i segreti della pasticceria francese con un pasticcere professionista nel centro di Parigi. Preparerai macarons colorati e croissants sfogliati croccanti, da poter poi rifare a casa.",
                target_audience="famiglie, coppie, buongustai", available_months="1,2,3,4,5,6,7,8,9,10,11,12"
            ),
            Activity(
                title="Spettacolo e Champagne allo storico Moulin Rouge",
                city="Paris", country="France", price=165.00,
                description="Trascorri una serata leggendaria a Montmartre assistendo allo spettacolo 'Féerie' del cabaret Moulin Rouge. Ammira i costumi piumati, le ballerine di Can-Can e sorseggia champagne d'annata in un'atmosfera scintillante.",
                target_audience="coppie, giovani, nightlife", available_months="1,2,3,4,5,6,7,8,9,10,11,12"
            ),
            
            # ======================== NEW YORK ========================
            Activity(
                title="Volo adrenalinico in Elicottero sopra Manhattan",
                city="New York", country="United States", price=240.00,
                description="Sorvola i grattacieli di New York, Central Park, la Statua della Libertà e l'Empire State Building in elicottero. Emozione indescrivibile e vista aerea spettacolare per foto uniche e indimenticabili.",
                target_audience="giovani, avventura, coppie", available_months="1,2,3,4,5,6,7,8,9,10,11,12"
            ),
            Activity(
                title="Tour in bicicletta a Central Park e Brooklyn Bridge",
                city="New York", country="United States", price=40.00,
                description="Noleggia una bici ed esplora i sentieri storici di Central Park per poi pedalare attraverso il famoso ponte di Brooklyn con una guida locale. Perfetto per sportivi ed esploratori urbani.",
                target_audience="sportivi, giovani, famiglie", available_months="3,4,5,6,7,8,9,10,11"
            ),
            Activity(
                title="Musical a Broadway: Biglietto Premium e Cena",
                city="New York", country="United States", price=155.00,
                description="Vivi la magia del teatro di New York con un biglietto riservato per uno dei celebri musical di Broadway (es. Il Re Leone o Aladdin), preceduto da una deliziosa cena di due portate in un ristorante selezionato a Times Square.",
                target_audience="famiglie, cultura, coppie", available_months="1,2,3,4,5,6,7,8,9,10,11,12"
            ),
            Activity(
                title="Tour del Memoriale dell'11 Settembre e Osservatorio One World",
                city="New York", country="United States", price=55.00,
                description="Visita guidata a Ground Zero, le vasche riflettenti dell'11 Settembre e ingresso prioritario all'Osservatorio One World Trade Center per godere della vista panoramica a 360 gradi più alta di New York.",
                target_audience="cultura, famiglie", available_months="1,2,3,4,5,6,7,8,9,10,11,12"
            ),
            
            # ======================== LONDRA ========================
            Activity(
                title="Tour dei Pub Storici e Jack lo Squartatore",
                city="London", country="United Kingdom", price=35.00,
                description="Esplora i vicoli fumosi dell'East End di Londra al tramonto, ascoltando le storie di Jack lo Squartatore e fermandoti in tre storici pub storici del XVII secolo per degustare birre tradizionali.",
                target_audience="giovani, nightlife, cultura", available_months="1,2,3,4,5,6,7,8,9,10,11,12"
            ),
            Activity(
                title="Tè Pomeridiano tradizionale su Bus Vintage a due Piani",
                city="London", country="United Kingdom", price=52.00,
                description="Sali a bordo di un classico autobus rosso a due piani degli anni '60 per ammirare il Big Ben, Westminster Abbey e Harrods, gustando un classico Afternoon Tea con scones, marmellata, panna montata e pasticcini.",
                target_audience="famiglie, coppie, relax", available_months="1,2,3,4,5,6,7,8,9,10,11,12"
            ),
            Activity(
                title="Tour Harry Potter e Warner Bros Studio Tour",
                city="London", country="United Kingdom", price=95.00,
                description="Trasporto in bus da Londra centro e biglietto d'ingresso per gli studi della Warner Bros. Cammina nella Sala Grande di Hogwarts, esplora Diagon Alley ed assaggia la celebre Burrobirra.",
                target_audience="famiglie, giovani, cultura", available_months="1,2,3,4,5,6,7,8,9,10,11,12"
            ),
            Activity(
                title="Ingresso Prioritario al London Eye con Champagne",
                city="London", country="United Kingdom", price=75.00,
                description="Evita le lunghe attese ed entra in una delle cabine panoramiche della gigantesca ruota di Londra. Ammira lo skyline della città da 135 metri d'altezza sorseggiando un calice di champagne Pommery Brut Royal.",
                target_audience="coppie, relax", available_months="1,2,3,4,5,6,7,8,9,10,11,12"
            ),
            
            # ======================== REYKJAVIK ========================
            Activity(
                title="Caccia guidata all'Aurora Boreale in Super Jeep",
                city="Reykjavik", country="Iceland", price=125.00,
                description="Parti da Reykjavik di notte a bordo di una potente Jeep 4x4 guidata da un fotografo esperto per cacciare le magiche luci dell'aurora boreale lontano dall'inquinamento luminoso della città. Cioccolata calda inclusa.",
                target_audience="avventura, coppie, natura", available_months="9,10,11,12,1,2,3,4"
            ),
            Activity(
                title="Tour del Circolo d'Oro e Bagno alla Laguna Segreta",
                city="Reykjavik", country="Iceland", price=98.00,
                description="Esplora le meraviglie naturali del Parco Nazionale Thingvellir, i geyser spumeggianti di Geysir e la maestosa cascata Gullfoss. Concludi la giornata rilassandoti nelle calde acque termali della Laguna Segreta.",
                target_audience="famiglie, relax, natura", available_months="1,2,3,4,5,6,7,8,9,10,11,12"
            ),
            Activity(
                title="Trekking su Ghiacciaio ed Esplorazione Grotte di Ghiaccio",
                city="Reykjavik", country="Iceland", price=160.00,
                description="Un'escursione avventurosa con ramponi e piccozza sul ghiacciaio Vatnajökull. Visita le spettacolari grotte di ghiaccio azzurro naturale modellate dall'acqua. Perfetto per gli amanti degli sport estremi e della natura incontaminata.",
                target_audience="sportivi, avventura, natura", available_months="11,12,1,2,3"
            ),
            Activity(
                title="Whale Watching: Avvistamento Balene e Delfini",
                city="Reykjavik", country="Iceland", price=75.00,
                description="Naviga nella baia di Faxaflói in barca per avvistare balenottere, megattere, delfini dal becco bianco e pulcinelle di mare nel loro habitat naturale, con commenti scientifici della guida marina a bordo.",
                target_audience="famiglie, natura", available_months="4,5,6,7,8,9,10"
            ),
            
            # ======================== SYDNEY ========================
            Activity(
                title="Corso di Surf a Bondi Beach per Principianti",
                city="Sydney", country="Australia", price=65.00,
                description="Impara a cavalcare le famose onde di Bondi Beach con un istruttore professionista certificato. Include noleggio di muta termica e tavola da surf speciale soft-top per facilitare l'apprendimento. Ideale per amanti dello sport.",
                target_audience="sportivi, giovani, avventura", available_months="9,10,11,12,1,2,3,4,5"
            ),
            Activity(
                title="Scalata Adrenalinica sul Sydney Harbour Bridge",
                city="Sydney", country="Australia", price=195.00,
                description="Scalata guidata in totale sicurezza fino alla cima della campata del ponte di Sydney, ad un'altezza di 134 metri. Una vista mozzafiato a 360 gradi sulla Sydney Opera House, la baia ed i quartieri circostanti.",
                target_audience="giovani, avventura, coppie", available_months="1,2,3,4,5,6,7,8,9,10,11,12"
            ),
            Activity(
                title="Escursione di una Giornata alle Blue Mountains",
                city="Sydney", country="Australia", price=110.00,
                description="Unisciti a una gita di un giorno per esplorare le spettacolari Blue Mountains (patrimonio UNESCO). Visita la formazione rocciosa delle Three Sisters, cammina in foreste pluviali giurassiche e ammira cascate spumeggianti.",
                target_audience="natura, famiglie, relax", available_months="1,2,3,4,5,6,7,8,9,10,11,12"
            ),
            
            # ======================== ROMA ========================
            Activity(
                title="Corso di pasta fresca e tiramisù a Trastevere",
                city="Rome", country="Italy", price=65.00,
                description="Impara a impastare e stendere le fettuccine fatte in casa e prepara il tiramisù perfetto seguendo la ricetta di una nonna romana. Vino locale e assaggi inclusi! Un'esperienza culinaria calda e divertente.",
                target_audience="famiglie, coppie, buongustai", available_months="1,2,3,4,5,6,7,8,9,10,11,12"
            ),
            Activity(
                title="Tour notturno sotterraneo del Colosseo e dei Fori",
                city="Rome", country="Italy", price=80.00,
                description="Esplora il Colosseo sotto la luna, scendendo nei suoi sotterranei solitamente chiusi al pubblico, dove attendevano i gladiatori. Atmosfera suggestiva e fresca fuori dal caldo diurno. Perfetto per gli appassionati di cultura e archeologia.",
                target_audience="cultura, coppie, famiglie", available_months="5,6,7,8,9,10"
            ),
            Activity(
                title="Trekking avventura nella Riserva di Decima Malafede",
                city="Rome", country="Italy", price=30.00,
                description="Una camminata immersa nella macchia mediterranea appena fuori Roma, esplorando canyon di tufo e antiche rovine romane nascoste nella vegetazione. Ideale per amanti dello sport e dell'avventura selvaggia.",
                target_audience="sportivi, avventura, giovani", available_months="3,4,5,6,7,8,9,10,11"
            ),
            Activity(
                title="Tour Gastronomico nel Ghetto Ebraico e Campo de' Fiori",
                city="Rome", country="Italy", price=48.00,
                description="Unisciti a una passeggiata gourmet nel centro storico di Roma. Assaggia carciofi alla giudia, pizza bianca con mortadella, supplì caldi e gelato artigianale biologico, visitando monumenti nascosti con un esperto locale.",
                target_audience="buongustai, famiglie, coppie", available_months="1,2,3,4,5,6,7,8,9,10,11,12"
            ),
            Activity(
                title="Visita Esclusiva ai Musei Vaticani all'Alba",
                city="Rome", country="Italy", price=95.00,
                description="Entra nei Musei Vaticani prima dell'apertura ufficiale al pubblico. Ammira le Stanze di Raffaello e la Cappella Sistina in totale silenzio e tranquillità senza folle, concludendo con una ricca colazione nel Cortile della Pigna.",
                target_audience="cultura, coppie, relax", available_months="1,2,3,4,5,6,7,8,9,10,11,12"
            )
        ]
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
