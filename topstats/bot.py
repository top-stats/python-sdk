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

import datetime
from typing import Tuple, Union, List

from .util import get_avatar


class Ranked:
  """Represents a ranked data point in topstats.gg. This class contains a value and its rank compared to others."""

  __slots__ = ('value', 'rank')

  """This data point's value."""
  value: int

  """This data point's rank compared to others."""
  rank: int

  def __init__(self, json: dict, key: str):
    self.value = json[key]
    self.rank = json[f'{key}_rank']

  def __int__(self) -> int:
    return self.value

  def __str__(self) -> str:
    return str(self.value)

  def __eq__(self, other: Union['Ranked', int]) -> bool:
    return self.value == int(other)

  def __lt__(self, other: Union['Ranked', int]) -> bool:
    return self.value < int(other)

  def __gt__(self, other: Union['Ranked', int]) -> bool:
    return self.value > int(other)

  def __le__(self, other: Union['Ranked', int]) -> bool:
    return self.value <= int(other)

  def __ge__(self, other: Union['Ranked', int]) -> bool:
    return self.value >= int(other)

  def __repr__(self) -> str:
    return f'<{__class__.__name__}({self.value}, #{self.rank})>'


class Bot:
  """Represents a bot listed in topstats.gg."""

  __slots__: Tuple[str, ...] = (
    'id',
    'is_certified',
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
  )

  id: int
  """The ID of this bot."""

  is_certified: bool
  """Whether this bot is Top.gg certified or not."""

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

  shard_count: int
  """The amount of shards this bot has according to posted stats."""

  timestamp: datetime
  """TODO: document this???"""

  def __init__(self, json: dict):
    self.id = int(json['id'])
    self.is_certified = json['certified']
    self.owners = [int(i) for i in json['owners']]
    self.is_deleted = json['deleted']
    self.name = json['name']
    self.avatar = get_avatar(json['avatar'], self.id)
    self.short_description = json['short_desc']
    self.prefix = json['prefix']
    self.website = json['website']
    self.approved_at = datetime.datetime.strptime(
      json['approved_at'], '%Y-%m-%dT%H:%M:%S.%fZ'
    )
    self.monthly_votes = Ranked(json, 'monthly_votes')
    self.server_count = Ranked(json, 'server_count')
    self.total_votes = Ranked(json, 'total_votes')
    self.shard_count = json['shard_count']
    self.timestamp = datetime.datetime.fromtimestamp(
      int(json['unix_timestamp']) // 1000, tz=datetime.timezone.utc
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

    return datetime.datetime.fromtimestamp(
      ((self.id >> 22) + 1420070400000) // 1000, tz=datetime.timezone.utc
    )
