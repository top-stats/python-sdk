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

from typing import List, Optional, Tuple, Union
from datetime import datetime, timezone

from .data import Ranked


class BotStats:
  __slots__: Tuple[str, ...] = (
    'monthly_votes',
    'total_votes',
    'server_count',
    'shard_count',
  )

  monthly_votes: Ranked
  """This bot's monthly votes."""

  total_votes: Ranked
  """This bot's total votes."""

  server_count: Ranked
  """This bot's server count."""

  shard_count: Ranked
  """This bot's shard count."""

  def __init__(self, json: dict):
    self.monthly_votes = Ranked(json, 'monthly_votes')
    self.total_votes = Ranked(json, 'total_votes')
    self.server_count = Ranked(json, 'server_count')
    self.shard_count = Ranked(json, 'shard_count')


class TimestampedBotStats(BotStats):
  """A timestamped bot stats in topstats.gg. This class contains several data points and their dated timestamp."""

  __slots__: Tuple[str, ...] = ('timestamp',)

  timestamp: datetime
  """Dated timestamp of this bot's stats."""

  def __init__(self, json: dict):
    self.timestamp = datetime.fromisoformat(json['time'].replace('Z', '+00:00'))

    super().__init__(json)

  def __repr__(self) -> str:
    return f'<{__class__.__name__} monthly_votes={self.monthly_votes!r} total_votes={self.total_votes!r} server_count={self.server_count!r} shard_count={self.shard_count!r} timestamp={self.timestamp!r}>'


class RecentBotStats:
  """A list of a ranked bot's recent stats for the past 30 hours and past month."""

  __slots__: Tuple[str, ...] = (
    'hourly',
    'daily',
  )

  hourly: List[TimestampedBotStats]
  """A list of this bot's stats for the past 30 hours."""

  daily: List[TimestampedBotStats]
  """A list of this bot's stats for the past month."""

  def __init__(self, json: dict):
    self.hourly = [TimestampedBotStats(entry) for entry in json['hourlyData']]
    self.daily = [TimestampedBotStats(entry) for entry in json['dailyData']]

  def __repr__(self) -> str:
    return f'<{__class__.__name__} hourly={self.hourly!r} daily={self.daily!r}>'


class PartialBot(BotStats):
  """A brief information of a ranked bot in topstats.gg."""

  __slots__: Tuple[str, ...] = ('id', 'name')

  id: int
  """The ID of this bot."""

  name: str
  """The username of this bot."""

  def __init__(self, json: dict):
    self.id = int(json['id'])
    self.name = json['name']

    super().__init__(json)

  def __repr__(self) -> str:
    return f'<{self.__class__.__name__} id={self.id} name={self.name!r} monthly_votes={self.monthly_votes!r} server_count={self.server_count!r} total_votes={self.total_votes!r}>'

  def __int__(self) -> int:
    return self.id

  def __eq__(self, other: Union['PartialBot', 'Bot']) -> bool:
    if isinstance(other, __class__):
      return self.id == other.id

    return NotImplemented

  @property
  def created_at(self) -> datetime:
    """The date when this bot was created."""

    return datetime.fromtimestamp(
      ((self.id >> 22) + 1420070400000) // 1000, tz=timezone.utc
    )


class Bot(PartialBot):
  """A detailed information of a ranked bot in topstats.gg."""

  __slots__: Tuple[str, ...] = (
    'owners',
    'tags',
    'is_deleted',
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

  owners: List[int]
  """A list of this bot's owner IDs."""

  tags: List[str]
  """A list of this bot's tags."""

  is_deleted: bool
  """Whether this bot is deleted or not."""

  avatar: str
  """This bot's avatar URL. Its format will either be PNG or GIF if animated."""

  short_description: str
  """The short description of this bot."""

  prefix: str
  """The prefix of this bot."""

  website: str
  """The website URL of this bot."""

  approved_at: datetime
  """The date when this bot was approved on Top.gg."""

  timestamp: datetime
  """The date when this bot was last updated by topstats.gg."""

  daily_difference: Optional[float]
  """Difference percentage from the previous day. This can be :py:obj:`None`."""

  monthly_difference: Optional[float]
  """Difference percentage from the previous month. This can be :py:obj:`None`."""

  def __init__(self, json: dict):
    self.owners = [int(i) for i in (json.get('owners') or ())]
    self.tags = json.get('tags') or []
    self.is_deleted = json['deleted']
    self.short_description = json['short_desc']
    self.prefix = json['prefix']
    self.website = json['website']
    self.approved_at = datetime.fromisoformat(
      json['approved_at'].replace('Z', '+00:00')
    )
    self.timestamp = datetime.fromtimestamp(
      int(json['unix_timestamp']) // 1000, tz=timezone.utc
    )

    if percentage_changes := json.get('percentageChanges'):
      daily = percentage_changes.get('daily')
      monthly = percentage_changes.get('monthly')

      self.daily_difference = daily and float(daily)
      self.monthly_difference = monthly and float(monthly)
    else:
      self.daily_difference = None
      self.monthly_difference = None

    snowflake = int(json['id'])

    if avatar := json.get('avatar'):
      ext = 'gif' if avatar.startswith('a_') else 'png'

      self.avatar = (
        f'https://cdn.discordapp.com/avatars/{snowflake}/{avatar}.{ext}?size=1024'
      )
    else:
      self.avatar = (
        f'https://cdn.discordapp.com/embed/avatars/{(snowflake >> 22) % 6}.png'
      )

    super().__init__(json)
