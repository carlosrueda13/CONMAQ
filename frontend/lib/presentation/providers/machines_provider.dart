import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../data/datasources/machine_datasource.dart';
import '../../data/models/machine/machine.dart';
import '../../data/repositories_impl/machine_repository_impl.dart';
import '../../domain/repositories_interfaces/machine_repository.dart';
import 'auth_provider.dart'; // To get dioClientProvider

// Dependency Injection
final machineDataSourceProvider = Provider((ref) {
  final dioClient = ref.watch(dioClientProvider);
  return MachineDataSource(dioClient);
});

final machineRepositoryProvider = Provider<MachineRepository>((ref) {
  final dataSource = ref.watch(machineDataSourceProvider);
  return MachineRepositoryImpl(dataSource);
});

// State
class MachinesState {
  final bool isLoading;
  final List<Machine> machines;
  final String? errorMessage;

  MachinesState({
    this.isLoading = false,
    this.machines = const [],
    this.errorMessage,
  });

  MachinesState copyWith({
    bool? isLoading,
    List<Machine>? machines,
    String? errorMessage,
  }) {
    return MachinesState(
      isLoading: isLoading ?? this.isLoading,
      machines: machines ?? this.machines,
      errorMessage: errorMessage,
    );
  }
}

// Notifier
class MachinesNotifier extends StateNotifier<MachinesState> {
  final MachineRepository _repository;

  MachinesNotifier(this._repository) : super(MachinesState()) {
    loadMachines();
  }

  Future<void> loadMachines({String? search, String? status}) async {
    state = state.copyWith(isLoading: true, errorMessage: null);
    try {
      final machines = await _repository.getMachines(
        search: search,
        status: status,
      );
      state = state.copyWith(isLoading: false, machines: machines);
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        errorMessage: 'Error al cargar máquinas: ${e.toString()}',
      );
    }
  }
}

// Provider
final machinesProvider = StateNotifierProvider<MachinesNotifier, MachinesState>(
  (ref) {
    final repository = ref.watch(machineRepositoryProvider);
    return MachinesNotifier(repository);
  },
);
