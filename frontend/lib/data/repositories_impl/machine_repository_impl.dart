import '../../data/datasources/machine_datasource.dart';
import '../../data/models/machine/machine.dart';
import '../../domain/repositories_interfaces/machine_repository.dart';

class MachineRepositoryImpl implements MachineRepository {
  final MachineDataSource _dataSource;

  MachineRepositoryImpl(this._dataSource);

  @override
  Future<List<Machine>> getMachines({String? status, String? search}) async {
    return await _dataSource.getMachines(status: status, search: search);
  }

  @override
  Future<Machine> getMachineById(int id) async {
    return await _dataSource.getMachineById(id);
  }
}
