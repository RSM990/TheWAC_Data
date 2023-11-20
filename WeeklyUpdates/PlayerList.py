from Tools.BeautifulSoup import get_soup
from string import ascii_uppercase
from Tools.Settings import Settings
from Tools.TeamCodes import translate_team_code_to_id
import pyodbc


class PlayerListModel:
    def __init__(self):
        settings = Settings()
        self.LAST_ACTIVE_YEAR_CHECK = settings.LAST_ACTIVE_YEAR_CHECK
        self.POSITION_LIST = settings.POSITION_LIST

        self.connection = pyodbc.connect(settings.CURRENT_CONNECTION_STRING)
        self.cursor = self.connection.cursor()

        for letter in ascii_uppercase:
            print(letter)
            soup = get_soup(f'https://www.pro-football-reference.com/players/{letter}/')

            players = soup.find("div", {"id": "div_players"}).find_all('p')
            for player in players:
                if int(player.get_text().split('-')[-1]) < self.LAST_ACTIVE_YEAR_CHECK:
                    continue

                retired = True
                if len(player.find_all('b')) > 0:
                    retired = False

                player_link = player.find("a", href=True)
                player_reference = player_link['href'].split('/')[3].split('.')[0]
                player_full_name = player_link.get_text()

                position = player.get_text().split('(')[1][0:-1].split(')')[0]
                if position in self.POSITION_LIST:
                    print(player_full_name)
                    player_soup = get_soup(f'https://www.pro-football-reference.com{player_link["href"]}')
                    jersey_number = self.get_jersey_number(player_soup)
                    current_team = self.get_current_team(player_soup)
                    player_id = self.get_player_id(player_reference)

                    if player_id is not None:
                        self.update_player(player_id, retired, jersey_number, current_team)

    def get_jersey_number(self, soup):
        jersey_number = ''
        jersey = soup.find("div", {"class": "uni_holder"})
        if jersey is not None:
            jersey_container = jersey.find_all('text')
            if len(jersey_container) > 0:
                jersey_number = jersey_container[-1].get_text()
        return jersey_number


    def get_current_team(self, soup):
        info_section = soup.find("div", {"id": "meta"})
        team_info = info_section.find("strong", text="Team")
        team = ''
        if team_info is not None:
            team_code = team_info.parent.find('a', href=True)['href'].split('/')[2]
            team = translate_team_code_to_id(team_code.upper())

        return team

    def update_player(self, player_id, retired, jersey_number, current_team):
        print(f'Player Id: {player_id} ({jersey_number}) Current Team Id: {current_team} Retired: {retired}')
        if not current_team:
            self.cursor.execute("UPDATE Players SET [JerseyNumber] = ?,[Retired] = ?,[NFLTeamId] = ? WHERE Id = ?",
                                jersey_number, retired, None, player_id)
        else:
            self.cursor.execute("UPDATE Players SET [JerseyNumber] = ?,[Retired] = ?,[NFLTeamId] = ? WHERE Id = ?",
                                jersey_number, retired, current_team, player_id)
        self.cursor.commit()

    def get_player_id(self, player_key):
        self.cursor.execute("SELECT Id FROM Players WHERE [ProReferenceKey] = ?", player_key)
        for row in self.cursor.fetchall():
            player_id = row[0]
            return player_id
