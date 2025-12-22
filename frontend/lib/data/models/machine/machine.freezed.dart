// coverage:ignore-file
// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'machine.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

T _$identity<T>(T value) => value;

final _privateConstructorUsedError = UnsupportedError(
  'It seems like you constructed your class using `MyClass._()`. This constructor is only meant to be used by freezed and you are not supposed to need it nor use it.\nPlease check the documentation here for more information: https://github.com/rrousselGit/freezed#adding-getters-and-methods-to-our-models',
);

Machine _$MachineFromJson(Map<String, dynamic> json) {
  return _Machine.fromJson(json);
}

/// @nodoc
mixin _$Machine {
  int get id => throw _privateConstructorUsedError;
  String? get name => throw _privateConstructorUsedError;
  String? get description => throw _privateConstructorUsedError;
  @JsonKey(name: 'serial_number')
  String? get serialNumber => throw _privateConstructorUsedError;
  @JsonKey(name: 'price_base_per_hour')
  double? get priceBasePerHour => throw _privateConstructorUsedError;
  String? get status => throw _privateConstructorUsedError;
  @JsonKey(name: 'image_url')
  String? get imageUrl => throw _privateConstructorUsedError;
  List<String>? get photos => throw _privateConstructorUsedError;
  Map<String, dynamic>? get specs => throw _privateConstructorUsedError;

  /// Serializes this Machine to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of Machine
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $MachineCopyWith<Machine> get copyWith => throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $MachineCopyWith<$Res> {
  factory $MachineCopyWith(Machine value, $Res Function(Machine) then) =
      _$MachineCopyWithImpl<$Res, Machine>;
  @useResult
  $Res call({
    int id,
    String? name,
    String? description,
    @JsonKey(name: 'serial_number') String? serialNumber,
    @JsonKey(name: 'price_base_per_hour') double? priceBasePerHour,
    String? status,
    @JsonKey(name: 'image_url') String? imageUrl,
    List<String>? photos,
    Map<String, dynamic>? specs,
  });
}

/// @nodoc
class _$MachineCopyWithImpl<$Res, $Val extends Machine>
    implements $MachineCopyWith<$Res> {
  _$MachineCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of Machine
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? id = null,
    Object? name = freezed,
    Object? description = freezed,
    Object? serialNumber = freezed,
    Object? priceBasePerHour = freezed,
    Object? status = freezed,
    Object? imageUrl = freezed,
    Object? photos = freezed,
    Object? specs = freezed,
  }) {
    return _then(
      _value.copyWith(
            id: null == id
                ? _value.id
                : id // ignore: cast_nullable_to_non_nullable
                      as int,
            name: freezed == name
                ? _value.name
                : name // ignore: cast_nullable_to_non_nullable
                      as String?,
            description: freezed == description
                ? _value.description
                : description // ignore: cast_nullable_to_non_nullable
                      as String?,
            serialNumber: freezed == serialNumber
                ? _value.serialNumber
                : serialNumber // ignore: cast_nullable_to_non_nullable
                      as String?,
            priceBasePerHour: freezed == priceBasePerHour
                ? _value.priceBasePerHour
                : priceBasePerHour // ignore: cast_nullable_to_non_nullable
                      as double?,
            status: freezed == status
                ? _value.status
                : status // ignore: cast_nullable_to_non_nullable
                      as String?,
            imageUrl: freezed == imageUrl
                ? _value.imageUrl
                : imageUrl // ignore: cast_nullable_to_non_nullable
                      as String?,
            photos: freezed == photos
                ? _value.photos
                : photos // ignore: cast_nullable_to_non_nullable
                      as List<String>?,
            specs: freezed == specs
                ? _value.specs
                : specs // ignore: cast_nullable_to_non_nullable
                      as Map<String, dynamic>?,
          )
          as $Val,
    );
  }
}

/// @nodoc
abstract class _$$MachineImplCopyWith<$Res> implements $MachineCopyWith<$Res> {
  factory _$$MachineImplCopyWith(
    _$MachineImpl value,
    $Res Function(_$MachineImpl) then,
  ) = __$$MachineImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call({
    int id,
    String? name,
    String? description,
    @JsonKey(name: 'serial_number') String? serialNumber,
    @JsonKey(name: 'price_base_per_hour') double? priceBasePerHour,
    String? status,
    @JsonKey(name: 'image_url') String? imageUrl,
    List<String>? photos,
    Map<String, dynamic>? specs,
  });
}

/// @nodoc
class __$$MachineImplCopyWithImpl<$Res>
    extends _$MachineCopyWithImpl<$Res, _$MachineImpl>
    implements _$$MachineImplCopyWith<$Res> {
  __$$MachineImplCopyWithImpl(
    _$MachineImpl _value,
    $Res Function(_$MachineImpl) _then,
  ) : super(_value, _then);

  /// Create a copy of Machine
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? id = null,
    Object? name = freezed,
    Object? description = freezed,
    Object? serialNumber = freezed,
    Object? priceBasePerHour = freezed,
    Object? status = freezed,
    Object? imageUrl = freezed,
    Object? photos = freezed,
    Object? specs = freezed,
  }) {
    return _then(
      _$MachineImpl(
        id: null == id
            ? _value.id
            : id // ignore: cast_nullable_to_non_nullable
                  as int,
        name: freezed == name
            ? _value.name
            : name // ignore: cast_nullable_to_non_nullable
                  as String?,
        description: freezed == description
            ? _value.description
            : description // ignore: cast_nullable_to_non_nullable
                  as String?,
        serialNumber: freezed == serialNumber
            ? _value.serialNumber
            : serialNumber // ignore: cast_nullable_to_non_nullable
                  as String?,
        priceBasePerHour: freezed == priceBasePerHour
            ? _value.priceBasePerHour
            : priceBasePerHour // ignore: cast_nullable_to_non_nullable
                  as double?,
        status: freezed == status
            ? _value.status
            : status // ignore: cast_nullable_to_non_nullable
                  as String?,
        imageUrl: freezed == imageUrl
            ? _value.imageUrl
            : imageUrl // ignore: cast_nullable_to_non_nullable
                  as String?,
        photos: freezed == photos
            ? _value._photos
            : photos // ignore: cast_nullable_to_non_nullable
                  as List<String>?,
        specs: freezed == specs
            ? _value._specs
            : specs // ignore: cast_nullable_to_non_nullable
                  as Map<String, dynamic>?,
      ),
    );
  }
}

/// @nodoc
@JsonSerializable()
class _$MachineImpl implements _Machine {
  const _$MachineImpl({
    required this.id,
    this.name,
    this.description,
    @JsonKey(name: 'serial_number') this.serialNumber,
    @JsonKey(name: 'price_base_per_hour') this.priceBasePerHour,
    this.status,
    @JsonKey(name: 'image_url') this.imageUrl,
    final List<String>? photos,
    final Map<String, dynamic>? specs,
  }) : _photos = photos,
       _specs = specs;

  factory _$MachineImpl.fromJson(Map<String, dynamic> json) =>
      _$$MachineImplFromJson(json);

  @override
  final int id;
  @override
  final String? name;
  @override
  final String? description;
  @override
  @JsonKey(name: 'serial_number')
  final String? serialNumber;
  @override
  @JsonKey(name: 'price_base_per_hour')
  final double? priceBasePerHour;
  @override
  final String? status;
  @override
  @JsonKey(name: 'image_url')
  final String? imageUrl;
  final List<String>? _photos;
  @override
  List<String>? get photos {
    final value = _photos;
    if (value == null) return null;
    if (_photos is EqualUnmodifiableListView) return _photos;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(value);
  }

  final Map<String, dynamic>? _specs;
  @override
  Map<String, dynamic>? get specs {
    final value = _specs;
    if (value == null) return null;
    if (_specs is EqualUnmodifiableMapView) return _specs;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableMapView(value);
  }

  @override
  String toString() {
    return 'Machine(id: $id, name: $name, description: $description, serialNumber: $serialNumber, priceBasePerHour: $priceBasePerHour, status: $status, imageUrl: $imageUrl, photos: $photos, specs: $specs)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$MachineImpl &&
            (identical(other.id, id) || other.id == id) &&
            (identical(other.name, name) || other.name == name) &&
            (identical(other.description, description) ||
                other.description == description) &&
            (identical(other.serialNumber, serialNumber) ||
                other.serialNumber == serialNumber) &&
            (identical(other.priceBasePerHour, priceBasePerHour) ||
                other.priceBasePerHour == priceBasePerHour) &&
            (identical(other.status, status) || other.status == status) &&
            (identical(other.imageUrl, imageUrl) ||
                other.imageUrl == imageUrl) &&
            const DeepCollectionEquality().equals(other._photos, _photos) &&
            const DeepCollectionEquality().equals(other._specs, _specs));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(
    runtimeType,
    id,
    name,
    description,
    serialNumber,
    priceBasePerHour,
    status,
    imageUrl,
    const DeepCollectionEquality().hash(_photos),
    const DeepCollectionEquality().hash(_specs),
  );

  /// Create a copy of Machine
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$MachineImplCopyWith<_$MachineImpl> get copyWith =>
      __$$MachineImplCopyWithImpl<_$MachineImpl>(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$MachineImplToJson(this);
  }
}

abstract class _Machine implements Machine {
  const factory _Machine({
    required final int id,
    final String? name,
    final String? description,
    @JsonKey(name: 'serial_number') final String? serialNumber,
    @JsonKey(name: 'price_base_per_hour') final double? priceBasePerHour,
    final String? status,
    @JsonKey(name: 'image_url') final String? imageUrl,
    final List<String>? photos,
    final Map<String, dynamic>? specs,
  }) = _$MachineImpl;

  factory _Machine.fromJson(Map<String, dynamic> json) = _$MachineImpl.fromJson;

  @override
  int get id;
  @override
  String? get name;
  @override
  String? get description;
  @override
  @JsonKey(name: 'serial_number')
  String? get serialNumber;
  @override
  @JsonKey(name: 'price_base_per_hour')
  double? get priceBasePerHour;
  @override
  String? get status;
  @override
  @JsonKey(name: 'image_url')
  String? get imageUrl;
  @override
  List<String>? get photos;
  @override
  Map<String, dynamic>? get specs;

  /// Create a copy of Machine
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$MachineImplCopyWith<_$MachineImpl> get copyWith =>
      throw _privateConstructorUsedError;
}
