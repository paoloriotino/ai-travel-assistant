import type { InterruptInfo } from '../types';
import './BookingApprovalModal.css';

interface BookingApprovalModalProps {
  interruptInfo: InterruptInfo;
  onApprove: () => void;
  onReject: () => void;
  isLoading: boolean;
}

/** Mappatura campi del tool_args → etichette italiane con emoji */
const FIELD_MAP: { key: string; label: string; emoji: string }[] = [
  { key: 'traveler_name', label: 'Viaggiatore', emoji: '👤' },
  { key: 'flight_details', label: 'Volo', emoji: '✈️' },
  { key: 'hotel_details', label: 'Hotel', emoji: '🏨' },
  { key: 'activity_details', label: 'Attività', emoji: '🎯' },
];

export default function BookingApprovalModal({
  interruptInfo,
  onApprove,
  onReject,
  isLoading,
}: BookingApprovalModalProps) {
  const args = interruptInfo.tool_args;
  const totalPrice = args.total_estimated_price as number | undefined;
  const isModification = interruptInfo.tool_name === 'modify_booking';

  return (
    <div className="booking-modal__overlay" role="dialog" aria-modal="true" aria-label={isModification ? "Conferma modifica" : "Conferma prenotazione"}>
      <div className="booking-modal__card">
        <div className="booking-modal__header">
          <span className="booking-modal__icon">✈️</span>
          <h2 className="booking-modal__title">{isModification ? "Conferma modifica" : "Conferma prenotazione"}</h2>
        </div>

        <div className="booking-modal__summary">
          {FIELD_MAP.map(({ key, label, emoji }) => {
            const value = args[key];
            if (!value) return null;
            return (
              <div className="booking-modal__field" key={key}>
                <span className="booking-modal__label">{emoji} {label}</span>
                <span className="booking-modal__value">{String(value)}</span>
              </div>
            );
          })}

          {totalPrice != null && (
            <div className="booking-modal__field">
              <span className="booking-modal__label">💰 Totale</span>
              <span className="booking-modal__price">€{totalPrice.toFixed(2)}</span>
            </div>
          )}
        </div>

        <div className="booking-modal__actions">
          <button
            className="booking-modal__btn booking-modal__btn--reject"
            onClick={onReject}
            disabled={isLoading}
          >
            Annulla
          </button>
          <button
            className="booking-modal__btn booking-modal__btn--confirm"
            onClick={onApprove}
            disabled={isLoading}
          >
            {isLoading ? 'Attendere...' : (isModification ? 'Conferma modifica' : 'Conferma prenotazione')}
          </button>
        </div>
      </div>
    </div>
  );
}
