import '../../data/models/machine/machine.dart';

abstract class MachineRepository {
  Future<List<Machine>> getMachines({String? status, String? search});
  Future<Machine> getMachineById(int id);
}
