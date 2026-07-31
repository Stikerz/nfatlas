import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../services/api_client.dart';

/// Thin wrapper over the atlas.draw HTTP surface (read-only in W7 Day 3).
///
/// GET /draws + GET /draws/{id} land here. POST /draws + close/reveal are
/// admin-only and stay in the Next.js admin, not the mobile client.
class DrawsApi {
  DrawsApi(this._dio);

  final Dio _dio;

  Future<List<DrawSummary>> listActive() async {
    final response = await _dio.get<Map<String, dynamic>>('/api/v1/draws');
    final items = (response.data?['items'] as List<dynamic>? ?? [])
        .cast<Map<String, dynamic>>();
    return items.map(DrawSummary.fromJson).toList();
  }

  Future<DrawSummary> get(String drawId) async {
    final response =
        await _dio.get<Map<String, dynamic>>('/api/v1/draws/$drawId');
    return DrawSummary.fromJson(response.data!);
  }
}

class DrawSummary {
  const DrawSummary({
    required this.id,
    required this.prizeCopy,
    required this.ticketPriceMinor,
    required this.currency,
    required this.closeTime,
    required this.drawTime,
    required this.state,
    required this.commitment,
  });

  factory DrawSummary.fromJson(Map<String, dynamic> json) {
    return DrawSummary(
      id: json['id'] as String,
      prizeCopy: json['prize_copy'] as String,
      ticketPriceMinor: json['ticket_price_minor'] as int,
      currency: json['currency'] as String,
      closeTime: DateTime.parse(json['close_time'] as String),
      drawTime: DateTime.parse(json['draw_time'] as String),
      state: json['state'] as String,
      commitment: json['commitment'] as String,
    );
  }

  final String id;
  final String prizeCopy;
  final int ticketPriceMinor;
  final String currency;
  final DateTime closeTime;
  final DateTime drawTime;
  final String state;
  final String commitment;
}

final drawsApiProvider = Provider<DrawsApi>((ref) {
  return DrawsApi(ref.watch(apiClientProvider));
});

final activeDrawsProvider = FutureProvider<List<DrawSummary>>((ref) async {
  return ref.watch(drawsApiProvider).listActive();
});
