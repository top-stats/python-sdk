# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2020 Arthurdw
# SPDX-FileCopyrightText: 2024-2026 null8626


class Error(Exception):
  """The base error class. Extends :py:class:`Exception`."""

  __slots__: tuple[str, ...] = ()


class RequestError(Error):
  """Thrown upon HTTP request failure. Extends :class:`~.errors.Error`."""

  __slots__: tuple[str, ...] = ('message', 'status')

  message: str | None
  """The message returned from the API."""

  status: int | None
  """The status code returned from the API."""

  def __init__(self, message: str | None, status: int | None):
    self.message = message
    self.status = status

    super().__init__(f'Got {status}: {self.message!r}')

  def __repr__(self) -> str:
    return f'<{__class__.__name__} message={self.message!r} status={self.status}>'


class Ratelimited(Error):
  """Thrown upon HTTP request failure due to the client being ratelimited. Because of this, the client is not allowed to make requests for a period of time. Extends :class:`~.errors.Error`."""

  __slots__: tuple[str, ...] = ('retry_after',)

  retry_after: float
  """How long the client should wait (in seconds) until it can make a request to the API again."""

  def __init__(self, retry_after: float):
    self.retry_after = retry_after

    super().__init__(
      f'The client is blocked by the API. Please try again in {retry_after} seconds.'
    )

  def __repr__(self) -> str:
    return f'<{__class__.__name__} retry_after={self.retry_after}>'
