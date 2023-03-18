KEY_COMPLETED = "completed"
KEY_HALTED = "halted"
KEY_UPDATED = "updated"

TYPE_SYNC = 0
TYPE_PING = 1
TYPE_RESYNC = 2

FLAG_RESET = 1

UTF_8 = "UTF-8"
PAD_MODULO = 16
START_STR = "BOBO"
END_BYTES = "BOBO".encode(UTF_8)
LEN_END_BYTES = len(END_BYTES)

BYTES_AES_128 = 16
BYTES_AES_192 = 24
BYTES_AES_256 = 32

EXC_CLOSED = "distributed is closed"
EXC_RUNNING = "distributed is already running"
EXC_NOT_RUNNING = "distributed is not running"
