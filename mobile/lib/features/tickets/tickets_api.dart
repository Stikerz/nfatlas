import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../services/api_client.dart';

/// Thin wrapper over the atlas.ticket HTTP surface (read-only in W7 Day 3).
///
/// GET /tickets/me lands here. POST /tickets/purchase + winner claim
/// arrive Day 4 alongside the mobile skill/checkout screens.
class TicketsApi {
  TicketsApi(this._dio);

  final Dio _dio;

  Future<List<TicketSummary>> listMine() async {
    final response = await _dio.get<Map<String, dynamic>>('/api/v1/tickets/me');
    final items = (response.data?['items'] as List<dynamic>? ?? [])
        .cast<Map<String, dynamic>>();
    return items.map(TicketSummary.fromJson).toList();
  }
}

class TicketSummary {
  const TicketSummary({
    required this.id,
    required this.drawId,
    required this.ticketNumber,
    required this.entrySource,
    required this.issuedAt,
  });

  factory TicketSummary.fromJson(Map<String, dynamic> json) {
    return TicketSummary(
      id: json['id'] as String,
      drawId: json['draw_id'] as String,
      ticketNumber: json['ticket_number'] as int,
      entrySource: json['entry_source'] as String,
      issuedAt: DateTime.parse(json['issued_at'] as String),
    );
  }

  final String id;
  final String drawId;
  final int ticketNumber;
  final String entrySource; // 'paid' | 'free'
  final DateTime issuedAt;
}

final ticketsApiProvider = Provider<TicketsApi>((ref) {
  return TicketsApi(ref.watch(apiClientProvider));
});

final myTicketsProvider = FutureProvider<List<TicketSummary>>((ref) async {
  return ref.watch(ticketsApiProvider).listMine();
});
