"""
WASI filesystem is a filesystem API primarily intended to let users run WASI
programs that access their files on their existing filesystems, without
significant overhead.

It is intended to be roughly portable between Unix-family platforms and
Windows, though it does not hide many of the major differences.

Paths are passed as interface-type `string`s, meaning they must consist of
a sequence of Unicode Scalar Values (USVs). Some filesystems may contain
paths which are not accessible by this API.

The directory separator in WASI is always the forward-slash (`/`).

All paths in WASI are relative paths, and are interpreted relative to a
`descriptor` referring to a base directory. If a `path` argument to any WASI
function starts with `/`, or if any step of resolving a `path`, including
`..` and symbolic link steps, reaches a directory outside of the base
directory, or reaches a symlink to an absolute or rooted path in the
underlying filesystem, the function fails with `error-code::not-permitted`.

For more information about WASI path resolution and sandboxing, see
[WASI filesystem path resolution].

[WASI filesystem path resolution]: https://github.com/WebAssembly/wasi-filesystem/blob/main/path-resolution.md
"""
from typing import TypeVar, Generic, Union, Optional, Protocol, Tuple, List, Any, Self
from types import TracebackType
from enum import Flag, Enum, auto
from dataclasses import dataclass
from abc import abstractmethod
import weakref

from ..types import Result, Ok, Err, Some
from ..imports import streams
from ..imports import wall_clock
from ..imports import error

class DescriptorType(Enum):
    """
    The type of a filesystem object referenced by a descriptor.
    
    Note: This was called `filetype` in earlier versions of WASI.
    """
    UNKNOWN = 0
    BLOCK_DEVICE = 1
    CHARACTER_DEVICE = 2
    DIRECTORY = 3
    FIFO = 4
    SYMBOLIC_LINK = 5
    REGULAR_FILE = 6
    SOCKET = 7

class DescriptorFlags(Flag):
    """
    Descriptor flags.
    
    Note: This was called `fdflags` in earlier versions of WASI.
    """
    READ = auto()
    WRITE = auto()
    FILE_INTEGRITY_SYNC = auto()
    DATA_INTEGRITY_SYNC = auto()
    REQUESTED_WRITE_SYNC = auto()
    MUTATE_DIRECTORY = auto()

class PathFlags(Flag):
    """
    Flags determining the method of how paths are resolved.
    """
    SYMLINK_FOLLOW = auto()

class OpenFlags(Flag):
    """
    Open flags used by `open-at`.
    """
    CREATE = auto()
    DIRECTORY = auto()
    EXCLUSIVE = auto()
    TRUNCATE = auto()

@dataclass
class DescriptorStat:
    """
    File attributes.
    
    Note: This was called `filestat` in earlier versions of WASI.
    """
    type: DescriptorType
    link_count: int
    size: int
    data_access_timestamp: Optional[wall_clock.Datetime]
    data_modification_timestamp: Optional[wall_clock.Datetime]
    status_change_timestamp: Optional[wall_clock.Datetime]


@dataclass
class NewTimestamp_NoChange:
    pass


@dataclass
class NewTimestamp_Now:
    pass


@dataclass
class NewTimestamp_Timestamp:
    value: wall_clock.Datetime


NewTimestamp = Union[NewTimestamp_NoChange, NewTimestamp_Now, NewTimestamp_Timestamp]
"""
When setting a timestamp, this gives the value to set it to.
"""


@dataclass
class DirectoryEntry:
    """
    A directory entry.
    """
    type: DescriptorType
    name: str

class ErrorCode(Enum):
    """
    Error codes returned by functions, similar to `errno` in POSIX.
    Not all of these error codes are returned by the functions provided by this
    API; some are used in higher-level library layers, and others are provided
    merely for alignment with POSIX.
    """
    ACCESS = 0
    WOULD_BLOCK = 1
    ALREADY = 2
    BAD_DESCRIPTOR = 3
    BUSY = 4
    DEADLOCK = 5
    QUOTA = 6
    EXIST = 7
    FILE_TOO_LARGE = 8
    ILLEGAL_BYTE_SEQUENCE = 9
    IN_PROGRESS = 10
    INTERRUPTED = 11
    INVALID = 12
    IO = 13
    IS_DIRECTORY = 14
    LOOP = 15
    TOO_MANY_LINKS = 16
    MESSAGE_SIZE = 17
    NAME_TOO_LONG = 18
    NO_DEVICE = 19
    NO_ENTRY = 20
    NO_LOCK = 21
    INSUFFICIENT_MEMORY = 22
    INSUFFICIENT_SPACE = 23
    NOT_DIRECTORY = 24
    NOT_EMPTY = 25
    NOT_RECOVERABLE = 26
    UNSUPPORTED = 27
    NO_TTY = 28
    NO_SUCH_DEVICE = 29
    OVERFLOW = 30
    NOT_PERMITTED = 31
    PIPE = 32
    READ_ONLY = 33
    INVALID_SEEK = 34
    TEXT_FILE_BUSY = 35
    CROSS_DEVICE = 36

class Advice(Enum):
    """
    File or memory access pattern advisory information.
    """
    NORMAL = 0
    SEQUENTIAL = 1
    RANDOM = 2
    WILL_NEED = 3
    DONT_NEED = 4
    NO_REUSE = 5

@dataclass
class MetadataHashValue:
    """
    A 128-bit hash value, split into parts because wasm doesn't have a
    128-bit integer type.
    """
    lower: int
    upper: int

class DirectoryEntryStream:
    """
    A stream of directory entries.
    """
    
    def read_directory_entry(self) -> Optional[DirectoryEntry]:
        """
        Read a single directory entry from a `directory-entry-stream`.
        
        Raises: `test.types.Err(test.imports.wasi_filesystem_types.ErrorCode)`
        """
        raise NotImplementedError
    def __enter__(self) -> Self:
        """Returns self"""
        return self
                                
    def __exit__(self, exc_type: type[BaseException] | None, exc_value: BaseException | None, traceback: TracebackType | None) -> bool | None:
        """
        Release this resource.
        """
        raise NotImplementedError


class Descriptor:
    """
    A descriptor is a reference to a filesystem object, which may be a file,
    directory, named pipe, special file, or other object on which filesystem
    calls may be made.
    """
    
    def read_via_stream(self, offset: int) -> streams.InputStream:
        """
        Return a stream for reading from a file, if available.
        
        May fail with an error-code describing why the file cannot be read.
        
        Multiple read, write, and append streams may be active on the same open
        file and they do not interfere with each other.
        
        Note: This allows using `read-stream`, which is similar to `read` in POSIX.
        
        Raises: `test.types.Err(test.imports.wasi_filesystem_types.ErrorCode)`
        """
        raise NotImplementedError
    def write_via_stream(self, offset: int) -> streams.OutputStream:
        """
        Return a stream for writing to a file, if available.
        
        May fail with an error-code describing why the file cannot be written.
        
        Note: This allows using `write-stream`, which is similar to `write` in
        POSIX.
        
        Raises: `test.types.Err(test.imports.wasi_filesystem_types.ErrorCode)`
        """
        raise NotImplementedError
    def append_via_stream(self) -> streams.OutputStream:
        """
        Return a stream for appending to a file, if available.
        
        May fail with an error-code describing why the file cannot be appended.
        
        Note: This allows using `write-stream`, which is similar to `write` with
        `O_APPEND` in in POSIX.
        
        Raises: `test.types.Err(test.imports.wasi_filesystem_types.ErrorCode)`
        """
        raise NotImplementedError
    def advise(self, offset: int, length: int, advice: Advice) -> None:
        """
        Provide file advisory information on a descriptor.
        
        This is similar to `posix_fadvise` in POSIX.
        
        Raises: `test.types.Err(test.imports.wasi_filesystem_types.ErrorCode)`
        """
        raise NotImplementedError
    def sync_data(self) -> None:
        """
        Synchronize the data of a file to disk.
        
        This function succeeds with no effect if the file descriptor is not
        opened for writing.
        
        Note: This is similar to `fdatasync` in POSIX.
        
        Raises: `test.types.Err(test.imports.wasi_filesystem_types.ErrorCode)`
        """
        raise NotImplementedError
    def get_flags(self) -> DescriptorFlags:
        """
        Get flags associated with a descriptor.
        
        Note: This returns similar flags to `fcntl(fd, F_GETFL)` in POSIX.
        
        Note: This returns the value that was the `fs_flags` value returned
        from `fdstat_get` in earlier versions of WASI.
        
        Raises: `test.types.Err(test.imports.wasi_filesystem_types.ErrorCode)`
        """
        raise NotImplementedError
    def get_type(self) -> DescriptorType:
        """
        Get the dynamic type of a descriptor.
        
        Note: This returns the same value as the `type` field of the `fd-stat`
        returned by `stat`, `stat-at` and similar.
        
        Note: This returns similar flags to the `st_mode & S_IFMT` value provided
        by `fstat` in POSIX.
        
        Note: This returns the value that was the `fs_filetype` value returned
        from `fdstat_get` in earlier versions of WASI.
        
        Raises: `test.types.Err(test.imports.wasi_filesystem_types.ErrorCode)`
        """
        raise NotImplementedError
    def set_size(self, size: int) -> None:
        """
        Adjust the size of an open file. If this increases the file's size, the
        extra bytes are filled with zeros.
        
        Note: This was called `fd_filestat_set_size` in earlier versions of WASI.
        
        Raises: `test.types.Err(test.imports.wasi_filesystem_types.ErrorCode)`
        """
        raise NotImplementedError
    def set_times(self, data_access_timestamp: NewTimestamp, data_modification_timestamp: NewTimestamp) -> None:
        """
        Adjust the timestamps of an open file or directory.
        
        Note: This is similar to `futimens` in POSIX.
        
        Note: This was called `fd_filestat_set_times` in earlier versions of WASI.
        
        Raises: `test.types.Err(test.imports.wasi_filesystem_types.ErrorCode)`
        """
        raise NotImplementedError
    def read(self, length: int, offset: int) -> Tuple[bytes, bool]:
        """
        Read from a descriptor, without using and updating the descriptor's offset.
        
        This function returns a list of bytes containing the data that was
        read, along with a bool which, when true, indicates that the end of the
        file was reached. The returned list will contain up to `length` bytes; it
        may return fewer than requested, if the end of the file is reached or
        if the I/O operation is interrupted.
        
        In the future, this may change to return a `stream<u8, error-code>`.
        
        Note: This is similar to `pread` in POSIX.
        
        Raises: `test.types.Err(test.imports.wasi_filesystem_types.ErrorCode)`
        """
        raise NotImplementedError
    def write(self, buffer: bytes, offset: int) -> int:
        """
        Write to a descriptor, without using and updating the descriptor's offset.
        
        It is valid to write past the end of a file; the file is extended to the
        extent of the write, with bytes between the previous end and the start of
        the write set to zero.
        
        In the future, this may change to take a `stream<u8, error-code>`.
        
        Note: This is similar to `pwrite` in POSIX.
        
        Raises: `test.types.Err(test.imports.wasi_filesystem_types.ErrorCode)`
        """
        raise NotImplementedError
    def read_directory(self) -> DirectoryEntryStream:
        """
        Read directory entries from a directory.
        
        On filesystems where directories contain entries referring to themselves
        and their parents, often named `.` and `..` respectively, these entries
        are omitted.
        
        This always returns a new stream which starts at the beginning of the
        directory. Multiple streams may be active on the same directory, and they
        do not interfere with each other.
        
        Raises: `test.types.Err(test.imports.wasi_filesystem_types.ErrorCode)`
        """
        raise NotImplementedError
    def sync(self) -> None:
        """
        Synchronize the data and metadata of a file to disk.
        
        This function succeeds with no effect if the file descriptor is not
        opened for writing.
        
        Note: This is similar to `fsync` in POSIX.
        
        Raises: `test.types.Err(test.imports.wasi_filesystem_types.ErrorCode)`
        """
        raise NotImplementedError
    def create_directory_at(self, path: str) -> None:
        """
        Create a directory.
        
        Note: This is similar to `mkdirat` in POSIX.
        
        Raises: `test.types.Err(test.imports.wasi_filesystem_types.ErrorCode)`
        """
        raise NotImplementedError
    def stat(self) -> DescriptorStat:
        """
        Return the attributes of an open file or directory.
        
        Note: This is similar to `fstat` in POSIX, except that it does not return
        device and inode information. For testing whether two descriptors refer to
        the same underlying filesystem object, use `is-same-object`. To obtain
        additional data that can be used do determine whether a file has been
        modified, use `metadata-hash`.
        
        Note: This was called `fd_filestat_get` in earlier versions of WASI.
        
        Raises: `test.types.Err(test.imports.wasi_filesystem_types.ErrorCode)`
        """
        raise NotImplementedError
    def stat_at(self, path_flags: PathFlags, path: str) -> DescriptorStat:
        """
        Return the attributes of a file or directory.
        
        Note: This is similar to `fstatat` in POSIX, except that it does not
        return device and inode information. See the `stat` description for a
        discussion of alternatives.
        
        Note: This was called `path_filestat_get` in earlier versions of WASI.
        
        Raises: `test.types.Err(test.imports.wasi_filesystem_types.ErrorCode)`
        """
        raise NotImplementedError
    def set_times_at(self, path_flags: PathFlags, path: str, data_access_timestamp: NewTimestamp, data_modification_timestamp: NewTimestamp) -> None:
        """
        Adjust the timestamps of a file or directory.
        
        Note: This is similar to `utimensat` in POSIX.
        
        Note: This was called `path_filestat_set_times` in earlier versions of
        WASI.
        
        Raises: `test.types.Err(test.imports.wasi_filesystem_types.ErrorCode)`
        """
        raise NotImplementedError
    def link_at(self, old_path_flags: PathFlags, old_path: str, new_descriptor: Self, new_path: str) -> None:
        """
        Create a hard link.
        
        Note: This is similar to `linkat` in POSIX.
        
        Raises: `test.types.Err(test.imports.wasi_filesystem_types.ErrorCode)`
        """
        raise NotImplementedError
    def open_at(self, path_flags: PathFlags, path: str, open_flags: OpenFlags, flags: DescriptorFlags) -> Self:
        """
        Open a file or directory.
        
        The returned descriptor is not guaranteed to be the lowest-numbered
        descriptor not currently open/ it is randomized to prevent applications
        from depending on making assumptions about indexes, since this is
        error-prone in multi-threaded contexts. The returned descriptor is
        guaranteed to be less than 2**31.
        
        If `flags` contains `descriptor-flags::mutate-directory`, and the base
        descriptor doesn't have `descriptor-flags::mutate-directory` set,
        `open-at` fails with `error-code::read-only`.
        
        If `flags` contains `write` or `mutate-directory`, or `open-flags`
        contains `truncate` or `create`, and the base descriptor doesn't have
        `descriptor-flags::mutate-directory` set, `open-at` fails with
        `error-code::read-only`.
        
        Note: This is similar to `openat` in POSIX.
        
        Raises: `test.types.Err(test.imports.wasi_filesystem_types.ErrorCode)`
        """
        raise NotImplementedError
    def readlink_at(self, path: str) -> str:
        """
        Read the contents of a symbolic link.
        
        If the contents contain an absolute or rooted path in the underlying
        filesystem, this function fails with `error-code::not-permitted`.
        
        Note: This is similar to `readlinkat` in POSIX.
        
        Raises: `test.types.Err(test.imports.wasi_filesystem_types.ErrorCode)`
        """
        raise NotImplementedError
    def remove_directory_at(self, path: str) -> None:
        """
        Remove a directory.
        
        Return `error-code::not-empty` if the directory is not empty.
        
        Note: This is similar to `unlinkat(fd, path, AT_REMOVEDIR)` in POSIX.
        
        Raises: `test.types.Err(test.imports.wasi_filesystem_types.ErrorCode)`
        """
        raise NotImplementedError
    def rename_at(self, old_path: str, new_descriptor: Self, new_path: str) -> None:
        """
        Rename a filesystem object.
        
        Note: This is similar to `renameat` in POSIX.
        
        Raises: `test.types.Err(test.imports.wasi_filesystem_types.ErrorCode)`
        """
        raise NotImplementedError
    def symlink_at(self, old_path: str, new_path: str) -> None:
        """
        Create a symbolic link (also known as a "symlink").
        
        If `old-path` starts with `/`, the function fails with
        `error-code::not-permitted`.
        
        Note: This is similar to `symlinkat` in POSIX.
        
        Raises: `test.types.Err(test.imports.wasi_filesystem_types.ErrorCode)`
        """
        raise NotImplementedError
    def unlink_file_at(self, path: str) -> None:
        """
        Unlink a filesystem object that is not a directory.
        
        Return `error-code::is-directory` if the path refers to a directory.
        Note: This is similar to `unlinkat(fd, path, 0)` in POSIX.
        
        Raises: `test.types.Err(test.imports.wasi_filesystem_types.ErrorCode)`
        """
        raise NotImplementedError
    def is_same_object(self, other: Self) -> bool:
        """
        Test whether two descriptors refer to the same filesystem object.
        
        In POSIX, this corresponds to testing whether the two descriptors have the
        same device (`st_dev`) and inode (`st_ino` or `d_ino`) numbers.
        wasi-filesystem does not expose device and inode numbers, so this function
        may be used instead.
        """
        raise NotImplementedError
    def metadata_hash(self) -> MetadataHashValue:
        """
        Return a hash of the metadata associated with a filesystem object referred
        to by a descriptor.
        
        This returns a hash of the last-modification timestamp and file size, and
        may also include the inode number, device number, birth timestamp, and
        other metadata fields that may change when the file is modified or
        replaced. It may also include a secret value chosen by the
        implementation and not otherwise exposed.
        
        Implementations are encourated to provide the following properties:
        
         - If the file is not modified or replaced, the computed hash value should
           usually not change.
         - If the object is modified or replaced, the computed hash value should
           usually change.
         - The inputs to the hash should not be easily computable from the
           computed hash.
        
        However, none of these is required.
        
        Raises: `test.types.Err(test.imports.wasi_filesystem_types.ErrorCode)`
        """
        raise NotImplementedError
    def metadata_hash_at(self, path_flags: PathFlags, path: str) -> MetadataHashValue:
        """
        Return a hash of the metadata associated with a filesystem object referred
        to by a directory descriptor and a relative path.
        
        This performs the same hash computation as `metadata-hash`.
        
        Raises: `test.types.Err(test.imports.wasi_filesystem_types.ErrorCode)`
        """
        raise NotImplementedError
    def __enter__(self) -> Self:
        """Returns self"""
        return self
                                
    def __exit__(self, exc_type: type[BaseException] | None, exc_value: BaseException | None, traceback: TracebackType | None) -> bool | None:
        """
        Release this resource.
        """
        raise NotImplementedError



def filesystem_error_code(err: error.Error) -> Optional[ErrorCode]:
    """
    Attempts to extract a filesystem-related `error-code` from the stream
    `error` provided.
    
    Stream operations which return `stream-error::last-operation-failed`
    have a payload with more information about the operation that failed.
    This payload can be passed through to this function to see if there's
    filesystem-related information about the error to return.
    
    Note that this function is fallible because not all stream-related
    errors are filesystem-related errors.
    """
    raise NotImplementedError

