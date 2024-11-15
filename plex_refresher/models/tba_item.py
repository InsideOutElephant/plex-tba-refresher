# plex_refresher/models/tba_item.py
from dataclasses import dataclass
from typing import Optional, Any

@dataclass
class TBAItem:
    title: str
    type: str  # 'movie' or 'episode'
    item: Any  # The actual Plex item
    year: Optional[str] = None
    show: Optional[str] = None
    season: Optional[int] = None
    episode: Optional[int] = None

    @classmethod
    def from_movie(cls, movie):
        return cls(
            title=movie.title,
            type='movie',
            year=getattr(movie, 'year', 'Unknown'),
            item=movie
        )

    @classmethod
    def from_episode(cls, episode, show):
        return cls(
            title=episode.title,
            type='episode',
            show=show.title,
            season=episode.seasonNumber,
            episode=episode.episodeNumber,
            item=episode
        )

    def __str__(self):
        if self.type == 'movie':
            return f"{self.title} ({self.year})"
        return f"{self.show} - S{self.season:02d}E{self.episode:02d} - {self.title}"

