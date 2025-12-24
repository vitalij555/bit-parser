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


def _infer_multibit_name(labels):
    if not labels:
        return None

    colon_prefixes = [label.split(": ", 1)[0] for label in labels if ": " in label]
    if colon_prefixes and len(colon_prefixes) == len(labels):
        unique_prefixes = set(colon_prefixes)
        if len(unique_prefixes) == 1:
            return colon_prefixes[0]

    def candidate_from_label(label):
        if ": " in label:
            return label.split(": ", 1)[0].strip()

        lower = label.lower()
        if lower.endswith(" on"):
            return label[:-3].rstrip()
        if lower.endswith(" off"):
            return label[:-4].rstrip()

        idx = len(label)
        while idx > 0 and label[idx - 1].isdigit():
            idx -= 1
        if idx < len(label):
            return label[:idx].rstrip()

        return None

    candidates = []
    for label in labels:
        candidate = candidate_from_label(label)
        if candidate:
            candidates.append(candidate)

    if not candidates:
        return None

    counts = {}
    for candidate in candidates:
        counts[candidate] = counts.get(candidate, 0) + 1

    sorted_candidates = sorted(counts.items(), key=lambda item: (-item[1], item[0]))
    if len(sorted_candidates) > 1 and sorted_candidates[0][1] == sorted_candidates[1][1]:
        return None

    if sorted_candidates[0][1] < 2:
        return None

    return sorted_candidates[0][0]


def _parse_label_address(label, byte_length):
    parts = label.rsplit(":", 2)
    if len(parts) != 3:
        return label, None

    base = parts[0].strip()
    if not base:
        return label, None

    try:
        byte_index = int(parts[1].strip())
        bit_number = int(parts[2].strip())
    except ValueError:
        return label, None

    if byte_index < 0 or bit_number < 0 or bit_number > 7:
        raise ValueError("Addressed label must use 'name:byte:bit' with bit in 0..7")
    if byte_index >= byte_length:
        raise ValueError(f"Byte index {byte_index} out of range for {byte_length} bytes")

    descriptor_index = byte_index * 8 + (7 - bit_number)
    return base, descriptor_index


def describe_bits(descriptors: list) -> dict:
    bitFieldDescriptorLength = len(descriptors)

    if bitFieldDescriptorLength % 8 != 0:
        raise ValueError(f"Descriptor length ({bitFieldDescriptorLength}) is not divisible by 8!")

    multibit_groups = {}
    for index, descriptor in enumerate(descriptors):
        if isinstance(descriptor, MultiBitValueParser):
            multibit_groups.setdefault(descriptor, {"indices": [], "first_index": index})
            multibit_groups[descriptor]["indices"].append(index)

    group_items = sorted(multibit_groups.items(), key=lambda item: item[1]["first_index"])
    group_info = {}
    index_to_group = {}
    for group_id, (parser, info) in enumerate(group_items):
        indices = info["indices"]
        num_bits = parser.numOfElements
        if len(indices) != num_bits:
            raise ValueError(
                f"MultiBitValueParser expects {num_bits} bits but appears {len(indices)} times in descriptors"
            )

        labels = [label for _, label in parser.evaluator.items()]
        name = _infer_multibit_name(labels)
        values = [
            {
                "bits": bit_string,
                "label": label,
                "value_int": int(bit_string, 2),
            }
            for bit_string, label in parser.evaluator.items()
        ]
        values.sort(key=lambda entry: entry["value_int"])

        group_entry = {
            "group_id": group_id,
            "name": name,
            "num_bits": num_bits,
            "descriptor_indices": indices,
            "values": values,
        }
        group_info[parser] = group_entry
        for group_bit_index, descriptor_index in enumerate(indices):
            index_to_group[descriptor_index] = {
                "group_id": group_id,
                "group_bit_index": group_bit_index,
                "group_name": name,
            }

    bits = []
    for index, descriptor in enumerate(descriptors):
        entry = {
            "descriptor_index": index,
            "byte_index": index // 8,
            "bit_index": index % 8,
        }
        group = index_to_group.get(index)
        if group:
            entry.update({
                "kind": "multi_bit",
                "label": None,
                "group_id": group["group_id"],
                "group_bit_index": group["group_bit_index"],
                "group_name": group["group_name"],
            })
        else:
            entry.update({
                "kind": "bit",
                "label": descriptor,
            })
        bits.append(entry)

    return {
        "byte_length": bitFieldDescriptorLength // 8,
        "bits": bits,
        "multi_bit": [group_info[parser] for parser, _ in group_items],
    }


def encode_bits(enabled_labels, descriptors: list, values=None) -> str:
    bitFieldDescriptorLength = len(descriptors)

    if bitFieldDescriptorLength % 8 != 0:
        raise ValueError(f"Descriptor length ({bitFieldDescriptorLength}) is not divisible by 8!")

    byte_length = bitFieldDescriptorLength // 8

    if values is None:
        values = {}

    if isinstance(enabled_labels, (str, bytes)):
        raise ValueError("enabled_labels must be an iterable of strings")

    enabled_labels = list(enabled_labels or [])
    for label in enabled_labels:
        if not isinstance(label, str):
            raise ValueError("enabled_labels must contain only strings")

    if not isinstance(values, dict):
        raise ValueError("values must be a dict mapping field names to integers")

    single_label_positions = {}
    multibit_groups = {}
    for index, descriptor in enumerate(descriptors):
        if isinstance(descriptor, MultiBitValueParser):
            multibit_groups.setdefault(descriptor, []).append(index)
        else:
            single_label_positions.setdefault(descriptor, []).append(index)

    group_info = {}
    name_to_groups = {}
    index_to_group = {}
    for parser, indices in multibit_groups.items():
        num_bits = parser.numOfElements
        if len(indices) != num_bits:
            raise ValueError(
                f"MultiBitValueParser expects {num_bits} bits but appears {len(indices)} times in descriptors"
            )

        label_to_bits = {}
        for bit_string, label in parser.evaluator.items():
            label_to_bits.setdefault(label, []).append(bit_string)

        labels = list(label_to_bits.keys())
        name = _infer_multibit_name(labels)
        group_info[parser] = {
            "indices": indices,
            "num_bits": num_bits,
            "label_to_bits": label_to_bits,
            "name": name,
        }
        if name:
            name_to_groups.setdefault(name, []).append(parser)
        for descriptor_index in indices:
            index_to_group[descriptor_index] = parser

    group_set = set()
    bit_values = [0] * bitFieldDescriptorLength

    def apply_bit_string(indices, bit_string):
        if len(bit_string) != len(indices):
            raise ValueError("Multi-bit value does not match descriptor bit count")
        for index, bit in zip(indices, bit_string):
            if bit not in ("0", "1"):
                raise ValueError("Multi-bit value must be a binary string")
            bit_values[index] = 1 if bit == "1" else 0

    unused_values = {}
    addressed_values = []
    for key, value in values.items():
        if not isinstance(key, str):
            raise ValueError("values keys must be strings")
        base, descriptor_index = _parse_label_address(key, byte_length)
        if descriptor_index is None:
            unused_values[base] = value
        else:
            addressed_values.append((base, descriptor_index, value))

    for base, descriptor_index, value in addressed_values:
        descriptor = descriptors[descriptor_index]
        if not isinstance(descriptor, MultiBitValueParser):
            raise ValueError(f"Addressed value '{base}' does not point to a multi-bit field")

        parser = descriptor
        info = group_info[parser]
        if info["name"] and base != info["name"]:
            raise ValueError(f"Addressed value '{base}' does not match field name '{info['name']}'")
        if parser in group_set:
            raise ValueError(f"Multi-bit field '{base}' is already set")
        if not isinstance(value, int):
            raise ValueError(f"Value for '{base}' must be an integer")
        if value < 0:
            raise ValueError(f"Value for '{base}' must be non-negative")
        bit_string = format(value, f"0{info['num_bits']}b")
        if bit_string not in parser.evaluator:
            raise ValueError(f"Value {value} for '{base}' is not defined in descriptors")
        apply_bit_string(info["indices"], bit_string)
        group_set.add(parser)

    for name, groups in name_to_groups.items():
        if name in unused_values and len(groups) > 1:
            raise ValueError(f"Multi-bit field name '{name}' is ambiguous; use 'name:byte:bit'")

    for parser, info in group_info.items():
        name = info["name"]
        if name and name in unused_values:
            value = unused_values.pop(name)
            if not isinstance(value, int):
                raise ValueError(f"Value for '{name}' must be an integer")
            if value < 0:
                raise ValueError(f"Value for '{name}' must be non-negative")
            bit_string = format(value, f"0{info['num_bits']}b")
            if bit_string not in parser.evaluator:
                raise ValueError(f"Value {value} for '{name}' is not defined in descriptors")
            apply_bit_string(info["indices"], bit_string)
            group_set.add(parser)

    multi_label_groups = {}
    for parser, info in group_info.items():
        for label in info["label_to_bits"]:
            multi_label_groups.setdefault(label, []).append(parser)

    for label in enabled_labels:
        label_base, descriptor_index = _parse_label_address(label, byte_length)
        if descriptor_index is not None:
            descriptor = descriptors[descriptor_index]
            if isinstance(descriptor, MultiBitValueParser):
                parser = descriptor
                info = group_info[parser]
                if label_base not in info["label_to_bits"]:
                    raise ValueError(f"Unknown label '{label_base}' for addressed multi-bit field")
                if parser in group_set:
                    raise ValueError(f"Multi-bit field '{label_base}' is already set")
                label_bits = info["label_to_bits"][label_base]
                if len(label_bits) != 1:
                    raise ValueError(f"Label '{label_base}' is ambiguous for multi-bit encoding")
                apply_bit_string(info["indices"], label_bits[0])
                group_set.add(parser)
            else:
                if descriptor != label_base:
                    raise ValueError(
                        f"Label '{label_base}' does not match descriptor at byte {descriptor_index // 8} bit {7 - (descriptor_index % 8)}"
                    )
                bit_values[descriptor_index] = 1
            continue

        has_single = label in single_label_positions and single_label_positions[label]
        has_multi = label in multi_label_groups
        if has_single and has_multi:
            raise ValueError(f"Label '{label}' is ambiguous between single and multi-bit descriptors")

        if has_single:
            if len(single_label_positions[label]) > 1:
                raise ValueError(f"Label '{label}' matches multiple bits; use 'label:byte:bit'")
            bit_index = single_label_positions[label].pop(0)
            bit_values[bit_index] = 1
            continue

        if has_multi:
            groups = multi_label_groups[label]
            if len(groups) > 1:
                raise ValueError(f"Label '{label}' matches multiple multi-bit groups")
            parser = groups[0]
            if parser in group_set:
                raise ValueError(f"Multi-bit group for '{label}' is already set")
            label_bits = group_info[parser]["label_to_bits"][label]
            if len(label_bits) != 1:
                raise ValueError(f"Label '{label}' is ambiguous for multi-bit encoding")
            apply_bit_string(group_info[parser]["indices"], label_bits[0])
            group_set.add(parser)
            continue

        raise ValueError(f"Unknown label '{label}'")

    if unused_values:
        unknown = ", ".join(sorted(unused_values.keys()))
        raise ValueError(f"Unknown multi-bit field(s): {unknown}")

    for parser, info in group_info.items():
        if parser not in group_set:
            name = info["name"] or "unnamed"
            raise ValueError(f"Missing value for multi-bit field '{name}'")

    byte_values = [0] * (bitFieldDescriptorLength // 8)
    for index, bit in enumerate(bit_values):
        if bit:
            byte_index = index // 8
            bit_index = index % 8
            byte_values[byte_index] |= 1 << (7 - bit_index)

    return binascii.hexlify(bytes(byte_values)).decode("ascii").upper()
