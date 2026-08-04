import 'package:atlas_mobile/features/identity/identity_controller.dart';
import 'package:flutter_test/flutter_test.dart';

/// Pure validators + age-gate arithmetic on IdentityController.
///
/// These rules gate real money movement (18+ compliance) and OTP delivery
/// (E.164 shape); a regression here would land in production silently.
void main() {
  group('IdentityController.emailWellFormed', () {
    test('accepts a plain address', () {
      expect(IdentityController.emailWellFormed('a@b.co'), isTrue);
    });

    test('rejects a bare local part', () {
      expect(IdentityController.emailWellFormed('nolocal'), isFalse);
    });

    test('rejects whitespace', () {
      expect(IdentityController.emailWellFormed('a b@c.co'), isFalse);
    });

    test('rejects missing TLD dot', () {
      expect(IdentityController.emailWellFormed('a@bco'), isFalse);
    });
  });

  group('IdentityController.phoneWellFormed', () {
    test('accepts +234 7XX/8XX/9XX with 9 trailing digits', () {
      for (final p in ['+2347012345678', '+2348012345678', '+2349012345678']) {
        expect(IdentityController.phoneWellFormed(p), isTrue, reason: p);
      }
    });

    test('rejects wrong country code', () {
      expect(IdentityController.phoneWellFormed('+441234567890'), isFalse);
    });

    test('rejects mobile prefix outside {7,8,9}', () {
      expect(IdentityController.phoneWellFormed('+2341012345678'), isFalse);
    });

    test('rejects short trailing digits', () {
      expect(IdentityController.phoneWellFormed('+23470123'), isFalse);
    });

    test('rejects missing leading +', () {
      expect(IdentityController.phoneWellFormed('2348012345678'), isFalse);
    });
  });

  group('IdentityController.isAtLeast18', () {
    final today = DateTime(2026, 8, 3);

    test('exactly 18 on same month + day', () {
      expect(
        IdentityController.isAtLeast18(DateTime(2008, 8, 3), today),
        isTrue,
      );
    });

    test('one day short of 18', () {
      expect(
        IdentityController.isAtLeast18(DateTime(2008, 8, 4), today),
        isFalse,
      );
    });

    test('birthday next month = not yet 18', () {
      expect(
        IdentityController.isAtLeast18(DateTime(2008, 9, 1), today),
        isFalse,
      );
    });

    test('birthday earlier this year = already 18', () {
      expect(
        IdentityController.isAtLeast18(DateTime(2008, 1, 1), today),
        isTrue,
      );
    });

    test('older adult passes trivially', () {
      expect(
        IdentityController.isAtLeast18(DateTime(1990, 6, 15), today),
        isTrue,
      );
    });
  });
}
