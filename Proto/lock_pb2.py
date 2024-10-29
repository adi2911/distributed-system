# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# NO CHECKED-IN PROTOBUF GENCODE
# source: Proto/lock.proto
# Protobuf Python Version: 5.27.2
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(
    _runtime_version.Domain.PUBLIC,
    5,
    27,
    2,
    '',
    'Proto/lock.proto'
)
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x10Proto/lock.proto\x12\x0clock_service\"\x1e\n\tlock_args\x12\x11\n\tclient_id\x18\x01 \x01(\x05\"0\n\x08Response\x12$\n\x06status\x18\x01 \x01(\x0e\x32\x14.lock_service.Status\"A\n\tfile_args\x12\x10\n\x08\x66ilename\x18\x01 \x01(\t\x12\x0f\n\x07\x63ontent\x18\x02 \x01(\x0c\x12\x11\n\tclient_id\x18\x03 \x01(\x05\"\x11\n\x03Int\x12\n\n\x02rc\x18\x01 \x01(\x05*%\n\x06Status\x12\x0b\n\x07SUCCESS\x10\x00\x12\x0e\n\nFILE_ERROR\x10\x01\x32\xba\x02\n\x0bLockService\x12\x33\n\x0b\x63lient_init\x12\x11.lock_service.Int\x1a\x11.lock_service.Int\x12?\n\x0clock_acquire\x12\x17.lock_service.lock_args\x1a\x16.lock_service.Response\x12?\n\x0clock_release\x12\x17.lock_service.lock_args\x1a\x16.lock_service.Response\x12>\n\x0b\x66ile_append\x12\x17.lock_service.file_args\x1a\x16.lock_service.Response\x12\x34\n\x0c\x63lient_close\x12\x11.lock_service.Int\x1a\x11.lock_service.Intb\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'Proto.lock_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
  DESCRIPTOR._loaded_options = None
  _globals['_STATUS']._serialized_start=202
  _globals['_STATUS']._serialized_end=239
  _globals['_LOCK_ARGS']._serialized_start=34
  _globals['_LOCK_ARGS']._serialized_end=64
  _globals['_RESPONSE']._serialized_start=66
  _globals['_RESPONSE']._serialized_end=114
  _globals['_FILE_ARGS']._serialized_start=116
  _globals['_FILE_ARGS']._serialized_end=181
  _globals['_INT']._serialized_start=183
  _globals['_INT']._serialized_end=200
  _globals['_LOCKSERVICE']._serialized_start=242
  _globals['_LOCKSERVICE']._serialized_end=556
# @@protoc_insertion_point(module_scope)