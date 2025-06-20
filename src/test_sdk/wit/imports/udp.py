from typing import TypeVar, Generic, Union, Optional, Protocol, Tuple, List, Any, Self
from types import TracebackType
from enum import Flag, Enum, auto
from dataclasses import dataclass
from abc import abstractmethod
import weakref

from ..types import Result, Ok, Err, Some
from ..imports import poll
from ..imports import network

@dataclass
class IncomingDatagram:
    """
    A received datagram.
    """
    data: bytes
    remote_address: network.IpSocketAddress

@dataclass
class OutgoingDatagram:
    """
    A datagram to be sent out.
    """
    data: bytes
    remote_address: Optional[network.IpSocketAddress]

class IncomingDatagramStream:
    
    def receive(self, max_results: int) -> List[IncomingDatagram]:
        """
        Receive messages on the socket.
        
        This function attempts to receive up to `max-results` datagrams on the socket without blocking.
        The returned list may contain fewer elements than requested, but never more.
        
        This function returns successfully with an empty list when either:
        - `max-results` is 0, or:
        - `max-results` is greater than 0, but no results are immediately available.
        This function never returns `error(would-block)`.
        
        # Typical errors
        - `remote-unreachable`: The remote address is not reachable. (ECONNRESET, ENETRESET on Windows, EHOSTUNREACH, EHOSTDOWN, ENETUNREACH, ENETDOWN, ENONET)
        - `connection-refused`: The connection was refused. (ECONNREFUSED)
        
        # References
        - <https://pubs.opengroup.org/onlinepubs/9699919799/functions/recvfrom.html>
        - <https://pubs.opengroup.org/onlinepubs/9699919799/functions/recvmsg.html>
        - <https://man7.org/linux/man-pages/man2/recv.2.html>
        - <https://man7.org/linux/man-pages/man2/recvmmsg.2.html>
        - <https://learn.microsoft.com/en-us/windows/win32/api/winsock/nf-winsock-recv>
        - <https://learn.microsoft.com/en-us/windows/win32/api/winsock/nf-winsock-recvfrom>
        - <https://learn.microsoft.com/en-us/previous-versions/windows/desktop/legacy/ms741687(v=vs.85)>
        - <https://man.freebsd.org/cgi/man.cgi?query=recv&sektion=2>
        
        Raises: `test.types.Err(test.imports.network.ErrorCode)`
        """
        raise NotImplementedError
    def subscribe(self) -> poll.Pollable:
        """
        Create a `pollable` which will resolve once the stream is ready to receive again.
        
        Note: this function is here for WASI Preview2 only.
        It's planned to be removed when `future` is natively supported in Preview3.
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


class OutgoingDatagramStream:
    
    def check_send(self) -> int:
        """
        Check readiness for sending. This function never blocks.
        
        Returns the number of datagrams permitted for the next call to `send`,
        or an error. Calling `send` with more datagrams than this function has
        permitted will trap.
        
        When this function returns ok(0), the `subscribe` pollable will
        become ready when this function will report at least ok(1), or an
        error.
        
        Never returns `would-block`.
        
        Raises: `test.types.Err(test.imports.network.ErrorCode)`
        """
        raise NotImplementedError
    def send(self, datagrams: List[OutgoingDatagram]) -> int:
        """
        Send messages on the socket.
        
        This function attempts to send all provided `datagrams` on the socket without blocking and
        returns how many messages were actually sent (or queued for sending). This function never
        returns `error(would-block)`. If none of the datagrams were able to be sent, `ok(0)` is returned.
        
        This function semantically behaves the same as iterating the `datagrams` list and sequentially
        sending each individual datagram until either the end of the list has been reached or the first error occurred.
        If at least one datagram has been sent successfully, this function never returns an error.
        
        If the input list is empty, the function returns `ok(0)`.
        
        Each call to `send` must be permitted by a preceding `check-send`. Implementations must trap if
        either `check-send` was not called or `datagrams` contains more items than `check-send` permitted.
        
        # Typical errors
        - `invalid-argument`:        The `remote-address` has the wrong address family. (EAFNOSUPPORT)
        - `invalid-argument`:        The IP address in `remote-address` is set to INADDR_ANY (`0.0.0.0` / `::`). (EDESTADDRREQ, EADDRNOTAVAIL)
        - `invalid-argument`:        The port in `remote-address` is set to 0. (EDESTADDRREQ, EADDRNOTAVAIL)
        - `invalid-argument`:        The socket is in "connected" mode and `remote-address` is `some` value that does not match the address passed to `stream`. (EISCONN)
        - `invalid-argument`:        The socket is not "connected" and no value for `remote-address` was provided. (EDESTADDRREQ)
        - `remote-unreachable`:      The remote address is not reachable. (ECONNRESET, ENETRESET on Windows, EHOSTUNREACH, EHOSTDOWN, ENETUNREACH, ENETDOWN, ENONET)
        - `connection-refused`:      The connection was refused. (ECONNREFUSED)
        - `datagram-too-large`:      The datagram is too large. (EMSGSIZE)
        
        # References
        - <https://pubs.opengroup.org/onlinepubs/9699919799/functions/sendto.html>
        - <https://pubs.opengroup.org/onlinepubs/9699919799/functions/sendmsg.html>
        - <https://man7.org/linux/man-pages/man2/send.2.html>
        - <https://man7.org/linux/man-pages/man2/sendmmsg.2.html>
        - <https://learn.microsoft.com/en-us/windows/win32/api/winsock2/nf-winsock2-send>
        - <https://learn.microsoft.com/en-us/windows/win32/api/winsock2/nf-winsock2-sendto>
        - <https://learn.microsoft.com/en-us/windows/win32/api/winsock2/nf-winsock2-wsasendmsg>
        - <https://man.freebsd.org/cgi/man.cgi?query=send&sektion=2>
        
        Raises: `test.types.Err(test.imports.network.ErrorCode)`
        """
        raise NotImplementedError
    def subscribe(self) -> poll.Pollable:
        """
        Create a `pollable` which will resolve once the stream is ready to send again.
        
        Note: this function is here for WASI Preview2 only.
        It's planned to be removed when `future` is natively supported in Preview3.
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


class UdpSocket:
    """
    A UDP socket handle.
    """
    
    def start_bind(self, network: network.Network, local_address: network.IpSocketAddress) -> None:
        """
        Bind the socket to a specific network on the provided IP address and port.
        
        If the IP address is zero (`0.0.0.0` in IPv4, `::` in IPv6), it is left to the implementation to decide which
        network interface(s) to bind to.
        If the port is zero, the socket will be bound to a random free port.
        
        # Typical errors
        - `invalid-argument`:          The `local-address` has the wrong address family. (EAFNOSUPPORT, EFAULT on Windows)
        - `invalid-state`:             The socket is already bound. (EINVAL)
        - `address-in-use`:            No ephemeral ports available. (EADDRINUSE, ENOBUFS on Windows)
        - `address-in-use`:            Address is already in use. (EADDRINUSE)
        - `address-not-bindable`:      `local-address` is not an address that the `network` can bind to. (EADDRNOTAVAIL)
        - `not-in-progress`:           A `bind` operation is not in progress.
        - `would-block`:               Can't finish the operation, it is still in progress. (EWOULDBLOCK, EAGAIN)
        
        # Implementors note
        Unlike in POSIX, in WASI the bind operation is async. This enables
        interactive WASI hosts to inject permission prompts. Runtimes that
        don't want to make use of this ability can simply call the native
        `bind` as part of either `start-bind` or `finish-bind`.
        
        # References
        - <https://pubs.opengroup.org/onlinepubs/9699919799/functions/bind.html>
        - <https://man7.org/linux/man-pages/man2/bind.2.html>
        - <https://learn.microsoft.com/en-us/windows/win32/api/winsock/nf-winsock-bind>
        - <https://man.freebsd.org/cgi/man.cgi?query=bind&sektion=2&format=html>
        
        Raises: `test.types.Err(test.imports.network.ErrorCode)`
        """
        raise NotImplementedError
    def finish_bind(self) -> None:
        """
        Raises: `test.types.Err(test.imports.network.ErrorCode)`
        """
        raise NotImplementedError
    def stream(self, remote_address: Optional[network.IpSocketAddress]) -> Tuple[IncomingDatagramStream, OutgoingDatagramStream]:
        """
        Set up inbound & outbound communication channels, optionally to a specific peer.
        
        This function only changes the local socket configuration and does not generate any network traffic.
        On success, the `remote-address` of the socket is updated. The `local-address` may be updated as well,
        based on the best network path to `remote-address`.
        
        When a `remote-address` is provided, the returned streams are limited to communicating with that specific peer:
        - `send` can only be used to send to this destination.
        - `receive` will only return datagrams sent from the provided `remote-address`.
        
        This method may be called multiple times on the same socket to change its association, but
        only the most recently returned pair of streams will be operational. Implementations may trap if
        the streams returned by a previous invocation haven't been dropped yet before calling `stream` again.
        
        The POSIX equivalent in pseudo-code is:
        ```text
        if (was previously connected) {
        	connect(s, AF_UNSPEC)
        }
        if (remote_address is Some) {
        	connect(s, remote_address)
        }
        ```
        
        Unlike in POSIX, the socket must already be explicitly bound.
        
        # Typical errors
        - `invalid-argument`:          The `remote-address` has the wrong address family. (EAFNOSUPPORT)
        - `invalid-argument`:          The IP address in `remote-address` is set to INADDR_ANY (`0.0.0.0` / `::`). (EDESTADDRREQ, EADDRNOTAVAIL)
        - `invalid-argument`:          The port in `remote-address` is set to 0. (EDESTADDRREQ, EADDRNOTAVAIL)
        - `invalid-state`:             The socket is not bound.
        - `address-in-use`:            Tried to perform an implicit bind, but there were no ephemeral ports available. (EADDRINUSE, EADDRNOTAVAIL on Linux, EAGAIN on BSD)
        - `remote-unreachable`:        The remote address is not reachable. (ECONNRESET, ENETRESET, EHOSTUNREACH, EHOSTDOWN, ENETUNREACH, ENETDOWN, ENONET)
        - `connection-refused`:        The connection was refused. (ECONNREFUSED)
        
        # References
        - <https://pubs.opengroup.org/onlinepubs/9699919799/functions/connect.html>
        - <https://man7.org/linux/man-pages/man2/connect.2.html>
        - <https://learn.microsoft.com/en-us/windows/win32/api/winsock2/nf-winsock2-connect>
        - <https://man.freebsd.org/cgi/man.cgi?connect>
        
        Raises: `test.types.Err(test.imports.network.ErrorCode)`
        """
        raise NotImplementedError
    def local_address(self) -> network.IpSocketAddress:
        """
        Get the current bound address.
        
        POSIX mentions:
        > If the socket has not been bound to a local name, the value
        > stored in the object pointed to by `address` is unspecified.
        
        WASI is stricter and requires `local-address` to return `invalid-state` when the socket hasn't been bound yet.
        
        # Typical errors
        - `invalid-state`: The socket is not bound to any local address.
        
        # References
        - <https://pubs.opengroup.org/onlinepubs/9699919799/functions/getsockname.html>
        - <https://man7.org/linux/man-pages/man2/getsockname.2.html>
        - <https://learn.microsoft.com/en-us/windows/win32/api/winsock/nf-winsock-getsockname>
        - <https://man.freebsd.org/cgi/man.cgi?getsockname>
        
        Raises: `test.types.Err(test.imports.network.ErrorCode)`
        """
        raise NotImplementedError
    def remote_address(self) -> network.IpSocketAddress:
        """
        Get the address the socket is currently streaming to.
        
        # Typical errors
        - `invalid-state`: The socket is not streaming to a specific remote address. (ENOTCONN)
        
        # References
        - <https://pubs.opengroup.org/onlinepubs/9699919799/functions/getpeername.html>
        - <https://man7.org/linux/man-pages/man2/getpeername.2.html>
        - <https://learn.microsoft.com/en-us/windows/win32/api/winsock/nf-winsock-getpeername>
        - <https://man.freebsd.org/cgi/man.cgi?query=getpeername&sektion=2&n=1>
        
        Raises: `test.types.Err(test.imports.network.ErrorCode)`
        """
        raise NotImplementedError
    def address_family(self) -> network.IpAddressFamily:
        """
        Whether this is a IPv4 or IPv6 socket.
        
        Equivalent to the SO_DOMAIN socket option.
        """
        raise NotImplementedError
    def unicast_hop_limit(self) -> int:
        """
        Equivalent to the IP_TTL & IPV6_UNICAST_HOPS socket options.
        
        If the provided value is 0, an `invalid-argument` error is returned.
        
        # Typical errors
        - `invalid-argument`:     (set) The TTL value must be 1 or higher.
        
        Raises: `test.types.Err(test.imports.network.ErrorCode)`
        """
        raise NotImplementedError
    def set_unicast_hop_limit(self, value: int) -> None:
        """
        Raises: `test.types.Err(test.imports.network.ErrorCode)`
        """
        raise NotImplementedError
    def receive_buffer_size(self) -> int:
        """
        The kernel buffer space reserved for sends/receives on this socket.
        
        If the provided value is 0, an `invalid-argument` error is returned.
        Any other value will never cause an error, but it might be silently clamped and/or rounded.
        I.e. after setting a value, reading the same setting back may return a different value.
        
        Equivalent to the SO_RCVBUF and SO_SNDBUF socket options.
        
        # Typical errors
        - `invalid-argument`:     (set) The provided value was 0.
        
        Raises: `test.types.Err(test.imports.network.ErrorCode)`
        """
        raise NotImplementedError
    def set_receive_buffer_size(self, value: int) -> None:
        """
        Raises: `test.types.Err(test.imports.network.ErrorCode)`
        """
        raise NotImplementedError
    def send_buffer_size(self) -> int:
        """
        Raises: `test.types.Err(test.imports.network.ErrorCode)`
        """
        raise NotImplementedError
    def set_send_buffer_size(self, value: int) -> None:
        """
        Raises: `test.types.Err(test.imports.network.ErrorCode)`
        """
        raise NotImplementedError
    def subscribe(self) -> poll.Pollable:
        """
        Create a `pollable` which will resolve once the socket is ready for I/O.
        
        Note: this function is here for WASI Preview2 only.
        It's planned to be removed when `future` is natively supported in Preview3.
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



