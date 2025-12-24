![Upload Python Package](https://github.com/vitalij555/bit-parser/workflows/Upload%20Python%20Package/badge.svg)
[![PyPi version](https://img.shields.io/pypi/v/bit-parser.svg?style=flat-square) ](https://pypi.python.org/pypi/bit-parser) [![Supported Python versions](https://img.shields.io/pypi/pyversions/bit-parser.svg?style=flat-square) ](https://pypi.org/project/bit-parser) [![License](https://img.shields.io/pypi/l/bit-parser.svg?style=flat-square) ](https://choosealicense.com/licenses) [![Downloads](https://pepy.tech/badge/bit-parser)](https://pepy.tech/project/bit-parser) [![codecov](https://codecov.io/gh/vitalij555/bit-parser/branch/master/graph/badge.svg)](https://codecov.io/gh/vitalij555/bit-parser)

# bit-parser

bit-parser is a small helper for decoding compact bitfields into human-readable labels.

Use it when you receive short, fixed-size bitmaps where each bit has a meaning, or when a group of bits represents a value like a status code or counter. It is not intended for streaming protocols or large binary payloads, but it works well for logs, diagnostics, and UI tooling.

Inputs can be raw bytes or hex strings like `"A3"` (no spaces).

## Contents

- [Motivation](#motivation)
- [Usage](#usage)
  - [Simple example](#simple-example)
  - [Advanced example](#advanced-example)
  - [Full list output (for UI)](#full-list-output-for-ui)
  - [Encode (reverse)](#encode-reverse)
  - [Descriptor schema (for UI builders)](#descriptor-schema-for-ui-builders)
- [Installation](#installation)
- [API Overview](#api-overview)
- [Tests](#tests)
- [License](#license)
- [Contributing](#contribute)


## Motivation

Embedded and IoT devices often log compact status bytes instead of long, descriptive messages. Those hex values are fast for devices to output, but slow for humans to interpret.

bit-parser lets you describe what each bit (or bit range) means and turn those bytes into readable labels or values.

## Usage

### Simple example
Imagine a controller returns one status byte where each bit represents the state of an I/O pin. A `1` means high voltage and `0` means low:

```text
# Byte 0:
    Bit 7: I/O pin Nr7 high level
    Bit 6: I/O pin Nr6 high level
    Bit 5: I/O pin Nr5 high level
    Bit 4: I/O pin Nr4 high level
    Bit 3: I/O pin Nr3 high level
    Bit 2: I/O pin Nr2 high level
    Bit 1: I/O pin Nr1 high level
    Bit 0: I/O pin Nr0 high level
```
You can describe the bits and decode a response like this:

```python
from BitParser import parse_bits
from pprint import pprint

bits_meaning = [ "I/O pin Nr7 high level",
                 "I/O pin Nr6 high level",
                 "I/O pin Nr5 high level",
                 "I/O pin Nr4 high level",
                 "I/O pin Nr3 high level",
                 "I/O pin Nr2 high level",
                 "I/O pin Nr1 high level",
                 "I/O pin Nr0 high level",]

# Parse the input bytes or hex string
pprint(parse_bits("A3", bits_meaning))
```
Console output:
```console
['I/O pin Nr7 high level',
 'I/O pin Nr5 high level',
 'I/O pin Nr1 high level',
 'I/O pin Nr0 high level']
```

### Advanced example

Often, protocols pack multiple bits together to represent a value. For example, bits 2-4 in a byte can encode a status code. With 3 bits you can represent 8 statuses (000, 001, 010, ... 111), while other bits still represent a single flag.

Let's consider a more advanced case.

Imagine we have a thermostat controller and the main module. Main manages temperature controller by sending it commands and obtaining back responses. For example, one of the responses could be represented by two bytes like following:

```
# Byte 0:
 "sensor ID",            | bit 7:    10000000
 "sensor ID",            | bit 6:    01000000
 "sensor ID",            | bit 5:    00100000
 "temperature status",   | bit 4:    00010000
 "temperature status",   | bit 3:    00001000
 "LED is ON",            | bit 2:    00000100
 "heating mode",         | bits 0-1: 000000xx
# Byte 1:                |
 "heating mode",         | bits 6-7: xx000000
 "heating module 1 on",  | bit 5:    00100000
 "heating module 2 on",  | bit 4:    00010000
 "heating module 3 on",  | bit 3:    00001000
 "heating module 4 on",  | bit 2:    00000100
 "RFU",                  | bit 1:    00000010
 "RFU",                  | bit 0:    00000001

Where
sensor ID - 3 bits representing device ID (meaning we can handle only 8 devices max in the system)
Temperature status (2 bits) can have following values:
    "00" - temperature OK
    "01" - temperature too low
    "10" - temperature too high
    "11" - broken sensor

Heating mode (4 bits):
     0 - 0000 - mode off
     1 - 0001 - mode 1
     2 - 0010 - mode 2
     3 - 0011 - mode 3
     4 - 0100 - mode 4
     5 - 0101 - mode 5
     6 - 0110 - mode 6
     7 - 0111 - mode 7
     8 - 1000 - mode 8
     9 - 1001 - RFU
    10 - 1010 - RFU
    11 - 1011 - RFU
    12 - 1100 - RFU
    13 - 1101 - RFU
    14 - 1110 - RFU
    15 - 1111 - RFU        
```  

From the description above, there are four cases to handle:
1. Single-bit flags (e.g., "heating module N on" or "RFU")
2. A multi-bit value where we care about the numeric value (sensor ID)
3. A multi-bit value that spans bytes (heating mode)
4. A single-bit status that should always be reported (LED ON/OFF)

Now let's define a parser for these two bytes:

```python
from BitParser import parse_bits, MultiBitValueParser, SameValueRange
from pprint import pprint

# describing sensor_id 
sensor_id = MultiBitValueParser(SameValueRange(0b000, 0b111, 3, "sensor ID", return_value_instead_of_name=True))


# describing Heating Mode
heating_mode = MultiBitValueParser({ "0000": "heating mode off",
                                     "0001": "heating mode 1",
                                     "0010": "heating mode 2",
                                     "0011": "heating mode 3",
                                     "0100": "heating mode 4",  # important to describe full range here and not leave 
                                     "0101": "heating mode 5",
                                     "0110": "heating mode 6",
                                     "0111": "heating mode 7",
                                     "1000": "heating mode 8"},  # here dictionary ends. We can have unlimited number of dictionaries or SameValueRange objects separated by comas inside MultiBitValueParser constructor.
                                     SameValueRange(0b1001, 0b1111, 4, "RFU"))  # in this way we can define the whole range having same values

# describing Status
status = MultiBitValueParser({  "00": "temperature OK",
                                "01": "temperature too low",
                                "10": "temperature too high",
                                "11": "broken sensor"})

# LED ON/OFF
led_status = MultiBitValueParser({ "0": "LED is OFF",
                                   "1": "LED is ON"})

# bringing all together
advanced_protocol = [
                        # Byte 0:
                         sensor_id,             # bit 7: 10000000   
                         sensor_id,             # bit 6: 01000000
                         sensor_id,             # bit 5: 00100000
                         status,                # bit 4: 00010000
                         status,                # bit 3: 00001000
                         led_status,            # bit 2: 00000100
                         heating_mode,          # bit 1: 00000010
                         heating_mode,          # bit 0: 00000001
                        # Byte 1:
                         heating_mode,          # bit 7: 10000000
                         heating_mode,          # bit 6: 01000000
                         "heating module 1 on", # bit 5: 00100000
                         "heating module 2 on", # bit 4: 00010000
                         "heating module 3 on", # bit 3: 00001000
                         "heating module 4 on", # bit 2: 00000100
                         "RFU",                 # bit 1: 00000010
                         "RFU",                 # bit 0: 00000001
                      ]

def advanced_protocol_parser(bytes_to_parse):
    return parse_bits(bytes_to_parse, advanced_protocol)

advanced_parser = advanced_protocol_parser

pprint(advanced_parser("40F0"))
```
Output:
```console
['sensor ID: 2',
 'temperature OK',
 'LED is OFF',
 'heating mode 3',
 'heating module 1 on',
 'heating module 2 on']
```
To see LED ON, set bit 2:
```python
pprint(advanced_parser("4CF0"))
```
Output:
```console
['sensor ID: 2',
 'temperature too low',
 'LED is ON',
 'heating mode 3',
 'heating module 1 on',
 'heating module 2 on']
```

### Full list output (for UI)

If you want to show every bit (enabled or not), use `parse_bits_full`. It returns:
- One entry per bit with `enabled: True/False`
- For multi-bit fields, an extra summary entry with the aggregated value

```python
from BitParser import parse_bits_full

descriptors = [
    "I/O pin Nr7 high level",
    "I/O pin Nr6 high level",
    "I/O pin Nr5 high level",
    "I/O pin Nr4 high level",
    "I/O pin Nr3 high level",
    "I/O pin Nr2 high level",
    "I/O pin Nr1 high level",
    "I/O pin Nr0 high level",
]

rows = parse_bits_full("80", descriptors)
print(rows[0])
print(rows[-1])
```
Example output:
```console
{'kind': 'bit', 'label': 'I/O pin Nr7 high level', 'enabled': True, 'raw_bit': 1, ...}
{'kind': 'bit', 'label': 'I/O pin Nr0 high level', 'enabled': False, 'raw_bit': 0, ...}
```

### Encode (reverse)

Use `encode_bits` to generate a hex string from enabled labels and numeric multi-bit values.
For multi-bit fields you must provide either:
- a label (e.g., `"LED is ON"`) in `enabled_labels`, or
- a numeric value in `values` (e.g., `{"heating mode": 3}`).
Field names for `values` are inferred from the multi-bit labels (for example: `"sensor ID"` or `"heating mode"`).
This is handy when building web-based hex configuration generators or diagnostic calculators.
If a label appears multiple times (like `"RFU"`), use `label:byte:bit` to disambiguate (bytes are 0-based, bit 0 is LSB).
You can use the same `name:byte:bit` form in `values` when multiple multi-bit fields share the same name.

```python
from BitParser import encode_bits, MultiBitValueParser, SameValueRange

heating_mode = MultiBitValueParser(
    {"0000": "heating mode off",
     "0001": "heating mode 1",
     "0010": "heating mode 2",
     "0011": "heating mode 3"}
)

descriptors = [
    "I/O pin Nr7 high level",
    "I/O pin Nr6 high level",
    "I/O pin Nr5 high level",
    "I/O pin Nr4 high level",
    "I/O pin Nr3 high level",
    "I/O pin Nr2 high level",
    "I/O pin Nr1 high level",
    "I/O pin Nr0 high level",
]

hex_out = encode_bits(
    ["I/O pin Nr7 high level", "I/O pin Nr1 high level", "I/O pin Nr0 high level"],
    descriptors
)
print(hex_out)  # "83"
```

### Descriptor schema (for UI builders)

If you want to build a UI without hardcoding the descriptor list, use `describe_bits`.
It returns a JSON-friendly schema with per-bit entries and multi-bit value options.

```python
from BitParser import describe_bits

schema = describe_bits(descriptors)
print(schema["multi_bit"][0]["values"][0])
```

## Installation

```
pip install -U bit-parser
```


## API Overview

### Functions

- `parse_bits(bytes_or_hex, descriptors) -> list[str]`  
  Returns only enabled descriptors (bits with value 1) and aggregated multi-bit values.
- `parse_bits_full(bytes_or_hex, descriptors) -> list[dict]`  
  Returns one entry for every bit, with `enabled` markers so UIs can grey out disabled bits. For multi-bit fields, also returns a summary entry with the aggregated value.
- `encode_bits(enabled_labels, descriptors, values=None) -> str`  
  Returns an uppercase hex string from enabled labels and multi-bit numeric values. Use `label:byte:bit` to disambiguate.
- `describe_bits(descriptors) -> dict`  
  Returns a JSON-friendly schema for UI builders (bits plus multi-bit value options).

### Descriptor helpers

- `MultiBitValueParser`  
  Collects consecutive bits and maps the resulting bit string to a label.
- `SameValueRange`  
  Generates a mapping for a continuous range of values (useful for RFU or counters).

### parse_bits_full output shape

Each result entry is a `dict`.

Bit entry:
- `kind`: `"bit"`
- `label`: descriptor string (or `None` for multi-bit contributors)
- `enabled`: `True`/`False`
- `raw_bit`: `0`/`1`
- `byte_index`, `bit_index`, `descriptor_index`
- For multi-bit contributors: `group_id`, `group_bit_index`, `group_label`, `summary_index`

Summary entry:
- `kind`: `"multi_bit"`
- `label`: evaluated value (e.g., `"heating mode 3"`)
- `raw_bits`: assembled bit string
- `value_int`: integer value of `raw_bits`
- `group_id`, `descriptor_indices`

## Tests

[PyTest][pytest] is used for tests. Python 2 is not supported.

**Install PyTest**

```sh
$ pip install pytest
```

**Run tests**

```sh
$ pytest test/*
```

[pytest]: http://pytest.org/

**Check test coverage**

In order to generate test coverage report install pytest-cov:

```sh
$ pip install pytest-cov
```

Then inside test subdirectory call: 

```sh
pytest --cov=../BitParser --cov-report=html
```

## License

License
Copyright (C) 2022 Vitalij Gotovskij

bit-parser binaries and source code can be used according to the MIT License


## Contribute
TBD
