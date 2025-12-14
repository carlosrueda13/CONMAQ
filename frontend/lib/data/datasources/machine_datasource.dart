import '../../core/api/dio_client.dart';
import '../../core/constants/api_constants.dart';
import '../models/machine/machine.dart';

class MachineDataSource {
  final DioClient _dioClient;

  MachineDataSource(this._dioClient);

  Future<List<Machine>> getMachines({String? status, String? search}) async {
    try {
      final Map<String, dynamic> queryParams = {};
      if (status != null) queryParams['status'] = status;
      if (search != null) queryParams['search'] = search;

      final response = await _dioClient.dio.get(
        ApiConstants.machinesEndpoint,
        queryParameters: queryParams,
      );

      return (response.data as List)
          .map((json) => Machine.fromJson(json))
          .toList();
    } catch (e) {
      rethrow;
    }
  }

  Future<Machine> getMachineById(int id) async {
    try {
      final response = await _dioClient.dio.get(
        '${ApiConstants.machinesEndpoint}$id',
      );
      return Machine.fromJson(response.data);
    } catch (e) {
      rethrow;
    }
  }
}
