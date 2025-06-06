from Tools.Settings import Settings
from Tools.BeautifulSoup import get_soup
from Tools.TeamCodes import translate_team_code_to_id

import pyodbc


class NFLGameLoader:
    def __init__(self):
        print('Loading NFL Games')
        settings = Settings()

        self.connection = pyodbc.connect(settings.CURRENT_CONNECTION_STRING)
        self.cursor = self.connection.cursor()

        url = 'https://www.pro-football-reference.com/years/2024/games.htm'

        current_game_id = 1329

        soup = get_soup(url)
        rows = soup.find_all("table")[0].find_all('tbody')[0].find_all('tr')
        for data in rows:
            week = data.find_all('th')[0].get_text()
            print(week)
            if 'Pre' in week:
                continue
            if week == 'Week':
                continue
            cols = data.find_all('td')
            link = cols[1].find("a", href=True)
            if link is None:
                continue

            date_link = link['href']
            date = date_link.split('/')[2].split('.')[0][:-4]
            year = date[:-4]
            month = date[4:-2]
            day = date[6:]
            away_link = cols[2].find("a", href=True)
            away = away_link['href'].split('/')[2].upper()
            away_team_id = translate_team_code_to_id(away)

            home_link = cols[5].find("a", href=True)
            home = home_link['href'].split('/')[2].upper()
            home_team_id = translate_team_code_to_id(home)
            time = cols[7].get_text()
            self.cursor.execute(
                "INSERT INTO NFLSchedule ([Id],[SeasonId], [Week], [HomeTeamId], [AwayTeamId], [StartTime],[BoxscoreLink]) VALUES (?,?,?,?,?,?,?)",
                current_game_id, 7, week, home_team_id, away_team_id, "{}-{}-{} {}".format(year, month, day, time), date_link)
            self.cursor.commit()
            print(
                "Week {} : {} ({}) @ {} ({}) {}/{}/{} {} {}".format(week, away, away_team_id, home, home_team_id, month, day, year,
                                                                    time, date_link))
            current_game_id += 1
