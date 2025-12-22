import '../../data/models/auth/token_response.dart';
import '../../data/models/auth/user.dart';

abstract class AuthRepository {
  Future<TokenResponse> login(String username, String password);
  Future<User> register(
    String email,
    String password,
    String fullName,
    String phone,
    String role,
  );
  Future<User> getUserMe();
  Future<void> saveToken(String token);
  Future<String?> getToken();
  Future<void> logout();
}
