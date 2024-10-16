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

from datetime import datetime, timezone
from typing import Any, Tuple, Union, List
from enum import Enum


class DataPoint:
  __slots__ = ('value',)

  value: int
  """This data point's value."""

  def __init__(self, value: int):
    self.value = value

  def __int__(self) -> int:
    return self.value

  def __float__(self) -> float:
    return float(self.value)

  def __str__(self) -> str:
    return str(self.value)

  def __eq__(self, other: Union['DataPoint', float, int]) -> bool:
    return self.value == float(other)

  def __lt__(self, other: Union['DataPoint', float, int]) -> bool:
    return self.value < float(other)

  def __gt__(self, other: Union['DataPoint', float, int]) -> bool:
    return self.value > float(other)

  def __le__(self, other: Union['DataPoint', float, int]) -> bool:
    return self.value <= float(other)

  def __ge__(self, other: Union['DataPoint', float, int]) -> bool:
    return self.value >= float(other)


class Ranked(DataPoint):
  """A ranked data point in topstats.gg. This class contains a value and its rank compared to others."""

  __slots__ = ('rank',)

  rank: int
  """This data point's rank compared to others."""

  def __init__(self, json: dict, key: str):
    self.rank = json[f'{key}_rank']

    super().__init__(json[key])

  def __repr__(self) -> str:
    return f'<{__class__.__name__}({self.value}, #{self.rank})>'


class Period(Enum):
  """The requested period for fetching historical bot graphs."""

  __slots__: Tuple[str, ...] = ()

  ALL_TIME = 'alltime'
  LAST_5_YEARS = '5y'
  LAST_3_YEARS = '3y'
  LAST_YEAR = '1y'
  LAST_90_DAYS = '90d'
  LAST_30_DAYS = '30d'
  LAST_WEEK = '7d'
  LAST_3_DAYS = '3d'
  LAST_DAY = '1d'
  LAST_12_HOURS = '12h'
  LAST_6_HOURS = '6h'

  def __repr__(self) -> str:
    return f'{__class__.__name__}.{self.name}'

  def __str__(self) -> str:
    return self.name.replace('_', ' ').title()


class HistoryEntry(DataPoint):
  """A historical data point entry in topstats.gg. This class contains a value and its dated timestamp."""

  __slots__: Tuple[str, ...] = ('timestamp',)

  timestamp: datetime
  """Timestamp of this history entry."""

  def __init__(self, json: dict, key: str):
    self.timestamp = datetime.strptime(
      json['time'], '%Y-%m-%dT%H:%M:%S.%fZ', tz=timezone.utc
    )

    super().__init__(json[key])

  def __repr__(self) -> str:
    return f'<{__class__.__name__}({self.value} at {self.timestamp.strftime("%-d %B %Y %H:%M:%S")} UTC)>'


class Bot:
  """A bot listed in topstats.gg."""

  __slots__: Tuple[str, ...] = (
    'id',
    'owners',
    'is_deleted',
    'name',
    'avatar',
    'short_description',
    'prefix',
    'website',
    'approved_at',
    'monthly_votes',
    'server_count',
    'total_votes',
    'shard_count',
    'timestamp',
    'updated_at',
  )

  id: int
  """The ID of this bot."""

  owners: List[int]
  """A list of IDs of this bot's owners."""

  is_deleted: bool
  """Whether this bot is deleted or not."""

  name: str
  """The username of this bot."""

  avatar: str
  """The bot's avatar URL. Its format will either be PNG or GIF if animated."""

  short_description: str
  """The short description of this bot."""

  prefix: str
  """The prefix of this bot."""

  website: str
  """The website URL of this bot."""

  approved_at: datetime
  """The date when this bot was approved on Top.gg."""

  monthly_votes: Ranked
  """The amount of upvotes this bot has this month including its rank compared to others."""

  server_count: Ranked
  """The amount of servers this bot is in according to posted stats including its rank compared to others."""

  total_votes: Ranked
  """The amount of upvotes this bot has regardless of timeframe including its rank compared to others."""

  shard_count: Ranked
  """The amount of shards this bot has according to posted stats including its rank compared to others."""

  updated_at: datetime
  """The date when this bot was last updated by topstats.gg."""

  def __init__(self, json: dict):
    self.id = int(json['id'])
    self.owners = [int(i) for i in (json.get('owners') or ())]
    self.is_deleted = json['deleted']
    self.name = json['name']
    self.avatar = get_avatar(json.get('avatar'), self.id)
    self.short_description = json['short_desc']
    self.prefix = json['prefix']
    self.website = json['website']
    self.approved_at = datetime.strptime(
      json['approved_at'], '%Y-%m-%dT%H:%M:%S.%fZ', tz=timezone.utc
    )
    self.monthly_votes = Ranked(json, 'monthly_votes')
    self.server_count = Ranked(json, 'server_count')
    self.total_votes = Ranked(json, 'total_votes')
    self.shard_count = Ranked(json, 'shard_count')
    self.updated_at = datetime.fromtimestamp(
      int(json['unix_timestamp']) // 1000, tz=timezone.utc
    )

    if avatar := json.get('avatar'):
      ext = 'gif' if avatar.startswith('a_') else 'png'

      self.avatar = (
        f'https://cdn.discordapp.com/avatars/{self.id}/{avatar}.{ext}?size=1024'
      )
    else:
      self.avatar = (
        f'https://cdn.discordapp.com/embed/avatars/{(self.id >> 22) % 6}.png'
      )

  def __int__(self) -> int:
    return self.id

  def __eq__(self, other: 'Bot') -> bool:
    if isinstance(other, Bot):
      return self.id == other.id

    return NotImplemented

  def __repr__(self) -> str:
    return f'<{__class__.__name__} id={self.id} name={self.name!r} monthly_votes={self.monthly_votes!r} server_count={self.server_count!r} total_votes={self.total_votes!r}>'

  @property
  def created_at(self) -> datetime:
    """The bot's creation time in UTC."""

    return datetime.fromtimestamp(
      ((self.id >> 22) + 1420070400000) // 1000, tz=timezone.utc
    )
