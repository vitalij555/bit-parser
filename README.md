![Upload Python Package](https://github.com/vitalij555/bit-parser/workflows/Upload%20Python%20Package/badge.svg)
[![PyPi version](https://img.shields.io/pypi/v/bit-parser.svg?style=flat-square) ](https://pypi.python.org/pypi/bit-parser) [![Supported Python versions](https://img.shields.io/pypi/pyversions/bit-parser.svg?style=flat-square) ](https://pypi.org/project/bit-parser) [![License](https://img.shields.io/pypi/l/bit-parser.svg?style=flat-square) ](https://choosealicense.com/licenses) [![Downloads](https://pepy.tech/badge/bit-parser)](https://pepy.tech/project/bit-parser) [![codecov](https://codecov.io/gh/vitalij555/bit-parser/branch/master/graph/badge.svg)](https://codecov.io/gh/vitalij555/bit-parser)

# bit-parser

This is a configurable parser allowing to define your own low-level protocol and parse its representation provided as hexadecimal string and convert it into a human-readable form.

With bit-parser you can parse bit maps consisting of several bytes, where each bit has its own unique meaning or where several bits are grouped together to represent some kind of status, error code or counter.  Also, special helpers are provided for cases where several consecutive bits represent the same value (for example RFU - Reserved for Future Use bits).

This module is not intended for parsing complex streaming protocols or protocols containing many hundreds and thousands of bytes of information, but it can be useful as a sub-component for a more complex parsers or as a parser for a log files containing much of useful information provided in a hexadecimal format.

Byte arrays and hexadecimal strings are accepted as an input.     

## Contents

- [Motivation](#motivation)
- [Usage](#usage)
  - [Simple example](#simple-example)
  - [Advanced example](#advanced-example)
- [Installation](#installation)
- [API Overview](#api-overview)
- [Tests](#tests)
- [License](#license)
- [Contributing](#contribute)


## Motivation

In software development it's quite often happens to deal with different data represented in not-so-easy-readable formats. Usually microcontrollers used in IoT or other embedded systems, does not have enough resources to output "novels" into their log files describing what just happened in the system. As a result, most of such log files contain a lot of hexadecimal numbers representing statuses, error codes, counters, levels and many more.

Because of that, it is always worth to write additional tooling enabling fast and error-prone reading of such a files.

bit-parser can definitely serve here as a corner-stone component for implementing such a tooling.

## Usage

### Simple example 
Let's start from something simple. Let's imagine in our current IoT project we need to deal with some very simple protocol: controller sends command to one of its peripherals and gets back status of its I/O pins. As a result of such a request we get several bytes of a response, one byte of which encodes situation on I/O pins. There "1" means high voltage level on CPU pin and "0" means low. We can describe our byte of interest as follows:

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
Controller then writes request and response pair into a log file (or console). And we would like to create a tool allowing us to pass such a log line and get human-readable representation of response bytes. 

Here is how we can do that with a help of bit-parser:

```python
# 0. Import parse_bits function
from BitParser import parse_bits
from pprint import pprint

# 1. First we describe bits as python list:
bits_meaning = [ "I/O pin Nr7 high level",
                 "I/O pin Nr6 high level",
                 "I/O pin Nr5 high level",
                 "I/O pin Nr4 high level",
                 "I/O pin Nr3 high level",
                 "I/O pin Nr2 high level",
                 "I/O pin Nr1 high level",
                 "I/O pin Nr0 high level",]

# 2. Just parse..
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

Although it's not a rare case when one bit represents one "thing" in a byte, most of the time information is packed into a bytes in a more efficient way. For example, it is quite often to have situation when part of a byte (some of its bits located one after another) is dedicated to encode some number or a code. For example, we can say that bits 2-4 in a byte 2 are representing some status code. Now, instead of being able to encode only 3 different statuses with 3 bits we are able to encode 8 different statuses (000, 001, 010, .. 111). At the same time other bits in a byte can still represent only one "thing" per bit.

Having that in mind, let's consider more sophisticatyed case. 

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

From above description we can make conclusion that in this particular case we have 4 different sutuations to handle:
1. Bits like Byte1.bit2-bit5 ("heating module N on") or Byte1.bit1 ("RFU") represent something on their own (as in the simplest case we had in the first example above)
2. Byte0.bit5-bit7 represent device ID which means we are interested in a value itself (1,2,3,4,5..) and not in a label ("device id") here, because label will be able to tell only that device "has some id assigned" - which we already know anyway.
3. Byte0.bit0,bit1-Byte1.bit6,bit7 encode heating mode. Although it would be not too smart to organise these four bits in a way it is shown in our example (bit pairs located in a different bytes), let's assume we got it "as is" and there is no chance to change this protocol. Shortly we will ensure that bit-parser is able to handle even cases like this without a problem. Also note, we have codes from 9 to 15 "Reserved for Future Use. This situation is also quite common in embedded world when we whant to leave some space for future improvements (or vice versa - sometimes empty spaces in a protocol might appear after we improve something)
4. Byte0.bit2 ("LED is ON") in general looks the same as a bit representing one "thing" (case described in bullet 1). The difference here is that compared to simple case we are interested not only in getting to know when LED is ON, but also to know if LED is OFF. In other words, there should be always a line amongst our parsed lines saying whether LED is ON or OFF. 
           
Now having all these peculiarities in mind, let's define our parser for these two bytes:

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

def create_advanced_protocol_parser():
  def advanced_protocol_parser(bytes_to_parse):
      return parse_bits(bytes_to_parse, advanced_protocol)
  return advanced_protocol_parser

advanced_parser = create_advanced_protocol_parser()

pprint(advanced_parser("40 F0")) # spaces are allowed but are not mandatory
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
Let's try to switch LED ON...
```
pprint(advanced_parser("4C F0"))
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

## Installation

```
pip install -U bit-parser
```


## API Overview

TBD

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
