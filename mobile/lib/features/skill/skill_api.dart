import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../services/api_client.dart';

class SkillApi {
  SkillApi(this._dio);

  final Dio _dio;

  Future<SkillQuestion> next(String drawId) async {
    final response = await _dio
        .get<Map<String, dynamic>>('/api/v1/draws/$drawId/skill-questions/next');
    return SkillQuestion.fromJson(response.data!);
  }

  Future<SkillAnswerResult> answer({
    required String attemptId,
    required String optionId,
  }) async {
    final response = await _dio.post<Map<String, dynamic>>(
      '/api/v1/skill-questions/attempts/$attemptId/answer',
      data: {'option_id': optionId},
    );
    return SkillAnswerResult.fromJson(response.data!);
  }
}

class SkillQuestion {
  const SkillQuestion({
    required this.attemptId,
    required this.questionId,
    required this.prompt,
    required this.options,
    required this.expiresAt,
  });

  factory SkillQuestion.fromJson(Map<String, dynamic> json) {
    return SkillQuestion(
      attemptId: json['attempt_id'] as String,
      questionId: json['question_id'] as String,
      prompt: json['prompt'] as String,
      options: (json['options'] as List<dynamic>)
          .cast<Map<String, dynamic>>()
          .map(SkillOption.fromJson)
          .toList(),
      expiresAt: DateTime.parse(json['expires_at'] as String),
    );
  }

  final String attemptId;
  final String questionId;
  final String prompt;
  final List<SkillOption> options;
  final DateTime expiresAt;
}

class SkillOption {
  const SkillOption({required this.id, required this.text});

  factory SkillOption.fromJson(Map<String, dynamic> json) {
    return SkillOption(id: json['id'] as String, text: json['text'] as String);
  }

  final String id;
  final String text;
}

class SkillAnswerResult {
  const SkillAnswerResult({
    required this.attemptId,
    required this.isCorrect,
    required this.entitlementExpiresAt,
  });

  factory SkillAnswerResult.fromJson(Map<String, dynamic> json) {
    return SkillAnswerResult(
      attemptId: json['attempt_id'] as String,
      isCorrect: json['is_correct'] as bool,
      entitlementExpiresAt: json['entitlement_expires_at'] != null
          ? DateTime.parse(json['entitlement_expires_at'] as String)
          : null,
    );
  }

  final String attemptId;
  final bool isCorrect;
  final DateTime? entitlementExpiresAt;
}

final skillApiProvider = Provider<SkillApi>((ref) {
  return SkillApi(ref.watch(apiClientProvider));
});
