class ApiConstants {
  // For Android Emulator use 10.0.2.2, for iOS Simulator use localhost
  // Ideally this should come from .env
  static const String baseUrl = 'http://localhost:8000/api/v1';

  static const String loginEndpoint = '/auth/login/access-token';
  static const String usersEndpoint = '/users/';
  static const String machinesEndpoint = '/machines/';
  static const String offersEndpoint = '/offers/';
  static const String bookingsEndpoint = '/bookings/';
  static const String watchlistEndpoint = '/watchlist/';
  static const String notificationsEndpoint = '/notifications/';
  static const String paymentsEndpoint = '/payments/';
}
