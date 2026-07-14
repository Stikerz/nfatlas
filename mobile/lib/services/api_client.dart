import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:uuid/uuid.dart';

import 'session_storage.dart';

/// Base URL for the Atlas backend as reachable from the device/simulator.
///
/// - iOS simulator, Android emulator + Chrome dev: `http://localhost:8000`
///   works because the compose backend exposes 8000 on the host.
/// - Physical devices need the host machine's LAN IP; override via
///   `--dart-define=ATLAS_API_BASE_URL=http://192.168.x.x:8000`.
const _defaultBaseUrl = String.fromEnvironment(
  'ATLAS_API_BASE_URL',
  defaultValue: 'http://localhost:8000',
);

/// Adds an auto-generated Idempotency-Key UUIDv4 to every non-GET request
/// that doesn't already carry one.
///
/// Split out as a top-level class so `mobile/test/api_client_test.dart` can
/// exercise it in isolation (per plan §8.7 risk mitigation).
class IdempotencyKeyInterceptor extends Interceptor {
  IdempotencyKeyInterceptor({Uuid? uuid}) : _uuid = uuid ?? const Uuid();

  static const _header = 'Idempotency-Key';
  static const _idempotentMethods = {'POST', 'PUT', 'PATCH', 'DELETE'};

  final Uuid _uuid;

  @override
  void onRequest(RequestOptions options, RequestInterceptorHandler handler) {
    final method = options.method.toUpperCase();
    if (_idempotentMethods.contains(method) &&
        !options.headers.containsKey(_header)) {
      options.headers[_header] = _uuid.v4();
    }
    handler.next(options);
  }
}

/// Attaches `Authorization: Bearer <token>` from secure storage.
class BearerTokenInterceptor extends Interceptor {
  BearerTokenInterceptor(this._storage);

  final SessionStorage _storage;

  @override
  Future<void> onRequest(
    RequestOptions options,
    RequestInterceptorHandler handler,
  ) async {
    if (!options.headers.containsKey('Authorization')) {
      final token = await _storage.readToken();
      if (token != null) {
        options.headers['Authorization'] = 'Bearer $token';
      }
    }
    handler.next(options);
  }
}

Dio buildDio({
  required SessionStorage storage,
  String baseUrl = _defaultBaseUrl,
}) {
  final dio = Dio(
    BaseOptions(
      baseUrl: baseUrl,
      connectTimeout: const Duration(seconds: 10),
      receiveTimeout: const Duration(seconds: 15),
      sendTimeout: const Duration(seconds: 15),
      contentType: 'application/json',
      responseType: ResponseType.json,
      validateStatus: (code) => code != null && code >= 200 && code < 500,
    ),
  );
  dio.interceptors.add(IdempotencyKeyInterceptor());
  dio.interceptors.add(BearerTokenInterceptor(storage));
  return dio;
}

final apiClientProvider = Provider<Dio>((ref) {
  final storage = ref.watch(sessionStorageProvider);
  return buildDio(storage: storage);
});
