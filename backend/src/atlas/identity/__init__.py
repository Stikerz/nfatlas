"""Identity module.

Owns: users, otps, sessions. Day 2 lands POST /api/v1/users; Day 3 lands
OTP + password + session endpoints.

Invariant: SELECT / INSERT on users, otps, sessions from any other module
is forbidden. Cross-module reads go through the module's public service API.
"""
