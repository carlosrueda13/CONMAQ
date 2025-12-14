import 'package:dio/dio.dart';
import '../../core/api/dio_client.dart';
import '../../core/constants/api_constants.dart';
import '../models/auth/token_response.dart';
import '../models/auth/user.dart';

class AuthDataSource {
  final DioClient _dioClient;

  AuthDataSource(this._dioClient);

  Future<TokenResponse> login(String username, String password) async {
    try {
      final response = await _dioClient.dio.post(
        ApiConstants.loginEndpoint,
        data: {'username': username, 'password': password},
        options: Options(contentType: Headers.formUrlEncodedContentType),
      );
      return TokenResponse.fromJson(response.data);
    } catch (e) {
      rethrow;
    }
  }

  Future<User> getUserMe() async {
    try {
      final response = await _dioClient.dio.get(
        '${ApiConstants.usersEndpoint}me',
      );
      return User.fromJson(response.data);
    } catch (e) {
      rethrow;
    }
  }
}
