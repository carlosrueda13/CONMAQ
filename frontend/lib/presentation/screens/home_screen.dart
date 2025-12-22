import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../config/theme/app_theme.dart';
import '../providers/auth_provider.dart';
import '../providers/machines_provider.dart';
import '../widgets/machine_card.dart';

class HomeScreen extends ConsumerStatefulWidget {
  const HomeScreen({super.key});

  @override
  ConsumerState<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends ConsumerState<HomeScreen> {
  final TextEditingController _searchController = TextEditingController();

  @override
  void dispose() {
    _searchController.dispose();
    super.dispose();
  }

  void _onSearchChanged(String value) {
    // Debounce could be added here
    ref.read(machinesProvider.notifier).loadMachines(search: value);
  }

  @override
  Widget build(BuildContext context) {
    final machinesState = ref.watch(machinesProvider);

    ref.listen(authProvider, (previous, next) {
      if (next.status == AuthStatus.unauthenticated) {
        context.go('/login');
      }
    });

    return Scaffold(
      body: CustomScrollView(
        slivers: [
          // App Bar with Search
          SliverAppBar(
            floating: true,
            pinned: true,
            expandedHeight: 120.0,
            backgroundColor: AppTheme.primaryColor,
            flexibleSpace: FlexibleSpaceBar(
              background: Container(
                decoration: const BoxDecoration(
                  gradient: LinearGradient(
                    begin: Alignment.topLeft,
                    end: Alignment.bottomRight,
                    colors: [AppTheme.primaryColor, Color(0xFF1A4B8C)],
                  ),
                ),
              ),
              titlePadding: const EdgeInsets.only(
                left: 16,
                right: 16,
                bottom: 16,
              ),
              title: SizedBox(
                height: 40,
                child: TextField(
                  controller: _searchController,
                  onChanged: _onSearchChanged,
                  style: const TextStyle(color: Colors.black87, fontSize: 14),
                  decoration: InputDecoration(
                    hintText: 'Buscar maquinaria...',
                    hintStyle: TextStyle(color: Colors.grey[600]),
                    prefixIcon: const Icon(Icons.search, color: Colors.grey),
                    filled: true,
                    fillColor: Colors.white.withValues(alpha: 0.9),
                    contentPadding: const EdgeInsets.symmetric(vertical: 0),
                    border: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(20),
                      borderSide: BorderSide.none,
                    ),
                  ),
                ),
              ),
            ),
            actions: [
              IconButton(
                icon: const Icon(Icons.logout, color: Colors.white),
                onPressed: () {
                  ref.read(authProvider.notifier).logout();
                },
              ),
            ],
          ),

          // Content
          if (machinesState.isLoading)
            const SliverFillRemaining(
              child: Center(child: CircularProgressIndicator()),
            )
          else if (machinesState.errorMessage != null)
            SliverFillRemaining(
              child: Center(
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    const Icon(
                      Icons.error_outline,
                      size: 48,
                      color: Colors.red,
                    ),
                    const SizedBox(height: 16),
                    Text(
                      machinesState.errorMessage!,
                      textAlign: TextAlign.center,
                      style: const TextStyle(color: Colors.red),
                    ),
                    const SizedBox(height: 16),
                    ElevatedButton(
                      onPressed: () {
                        ref.read(machinesProvider.notifier).loadMachines();
                      },
                      child: const Text('Reintentar'),
                    ),
                  ],
                ),
              ),
            )
          else if (machinesState.machines.isEmpty)
            const SliverFillRemaining(
              child: Center(child: Text('No se encontraron máquinas.')),
            )
          else
            SliverPadding(
              padding: const EdgeInsets.all(16),
              sliver: SliverGrid(
                gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                  crossAxisCount: 2, // Responsive logic could be added here
                  childAspectRatio: 0.75,
                  crossAxisSpacing: 16,
                  mainAxisSpacing: 16,
                ),
                delegate: SliverChildBuilderDelegate((context, index) {
                  final machine = machinesState.machines[index];
                  return MachineCard(
                    machine: machine,
                    onTap: () {
                      context.push('/machine/${machine.id}');
                    },
                  );
                }, childCount: machinesState.machines.length),
              ),
            ),
        ],
      ),
    );
  }
}
