import '../../core/utils/storage_service.dart';
import '../../data/datasources/auth_datasource.dart';
import '../../data/models/auth/token_response.dart';
import '../../data/models/auth/user.dart';
import '../../domain/repositories_interfaces/auth_repository.dart';

class AuthRepositoryImpl implements AuthRepository {
  final AuthDataSource _dataSource;
  final StorageService _storageService;

  AuthRepositoryImpl(this._dataSource, this._storageService);

  @override
  Future<TokenResponse> login(String username, String password) async {
    final tokenResponse = await _dataSource.login(username, password);
    await saveToken(tokenResponse.accessToken);
    return tokenResponse;
  }

  @override
  Future<User> register(
    String email,
    String password,
    String fullName,
    String phone,
    String role,
  ) async {
    return await _dataSource.register(email, password, fullName, phone, role);
  }

  @override
  Future<User> getUserMe() async {
    return await _dataSource.getUserMe();
  }

  @override
  Future<void> saveToken(String token) async {
    await _storageService.saveToken(token);
  }

  @override
  Future<String?> getToken() async {
    return await _storageService.getToken();
  }

  @override
  Future<void> logout() async {
    await _storageService.deleteToken();
  }
}
