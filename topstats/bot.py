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
from typing import Tuple, Union, List
from enum import Enum


class DataPoint:
  __slots__: Tuple[str, ...] = ('value',)

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

  __slots__: Tuple[str, ...] = ('rank',)

  rank: int
  """This data point's rank compared to others."""

  def __init__(self, json: dict, key: str):
    self.rank = json[f'{key}_rank']

    super().__init__(json[key])

  def __repr__(self) -> str:
    return f'<{__class__.__name__} value={self.value!r} rank={self.rank!r}>'


class Changed(DataPoint):
  """A changed data point in topstats.gg. This class contains a value and its change difference compared to the previous data point."""

  __slots__: Tuple[str, ...] = ('difference',)

  difference: int
  """This data point's change difference compared to the previous data point."""

  def __init__(self, json: dict, key: str):
    self.difference = json[f'{key}_change']

    super().__init__(json[key])

  def __repr__(self) -> str:
    return f'<{__class__.__name__} value={self.value!r} difference={self.difference!r}>'


class Period(Enum):
  """The requested time period for fetching historical bot graphs."""

  __slots__: Tuple[str, ...] = ()

  ALL_TIME = 'alltime'
  LAST_5_YEARS = '5y'
  LAST_3_YEARS = '3y'
  LAST_YEAR = '1y'
  LAST_90_DAYS = '90d'
  LAST_MONTH = '30d'
  LAST_WEEK = '7d'
  LAST_3_DAYS = '3d'
  LAST_DAY = '1d'
  LAST_12_HOURS = '12h'
  LAST_6_HOURS = '6h'

  def __repr__(self) -> str:
    return f'{__class__.__name__}.{self.name}'

  def __str__(self) -> str:
    return self.name.replace('_', ' ').title()


class HistoricalEntry(DataPoint):
  """A historical data point entry in topstats.gg. This class contains a value and its dated timestamp."""

  __slots__: Tuple[str, ...] = ('timestamp',)

  timestamp: datetime
  """Timestamp of this history entry."""

  def __init__(self, json: dict, key: str):
    self.timestamp = datetime.fromisoformat(json['time'])

    super().__init__(json[key])

  def __repr__(self) -> str:
    return f'<{__class__.__name__} value={self.value!r} timestamp={self.timestamp!r}>'


class RecentEntry:
  """A recent data point entry in topstats.gg. This class contains several data points and a dated timestamp."""

  __slots__: Tuple[str, ...] = (
    'timestamp',
    'monthly_votes',
    'total_votes',
    'server_count',
    'shard_count',
  )

  timestamp: datetime
  """Timestamp of this recent entry."""

  monthly_votes: Changed
  """Monthly votes at this timestamp alongside its change difference compared to the previous one."""

  total_votes: Changed
  """Total votes at this timestamp alongside its change difference compared to the previous one."""

  server_count: Changed
  """Server count at this timestamp alongside its change difference compared to the previous one."""

  shard_count: Changed
  """Shard count at this timestamp alongside its change difference compared to the previous one."""

  def __init__(self, json: dict):
    self.timestamp = datetime.fromisoformat(json['time'])
    self.monthly_votes = Changed(json, 'monthly_votes')
    self.total_votes = Changed(json, 'total_votes')
    self.server_count = Changed(json, 'server_count')
    self.shard_count = Changed(json, 'shard_count')

  def __repr__(self) -> str:
    return f'<{__class__.__name__} monthly_votes={self.monthly_votes!r} total_votes={self.total_votes!r} server_count={self.server_count!r} shard_count={self.shard_count!r} timestamp={self.timestamp!r}>'


class RecentGraph:
  """Recent graph of for the past 30 hours and past month."""

  __slots__: Tuple[str, ...] = (
    'hourly',
    'daily',
  )

  hourly: List[RecentEntry]
  """List of recent data entries for the past 30 hours."""

  daily: List[RecentEntry]
  """List of recent data entries for the past month."""

  def __init__(self, json: dict):
    self.hourly = [RecentEntry(entry) for entry in json['hourlyData']]
    self.daily = [RecentEntry(entry) for entry in json['dailyData']]

  def __repr__(self) -> str:
    return f'<{__class__.__name__} hourly={self.hourly!r} daily={self.daily!r}>'


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
    'daily_difference',
    'monthly_difference',
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

  timestamp: datetime
  """The date when this bot was last updated by topstats.gg."""

  daily_difference: float
  """Difference percentage from the previous day."""

  monthly_difference: float
  """Difference percentage from the previous month."""

  def __init__(self, json: dict):
    self.id = int(json['id'])
    self.owners = [int(i) for i in (json.get('owners') or ())]
    self.is_deleted = json['deleted']
    self.name = json['name']
    self.short_description = json['short_desc']
    self.prefix = json['prefix']
    self.website = json['website']
    self.approved_at = datetime.fromisoformat(json['approved_at'])
    self.monthly_votes = Ranked(json, 'monthly_votes')
    self.server_count = Ranked(json, 'server_count')
    self.total_votes = Ranked(json, 'total_votes')
    self.shard_count = Ranked(json, 'shard_count')
    self.timestamp = datetime.fromisoformat(json['timestamp'])
    self.daily_difference = float(json['percentageChanges']['daily'])
    self.monthly_difference = float(json['percentageChanges']['monthly'])

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
    """The date when this bot was created."""

    return datetime.fromtimestamp(
      ((self.id >> 22) + 1420070400000) // 1000, tz=timezone.utc
    )
