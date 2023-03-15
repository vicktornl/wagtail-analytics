from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Tuple


@dataclass
class TopPage:
    url: str
    pageviews: int


@dataclass
class TopSource:
    name: str
    pageviews: int


@dataclass
class Report:
    visitors_this_week: List[Tuple[datetime, int]]
    visitors_last_week: List[Tuple[datetime, int]]
    top_pages: List[TopPage]
    top_sources: List[TopSource]
