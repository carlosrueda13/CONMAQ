// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'machine.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_$MachineImpl _$$MachineImplFromJson(Map<String, dynamic> json) =>
    _$MachineImpl(
      id: (json['id'] as num).toInt(),
      name: json['name'] as String?,
      description: json['description'] as String?,
      serialNumber: json['serial_number'] as String?,
      priceBasePerHour: (json['price_base_per_hour'] as num?)?.toDouble(),
      status: json['status'] as String?,
      imageUrl: json['image_url'] as String?,
      photos: (json['photos'] as List<dynamic>?)
          ?.map((e) => e as String)
          .toList(),
      specs: json['specs'] as Map<String, dynamic>?,
    );

Map<String, dynamic> _$$MachineImplToJson(_$MachineImpl instance) =>
    <String, dynamic>{
      'id': instance.id,
      'name': instance.name,
      'description': instance.description,
      'serial_number': instance.serialNumber,
      'price_base_per_hour': instance.priceBasePerHour,
      'status': instance.status,
      'image_url': instance.imageUrl,
      'photos': instance.photos,
      'specs': instance.specs,
    };
