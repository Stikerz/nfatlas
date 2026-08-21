"""Notification module (W8 Day 3).

W8 replaced the direct-call `notify_winner` from reveal_draw with an
outbox producer (`atlas.draw.service.reveal_draw` → `atlas.outbox.
writer.emit(WINNER_SELECTED_V1, ...)`). The consumer is
`atlas.notification.winner.deliver_from_payload`, registered in
`atlas.outbox.dispatcher.HANDLERS`. Delivery is worker-driven with
at-least-once semantics per ADR-002.

Mailhog remains the V0.5 delivery target; the WhatsApp / real-SMS
producers are V1 additions on top of the same outbox contract.
"""
