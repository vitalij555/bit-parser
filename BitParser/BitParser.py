import binascii
from pprint import pprint, pformat
from collections.abc import MutableMapping

try:
    from bitops import get_bit, ENDIANNESS
except ModuleNotFoundError:
    from enum import Enum

    class ENDIANNESS(Enum):
        LITTLE = "little"
        BIG = "big"

    def get_bit(value, bit_num, endiannes=ENDIANNESS.LITTLE):
        if endiannes == ENDIANNESS.LITTLE:
            bit_num = 7 - bit_num
        return (value >> bit_num) & 1


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


def parse_bits_binary_full(bytes, descriptors: list) -> list:
    bitFieldDescriptorLength = len(descriptors)

    if bitFieldDescriptorLength % 8 != 0:
        raise ValueError(f"Descriptor length ({bitFieldDescriptorLength}) is not divisible by 8!")

    bytes_len = len(bytes)

    if bytes_len != bitFieldDescriptorLength // 8:
        raise ValueError(f"bytesStr length ({bytes_len}) does not correspond to descriptors list length ({bitFieldDescriptorLength // 8})")

    results = []
    multibit_states = {}
    next_group_id = 0

    for byteNum, byte in enumerate(bytes):
        for bitNum in range(0, 8):
            descriptor_index = byteNum * 8 + bitNum
            descriptor = descriptors[descriptor_index]
            bit = get_bit(byte, bitNum, endiannes=ENDIANNESS.LITTLE)

            if isinstance(descriptor, MultiBitValueParser):
                state = multibit_states.get(descriptor)
                if state is None:
                    state = {
                        "group_id": None,
                        "pending_entries": [],
                        "pending_bits": [],
                        "pending_indices": [],
                    }
                    multibit_states[descriptor] = state

                if not state["pending_bits"]:
                    state["group_id"] = next_group_id
                    next_group_id += 1

                group_bit_index = len(state["pending_bits"])
                entry = {
                    "kind": "bit",
                    "label": None,
                    "enabled": bit == 1,
                    "raw_bit": bit,
                    "byte_index": byteNum,
                    "bit_index": bitNum,
                    "descriptor_index": descriptor_index,
                    "group_id": state["group_id"],
                    "group_bit_index": group_bit_index,
                    "group_label": None,
                }
                results.append(entry)
                state["pending_entries"].append(len(results) - 1)
                state["pending_bits"].append(str(bit))
                state["pending_indices"].append(descriptor_index)

                ret = descriptor(str(bit))
                if ret is not None:
                    raw_bits = "".join(state["pending_bits"])
                    summary_entry = {
                        "kind": "multi_bit",
                        "label": ret,
                        "enabled": True,
                        "raw_bits": raw_bits,
                        "value_int": int(raw_bits, 2),
                        "group_id": state["group_id"],
                        "descriptor_indices": state["pending_indices"],
                    }
                    results.append(summary_entry)
                    summary_index = len(results) - 1

                    for entry_index in state["pending_entries"]:
                        results[entry_index]["group_label"] = ret
                        results[entry_index]["summary_index"] = summary_index

                    state["pending_entries"] = []
                    state["pending_bits"] = []
                    state["pending_indices"] = []
            else:
                results.append({
                    "kind": "bit",
                    "label": descriptor,
                    "enabled": bit == 1,
                    "raw_bit": bit,
                    "byte_index": byteNum,
                    "bit_index": bitNum,
                    "descriptor_index": descriptor_index,
                })

    return results


def parse_bits_full(bytes, descriptors: list) -> list:
    if isinstance(bytes, str):  # hexadecimal string is supported (like "001122AAEEFF"
        return parse_bits_binary_full(binascii.unhexlify(bytes), descriptors)
    else:
        return parse_bits_binary_full(bytes, descriptors)


