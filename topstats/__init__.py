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

from .bot import (
  Bot,
  PartialBot,
  Ranked,
  RecentBotStats,
  TimestampedBotStats,
)
from .client import Client
from .data import Period, SortBy, Timestamped
from .errors import Error, RequestError, Ratelimited

__title__ = 'topstats'
__author__ = 'null8626'
__license__ = 'MIT'
__copyright__ = 'Copyright (c) 2020 Arthurdw; Copyright (c) 2024 null8626'
__version__ = '1.0.0'
__all__ = (
  'Bot',
  'Client',
  'Error',
  'PartialBot',
  'Period',
  'RequestError',
  'Ranked',
  'Ratelimited',
  'RecentBotStats',
  'SortBy',
  'Timestamped',
  'TimestampedBotStats',
)
