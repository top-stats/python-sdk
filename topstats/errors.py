"""
The MIT License (MIT)

Copyright (c) 2020 Arthurdw
Copyright (c) 2024 null8626

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from typing import Tuple, Optional


class Error(Exception):
  """Represents a topstats error class. Extends :py:class:`Exception`."""

  __slots__: Tuple[str, ...] = ()


class RequestError(Error):
  """Thrown upon HTTP request failure. Extends :class:`~.errors.Error`."""

  __slots__: Tuple[str, ...] = ('message',)

  message: Optional[str]
  """The message returned from the topstats.gg API. This can be ``None``."""

  def __init__(self, json: dict):
    self.message = json['message']

    super().__init__()


class Ratelimited(RequestError):
  """Thrown upon HTTP request failure due to being ratelimited and not allowed to make requests for a period of time. Extends :class:`~.errors.RequestError`."""

  __slots__: Tuple[str, ...] = ('retry_after',)

  retry_after: int
  """How long you should wait until you can make a request to this endpoint again."""

  def __init__(self, json: dict):
    self.retry_after = int(json['retry_after'])

    super().__init__(json)
