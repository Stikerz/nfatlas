import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../services/api_client.dart';

/// Typed thin wrapper over the atlas.identity HTTP surface.
///
/// Every mutation call lets dio's IdempotencyKeyInterceptor generate the
/// Idempotency-Key header; the caller never has to manage it explicitly.
class IdentityApi {
  IdentityApi(this._dio);

  final Dio _dio;

  Future<RegisterResult> register({
    required String email,
    required String phoneE164,
    required DateTime dateOfBirth,
    required bool termsAccepted,
  }) async {
    final response = await _dio.post<Map<String, dynamic>>(
      '/api/v1/users',
      data: {
        'email': email,
        'phone_e164': phoneE164,
        'date_of_birth':
            '${dateOfBirth.year.toString().padLeft(4, '0')}-'
            '${dateOfBirth.month.toString().padLeft(2, '0')}-'
            '${dateOfBirth.day.toString().padLeft(2, '0')}',
        'terms_accepted': termsAccepted,
      },
    );
    _assertOk(response, expected: 201);
    final body = response.data!;
    return RegisterResult(
      userId: body['user_id'] as String,
      status: body['status'] as String,
    );
  }

  Future<void> issueOtp({required String userId, required String purpose}) async {
    final response = await _dio.post<Map<String, dynamic>>(
      '/api/v1/otps',
      data: {'user_id': userId, 'purpose': purpose},
    );
    _assertOk(response, expected: 201);
  }

  Future<void> verifyOtp({
    required String userId,
    required String purpose,
    required String code,
  }) async {
    final response = await _dio.post<Map<String, dynamic>>(
      '/api/v1/otps/verify',
      data: {'user_id': userId, 'purpose': purpose, 'code': code},
    );
    _assertOk(response, expected: 200);
  }

  Future<void> setPassword({required String userId, required String password}) async {
    final response = await _dio.post<Map<String, dynamic>>(
      '/api/v1/users/$userId/password',
      data: {'password': password},
    );
    _assertOk(response, expected: 204);
  }

  Future<LoginResult> login({required String email, required String password}) async {
    final response = await _dio.post<Map<String, dynamic>>(
      '/api/v1/sessions',
      data: {'email': email, 'password': password},
    );
    _assertOk(response, expected: 201);
    final body = response.data!;
    return LoginResult(
      accessToken: body['access_token'] as String,
      sessionId: body['session_id'] as String,
      userId: body['user_id'] as String,
      expiresAt: DateTime.parse(body['expires_at'] as String),
    );
  }

  Future<CurrentSession?> currentSession() async {
    final response = await _dio.get<Map<String, dynamic>>(
      '/api/v1/sessions/current',
      options: Options(validateStatus: (c) => c != null && (c == 200 || c == 401)),
    );
    if (response.statusCode == 401) return null;
    final body = response.data!;
    return CurrentSession(
      sessionId: body['session_id'] as String,
      userId: body['user_id'] as String,
      expiresAt: DateTime.parse(body['expires_at'] as String),
    );
  }

  Future<void> logout() async {
    await _dio.post<void>('/api/v1/sessions/current/logout');
  }

  static void _assertOk(Response<Object?> response, {required int expected}) {
    if (response.statusCode != expected) {
      throw IdentityApiError(
        statusCode: response.statusCode ?? 0,
        body: response.data,
      );
    }
  }
}

class IdentityApiError implements Exception {
  IdentityApiError({required this.statusCode, required this.body});

  final int statusCode;
  final Object? body;

  String? get code {
    final data = body;
    if (data is Map && data['detail'] is Map) {
      final detail = data['detail'] as Map;
      return detail['code'] as String?;
    }
    return null;
  }

  String get message {
    final data = body;
    if (data is Map && data['detail'] is Map) {
      final detail = data['detail'] as Map;
      return (detail['message'] as String?) ?? 'Request failed ($statusCode).';
    }
    return 'Request failed ($statusCode).';
  }

  @override
  String toString() => 'IdentityApiError($statusCode, code=$code, message=$message)';
}

class RegisterResult {
  const RegisterResult({required this.userId, required this.status});
  final String userId;
  final String status;
}

class LoginResult {
  const LoginResult({
    required this.accessToken,
    required this.sessionId,
    required this.userId,
    required this.expiresAt,
  });
  final String accessToken;
  final String sessionId;
  final String userId;
  final DateTime expiresAt;
}

class CurrentSession {
  const CurrentSession({
    required this.sessionId,
    required this.userId,
    required this.expiresAt,
  });
  final String sessionId;
  final String userId;
  final DateTime expiresAt;
}

final identityApiProvider = Provider<IdentityApi>(
  (ref) => IdentityApi(ref.watch(apiClientProvider)),
);
