from typing import Optional


# TODO: make this a part of some abstract Bot class
def get_avatar(avatar: Optional[str], id: int) -> str:
  if avatar is None:
    return f'https://cdn.discordapp.com/embed/avatars/{(id >> 22) % 6}.png'
  else:
    ext = 'gif' if avatar.startswith('a_') else 'png'

    return f'https://cdn.discordapp.com/avatars/{id}/{avatar}.{ext}?size=1024'
