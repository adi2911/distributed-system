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




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x10Proto/lock.proto\x12\x0clock_service\"2\n\tlock_args\x12\x11\n\tclient_id\x18\x01 \x01(\x05\x12\x12\n\nrequest_id\x18\x02 \x01(\t\"(\n\x13\x63urrent_lock_holder\x12\x11\n\tclient_id\x18\x01 \x01(\x05\"\x81\x01\n\x08Response\x12$\n\x06status\x18\x01 \x01(\x0e\x32\x14.lock_service.Status\x12\x0f\n\x07version\x18\x02 \x01(\x05\x12>\n\x13\x63urrent_lock_holder\x18\x03 \x01(\x0b\x32!.lock_service.current_lock_holder\"U\n\tfile_args\x12\x10\n\x08\x66ilename\x18\x01 \x01(\t\x12\x0f\n\x07\x63ontent\x18\x02 \x01(\x0c\x12\x11\n\tclient_id\x18\x03 \x01(\x05\x12\x12\n\nrequest_id\x18\x04 \x01(\t\"\x11\n\x03Int\x12\n\n\x02rc\x18\x01 \x01(\x05\"\x1e\n\tHeartbeat\x12\x11\n\tclient_id\x18\x01 \x01(\x05\"1\n\x0bVoteRequest\x12\x14\n\x0c\x63\x61ndidate_id\x18\x01 \x01(\t\x12\x0c\n\x04term\x18\x02 \x01(\x05\"$\n\x0cVoteResponse\x12\x14\n\x0cvote_granted\x18\x01 \x01(\x08\"5\n\x10\x46ileAppendBackup\x12\x10\n\x08\x66ilename\x18\x01 \x01(\t\x12\x0f\n\x07\x63ontent\x18\x02 \x01(\x0c*M\n\x06Status\x12\x0b\n\x07SUCCESS\x10\x00\x12\x0e\n\nFILE_ERROR\x10\x01\x12\x11\n\rTIMEOUT_ERROR\x10\x02\x12\x13\n\x0f\x44UPLICATE_ERROR\x10\x03\x32\xda\x04\n\x0bLockService\x12\x33\n\x0b\x63lient_init\x12\x11.lock_service.Int\x1a\x11.lock_service.Int\x12?\n\x0clock_acquire\x12\x17.lock_service.lock_args\x1a\x16.lock_service.Response\x12?\n\x0clock_release\x12\x17.lock_service.lock_args\x1a\x16.lock_service.Response\x12>\n\x0b\x66ile_append\x12\x17.lock_service.file_args\x1a\x16.lock_service.Response\x12\x34\n\x0c\x63lient_close\x12\x11.lock_service.Int\x1a\x11.lock_service.Int\x12<\n\theartbeat\x12\x17.lock_service.Heartbeat\x1a\x16.lock_service.Response\x12S\n\x16getCurrent_lock_holder\x12!.lock_service.current_lock_holder\x1a\x16.lock_service.Response\x12=\n\x04vote\x12\x19.lock_service.VoteRequest\x1a\x1a.lock_service.VoteResponse\x12L\n\x12\x66ile_append_backup\x12\x1e.lock_service.FileAppendBackup\x1a\x16.lock_service.Responseb\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'Proto.lock_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
  DESCRIPTOR._loaded_options = None
  _globals['_STATUS']._serialized_start=542
  _globals['_STATUS']._serialized_end=619
  _globals['_LOCK_ARGS']._serialized_start=34
  _globals['_LOCK_ARGS']._serialized_end=84
  _globals['_CURRENT_LOCK_HOLDER']._serialized_start=86
  _globals['_CURRENT_LOCK_HOLDER']._serialized_end=126
  _globals['_RESPONSE']._serialized_start=129
  _globals['_RESPONSE']._serialized_end=258
  _globals['_FILE_ARGS']._serialized_start=260
  _globals['_FILE_ARGS']._serialized_end=345
  _globals['_INT']._serialized_start=347
  _globals['_INT']._serialized_end=364
  _globals['_HEARTBEAT']._serialized_start=366
  _globals['_HEARTBEAT']._serialized_end=396
  _globals['_VOTEREQUEST']._serialized_start=398
  _globals['_VOTEREQUEST']._serialized_end=447
  _globals['_VOTERESPONSE']._serialized_start=449
  _globals['_VOTERESPONSE']._serialized_end=485
  _globals['_FILEAPPENDBACKUP']._serialized_start=487
  _globals['_FILEAPPENDBACKUP']._serialized_end=540
  _globals['_LOCKSERVICE']._serialized_start=622
  _globals['_LOCKSERVICE']._serialized_end=1224
# @@protoc_insertion_point(module_scope)
