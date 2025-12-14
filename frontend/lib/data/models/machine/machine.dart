// ignore_for_file: invalid_annotation_target
import 'package:freezed_annotation/freezed_annotation.dart';

part 'machine.freezed.dart';
part 'machine.g.dart';

@freezed
class Machine with _$Machine {
  const factory Machine({
    required int id,
    required String name,
    required String description,
    @JsonKey(name: 'serial_number') required String serialNumber,
    @JsonKey(name: 'price_base_per_hour') required double priceBasePerHour,
    required String status,
    @JsonKey(name: 'image_url') String? imageUrl,
    List<String>? photos,
    Map<String, dynamic>? specs,
  }) = _Machine;

  factory Machine.fromJson(Map<String, dynamic> json) =>
      _$MachineFromJson(json);
}
