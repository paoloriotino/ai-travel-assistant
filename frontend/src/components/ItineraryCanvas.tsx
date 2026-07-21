import { useState, useCallback, type MouseEvent } from 'react';
import type { StructuredItinerary } from '../types';
import './ItineraryCanvas.css';

interface ItineraryCanvasProps {
  itinerary: StructuredItinerary | null;
  onClose?: () => void;
}

export default function ItineraryCanvas({ itinerary }: ItineraryCanvasProps) {
  const [width, setWidth] = useState<number>(380);

  const startResizing = useCallback((mouseDownEvent: MouseEvent) => {
    mouseDownEvent.preventDefault();
    const startX = mouseDownEvent.clientX;
    const startWidth = width;

    const onMouseMove = (moveEvent: globalThis.MouseEvent) => {
      const deltaX = startX - moveEvent.clientX;
      const newWidth = Math.min(Math.max(startWidth + deltaX, 280), 700);
      setWidth(newWidth);
    };

    const onMouseUp = () => {
      document.removeEventListener('mousemove', onMouseMove);
      document.removeEventListener('mouseup', onMouseUp);
    };

    document.addEventListener('mousemove', onMouseMove);
    document.addEventListener('mouseup', onMouseUp);
  }, [width]);

  if (!itinerary) {
    return (
      <aside className="itinerary-canvas" style={{ width: `${width}px` }}>
        <div className="itinerary-canvas__resize-handle" onMouseDown={startResizing} title="Trascina per ridimensionare" />
        <div className="itinerary-canvas__header">
          <h3 className="itinerary-canvas__title">🗺️ Itinerario Live</h3>
        </div>
        <div className="itinerary-canvas__empty">
          <span className="itinerary-canvas__empty-icon">🧭</span>
          <p>
            Nessun viaggio ancora in definizione.<br />
            Parla con l'assistente per iniziare a costruire il tuo itinerario in tempo reale!
          </p>
        </div>
      </aside>
    );
  }

  return (
    <aside className="itinerary-canvas" style={{ width: `${width}px` }}>
      <div className="itinerary-canvas__resize-handle" onMouseDown={startResizing} title="Trascina per ridimensionare" />
      <div className="itinerary-canvas__header">
        <div>
          <h3 className="itinerary-canvas__title">🗺️ Scheda Viaggio</h3>
          <span className="itinerary-canvas__subtitle">Aggiornato in tempo reale</span>
        </div>
      </div>

      <div className="itinerary-canvas__content">
        <div className="itinerary-canvas__banner">
          <h2 className="itinerary-canvas__dest">
            📍 {itinerary.destination.startsWith('Viaggio a') ? itinerary.destination : `Viaggio a ${itinerary.destination}`}
          </h2>
          {itinerary.duration_days && (
            <div style={{ fontSize: '0.85rem', color: 'var(--color-mist)' }}>
              ⏱️ Durata: {itinerary.duration_days} giorni
            </div>
          )}
          {itinerary.estimated_total_price && (
            <div className="itinerary-canvas__price-badge">
              €{itinerary.estimated_total_price} totale stimato
            </div>
          )}
        </div>

        {itinerary.flight_summary && (
          <div className="itinerary-canvas__section">
            <div className="itinerary-canvas__section-title">✈️ Volo Selezionato</div>
            <div className="itinerary-canvas__section-content">
              {itinerary.flight_summary}
            </div>
          </div>
        )}

        {itinerary.hotel_summary && (
          <div className="itinerary-canvas__section">
            <div className="itinerary-canvas__section-title">🏨 Alloggio Selezionato</div>
            <div className="itinerary-canvas__section-content">
              {itinerary.hotel_summary}
            </div>
          </div>
        )}

        {itinerary.daily_plan && itinerary.daily_plan.length > 0 && (
          <div>
            <h4 style={{ fontSize: '0.9rem', color: 'var(--color-cloud)', marginBottom: 'var(--space-2)' }}>
              🗓️ Programma Giornaliero
            </h4>
            <div className="itinerary-canvas__timeline">
              {itinerary.daily_plan.map((day) => (
                <div key={day.day} className="itinerary-canvas__day-card">
                  <div className="itinerary-canvas__day-title">
                    Giorno {day.day}: {day.title}
                  </div>
                  {day.activities && day.activities.length > 0 && (
                    <ul className="itinerary-canvas__day-activities">
                      {day.activities.map((act, i) => (
                        <li key={i}>{act}</li>
                      ))}
                    </ul>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </aside>
  );
}
