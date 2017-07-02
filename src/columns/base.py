import struct

from ..reader import read_binary_uint8
from ..writer import write_binary_uint8


size_by_type = {
    'Date': 2,
    'DateTime': 4,
    'Int8': 1,
    'UInt8': 1,
    'Int16': 2,
    'UInt16': 2,
    'Int32': 4,
    'UInt32': 4,
    'Int64': 8,
    'UInt64': 8,
    'Float32': 4,
    'Float64': 8,
    'Enum8': 1,
    'Enum16': 2
}


class Column(object):
    ch_type = None
    py_types = None

    def __init__(self):
        self.nullable = False
        super(Column, self).__init__()

    @property
    def size(self):
        return size_by_type[self.ch_type]

    def read(self, buf):
        raise NotImplementedError

    def _read_null(self, buf):
        raise NotImplementedError

    def write(self, value, buf):
        raise NotImplementedError

    def _write_null(self, buf):
        raise NotImplementedError

    def _read(self, buf, fmt):
        return struct.unpack(fmt, buf.read(self.size))[0]

    def _read_nulls_map(self, rows, buf):
        return tuple(read_binary_uint8(buf) for _i in range(rows))

    def _write(self, x, buf, fmt):
        return buf.write(struct.pack(fmt, x))

    def _write_nulls_map(self, data, buf):
        for x in data:
            write_binary_uint8(x is None, buf)

    def write_data(self, data, buf):
        if self.nullable:
            self._write_nulls_map(data, buf)

        for x in data:
            if self.nullable and x is None:
                self._write_null(buf)

            else:
                if not isinstance(x, self.py_types):
                    raise TypeError(x)

                self.write(x, buf)

    def read_data(self, rows, buf):
        if self.nullable:
            nulls_map = self._read_nulls_map(rows, buf)
        else:
            nulls_map = [0] * rows

        return tuple(
            self._read_null(buf) if is_null else self.read(buf)
            for is_null in nulls_map
        )