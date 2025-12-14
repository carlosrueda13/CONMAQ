import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import '../../presentation/screens/home_screen.dart';
import '../../presentation/screens/login_screen.dart';
import '../../presentation/screens/splash_screen.dart';

class AppRouter {
  static final GoRouter router = GoRouter(
    initialLocation: '/splash',
    routes: [
      GoRoute(
        path: '/splash',
        builder: (context, state) => const SplashScreen(),
      ),
      GoRoute(path: '/login', builder: (context, state) => const LoginScreen()),
      GoRoute(path: '/home', builder: (context, state) => const HomeScreen()),
      GoRoute(
        path: '/machine/:id',
        builder: (context, state) {
          final id = state.pathParameters['id'];
          return Scaffold(
            appBar: AppBar(title: Text('Máquina $id')),
            body: const Center(
              child: Text('Detalle de Máquina (En construcción)'),
            ),
          );
        },
      ),
    ],
  );
}
