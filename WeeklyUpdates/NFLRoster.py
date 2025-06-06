from selenium.common import NoSuchElementException
from selenium import webdriver
from selenium.webdriver.chrome.service import Service

from Tools.BeautifulSoup import get_soup
from Tools.TeamCodes import translate_team_id_to_code
from Tools.Settings import Settings

from selenium.webdriver.common.by import By
import pyodbc


class NFLRosterModel:
    def __init__(self):
        print('Updating Rosters')
        settings = Settings()
        self.POSITION_LIST = settings.POSITION_LIST

        self.connection = pyodbc.connect(settings.CURRENT_CONNECTION_STRING)
        self.connection1 = pyodbc.connect(settings.CURRENT_CONNECTION_STRING)
        self.cursor = self.connection.cursor()

        for team_id in range(1, 33):
            team = translate_team_id_to_code(team_id).lower()
            print(f"Currently on team id: {team_id}")
            url = f'https://www.pro-football-reference.com/teams/{team}/2024_roster.htm'
            print(url)

            service = Service()
            options = webdriver.ChromeOptions()
            options.add_argument("enable-automation")
            options.add_argument("--headless")
            options.add_argument("--window-size=1920,1080")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-extensions")
            options.add_argument("--dns-prefetch-disable")
            # options.add_argument("--disable-gpu")
            driver = webdriver.Chrome(service=service, options=options)
            driver.get(url)

            player_table = driver.find_elements(By.ID, 'roster')
            if player_table is not None:
                self.clear_players_on_team(team_id)
                player_rows = player_table[0].find_elements(By.TAG_NAME, 'tbody')[0].find_elements(By.TAG_NAME, 'tr')
                for player in player_rows:
                    self.parse_player_row(player, team_id)

    def parse_player_row(self, player, team_id):
        player_columns = player.find_elements(By.TAG_NAME, 'td')
        if len(player_columns) > 0:
            player_name = player_columns[0].text
            print(player_name)
            player_position = player_columns[2].text
            if '/' in player_position:
                player_position = player_position.split('/')[0]
            if player_position in self.POSITION_LIST:
                try:
                    player_anchor = player.find_element(By.TAG_NAME, 'a')
                    if player_anchor is not None:

                        player_key = player_anchor.get_attribute('href').split('/')[5].split('.')[0]
                        if player_key != '':
                            player_id = self.get_player_id(player_key)

                            if player_id is None:

                                print(f"player key :{player_key}")
                                player_href = player_anchor.get_attribute('href').split('.com')[1]
                                print(f"player href :{player_href}")

                                self.add_missing_player(player_name, player_href, player_key, player_position, team_id, player_columns)
                            else:
                                self.update_player_team(player_id, team_id)
                except NoSuchElementException:
                    return


    def clear_players_on_team(self, nfl_team_id):
        self.cursor.execute("UPDATE Players SET [NFLTeamId] = Null WHERE NFLTeamId = ? AND Id > 0", nfl_team_id)
        self.cursor.commit()

    def update_player_team(self, player_id, nfl_team_id):
        self.cursor.execute("UPDATE Players SET [NFLTeamId] = ?, [Retired] = ? WHERE Id = ?", nfl_team_id, False, player_id)
        self.cursor.commit()

    def get_player_id(self, player_key):
        cursor = self.connection1.cursor()
        cursor.execute("SELECT Id FROM Players WHERE [ProReferenceKey] = ?", player_key)
        for row in cursor.fetchall():
            player_id = row[0]
            return player_id

    def add_missing_player(self, player_name, player_href, player_key, position, team_id, player_columns):
        print(f'No Player Found for {player_name}')

        player_name = player_name.replace(" (IR)", " ")
        player_name = player_name.replace(" (PUP)", " ")
        player_name = player_name.replace(" (IRD)", " ")
        player_name = player_name.replace(" (IR)", " ")
        player_name = player_name.replace(" (NON)", " ")
        player_name = player_name.replace(" (SUS)", " ")
        weight = player_columns[5].text
        height = player_columns[6].text
        playerCollege = player_columns[7].text

        date_of_birth = player_columns[8].text
        is_rookie = player_columns[9].text == 'Rook'

        playerUrl = 'https://www.pro-football-reference.com{}'.format(player_href)

        playerSoup = get_soup(playerUrl)
        jerseyContainer = playerSoup.find("div", {"class": "uni_holder"}).find_all('text');
        jerseyNumber = ''
        if len(jerseyContainer) > 0:
            jerseyNumber = jerseyContainer[-1].get_text()

        names = player_name.split(" ")
        first = names[0]
        last = ''
        for name in names[1:]:
            last = last + ' ' + name
        team = team_id



        print("{} {} {} {} {} {} {} {} {} {} {} {}".format(player_key, player_href, first.strip(),
                                                           last.strip(), team, date_of_birth, jerseyNumber,
                                                           is_rookie, position, playerCollege, jerseyNumber,
                                                           date_of_birth, height, weight))


        self.cursor.execute(
            "INSERT INTO Players ([ProReferenceKey],[ProReferenceURL], [FullName],[FirstName], [LastName], [NFLTeamId], [JerseyNumber], [Rookie], [Position], [College], [DateOfBirth], [Height], [Weight],[TradingBlock], [Retired],[WeeksLeftOnIR]) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            player_key, player_href, player_name, first.strip(), last.strip(), team, jerseyNumber, is_rookie,
            position, playerCollege, date_of_birth, height, weight, False, False, 0)
        self.cursor.commit()
