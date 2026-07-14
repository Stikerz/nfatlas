import 'package:flutter/foundation.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../services/session_storage.dart';
import 'identity_api.dart';

/// State machine for the wf-01 register flow.
///
/// The registration draft (email, phone, dob, terms) is held in memory only —
/// nothing persists to disk until the password step succeeds (wireframe §2.6
/// "not persisted to disk until account is actually created at end of screen
/// 1.3"). After password → login writes the bearer token to secure storage
/// and the controller resets to signedIn state.
@immutable
class IdentityState {
  const IdentityState({
    this.email = '',
    this.phoneE164 = '',
    this.dateOfBirth,
    this.termsAccepted = false,
    this.userId,
    this.otpVerified = false,
    this.busy = false,
    this.error,
  });

  final String email;
  final String phoneE164; // full E.164 form (+234NNNNNNNNNN)
  final DateTime? dateOfBirth;
  final bool termsAccepted;
  final String? userId;
  final bool otpVerified;
  final bool busy;
  final String? error;

  IdentityState copyWith({
    String? email,
    String? phoneE164,
    DateTime? dateOfBirth,
    bool? termsAccepted,
    String? userId,
    bool? otpVerified,
    bool? busy,
    String? error,
    bool clearError = false,
  }) {
    return IdentityState(
      email: email ?? this.email,
      phoneE164: phoneE164 ?? this.phoneE164,
      dateOfBirth: dateOfBirth ?? this.dateOfBirth,
      termsAccepted: termsAccepted ?? this.termsAccepted,
      userId: userId ?? this.userId,
      otpVerified: otpVerified ?? this.otpVerified,
      busy: busy ?? this.busy,
      error: clearError ? null : (error ?? this.error),
    );
  }
}

class IdentityController extends StateNotifier<IdentityState> {
  IdentityController(this._api, this._storage) : super(const IdentityState());

  final IdentityApi _api;
  final SessionStorage _storage;

  void setEmail(String v) => state = state.copyWith(email: v.trim(), clearError: true);
  void setPhoneE164(String v) => state = state.copyWith(phoneE164: v, clearError: true);
  void setDateOfBirth(DateTime v) =>
      state = state.copyWith(dateOfBirth: v, clearError: true);
  void setTermsAccepted(bool v) =>
      state = state.copyWith(termsAccepted: v, clearError: true);

  bool get canSubmitRegister =>
      emailWellFormed(state.email) &&
      phoneWellFormed(state.phoneE164) &&
      state.dateOfBirth != null &&
      isAtLeast18(state.dateOfBirth!, DateTime.now()) &&
      state.termsAccepted;

  Future<bool> submitRegister() async {
    if (!canSubmitRegister) return false;
    state = state.copyWith(busy: true, clearError: true);
    try {
      final result = await _api.register(
        email: state.email,
        phoneE164: state.phoneE164,
        dateOfBirth: state.dateOfBirth!,
        termsAccepted: state.termsAccepted,
      );
      await _api.issueOtp(userId: result.userId, purpose: 'registration');
      state = state.copyWith(userId: result.userId, busy: false);
      return true;
    } on IdentityApiError catch (e) {
      state = state.copyWith(busy: false, error: e.message);
      return false;
    } catch (e) {
      state = state.copyWith(
        busy: false,
        error: "We couldn't send the code. Check your connection and try again.",
      );
      return false;
    }
  }

  Future<bool> submitOtp(String code) async {
    final uid = state.userId;
    if (uid == null) return false;
    state = state.copyWith(busy: true, clearError: true);
    try {
      await _api.verifyOtp(userId: uid, purpose: 'registration', code: code);
      state = state.copyWith(otpVerified: true, busy: false);
      return true;
    } on IdentityApiError catch (e) {
      state = state.copyWith(busy: false, error: e.message);
      return false;
    }
  }

  Future<bool> resendOtp() async {
    final uid = state.userId;
    if (uid == null) return false;
    state = state.copyWith(busy: true, clearError: true);
    try {
      await _api.issueOtp(userId: uid, purpose: 'registration');
      state = state.copyWith(busy: false);
      return true;
    } on IdentityApiError catch (e) {
      state = state.copyWith(busy: false, error: e.message);
      return false;
    }
  }

  Future<bool> submitPassword(String password) async {
    final uid = state.userId;
    if (uid == null || !state.otpVerified) return false;
    state = state.copyWith(busy: true, clearError: true);
    try {
      await _api.setPassword(userId: uid, password: password);
      final login = await _api.login(email: state.email, password: password);
      await _storage.writeToken(login.accessToken);
      state = state.copyWith(busy: false);
      return true;
    } on IdentityApiError catch (e) {
      state = state.copyWith(busy: false, error: e.message);
      return false;
    }
  }

  Future<void> signOut() async {
    try {
      await _api.logout();
    } catch (_) {
      // best effort; local clear proceeds regardless.
    }
    await _storage.clear();
    state = const IdentityState();
  }

  static bool emailWellFormed(String v) =>
      RegExp(r'^[^\s@]+@[^\s@]+\.[^\s@]+$').hasMatch(v);

  static bool phoneWellFormed(String v) =>
      RegExp(r'^\+234[789]\d{9}$').hasMatch(v);

  static bool isAtLeast18(DateTime dob, DateTime today) {
    var years = today.year - dob.year;
    if (today.month < dob.month ||
        (today.month == dob.month && today.day < dob.day)) {
      years -= 1;
    }
    return years >= 18;
  }
}

final identityControllerProvider =
    StateNotifierProvider<IdentityController, IdentityState>((ref) {
  return IdentityController(
    ref.watch(identityApiProvider),
    ref.watch(sessionStorageProvider),
  );
});
