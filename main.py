from string import ascii_uppercase
from Tools.BeautifulSoup import get_soup
from Tools.TeamCodes import get_team_codes
from WeeklyUpdates.GameScorer import GameScorerModel

# Variables & Settings
POSITION_LIST = ['QB', 'RB', 'WR', 'TE', 'K']
LAST_ACTIVE_YEAR_CHECK = 2016
from WeeklyUpdates.NFLRoster import NFLRosterModel
from WeeklyUpdates.PlayerList import PlayerListModel
from NFLData.NFLGameLoader import NFLGameLoader
from NFLData.SeasonStatBuilder import SeasonStatBuilder
from NFLData.ProjectionStatBuilder import ProjectionStatBuilder
from NFLData.RookieLoader import RookieLoader

# rosters = NFLRosterModel()
# players = PlayerListModel()
# nflGames = NFLGameLoader()

# rookies = RookieLoader(2023)

# data = SeasonStatBuilder(2019, 2)
# data = SeasonStatBuilder(2020, 3)
# data = SeasonStatBuilder(2021, 4)
# data = SeasonStatBuilder(2022, 5)
# data = SeasonStatBuilder(2023, 6)

# data = ProjectionStatBuilder(6, 'draft')
# data = ProjectionStatBuilder(6, 11)
data = GameScorerModel(6, 11)

