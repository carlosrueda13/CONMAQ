import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../core/api/dio_client.dart';
import '../../core/utils/storage_service.dart';
import '../../data/datasources/auth_datasource.dart';
import '../../data/models/auth/user.dart';
import '../../data/repositories_impl/auth_repository_impl.dart';
import '../../domain/repositories_interfaces/auth_repository.dart';

enum AuthStatus { checking, authenticated, unauthenticated }

class AuthState {
  final AuthStatus status;
  final User? user;
  final String? errorMessage;

  AuthState({this.status = AuthStatus.checking, this.user, this.errorMessage});

  AuthState copyWith({AuthStatus? status, User? user, String? errorMessage}) {
    return AuthState(
      status: status ?? this.status,
      user: user ?? this.user,
      errorMessage: errorMessage,
    );
  }
}

class AuthNotifier extends StateNotifier<AuthState> {
  final AuthRepository _authRepository;

  AuthNotifier(this._authRepository) : super(AuthState()) {
    checkAuthStatus();
  }

  Future<void> checkAuthStatus() async {
    final token = await _authRepository.getToken();
    if (token == null) {
      state = state.copyWith(status: AuthStatus.unauthenticated);
      return;
    }

    try {
      final user = await _authRepository.getUserMe();
      state = state.copyWith(status: AuthStatus.authenticated, user: user);
    } catch (e) {
      await _authRepository.logout();
      state = state.copyWith(status: AuthStatus.unauthenticated);
    }
  }

  Future<void> login(String username, String password) async {
    state = state.copyWith(status: AuthStatus.checking, errorMessage: null);
    try {
      await _authRepository.login(username, password);
      final user = await _authRepository.getUserMe();
      state = state.copyWith(status: AuthStatus.authenticated, user: user);
    } catch (e) {
      state = state.copyWith(
        status: AuthStatus.unauthenticated,
        errorMessage: 'Credenciales incorrectas o error de conexión',
      );
    }
  }

  Future<void> logout() async {
    await _authRepository.logout();
    state = state.copyWith(status: AuthStatus.unauthenticated, user: null);
  }
}

// Dependency Injection
final storageServiceProvider = Provider((ref) => StorageService());

final dioClientProvider = Provider((ref) {
  final storageService = ref.watch(storageServiceProvider);
  return DioClient(storageService);
});

final authDataSourceProvider = Provider((ref) {
  final dioClient = ref.watch(dioClientProvider);
  return AuthDataSource(dioClient);
});

final authRepositoryProvider = Provider<AuthRepository>((ref) {
  final dataSource = ref.watch(authDataSourceProvider);
  final storage = ref.watch(storageServiceProvider);
  return AuthRepositoryImpl(dataSource, storage);
});

final authProvider = StateNotifierProvider<AuthNotifier, AuthState>((ref) {
  final authRepository = ref.watch(authRepositoryProvider);
  return AuthNotifier(authRepository);
});
