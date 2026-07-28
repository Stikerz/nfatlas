"""Notification module (Week 6 skeleton).

V0.5: winner notification via mailhog. `notify_winner` is called from
`atlas.draw.service.reveal_draw` wrapped in try/except so SMTP
failures never abort the reveal transaction (week-6-build-plan §0 ask
5). Emits `notification.winner_selected` audit event either way — the
event fires even if the email delivery didn't so the audit trail
records "we tried".

V1 replaces this module with a real outbox + WhatsApp adapter per
ADR-002.
"""
