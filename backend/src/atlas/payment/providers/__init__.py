"""Payment provider adapters (ADR-008).

One module per vendor. All vendors implement `atlas.payment.providers.
protocol.PaymentProvider`. Payment-module code depends on the protocol,
never on a concrete vendor. CI grep enforces that direct vendor SDK
imports live only inside the matching adapter module.
"""
