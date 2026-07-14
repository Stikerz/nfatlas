import 'package:atlas_mobile/services/api_client.dart';
import 'package:dio/dio.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:uuid/uuid.dart';

/// Interceptor contract per plan §8.7 risk mitigation:
///   Every non-GET call gets a fresh Idempotency-Key UUID unless the caller
///   explicitly set one. GET calls never get one. Two consecutive POSTs
///   from the same dio instance must NOT share a key (each is a new
///   intent).
void main() {
  group('IdempotencyKeyInterceptor', () {
    test('POST without an explicit key gets a UUIDv4', () async {
      final captured = <String?>[];
      final dio = _dioCapturingRequests(captured);

      await dio.post<void>('/api/v1/anything', data: {'x': 1});

      expect(captured, hasLength(1));
      _expectValidUuid(captured.single);
    });

    test('POST with an explicit Idempotency-Key preserves the caller value',
        () async {
      final captured = <String?>[];
      final dio = _dioCapturingRequests(captured);

      await dio.post<void>(
        '/api/v1/anything',
        data: {'x': 1},
        options: Options(headers: {'Idempotency-Key': 'caller-supplied-key'}),
      );

      expect(captured, hasLength(1));
      expect(captured.single, equals('caller-supplied-key'));
    });

    test('two consecutive POSTs get DIFFERENT keys', () async {
      final captured = <String?>[];
      final dio = _dioCapturingRequests(captured);

      await dio.post<void>('/api/v1/anything', data: {'x': 1});
      await dio.post<void>('/api/v1/anything', data: {'x': 2});

      expect(captured, hasLength(2));
      expect(captured[0], isNot(equals(captured[1])));
      _expectValidUuid(captured[0]);
      _expectValidUuid(captured[1]);
    });

    test('GET requests do NOT get an Idempotency-Key', () async {
      final captured = <String?>[];
      final dio = _dioCapturingRequests(captured);

      await dio.get<void>('/api/v1/sessions/current');

      expect(captured, hasLength(1));
      expect(captured.single, isNull);
    });

    test('PUT and DELETE also get keys', () async {
      final captured = <String?>[];
      final dio = _dioCapturingRequests(captured);

      await dio.put<void>('/api/v1/anything', data: {'x': 1});
      await dio.delete<void>('/api/v1/anything');

      expect(captured, hasLength(2));
      _expectValidUuid(captured[0]);
      _expectValidUuid(captured[1]);
    });
  });
}

Dio _dioCapturingRequests(List<String?> captured) {
  final dio = Dio(BaseOptions(baseUrl: 'http://test.local'));
  dio.interceptors.add(IdempotencyKeyInterceptor());
  dio.interceptors.add(
    InterceptorsWrapper(
      onRequest: (options, handler) {
        captured.add(options.headers['Idempotency-Key'] as String?);
        handler.resolve(Response<void>(requestOptions: options, statusCode: 200));
      },
    ),
  );
  return dio;
}

void _expectValidUuid(String? value) {
  expect(value, isNotNull);
  expect(Uuid.isValidUUID(fromString: value!), isTrue);
}
