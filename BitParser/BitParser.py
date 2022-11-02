from pprint import pprint, pformat
from collections.abc import MutableMapping


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

        if number_of_bits == 1:
            self.__generated_range_descriptor = Dict_Returning_Key_With_Value({f"{flag_value:01b}":value for flag_value in range(range_start, range_end+1)})
        elif number_of_bits == 2:
            self.__generated_range_descriptor = Dict_Returning_Key_With_Value({f"{flag_value:02b}": value for flag_value in range(range_start, range_end + 1)})
        elif number_of_bits == 3:
            self.__generated_range_descriptor = Dict_Returning_Key_With_Value({f"{flag_value:03b}": value for flag_value in range(range_start, range_end + 1)})
        elif number_of_bits == 4:
            self.__generated_range_descriptor = Dict_Returning_Key_With_Value({f"{flag_value:04b}": value for flag_value in range(range_start, range_end + 1)})
        elif number_of_bits == 5:
            self.__generated_range_descriptor = Dict_Returning_Key_With_Value({f"{flag_value:05b}": value for flag_value in range(range_start, range_end + 1)})
        elif number_of_bits == 6:
            self.__generated_range_descriptor = Dict_Returning_Key_With_Value({f"{flag_value:06b}": value for flag_value in range(range_start, range_end + 1)})
        elif number_of_bits == 7:
            self.__generated_range_descriptor = Dict_Returning_Key_With_Value({f"{flag_value:07b}": value for flag_value in range(range_start, range_end + 1)})
        elif number_of_bits == 8:
            self.__generated_range_descriptor = Dict_Returning_Key_With_Value({f"{flag_value:08b}": value for flag_value in range(range_start, range_end + 1)})


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
        # print("self.evaluator:")
        # pprint(self.evaluator)

    # def __repr__(self):
    #     return pformat(self.evaluator)

    def __call__(self, value):
        if(self.numOfElementsMissing == 0):
            self.numOfElementsMissing = len(list(self.evaluator.keys())[0])
            self.bytesAssembled = ""
        self.numOfElementsMissing -= 1
        self.bytesAssembled = self.bytesAssembled + value
        # print(f"self.bytesAssembled: {self.bytesAssembled}")

        if(self.numOfElementsMissing == 0):
            # print(self.evaluator)
            return self.evaluator[self.bytesAssembled]
        else:
            return None

#-----------------------------------------------------------------------------------------------------------------------


def pairwise(iterable):
    "s -> (s0, s1), (s2, s3), (s4, s5), ..."
    a = iter(iterable)
    return zip(a, a)


def parse_bits(bytesStr: str, descriptors: list) -> str:
    bytesStr = bytesStr.strip()
    bytesStr = bytesStr.replace("  ", " ")
    bytesStr = bytesStr.replace(" ", "")
    bitFieldDescriptorLength = len(descriptors)

    if bitFieldDescriptorLength % 8 != 0:
        raise ValueError(f"Descriptor length ({bitFieldDescriptorLength}) is not divisible by 8!")

    bytesStrLen = len(bytesStr)

    if bytesStrLen % 2 != 0:
        raise ValueError(f"bytesStr length ({bytesStrLen}) is not divisible by 2!")

    if bytesStrLen//2 != bitFieldDescriptorLength // 8:
        raise ValueError(f"bytesStr length ({bytesStrLen//2}) does not correspond to descriptors list length ({bitFieldDescriptorLength // 8})")


    # print(f"Pairwise result: {list(pairwise(bytesStr))}")
    results = []
    for byteNum, (byte_nibble1, byte_nibble2) in enumerate(pairwise(bytesStr)):
        # print(f"Current byte num: {byteNum} and byteStr: {byte_nibble1 + byte_nibble2}")
        byteAsInt = int(byte_nibble1 + byte_nibble2, 16)
        bitsStr   = bin(byteAsInt)
        bitsStr   = bitsStr[2:10]
        bitsStr   = f"{bitsStr:0>8}"
        # print(f"bitsStr: {bitsStr}")

        for bitNum, bit in enumerate(bitsStr):
            if isinstance(descriptors[byteNum * 8 + bitNum], MultiBitValueParser):
                # print(f"Checking byteNum= {byteNum} bitNum={bitNum} and bit value is {bit}")
                ret = descriptors[byteNum * 8 + bitNum](bit)
                if ret != None:
                    results.append(ret)
            else:
                if bit == "1":
                    results.append(descriptors[byteNum * 8 + bitNum])

    return results


