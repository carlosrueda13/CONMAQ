import 'package:dio/dio.dart';
import 'package:flutter/foundation.dart';
import '../constants/api_constants.dart';
import '../utils/storage_service.dart';

class DioClient {
  late final Dio _dio;
  final StorageService _storageService;

  DioClient(this._storageService) {
    _dio = Dio(
      BaseOptions(
        baseUrl: ApiConstants.baseUrl,
        connectTimeout: const Duration(seconds: 15),
        receiveTimeout: const Duration(seconds: 15),
        responseType: ResponseType.json,
      ),
    );

    _dio.interceptors.add(
      InterceptorsWrapper(
        onRequest: (options, handler) async {
          // Auth Interceptor: Inject Token
          final token = await _storageService.getToken();
          if (token != null && token.isNotEmpty) {
            options.headers['Authorization'] = 'Bearer $token';
          }

          if (kDebugMode) {
            print('REQUEST[${options.method}] => PATH: ${options.path}');
            print('Headers: ${options.headers}');

            // Sanitize sensitive data before printing
            final data = options.data;
            if (data is Map<String, dynamic>) {
              final sanitizedData = Map<String, dynamic>.from(data);
              if (sanitizedData.containsKey('password')) {
                sanitizedData['password'] = '*****';
              }
              print('Data: $sanitizedData');
            } else {
              print('Data: $data');
            }
          }
          return handler.next(options);
        },
        onResponse: (response, handler) {
          if (kDebugMode) {
            print(
              'RESPONSE[${response.statusCode}] => PATH: ${response.requestOptions.path}',
            );
          }
          return handler.next(response);
        },
        onError: (DioException err, handler) {
          if (kDebugMode) {
            print(
              'ERROR[${err.response?.statusCode}] => PATH: ${err.requestOptions.path}',
            );
            print('Message: ${err.message}');
          }
          return handler.next(err);
        },
      ),
    );
  }

  Dio get dio => _dio;
}
