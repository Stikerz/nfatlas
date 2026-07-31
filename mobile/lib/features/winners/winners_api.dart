import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../services/api_client.dart';

class WinnersApi {
  WinnersApi(this._dio);

  final Dio _dio;

  Future<List<WinnerSummary>> listForDraw(String drawId) async {
    final response =
        await _dio.get<Map<String, dynamic>>('/api/v1/draws/$drawId/winners');
    final items = (response.data?['items'] as List<dynamic>? ?? [])
        .cast<Map<String, dynamic>>();
    return items.map(WinnerSummary.fromJson).toList();
  }

  Future<ClaimResult> claimPrize({
    required String drawId,
    required String ticketId,
  }) async {
    final response = await _dio.post<Map<String, dynamic>>(
      '/api/v1/draws/$drawId/winners/$ticketId/claim',
    );
    return ClaimResult.fromJson(response.data!);
  }
}

class WinnerSummary {
  const WinnerSummary({
    required this.position,
    required this.isPrimary,
    required this.ticketId,
    required this.userId,
    required this.contactStatus,
  });

  factory WinnerSummary.fromJson(Map<String, dynamic> json) {
    return WinnerSummary(
      position: json['position'] as int,
      isPrimary: json['is_primary'] as bool,
      ticketId: json['ticket_id'] as String,
      userId: json['user_id'] as String,
      contactStatus: json['contact_status'] as String,
    );
  }

  final int position;
  final bool isPrimary;
  final String ticketId;
  final String userId;
  final String contactStatus;
}

class ClaimResult {
  const ClaimResult({
    required this.drawId,
    required this.ticketId,
    required this.position,
    required this.isPrimary,
    required this.contactStatus,
  });

  factory ClaimResult.fromJson(Map<String, dynamic> json) {
    return ClaimResult(
      drawId: json['draw_id'] as String,
      ticketId: json['ticket_id'] as String,
      position: json['position'] as int,
      isPrimary: json['is_primary'] as bool,
      contactStatus: json['contact_status'] as String,
    );
  }

  final String drawId;
  final String ticketId;
  final int position;
  final bool isPrimary;
  final String contactStatus;
}

final winnersApiProvider = Provider<WinnersApi>((ref) {
  return WinnersApi(ref.watch(apiClientProvider));
});
