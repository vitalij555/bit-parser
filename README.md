![Upload Python Package](https://github.com/vitalij555/bit-parser/workflows/Upload%20Python%20Package/badge.svg)
[![PyPi version](https://img.shields.io/pypi/v/bit-parser.svg?style=flat-square) ](https://pypi.python.org/pypi/bit-parser) [![Supported Python versions](https://img.shields.io/pypi/pyversions/bit-parser.svg?style=flat-square) ](https://pypi.org/project/bit-parser) [![License](https://img.shields.io/pypi/l/bit-parser.svg?style=flat-square) ](https://choosealicense.com/licenses) [![Downloads](https://pepy.tech/badge/bit-parser)](https://pepy.tech/project/bit-parser) [![codecov](https://codecov.io/gh/vitalij555/bit-parser/branch/master/graph/badge.svg)](https://codecov.io/gh/vitalij555/bit-parser)

# bit-parser

This is a configurable parser allowing you to describe all bits in a byte representing bit field set (or a bit map) and convert it into a human-readable form.  

It allows to parse bit maps consisting of several bytes, where each bit has its own meaning. Cases where several bits encode one parameter (like status code or counter) are covered as well. Also, special helpers are provided for cases where several consecutive bits represent the same value (for example RFU - Reserved for Future Use bits).

This module is not intended for parsing complex streaming protocols or protocols containing many hundreds and thousands of bytes of information, but it can be very useful as a component of more complex parsers or as a parser of parts of protocols contained in log files to make them easier for people to understand.

Currently, bit-parser is only able to parse binary data provided in a form of hexadecimal string (i.e. "FA 02 44", for example). If you are working with real binary data and want to convert it to a hexadecimal     

## Contents

- [Motivation](#motivation)
- [Installation](#installation)
- [Example](#example)
- [Constructor](#constructor)
- [API Overview](#api-overview)
- [Tests](#tests)
- [License](#license)
- [Contributing](#contribute)


## Motivation

Let's imagine we are working in an IoT area and for current project we need to deal with some very simple protocol: controller sends command to one of its peripherals and gets back status of its I/O pins. As a result of such a request we get several bytes of a response, one byte of which encodes situation on I/O pins. There "1" means high voltage level on CPU pin and "0" means low. We can describe our byte of interest as follows:

```text
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
print(parseBits("A3", bits_meaning))

```


## Installation

```
pip install -U bit-parser
```


## Example

```python

```



## Constructor

```python

```


**Parameters**

- `eventNames` - `list of any` - mandatory, provides list of all supported events. Values provided here can be used for raising events later.
 Values provided in this list can be of any type.
- `logger` - `object` - optional, logger supporting standard logging methods (info, warning error, etc..), default: `None`. 
If None is provided, then internal logger outputting warnings and errors to console will be created.



**Example**

Any object can be used as event name. Example below illustrates that:

```python
```


## API Overview


### subscribe(eventName, subscriber) 

**Description**


**Parameters**

- `eventName` - `any` - mandatory, specifies name of the event, subscriber will be interested in.
- `subscriber` - `any` - mandatory, callable subscriber (function, class method or class with __call__ implemented)

**Example**

```python
```


### subscribe_to_all(subscriber):

**Description**

Method allows to register one callable for all events supported by notifier.


**Parameters**

- `subscriber` - `callable` - mandatory, will be called when event rises.

**Example**

```python

```

Console output:

```console
Event onCreate at path some\path\here is called with following simple args: ['onCreate'] and with following keyword args: {'fileName': 'test_file.txt'}
Event onOpen at path some\path\here is called with following simple args: ['onOpen'] and with following keyword args: {'openMode': 'w+', 'fileName': 'test_file.txt'}
```


### get_registered_events():

**Description**

Returns all supported events as a list.

**Example**

```python
from EventNotifier import Notifier
notifier = Notifier(["onCreate", "onOpen", "onModify", "onClose", "onDelete"])
print(notifier.get_registered_events())
```
will output:
```console
['onCreate', 'onOpen', 'onModify', 'onClose', 'onDelete']
```


### raise_event(eventName, *args, **kwargs)

**Description**

Rises specific event registered during initialization.

**Parameters**

- `eventName` - `any` - mandatory, name of the event to be raised.
- `*args` - `list` - optional, all simple parameters we want to pass to our subscribers (param1, param2, param3...).
- `**kwargs` - `dictionary` - optional, all named parameters we want to pass (param1=value1, param2=value2, param3=value3) 

**Example**

Check subscribe method's example link [above](#subscribeeventname-subscriber).


### remove_subscribers_by_event_name(event_name)

**Description**

Removes all subscribers for the specified event_name

**Parameters**

- `eventName` - `any` - mandatory, name of the event we want to remove subscribers for.

**Example**

```python
from EventNotifier import Notifier
class FileWatchDog():
    def onOpen(self, fileName, openMode):
        print(f"File {fileName} opened with {openMode} mode")

    def onClose(self, fileName):
        print(f"File {fileName} closed")


def onOpenStandaloneMethod(fileName, openMode):
    print(f"StandaloneMethod: File {fileName} opened with {openMode} mode")

watchDog = FileWatchDog()

notifier = Notifier(["onCreate", "onOpen", "onModify", "onClose", "onDelete"])

notifier.subscribe("onOpen", watchDog.onOpen)
notifier.subscribe("onOpen", onOpenStandaloneMethod)
notifier.subscribe("onClose", watchDog.onClose)

print("\nAfter subscription:")
notifier.raise_event("onOpen", openMode="w+", fileName="test_file.txt")  # order of named parameters is not important
notifier.raise_event("onClose", fileName="test_file.txt")

notifier.remove_subscribers_by_event_name("onOpen")

print("\nAfter removal of onOpen subscribers:")
notifier.raise_event("onOpen", openMode="w+", fileName="test_file.txt")  # order of named parameters is not important
notifier.raise_event("onClose", fileName="test_file.txt")

notifier.remove_subscribers_by_event_name("onClose")

print("\nAfter removal of onClose subscribers:")
notifier.raise_event("onOpen", openMode="w+", fileName="test_file.txt")  # order of named parameters is not important
notifier.raise_event("onClose", fileName="test_file.txt")
```

will output:
```console
After subscription:
File test_file.txt opened with w+ mode
StandaloneMethod: File test_file.txt opened with w+ mode
File test_file.txt closed

After removal of onOpen subscribers:
File test_file.txt closed

After removal of onClose subscribers:
```


### remove_all_subscribers()

**Description**

Removes all subscribers for all events

**Example**

```python
from EventNotifier import Notifier
class FileWatchDog():
    def onOpen(self, fileName, openMode):
        print(f"File {fileName} opened with {openMode} mode")

    def onClose(self, fileName):
        print(f"File {fileName} closed")


def onOpenStandaloneMethod(fileName, openMode):
    print(f"StandaloneMethod: File {fileName} opened with {openMode} mode")

watchDog = FileWatchDog()

notifier = Notifier(["onCreate", "onOpen", "onModify", "onClose", "onDelete"])

notifier.subscribe("onOpen", watchDog.onOpen)
notifier.subscribe("onOpen", onOpenStandaloneMethod)
notifier.subscribe("onClose", watchDog.onClose)

print("\nAfter subscription:")
notifier.raise_event("onOpen", openMode="w+", fileName="test_file.txt")
notifier.raise_event("onClose", fileName="test_file.txt")

notifier.remove_all_subscribers()

print("\nAfter removal of all subscribers:")
notifier.raise_event("onOpen", openMode="w+", fileName="test_file.txt")
notifier.raise_event("onClose", fileName="test_file.txt")
```

will give:
```console
After subscription:
File test_file.txt opened with w+ mode
StandaloneMethod: File test_file.txt opened with w+ mode
File test_file.txt closed

After removal of all subscribers:
```



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
pytest --cov=../EventNotifier --cov-report=html
```

## License

License
Copyright (C) 2020 Vitalij Gotovskij

event-notifier binaries and source code can be used according to the MIT License


## Contribute
TBD
