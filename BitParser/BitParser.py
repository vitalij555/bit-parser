import binascii
from pprint import pprint, pformat
from collections.abc import MutableMapping

from bitops import get_bit, ENDIANNESS


class Dict_Returning_Key_With_Value(MutableMapping):
    def __init__(self, *args, **kwargs):
        self.store = dict()
        self.update(dict(*args, **kwargs))
        self.__return_int_value_instead_of_name = False

    def enable_return_value_instead_of_name(self):
        self.__return_int_value_instead_of_name = True

    def __getitem__(self, key):
        if not self.__return_int_value_instead_of_name:
            return self.store[key]
        else:
            return self.store[key] + ": " + str(int(key, 2))

    def __setitem__(self, key, value):
        self.store[key] = value

    def __delitem__(self, key):
        del self.store[key]

    def __iter__(self):
        return iter(self.store)

    def __len__(self):
        return len(self.store)


class SameValueRange():
    def __init__(self, range_start, range_end, number_of_bits, value, return_value_instead_of_name=False):
        self.__return_value_instead_of_name = return_value_instead_of_name

        if number_of_bits < 1 and number_of_bits > 8:
            raise AssertionError(f"Wrong number of bits passed: {number_of_bits}")

        self.__generated_range_descriptor = Dict_Returning_Key_With_Value({f"{flag_value:b}".zfill(number_of_bits):value for flag_value in range(range_start, range_end+1)})

    def get_dict(self):
        if self.__return_value_instead_of_name:
            self.__generated_range_descriptor.enable_return_value_instead_of_name()
        return self.__generated_range_descriptor


class MultiBitValueParser():

    def __init__(self, *resultEvaluationDicts):
        self.evaluator = {}

        for resultEvaluationDict in resultEvaluationDicts:
            if isinstance(resultEvaluationDict, SameValueRange):
                self.evaluator = {**self.evaluator, **resultEvaluationDict.get_dict()}
            else:
                self.evaluator = {**self.evaluator, **resultEvaluationDict}

        self.bytesAssembled = ""
        self.numOfElements = len(list(self.evaluator.keys())[0])
        self.numOfElementsMissing = self.numOfElements


    def __call__(self, value):
        if(self.numOfElementsMissing == 0):
            self.numOfElementsMissing = len(list(self.evaluator.keys())[0])
            self.bytesAssembled = ""
        self.numOfElementsMissing -= 1
        self.bytesAssembled = self.bytesAssembled + value

        if(self.numOfElementsMissing == 0):
            return self.evaluator[self.bytesAssembled]
        else:
            return None

def pairwise(iterable):
    "s -> (s0, s1), (s2, s3), (s4, s5), ..."
    a = iter(iterable)
    return zip(a, a)


def parse_bits_binary(bytes, descriptors: list) -> str:
    bitFieldDescriptorLength = len(descriptors)

    if bitFieldDescriptorLength % 8 != 0:
        raise ValueError(f"Descriptor length ({bitFieldDescriptorLength}) is not divisible by 8!")

    bytes_len = len(bytes)

    if bytes_len != bitFieldDescriptorLength // 8:
        raise ValueError(f"bytesStr length ({bytes_len}) does not correspond to descriptors list length ({bitFieldDescriptorLength // 8})")

    results = []
    for byteNum, byte in enumerate(bytes):
        for bitNum in range(0, 8):
            bit = get_bit(byte, bitNum, endiannes=ENDIANNESS.LITTLE)
            if isinstance(descriptors[byteNum * 8 + bitNum], MultiBitValueParser):
                ret = descriptors[byteNum * 8 + bitNum](str(bit))
                if ret != None:
                    results.append(ret)
            else:
                if bit == 1:
                    results.append(descriptors[byteNum * 8 + bitNum])

    return results


def parse_bits(bytes, descriptors: list) -> str:
    if isinstance(bytes, str):  # hexadecimal string is supported (like "001122AAEEFF"
        return parse_bits_binary(binascii.unhexlify(bytes), descriptors)
    else:
        return parse_bits_binary(bytes, descriptors)




