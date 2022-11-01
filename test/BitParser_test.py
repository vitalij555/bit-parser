import pytest
from unittest.mock import Mock
import sys

# insert at 1, 0 is the script path (or '' in REPL)
if not '../bit-parser' in sys.path:
    sys.path.insert(1, '../bit-parser')

from BitParser.BitParser import MultiBitValueParser, parseBits, SameValueRange


@pytest.fixture(scope="class")  # scope="function" is default
def simple_one_byte_parser():
    """ One byte protocol parser:
    Bit 7: I/O pin Nr7 high level
    Bit 6: I/O pin Nr6 high level
    Bit 5: I/O pin Nr5 high level
    Bit 4: I/O pin Nr4 high level
    Bit 3: I/O pin Nr3 high level
    Bit 2: I/O pin Nr2 high level
    Bit 1: I/O pin Nr1 high level
    Bit 0: I/O pin Nr0 high level
    """

    simple_one_byte_protocol_bit_descriptions = [ "I/O pin Nr7 high level",
                                                  "I/O pin Nr6 high level",
                                                  "I/O pin Nr5 high level",
                                                  "I/O pin Nr4 high level",
                                                  "I/O pin Nr3 high level",
                                                  "I/O pin Nr2 high level",
                                                  "I/O pin Nr1 high level",
                                                  "I/O pin Nr0 high level"]

    def one_byte_parser(bytes_to_parse):
        return parseBits(bytes_to_parse, simple_one_byte_protocol_bit_descriptions)
    return one_byte_parser


@pytest.fixture(scope="class")  # scope="function" is default
def simple_three_byte_parser():
    three_byte_protocol = [
                            # Byte 0:
                             "led Nr 1 on",         # bit 7: 10000000
                             "led Nr 2 on",         # bit 6: 01000000
                             "led Nr 3 on",         # bit 5: 00100000
                             "led Nr 4 on",         # bit 4: 00010000
                             "led Nr 5 on",         # bit 3: 00001000
                             "led Nr 6 on",         # bit 2: 00000100
                             "led Nr 7 on",         # bit 1: 00000010
                             "led Nr 8 on",         # bit 0: 00000001
                            # Byte 1:
                             "front door opened",   # bit 7: 10000000
                             "back door opened",    # bit 6: 01000000
                             "zone 1 alarm",        # bit 5: 00100000
                             "zone 2 alarm",        # bit 4: 00010000
                             "zone 3 alarm",        # bit 3: 00001000
                             "zone 4 alarm",        # bit 2: 00000100
                             "zone 5 alarm",        # bit 1: 00000010
                             "zone 6 alarm",        # bit 0: 00000001
                            # Byte 2:
                             "zone 7 alarm",        # bit 7: 10000000
                             "zone 1 fire",         # bit 6: 01000000
                             "zone 2 fire",         # bit 5: 00100000
                             "zone 3 fire",         # bit 4: 00010000
                             "zone 4 fire",         # bit 3: 00001000
                             "zone 5 fire",         # bit 2: 00000100
                             "flood sensor active", # bit 1: 00000010
                             "flood sensor active"  # bit 0: 00000001
    ]
    def three_byte_simple_parser(bytes_to_parse):
        return parseBits(bytes_to_parse, three_byte_protocol)
    return three_byte_simple_parser


@pytest.fixture(scope="class")  # scope="function" is default
def multibyte_protocol_with_counter():
    """
    # Byte 0:
     "front door opened",   # bit 7: 10000000
     "back door opened",    # bit 6: 01000000
     "zone 1 alarm",        # bit 5: 00100000
     "zone 2 alarm",        # bit 4: 00010000
     "zone 3 alarm",        # bit 3: 00001000
     "zone 4 alarm",        # bit 2: 00000100
     "zone 5 alarm",        # bit 1: 00000010
     "zone 6 alarm",        # bit 0: 00000001
    # Byte 1:
     "zone 7 alarm",        # bit 7: 10000000
     "zone 1 fire",         # bit 6: 01000000
     "zone 2 fire",         # bit 5: 00100000
     "zone 3 fire",         # bit 4: 00010000
     "zone 4 fire",         # bit 3: 00001000
     "zone 5 fire",         # bit 2: 00000100
     "flood sensor 1 alarm",  # bit 1: 00000010
     "flood sensor 2 alarm",  # bit 0: 00000001
    # Byte 2:
     "RFU",                 # bit 7: 10000000
     "RFU",                 # bit 6: 01000000
     "Number of people in the building",   # bit 5: 00100000
     "Number of people in the building",   # bit 4: 00010000
     "Number of people in the building",   # bit 3: 00001000
     "Number of people in the building",   # bit 2: 00000100
     "RFU",                 # bit 1: 00000010
     "RFU",                 # bit 0: 00000001"""


    people_counter = MultiBitValueParser(SameValueRange(  0b0000,
                                                          0b1111,
                                                          4,
                                                          "Number of people in the building",
                                                          return_value_instead_of_name=True))

    protocol_with_counter = [
                            # Byte 0:
                             "front door opened",    # bit 7: 10000000
                             "back door opened",     # bit 6: 01000000
                             "zone 1 alarm",         # bit 5: 00100000
                             "zone 2 alarm",         # bit 4: 00010000
                             "zone 3 alarm",         # bit 3: 00001000
                             "zone 4 alarm",         # bit 2: 00000100
                             "zone 5 alarm",         # bit 1: 00000010
                             "zone 6 alarm",         # bit 0: 00000001
                            # Byte 1:
                             "zone 7 alarm",         # bit 7: 10000000
                             "zone 1 fire",          # bit 6: 01000000
                             "zone 2 fire",          # bit 5: 00100000
                             "zone 3 fire",          # bit 4: 00010000
                             "zone 4 fire",          # bit 3: 00001000
                             "zone 5 fire",          # bit 2: 00000100
                             "flood sensor 1 alarm", # bit 1: 00000010
                             "flood sensor 2 alarm", # bit 0: 00000001
                            # Byte 2:
                             "RFU",                  # bit 7: 10000000
                             "RFU",                  # bit 6: 01000000
                             people_counter,         # bit 5: 00100000
                             people_counter,         # bit 4: 00010000
                             people_counter,         # bit 3: 00001000
                             people_counter,         # bit 2: 00000100
                             "RFU",                  # bit 1: 00000010
                             "RFU",                  # bit 0: 00000001

    ]
    def protocol_with_counter_parser(bytes_to_parse):
        return parseBits(bytes_to_parse, protocol_with_counter)
    return protocol_with_counter_parser



@pytest.fixture(scope="class")  # scope="function" is default
def advanced_multibyte_protocol_parser():

    # Temperature status
    # "00" - temperature OK
    # "01" - temperature too low
    # "10" - temperature too high
    # "11" - broken sensor

    # Heating mode
    #  0 - 0000 - mode off
    #  1 - 0001 - mode 1
    #  2 - 0010 - mode 2
    #  3 - 0011 - mode 3
    #  4 - 0100 - mode 4
    #  5 - 0101 - mode 5
    #  6 - 0110 - mode 6
    #  7 - 0111 - mode 7
    #  8 - 1000 - mode 8
    #  9 - 1001 - RFU
    # 10 - 1010 - RFU
    # 11 - 1011 - RFU
    # 12 - 1100 - RFU
    # 13 - 1101 - RFU
    # 14 - 1110 - RFU
    # 15 - 1111 - RFU

    # # Byte 0:
    # "sensor ID",            # bit 7: 10000000
    # "sensor ID",            # bit 6: 01000000
    # "sensor ID",            # bit 5: 00100000
    # "temperature status",   # bit 4: 00010000
    # "temperature status",   # bit 3: 00001000
    # "LED is ON",            # bit 2: 00000100
    # "heating mode",         # bit 1: 00000010
    # "heating mode",         # bit 0: 00000001
    # # Byte 1:
    # "heating mode",         # bit 7: 10000000
    # "heating mode",         # bit 6: 01000000
    # "heating module 1 on",  # bit 5: 00100000
    # "heating module 2 on",  # bit 4: 00010000
    # "heating module 3 on",  # bit 3: 00001000
    # "heating module 4 on",  # bit 2: 00000100
    # "RFU",                  # bit 1: 00000010
    # "RFU",                  # bit 0: 00000001


    advanced_protocol = [
                            # Byte 0:
                             "sensor ID",           # bit 7: 10000000
                             "sensor ID",           # bit 6: 01000000
                             "sensor ID",           # bit 5: 00100000
                             "temperature status",  # bit 4: 00010000
                             "temperature status",  # bit 3: 00001000
                             "LED is ON",           # bit 2: 00000100
                             "heating mode",        # bit 1: 00000010
                             "heating mode",        # bit 0: 00000001
                            # Byte 1:
                             "heating mode",        # bit 7: 10000000
                             "heating mode",        # bit 6: 01000000
                             "heating module 1 on", # bit 5: 00100000
                             "heating module 2 on", # bit 4: 00010000
                             "heating module 3 on", # bit 3: 00001000
                             "heating module 4 on", # bit 2: 00000100
                             "RFU",                 # bit 1: 00000010
                             "RFU",                 # bit 0: 00000001
                          ]
    def advanced_protocol_parser(bytes_to_parse):
        return parseBits(bytes_to_parse, advanced_protocol)
    return advanced_protocol_parser


class TestBitParser:
    def test_simple_parser_80(self, simple_one_byte_parser):
        parsed_80 = simple_one_byte_parser("80")
        expected_80 = ["I/O pin Nr7 high level"]
        assert len(parsed_80) == len(expected_80)
        print(all([a == b for a, b in zip(parsed_80, expected_80)]))
        assert all([a == b for a, b in zip(parsed_80, expected_80)])


    def test_simple_parser_41(self, simple_one_byte_parser):
        parsed_41 = simple_one_byte_parser("41")
        expected_41 = ["I/O pin Nr6 high level",
                       "I/O pin Nr0 high level"]
        assert len(parsed_41) == len(expected_41)
        print(all([a == b for a, b in zip(parsed_41,  expected_41)]))
        assert all([a == b for a, b in zip(parsed_41, expected_41)])


    def test_simple_parser_F0(self, simple_one_byte_parser):
        parsed_F0 = simple_one_byte_parser("F0")
        expected_F0 = ["I/O pin Nr7 high level",
                       "I/O pin Nr6 high level",
                       "I/O pin Nr5 high level",
                       "I/O pin Nr4 high level"]
        assert len(parsed_F0) == len(expected_F0)
        print(all([a == b for a, b in zip(parsed_F0, expected_F0)]))
        assert all([a == b for a, b in zip(parsed_F0, expected_F0)])


    def test_simple_parser_00(self, simple_one_byte_parser):
        parsed_00 = simple_one_byte_parser("00")
        expected_00 = []
        assert len(parsed_00) == len(expected_00)
        print(all([a == b for a, b in zip(parsed_00, expected_00)]))
        assert all([a == b for a, b in zip(parsed_00, expected_00)])


    def test_simple_parser_FF(self, simple_one_byte_parser):
        parsed_FF = simple_one_byte_parser("FF")
        expected_FF = [  "I/O pin Nr7 high level",
                         "I/O pin Nr6 high level",
                         "I/O pin Nr5 high level",
                         "I/O pin Nr4 high level",
                         "I/O pin Nr3 high level",
                         "I/O pin Nr2 high level",
                         "I/O pin Nr1 high level",
                         "I/O pin Nr0 high level",
                        ]
        assert len(parsed_FF) == len(expected_FF)
        print(all([a == b for a, b in zip(parsed_FF, expected_FF)]))
        assert all([a == b for a, b in zip(parsed_FF, expected_FF)])


    def test_three_bytes_parser_010000(self, simple_three_byte_parser):
        parsed   = simple_three_byte_parser("010000")
        expected = ["led Nr 8 on"]
        assert len(parsed) == len(expected)
        print(all([a == b for a, b in zip(parsed, expected)]))
        assert all([a == b for a, b in zip(parsed, expected)])


    def test_three_bytes_parser_804001(self, simple_three_byte_parser):
        parsed   = simple_three_byte_parser("804001")
        expected = ["led Nr 1 on", "back door opened", "flood sensor active"]
        assert len(parsed) == len(expected)
        print(all([a == b for a, b in zip(parsed, expected)]))
        assert all([a == b for a, b in zip(parsed, expected)])


    def test_three_bytes_parser_not_enough_input_error(self, simple_three_byte_parser):
        with pytest.raises(ValueError):
            simple_three_byte_parser("8040")


    def test_three_bytes_parser_input_too_long_error(self, simple_three_byte_parser):
        with pytest.raises(ValueError):
            simple_three_byte_parser("80400000")


    def test_multibyte_protocol_with_counter(self, multibyte_protocol_with_counter):
        parsed = multibyte_protocol_with_counter("020705")
        expected = ['zone 5 alarm', 'zone 5 fire', 'flood sensor 1 alarm', 'flood sensor 2 alarm', 'Number of people in the building: 1', 'RFU']
        assert len(parsed) == len(expected)
        print(all([a == b for a, b in zip(parsed, expected)]))
        assert all([a == b for a, b in zip(parsed, expected)])


        parsed = multibyte_protocol_with_counter("000028")
        print(parsed)
        expected = ['Number of people in the building: 10']
        assert len(parsed) == len(expected)
        print(all([a == b for a, b in zip(parsed, expected)]))
        assert all([a == b for a, b in zip(parsed, expected)])