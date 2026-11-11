#!/usr/bin/env python3
"""Telnet Connection Tester for Hargassner Boilers.

Tests telnet connection to a Hargassner boiler and displays real-time messages.

Usage:
    python telnet_tester.py <host> [--port <port>] [--timeout <seconds>] [--count <n>]

Examples:
    python telnet_tester.py 192.168.1.100
    python telnet_tester.py 192.168.1.100 --count 10
    python telnet_tester.py 192.168.1.100 --timeout 5
"""

import argparse
import socket
import sys
import time
from datetime import datetime
from typing import Optional


class TelnetTester:
    """Test telnet connection to Hargassner boiler."""

    def __init__(
        self,
        host: str,
        port: int = 23,
        timeout: float = 10.0,
        truncate: int = 0,
        log_path: Optional[str] = None,
    ):
        """Initialize tester.

        Args:
            host: Boiler IP address or hostname
            port: Telnet port (default: 23)
            timeout: Connection timeout in seconds
            truncate: Shorten displayed messages to this many characters (0 = full)
            log_path: Append every pm message with a timestamp to this file
        """
        self.truncate = truncate
        self.log_path = log_path
        self.host = host
        self.port = port
        self.timeout = timeout
        self.socket: Optional[socket.socket] = None
        self.message_count = 0
        self.pm_message_count = 0
        self.bytes_received = 0
        self._buffer = b""

    def connect(self) -> bool:
        """Connect to boiler.

        Returns:
            True if connected successfully
        """
        try:
            print(f"Connecting to {self.host}:{self.port}...")
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(self.timeout)
            self.socket.connect((self.host, self.port))
            print(f"✅ Connected to {self.host}:{self.port}")
            return True
        except ConnectionRefusedError:
            print(f"❌ Connection refused by {self.host}:{self.port}")
            print("   → Check if telnet is enabled on the boiler")
            return False
        except socket.timeout:
            print(f"❌ Connection timeout to {self.host}:{self.port}")
            print("   → Check network connectivity and firewall settings")
            return False
        except Exception as e:
            print(f"❌ Connection error: {e}")
            return False

    def _decode_data(self, data: bytes) -> str:
        """Try to decode data with multiple encodings.

        Args:
            data: Bytes to decode

        Returns:
            Decoded string
        """
        # Try multiple encodings
        for encoding in ["utf-8", "latin-1", "cp1252"]:
            try:
                return data.decode(encoding)
            except UnicodeDecodeError:
                continue

        # Fallback with error replacement
        return data.decode("utf-8", errors="replace")

    def read_messages(self, count: Optional[int] = None, duration: Optional[float] = None):
        """Read and display messages from boiler.

        Args:
            count: Number of messages to read (None for unlimited)
            duration: Duration to read in seconds (None for unlimited)
        """
        if not self.socket:
            print("❌ Not connected")
            return

        print(f"\n{'='*70}")
        print("RECEIVING MESSAGES")
        print(f"{'='*70}")
        print("Press Ctrl+C to stop\n")

        start_time = time.time()
        self.socket.settimeout(2.0)  # Set timeout for recv

        try:
            while True:
                # Check if we should stop
                if count and self.pm_message_count >= count:
                    break
                if duration and (time.time() - start_time) >= duration:
                    break

                # Read data with timeout
                try:
                    data = self.socket.recv(4096)
                except socket.timeout:
                    continue
                except Exception:
                    print("\n❌ Connection closed by remote host")
                    break

                if not data:
                    print("\n❌ Connection closed by remote host")
                    break

                self.bytes_received += len(data)
                self._buffer += data

                # Process complete lines
                while b"\n" in self._buffer:
                    line, self._buffer = self._buffer.split(b"\n", 1)

                    # Decode the line
                    text = self._decode_data(line).strip()

                    if text:
                        self.message_count += 1
                        timestamp = datetime.now().strftime("%H:%M:%S")

                        # Check if it's a pm message
                        is_pm = text.startswith("pm ")
                        if is_pm:
                            self.pm_message_count += 1

                            # Parse pm message
                            parts = text.split()
                            value_count = len(parts) - 1  # Subtract 'pm' prefix

                            # Full message by default - the values that matter
                            # are often at the end of the line
                            display_text = text
                            if self.truncate and len(text) > self.truncate:
                                display_text = text[: self.truncate] + "..."

                            if self.log_path:
                                stamp = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
                                with open(self.log_path, "a", encoding="utf-8") as log:
                                    log.write(f"{stamp} {text}\n")

                            print(f"[{timestamp}] PM Message #{self.pm_message_count} ({value_count} values)")
                            print(f"  {display_text}")
                        else:
                            print(f"[{timestamp}] Other: {text}")

        except KeyboardInterrupt:
            print("\n\n⚠️  Interrupted by user")

        finally:
            # Print statistics
            elapsed = time.time() - start_time
            print(f"\n{'='*70}")
            print("STATISTICS")
            print(f"{'='*70}")
            print(f"Duration:           {elapsed:.1f} seconds")
            print(f"Total Messages:     {self.message_count}")
            print(f"PM Messages:        {self.pm_message_count}")
            print(f"Bytes Received:     {self.bytes_received:,}")
            if elapsed > 0:
                print(f"Messages/sec:       {self.message_count / elapsed:.2f}")
                print(f"Bytes/sec:          {self.bytes_received / elapsed:.0f}")

    def disconnect(self):
        """Disconnect from boiler."""
        if self.socket:
            try:
                self.socket.close()
                print("\n✅ Disconnected")
            except Exception:
                pass


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Test telnet connection to Hargassner boiler",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python telnet_tester.py 192.168.1.100
  python telnet_tester.py 192.168.1.100 --count 10
  python telnet_tester.py 192.168.1.100 --duration 30
  python telnet_tester.py 192.168.1.100 --timeout 5 --count 20
  python telnet_tester.py 192.168.1.100 --duration 3600 --log capture.txt
        """,
    )

    parser.add_argument("host", help="Boiler IP address or hostname")
    parser.add_argument(
        "--port", "-p", type=int, default=23, help="Telnet port (default: 23)"
    )
    parser.add_argument(
        "--timeout",
        "-t",
        type=float,
        default=10.0,
        help="Connection timeout in seconds (default: 10)",
    )
    parser.add_argument(
        "--count",
        "-c",
        type=int,
        help="Number of PM messages to receive before stopping",
    )
    parser.add_argument(
        "--duration",
        "-d",
        type=float,
        help="Duration to run in seconds before stopping",
    )

    parser.add_argument(
        "--truncate",
        type=int,
        default=0,
        help="Shorten displayed messages to N characters (default: 0 = show full message)",
    )
    parser.add_argument(
        "--log",
        metavar="FILE",
        help="Append every pm message with a timestamp to FILE (same line format as DAQ files)",
    )

    args = parser.parse_args()

    # Create tester
    tester = TelnetTester(args.host, args.port, args.timeout, args.truncate, args.log)

    # Connect
    if not tester.connect():
        sys.exit(1)

    try:
        # Read messages
        tester.read_messages(count=args.count, duration=args.duration)
    finally:
        # Disconnect
        tester.disconnect()


if __name__ == "__main__":
    main()
