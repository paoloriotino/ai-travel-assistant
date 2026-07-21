import { useState, useEffect, useCallback } from 'react';
import { fetchBookings, cancelBooking } from '../services/api';
import type { Booking } from '../types';
import './DashboardView.css';

/** Mappa lo stato della prenotazione alla classe CSS del badge */
function statusClass(status: string): string {
  switch (status) {
    case 'confirmed': return 'dashboard__status--confirmed';
    case 'pending':   return 'dashboard__status--pending';
    case 'cancelled': return 'dashboard__status--cancelled';
    default:          return '';
  }
}

/** Mappa lo stato alla label italiana */
function statusLabel(status: string): string {
  switch (status) {
    case 'confirmed': return 'Confermato';
    case 'pending':   return 'In attesa';
    case 'cancelled': return 'Annullato';
    default:          return status;
  }
}

/** Estrarre il titolo 'Viaggio a Destinazione' dai dettagli della prenotazione */
function getTripTitle(booking: Booking): string {
  const detailsStr = `${booking.details.flight || ''} ${booking.details.hotel || ''} ${booking.details.activities || ''}`.toLowerCase();
  
  const destMap: Record<string, string> = {
    hnd: 'Tokyo', tokyo: 'Tokyo',
    cdg: 'Parigi', parigi: 'Parigi', paris: 'Parigi',
    jfk: 'New York', 'new york': 'New York',
    lhr: 'Londra', londra: 'Londra', london: 'Londra',
    kef: 'Reykjavik', reykjavik: 'Reykjavik',
    syd: 'Sydney', sydney: 'Sydney',
    fco: 'Roma', roma: 'Roma', rome: 'Roma',
    mxp: 'Milano', milano: 'Milano', milan: 'Milano',
    bcn: 'Barcellona', barcellona: 'Barcellona', barcelona: 'Barcellona',
    mad: 'Madrid', madrid: 'Madrid',
    ber: 'Berlino', berlino: 'Berlino', berlin: 'Berlino',
    muc: 'Monaco di Baviera', monaco: 'Monaco di Baviera', munich: 'Monaco di Baviera',
    ams: 'Amsterdam', amsterdam: 'Amsterdam',
    vie: 'Vienna', vienna: 'Vienna',
    ath: 'Atene', atene: 'Atene', athens: 'Atene',
    lis: 'Lisbona', lisbona: 'Lisbona', lisbon: 'Lisbona',
    prg: 'Praga', praga: 'Praga', prague: 'Praga',
    bud: 'Budapest', budapest: 'Budapest',
    cph: 'Copenaghen', copenaghen: 'Copenaghen', copenhagen: 'Copenaghen',
    arn: 'Stoccolma', stoccolma: 'Stoccolma', stockholm: 'Stoccolma',
    osl: 'Oslo', oslo: 'Oslo',
    hel: 'Helsinki', helsinki: 'Helsinki',
    cai: 'Il Cairo', 'il cairo': 'Il Cairo', cairo: 'Il Cairo',
    cpt: 'Città del Capo', 'città del capo': 'Città del Capo', 'cape town': 'Città del Capo',
    dxb: 'Dubai', dubai: 'Dubai',
    bkk: 'Bangkok', bangkok: 'Bangkok',
    sin: 'Singapore', singapore: 'Singapore',
    dps: 'Bali', bali: 'Bali',
    icn: 'Seul', seul: 'Seul', seoul: 'Seul',
    pek: 'Pechino', pechino: 'Pechino', beijing: 'Pechino',
    del: 'Delhi', delhi: 'Delhi',
    bom: 'Mumbai', mumbai: 'Mumbai',
    yyz: 'Toronto', toronto: 'Toronto',
    yvr: 'Vancouver', vancouver: 'Vancouver',
    lax: 'Los Angeles', 'los angeles': 'Los Angeles',
    sfo: 'San Francisco', 'san francisco': 'San Francisco',
    mia: 'Miami', miami: 'Miami',
    gig: 'Rio de Janeiro', 'rio de janeiro': 'Rio de Janeiro',
    eze: 'Buenos Aires', 'buenos aires': 'Buenos Aires',
    mex: 'Città del Messico', 'città del messico': 'Città del Messico', 'mexico city': 'Città del Messico',
    rak: 'Marrakech', marrakech: 'Marrakech',
    vce: 'Venezia', venezia: 'Venezia', venice: 'Venezia',
    flr: 'Firenze', firenze: 'Firenze', florence: 'Firenze',
  };

  for (const [key, name] of Object.entries(destMap)) {
    if (detailsStr.includes(key)) {
      return `Viaggio a ${name}`;
    }
  }

  return `Viaggio #${booking.id}`;
}

export default function DashboardView() {
  const [bookings, setBookings] = useState<Booking[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadBookings = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await fetchBookings();
      setBookings(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Errore nel caricamento');
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    loadBookings();
  }, [loadBookings]);

  const handleCancelBooking = async (id: number) => {
    if (!window.confirm('Sei sicuro di voler annullare questa prenotazione?')) return;
    try {
      await cancelBooking(id);
      setBookings((prev) =>
        prev.map((b) => (b.id === id ? { ...b, status: 'cancelled' } : b))
      );
    } catch (err) {
      alert(`Errore durante l'annullamento: ${err instanceof Error ? err.message : 'Errore sconosciuto'}`);
    }
  };

  return (
    <div className="dashboard">
      <div className="dashboard__header">
        <h2 className="dashboard__title">I tuoi viaggi</h2>
        <p className="dashboard__subtitle">Consulta lo storico delle tue prenotazioni</p>
      </div>

      {/* Stato di caricamento */}
      {isLoading && (
        <div className="dashboard__grid">
          {[1, 2, 3].map((i) => (
            <div className="dashboard__skeleton" key={i} />
          ))}
        </div>
      )}

      {/* Stato di errore */}
      {!isLoading && error && (
        <div className="dashboard__error">
          <p className="dashboard__error-text">{error}</p>
          <button className="dashboard__retry-btn" onClick={loadBookings}>
            Riprova
          </button>
        </div>
      )}

      {/* Stato vuoto */}
      {!isLoading && !error && bookings.length === 0 && (
        <div className="dashboard__empty">
          <span className="dashboard__empty-icon">🌍</span>
          <h3 className="dashboard__empty-title">Nessun viaggio prenotato</h3>
          <p className="dashboard__empty-text">
            Inizia una conversazione con l'assistente per pianificare il tuo prossimo viaggio!
          </p>
        </div>
      )}

      {/* Lista prenotazioni */}
      {!isLoading && !error && bookings.length > 0 && (
        <div className="dashboard__grid">
          {bookings.map((booking) => (
            <div className="dashboard__card" key={booking.id}>
              <div className="dashboard__card-header">
                <div>
                  <h3 style={{ margin: 0, fontSize: '1.1rem', color: 'var(--color-golden-hour)', fontFamily: 'var(--font-display)' }}>
                    📍 {getTripTitle(booking)}
                  </h3>
                  <span className="dashboard__card-id" style={{ fontSize: '0.8rem', color: 'var(--color-mist)' }}>
                    Prenotazione #{booking.id}
                  </span>
                </div>
                <span className={`dashboard__status ${statusClass(booking.status)}`}>
                  {statusLabel(booking.status)}
                </span>
              </div>

              <div className="dashboard__details">
                <div className="dashboard__detail">
                  <span className="dashboard__detail-icon">👤</span>
                  <span className="dashboard__detail-text">{booking.details.traveler}</span>
                </div>
                <div className="dashboard__detail">
                  <span className="dashboard__detail-icon">✈️</span>
                  <span className="dashboard__detail-text">{booking.details.flight}</span>
                </div>
                <div className="dashboard__detail">
                  <span className="dashboard__detail-icon">🏨</span>
                  <span className="dashboard__detail-text">{booking.details.hotel}</span>
                </div>
                <div className="dashboard__detail">
                  <span className="dashboard__detail-icon">🎯</span>
                  <span className="dashboard__detail-text">{booking.details.activities}</span>
                </div>
              </div>

              <div className="dashboard__card-footer">
                <div className="dashboard__price">
                  <span className="dashboard__price-label">Totale</span>
                  <span className="dashboard__price-value">€{booking.total_price.toFixed(2)}</span>
                </div>
                {booking.status !== 'cancelled' && (
                  <button
                    className="dashboard__cancel-btn"
                    onClick={() => handleCancelBooking(booking.id)}
                    title="Annulla prenotazione"
                  >
                    Annulla
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
