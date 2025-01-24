from utils.socketwrapper import SocketWrapper

class RTCMReader:
    def __init__(self,datastream:SocketWrapper):
        self._parsed=False
        self._stream = datastream
        pass

    def read(self):
        parsing = True

        while parsing:  # loop until end of valid message or EOF
            try:
                raw_data = None
                byte1 = self._read_bytes(1)  # read the first byte
                byte2 = self._read_bytes(1)
                bytehdr = byte1 + byte2
                # if it's a UBX message (b'\xb5\x62'), ignore it
                if byte1 == b"\xd3" and (byte2[0] & ~0x03) == 0:
                    raw_data = self._parse_rtcm3(bytehdr)
                    parsing = False
            except EOFError:
                return None
        return raw_data
    
    def _parse_rtcm3(self, hdr: bytes):
        """
        Parse any RTCM3 data in the stream.

        :param bytes hdr: first 2 bytes of RTCM3 header
        :return: tuple of (raw_data as bytes, parsed_stub as RTCMMessage)
        :rtype: tuple
        """

        hdr3 = self._read_bytes(1)
        size = (hdr[1] << 8) | hdr3[0]
        payload = self._read_bytes(size)
        crc = self._read_bytes(3)
        raw_data = hdr + hdr3 + payload + crc
        if self.calc_crc24q(raw_data):
            print("CRC error")
            return None
        return raw_data
    
    def calc_crc24q(self,message: bytes) -> int:
        """
        Perform CRC24Q cyclic redundancy check.

        If the message includes the appended CRC bytes, the
        function will return 0 if the message is valid.
        If the message excludes the appended CRC bytes, the
        function will return the applicable CRC.

        :param bytes message: message
        :return: CRC or 0
        :rtype: int

        """

        poly = 0x1864CFB
        crc = 0
        for octet in message:
            crc ^= octet << 16
            for _ in range(8):
                crc <<= 1
                if crc & 0x1000000:
                    crc ^= poly
        return crc & 0xFFFFFF
    
    def _read_bytes(self, size: int) -> bytes:
        """
        Read a specified number of bytes from stream.

        :param int size: number of bytes to read
        :return: bytes
        :rtype: bytes
        :raises: UBXStreamError if stream ends prematurely
        """

        data = self._stream.read(size)
        if len(data) == 0:  # EOF
            raise EOFError()
        if 0 < len(data) < size:  # truncated stream
            print(
                "Serial stream terminated unexpectedly. "+
                f"{size} bytes requested, {len(data)} bytes returned."
            )
        return data


