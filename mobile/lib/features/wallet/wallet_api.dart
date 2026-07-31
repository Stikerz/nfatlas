import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../services/api_client.dart';

/// Thin wrapper over the atlas.wallet HTTP surface.
///
/// V0.5: only the balance chip (GET /users/me/wallet). Withdrawals + top-up
/// UX arrive V1.
class WalletApi {
  WalletApi(this._dio);

  final Dio _dio;

  Future<WalletBalance> balance() async {
    final response =
        await _dio.get<Map<String, dynamic>>('/api/v1/users/me/wallet');
    return WalletBalance.fromJson(response.data!);
  }
}

class WalletBalance {
  const WalletBalance({
    required this.balanceMinor,
    required this.currency,
    required this.updatedAt,
  });

  factory WalletBalance.fromJson(Map<String, dynamic> json) {
    return WalletBalance(
      balanceMinor: json['balance_minor'] as int,
      currency: json['currency'] as String,
      updatedAt: DateTime.parse(json['updated_at'] as String),
    );
  }

  final int balanceMinor;
  final String currency;
  final DateTime updatedAt;

  String get formatted {
    // ₦ prefix for NGN; other currencies fall back to the code.
    final major = (balanceMinor / 100).toStringAsFixed(2);
    return currency == 'NGN' ? '₦$major' : '$currency $major';
  }
}

final walletApiProvider = Provider<WalletApi>((ref) {
  return WalletApi(ref.watch(apiClientProvider));
});

final walletBalanceProvider = FutureProvider<WalletBalance>((ref) async {
  return ref.watch(walletApiProvider).balance();
});
