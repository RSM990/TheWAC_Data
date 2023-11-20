import pyodbc

from selenium.common import NoSuchElementException
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

from Tools.BeautifulSoup import get_soup
from Tools.Settings import Settings
from Tools.TeamCodes import translate_team_id_to_code, translate_team_code_to_id


class GameScorerModel:
    def __init__(self, season, week):
        settings = Settings()
        self.connection = pyodbc.connect(settings.CURRENT_CONNECTION_STRING)
        self.cursor = self.connection.cursor()
        self.Score_Offense(season, week)
        self.score_kicking(season, week)
        self.score_other_offense(season, week)
        self.score_defense(season, week)


    def GetPlayerId(self, player_name):
        self.cursor.execute("SELECT Id FROM Players WHERE [ProReferenceKey] = ?", player_name)
        for row in self.cursor.fetchall():
            player_id = row[0]
            return player_id

    def Score_Offense(self, seasonId, currentWeek):
        self.cursor.execute("SELECT BoxscoreLink FROM NFLSchedule WHERE [SeasonId] = ? AND [Week] = ?", seasonId,
                       currentWeek)
        for row in self.cursor.fetchall():
            link = row[0]
            print(link)

            url = 'https://www.pro-football-reference.com{}'.format(link)
            soup = get_soup(url)

            offensiveTable = soup.find("table", id="player_offense")
            if offensiveTable is not None:
                for player in offensiveTable.find_all('tbody')[0].find_all('tr'):
                    playerKey = ''

                    if len(player.findAll('th')[0].findAll('a', href=True)) > 0:
                        playerKey = player.findAll('th')[0].findAll('a', href=True)[0]['href'].split('/')[3].split('.')[
                            0]

                    if playerKey != '':
                        playerId = self.GetPlayerId(playerKey)
                        pass_att = 0
                        if len(player.findAll("td", {"data-stat": "pass_att"})) > 0:
                            pass_att = player.findAll("td", {"data-stat": "pass_att"})[0].get_text()

                        pass_cmp = 0
                        if len(player.findAll("td", {"data-stat": "pass_cmp"})) > 0:
                            pass_cmp = player.findAll("td", {"data-stat": "pass_cmp"})[0].get_text()

                        pass_yds = 0
                        if len(player.findAll("td", {"data-stat": "pass_yds"})) > 0:
                            pass_yds = player.findAll("td", {"data-stat": "pass_yds"})[0].get_text()

                        pass_td = 0
                        if len(player.findAll("td", {"data-stat": "pass_td"})) > 0:
                            pass_td = player.findAll("td", {"data-stat": "pass_td"})[0].get_text()

                        pass_int = 0
                        if len(player.findAll("td", {"data-stat": "pass_int"})) > 0:
                            pass_int = player.findAll("td", {"data-stat": "pass_int"})[0].get_text()

                        rush_yds = 0
                        if len(player.findAll("td", {"data-stat": "rush_yds"})) > 0:
                            rush_yds = player.findAll("td", {"data-stat": "rush_yds"})[0].get_text()

                        rush_att = 0
                        if len(player.findAll("td", {"data-stat": "rush_att"})) > 0:
                            rush_att = player.findAll("td", {"data-stat": "rush_att"})[0].get_text()

                        rush_td = 0
                        if len(player.findAll("td", {"data-stat": "rush_td"})) > 0:
                            rush_td = player.findAll("td", {"data-stat": "rush_td"})[0].get_text()

                        targets = 0
                        if len(player.findAll("td", {"data-stat": "targets"})) > 0:
                            targets = player.findAll("td", {"data-stat": "targets"})[0].get_text()

                        rec = 0
                        if len(player.findAll("td", {"data-stat": "rec"})) > 0:
                            rec = player.findAll("td", {"data-stat": "rec"})[0].get_text()

                        rec_yds = 0
                        if len(player.findAll("td", {"data-stat": "rec_yds"})) > 0:
                            rec_yds = player.findAll("td", {"data-stat": "rec_yds"})[0].get_text()

                        rec_td = 0
                        if len(player.findAll("td", {"data-stat": "rec_td"})) > 0:
                            rec_td = player.findAll("td", {"data-stat": "rec_td"})[0].get_text()

                        fumbles_lost = 0
                        if len(player.findAll("td", {"data-stat": "fumbles_lost"})) > 0:
                            fumbles_lost = player.findAll("td", {"data-stat": "fumbles_lost"})[0].get_text()

                        if playerId is None:
                            print('No Player found for {}'.format(playerKey))
                        else:

                            sqlq = "SELECT COUNT(1) FROM PlayerStatLines WHERE NFLWeek = {} AND PlayerId = {} and SeasonId = {} and ProjectedStat = {}".format(
                                currentWeek, playerId, seasonId, 0)
                            self.cursor.execute(sqlq)
                            if self.cursor.fetchone()[0]:
                                self.cursor.execute(
                                    "UPDATE PlayerStatLines SET [PassYards] = ?, [PassAttempts] = ?, [Completions] = ?,[PassTDs] = ?,[Interceptions] = ?,[RushYards] = ?,[RushTDs] = ?,[RushAttempts] = ?,[Fumbles] = ?,[Receptions] = ?,[Targets] = ?,[RecYards] = ?,[RecTDs] = ? WHERE [NFLWeek] = ? AND [PlayerId] = ? AND [SeasonId] = ? AND [ProjectedStat] = ?",
                                    pass_yds, pass_att, pass_cmp, pass_td, pass_int, rush_yds, rush_td, rush_att,
                                    fumbles_lost, rec, targets, rec_yds, rec_td, currentWeek, playerId, seasonId, False)
                                self.cursor.commit()
                                print(
                                    "Update {} Passing: {}/{} {} yards {} TD {} int Rushing: {} attempts for {} yards and {} TDs  Passing: {} targets with {} comp for {} yards and {} TDs".format(
                                        playerId, pass_cmp, pass_att, pass_yds, pass_td, pass_int, rush_att, rush_yds,
                                        rush_td, targets, rec, rec_yds, rec_td))
                            else:
                                self.cursor.execute(
                                    "INSERT INTO PlayerStatLines ([NFLWeek],[PlayerId], [SeasonId],[ProjectedStat], [PassYards], [PassAttempts],[Completions],[PassTDs],[Interceptions],[RushYards],[RushTDs],[RushAttempts],[Fumbles],[Receptions],[Targets],[RecYards],[RecTDs]) Values (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                                    currentWeek, playerId, seasonId, False, pass_yds, pass_att, pass_cmp, pass_td, pass_int,
                                    rush_yds, rush_td, rush_att, fumbles_lost, rec, targets, rec_yds, rec_td)
                                self.cursor.commit()
                                print(
                                    "Add {} Passing: {}/{} {} yards {} TD {} int Rushing: {} attempts for {} yards and {} TDs  Passing: {} targets with {} comp for {} yards and {} TDs".format(
                                        playerId, pass_cmp, pass_att, pass_yds, pass_td, pass_int, rush_att, rush_yds,
                                        rush_td, targets, rec, rec_yds, rec_td))

    def score_kicking(self, seasonId, currentWeek):
        print('Score Kicking')
        self.cursor.execute("SELECT BoxscoreLink FROM NFLSchedule WHERE [SeasonId] = ? AND [Week] = ?", seasonId,
                       currentWeek)
        for row in self.cursor.fetchall():
            link = row[0]
            print(link)

            url = 'https://www.pro-football-reference.com{}'.format(link)
            soup = get_soup(url)

            scoringTable = soup.find("table", id="scoring")
            playerIdsScored = []
            if scoringTable is not None:
                for play in scoringTable.find_all('tbody')[0].find_all('tr'):
                    scoringPlay = play.findAll('td')[2]
                    if "field goal" in scoringPlay.get_text():
                        playerKey = ''

                        if len(scoringPlay.findAll('a', href=True)) > 0:
                            playerName = scoringPlay.findAll('a', href=True)[0].get_text()
                            playerKey = scoringPlay.findAll('a', href=True)[0]['href'].split('/')[3].split('.')[0]

                        play = scoringPlay.get_text()
                        distance = int(play[len(playerName) + 1:len(play)].split(' ')[0])

                        if playerKey != '':
                            playerId = self.GetPlayerId(playerKey)
                            if playerId is None:
                                print('No Player found for {}'.format(playerKey))
                            else:
                                if playerId not in playerIdsScored:
                                    deleteStatement = "DELETE FROM PlayerStatLines WHERE NFLWeek = {} AND PlayerId = {} and SeasonId = {} and ProjectedStat = {}".format(
                                        currentWeek, playerId, seasonId, 0)
                                    self.cursor.execute(deleteStatement)
                                    playerIdsScored.append(playerId)
                                sqlq = "SELECT COUNT(1) FROM PlayerStatLines WHERE NFLWeek = {} AND PlayerId = {} and SeasonId = {} and ProjectedStat = {}".format(
                                    currentWeek, playerId, seasonId, 0)
                                self.cursor.execute(sqlq)
                                if self.cursor.fetchone()[0]:
                                    if distance < 20:
                                        self.cursor.execute(
                                            "UPDATE PlayerStatLines SET  [FieldGoals1to19Made] = [FieldGoals1to19Made] + 1 WHERE [NFLWeek] = ? AND [PlayerId] = ? AND [SeasonId] = ? AND [ProjectedStat] = ?",
                                            currentWeek, playerId, seasonId, False)
                                    if distance >= 20 and distance < 30:
                                        self.cursor.execute(
                                            "UPDATE PlayerStatLines SET [FieldGoals20to29Made] = [FieldGoals20to29Made] + 1 WHERE [NFLWeek] = ? AND [PlayerId] = ? AND [SeasonId] = ? AND [ProjectedStat] = ?",
                                            currentWeek, playerId, seasonId, False)
                                    if distance >= 30 and distance < 40:
                                        self.cursor.execute(
                                            "UPDATE PlayerStatLines SET [FieldGoals30to39Made] = [FieldGoals30to39Made] + 1 WHERE [NFLWeek] = ? AND [PlayerId] = ? AND [SeasonId] = ? AND [ProjectedStat] = ?",
                                            currentWeek, playerId, seasonId, False)
                                    if distance >= 40 and distance < 50:
                                        self.cursor.execute(
                                            "UPDATE PlayerStatLines SET [FieldGoals40to49Made] = [FieldGoals40to49Made] + 1 WHERE [NFLWeek] = ? AND [PlayerId] = ? AND [SeasonId] = ? AND [ProjectedStat] = ?",
                                            currentWeek, playerId, seasonId, False)
                                    if distance >= 50:
                                        self.cursor.execute(
                                            "UPDATE PlayerStatLines SET [FieldGoals50PlusMade] = [FieldGoals50PlusMade] + 1 WHERE [NFLWeek] = ? AND [PlayerId] = ? AND [SeasonId] = ? AND [ProjectedStat] = ?",
                                            currentWeek, playerId, seasonId, False)
                                    self.cursor.commit()
                                    print("Update {} ({}) - {} yd FG".format(playerName, playerId, distance))
                                else:
                                    if distance < 20:
                                        self.cursor.execute(
                                            "INSERT INTO PlayerStatLines ([NFLWeek],[PlayerId], [SeasonId], [ProjectedStat], [FieldGoals1to19Made] ) Values (?,?,?,?,?)",
                                            currentWeek, playerId, seasonId, False, 1)
                                    if distance >= 20 and distance < 30:
                                        self.cursor.execute(
                                            "INSERT INTO PlayerStatLines ([NFLWeek],[PlayerId], [SeasonId], [ProjectedStat], [FieldGoals20to29Made] ) Values (?,?,?,?,?)",
                                            currentWeek, playerId, seasonId, False, 1)
                                    if distance >= 30 and distance < 40:
                                        self.cursor.execute(
                                            "INSERT INTO PlayerStatLines ([NFLWeek],[PlayerId], [SeasonId], [ProjectedStat], [FieldGoals30to39Made] ) Values (?,?,?,?,?)",
                                            currentWeek, playerId, seasonId, False, 1)
                                    if distance >= 40 and distance < 50:
                                        self.cursor.execute(
                                            "INSERT INTO PlayerStatLines ([NFLWeek],[PlayerId], [SeasonId], [ProjectedStat], [FieldGoals40to49Made] ) Values (?,?,?,?,?)",
                                            currentWeek, playerId, seasonId, False, 1)
                                    if distance >= 50:
                                        self.cursor.execute(
                                            "INSERT INTO PlayerStatLines ([NFLWeek],[PlayerId], [SeasonId], [ProjectedStat], [FieldGoals50PlusMade] ) Values (?,?,?,?,?)",
                                            currentWeek, playerId, seasonId, False, 1)
                                    self.cursor.commit()
                                    print("Add {} ({}) - {} yd FG".format(playerName, playerId, distance))

            # kickingTable = soup.find("table", id="kicking")
            # if kickingTable is not None:
            #     for kicker in kickingTable.find_all('tbody')[0].find_all('tr'):
            #         print(kicker)

    def score_other_offense(self, seasonId, currentWeek):
        self.cursor.execute("SELECT BoxscoreLink FROM NFLSchedule WHERE [SeasonId] = ? AND [Week] = ?", seasonId,
                       currentWeek)
        for row in self.cursor.fetchall():
            link = row[0]


            url = 'https://www.pro-football-reference.com{}'.format(link)

            service = Service()
            options = webdriver.ChromeOptions()
            options.add_argument("enable-automation")
            options.add_argument("--headless")
            options.add_argument("--window-size=1920,1080")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-extensions")
            options.add_argument("--dns-prefetch-disable")
            options.add_argument("--disable-gpu")
            # options.setPageLoadStrategy(PageLoadStrategy.NORMAL);

            driver = webdriver.Chrome(service=service, options=options)
            print(url)
            driver.get(url)

            driver.implicitly_wait(4)
            kickTable = driver.find_elements(By.ID, 'kicking')
            if len(kickTable) == 0:
                driver.close()
                continue
            rows = kickTable[0].find_elements(By.TAG_NAME, 'tbody')[0].find_elements(By.TAG_NAME, 'tr')
            for i in rows:
                try:
                    playerKey = i.find_element(By.TAG_NAME, 'a').get_attribute('href').split('/')[5].split('.')[0]
                    playerId = 0
                    if playerKey != '':
                        playerId = self.GetPlayerId(playerKey)
                    if playerId is not None:
                        xpm = i.find_elements(By.TAG_NAME, 'td')[1].text
                        if len(xpm) > 0:
                            sqlq = "SELECT COUNT(1) FROM PlayerStatLines WHERE NFLWeek = {} AND PlayerId = {} and SeasonId = {} and ProjectedStat = {}".format(
                                currentWeek, playerId, seasonId, 0)
                            self.cursor.execute(sqlq)
                            if self.cursor.fetchone()[0]:
                                self.cursor.execute(
                                    "UPDATE PlayerStatLines SET [PATMade] = ? WHERE [NFLWeek] = ? AND [PlayerId] = ? AND [SeasonId] = ? AND [ProjectedStat] = ?",
                                    xpm, currentWeek, playerId, seasonId, False)
                                self.cursor.commit()
                                print("UPDATE {} ({}) made {} XP".format(playerKey, playerId, xpm))
                            else:
                                self.cursor.execute(
                                    "INSERT INTO PlayerStatLines ([NFLWeek],[PlayerId], [SeasonId], [ProjectedStat], [PATMade] ) Values (?,?,?,?,?)",
                                    currentWeek, playerId, seasonId, False, xpm)
                                self.cursor.commit()
                                print("INSERT {} made {} XP".format(playerKey, xpm))
                except NoSuchElementException:
                    continue

            returnTable = driver.find_elements(By.ID, 'returns')
            if len(returnTable) > 0:
                rows = returnTable[0].find_elements(By.TAG_NAME, 'tbody')[0].find_elements(By.TAG_NAME, 'tr')
                for i in rows:
                    try:
                        playerKey = i.find_element(By.TAG_NAME, 'a').get_attribute('href').split('/')[5].split('.')[0]
                        playerId = 0
                        if playerKey != '':
                            playerId = self.GetPlayerId(playerKey)
                        krYards = i.find_elements(By.TAG_NAME, 'td')[2].text
                        krTD = i.find_elements(By.TAG_NAME, 'td')[4].text
                        prYards = i.find_elements(By.TAG_NAME, 'td')[7].text
                        prTD = i.find_elements(By.TAG_NAME, 'td')[9].text
                        if playerId is not None:
                            sqlq = "SELECT COUNT(1) FROM PlayerStatLines WHERE NFLWeek = {} AND PlayerId = {} and SeasonId = {} and ProjectedStat = {}".format(
                                currentWeek, playerId, seasonId, 0)
                            self.cursor.execute(sqlq)
                            if self.cursor.fetchone()[0]:
                                self.cursor.execute(
                                    "UPDATE PlayerStatLines SET [KRYards] = ?, [KRTDs] = ?, [PRYards] = ?, [PRTDs] = ? WHERE [NFLWeek] = ? AND [PlayerId] = ? AND [SeasonId] = ? AND [ProjectedStat] = ?",
                                    krYards, krTD, prYards, prTD, currentWeek, playerId, seasonId, False)
                                self.cursor.commit()
                                print("UPDATE {} ({}) KR Yards: {} TD: {}  PR Yards: {} TD:{}".format(playerKey, playerId,
                                                                                                      krYards, krTD,
                                                                                                      prYards, prTD))
                            else:
                                self.cursor.execute(
                                    "INSERT INTO PlayerStatLines ([NFLWeek],[PlayerId], [SeasonId], [ProjectedStat], [KRYards],[KRTDs],[PRYards],[PRTDs] ) Values (?,?,?,?,?,?,?,?)",
                                    currentWeek, playerId, seasonId, False, krYards, krTD, prYards, prTD)
                                self.cursor.commit()
                                print("INSERT {} ({}) KR Yards: {} TD: {}  PR Yards: {} TD:{}".format(playerKey, playerId,
                                                                                                      krYards, krTD,
                                                                                                      prYards, prTD))

                    except NoSuchElementException:
                        continue
            driver.close()

    def score_defense(self, seasonId, currentWeek):
        self.cursor.execute("SELECT BoxscoreLink FROM NFLSchedule WHERE [SeasonId] = ? AND [Week] = ?", seasonId,
                       currentWeek)
        for row in self.cursor.fetchall():
            link = row[0]
            print(link)
            url = 'https://www.pro-football-reference.com{}'.format(link)
            soup = get_soup(url)

            scoreContainer = soup.find("table", {"class": "linescore"})
            if scoreContainer is not None:
                rows = scoreContainer.find_all('tbody')[0].find_all('tr')
                homeScore = int(rows[1].find_all('td')[-1].get_text())
                awayScore = int(rows[0].find_all('td')[-1].get_text())

                service = Service()
                options = webdriver.ChromeOptions()
                options.add_argument("--headless")
                driver = webdriver.Chrome(service=service, options=options)
                driver.get(url)

                driver.implicitly_wait(4)
                teamStatTable = driver.find_elements(By.ID, 'team_stats')

                headerRow = teamStatTable[0].find_elements(By.TAG_NAME, 'thead')[0].find_elements(By.TAG_NAME, 'tr')[0]
                awayTeam = headerRow.find_elements(By.TAG_NAME, 'th')[1].text
                homeTeam = headerRow.find_elements(By.TAG_NAME, 'th')[2].text

                totalYardRow = teamStatTable[0].find_elements(By.TAG_NAME, 'tbody')[0].find_elements(By.TAG_NAME, 'tr')[
                    5]
                awayYardsAllowed = totalYardRow.find_elements(By.TAG_NAME, 'td')[1].text
                homeYardsAllowed = totalYardRow.find_elements(By.TAG_NAME, 'td')[0].text

                offensiveTable = driver.find_elements(By.ID, 'player_offense')
                offensiveRows = offensiveTable[0].find_elements(By.TAG_NAME, 'tbody')[0].find_elements(By.TAG_NAME,
                                                                                                       'tr')

                homeFR = 0
                awayFR = 0

                if offensiveTable is not None:
                    for oRow in offensiveRows:
                        cols = oRow.find_elements(By.TAG_NAME, 'td')
                        if len(cols) > 0:
                            team = cols[0].text
                            if team == homeTeam:
                                awayFR = awayFR + int(cols[20].text)
                            if team == awayTeam:
                                homeFR = homeFR + int(cols[20].text)

                defenseTable = driver.find_elements(By.ID, 'player_defense')
                defenseRows = defenseTable[0].find_elements(By.TAG_NAME, 'tbody')[0].find_elements(By.TAG_NAME, 'tr')
                homeInt = 0
                awayInt = 0

                homeTd = 0
                awayTd = 0

                homeSack = 0
                awaySack = 0
                for row in defenseRows:
                    columns = row.find_elements(By.TAG_NAME, 'td')
                    if len(columns) > 0:
                        team = columns[0].text
                        if team == homeTeam:
                            homeInt = homeInt + int(columns[1].text)
                            homeTd = homeTd + int(columns[3].text)
                            homeSack = homeSack + float(columns[6].text)
                        if team == awayTeam:
                            awayInt = awayInt + int(columns[1].text)
                            awayTd = awayTd + int(columns[3].text)
                            awaySack = awaySack + float(columns[6].text)
                home_points_allowed = homeScore - homeTd * 6
                away_points_allowed = awayScore - awayTd * 6

                print("Points Allowed - Home: {} vs Away: {}".format(home_points_allowed, away_points_allowed))
                print("Yards - Home ({}): {} vs Away ({}): {}".format(homeTeam, homeYardsAllowed, awayTeam,
                                                                      awayYardsAllowed))
                print("Int - Home: {} vs Away: {}".format(homeInt, awayInt))
                print("TD - Home: {} vs Away: {}".format(homeTd, awayTd))
                print("Sack - Home: {} vs Away: {}".format(homeSack, awaySack))
                print("Fumble Recovery - Home: {} vs Away: {}".format(homeFR, awayFR))

                sqlq = "SELECT COUNT(1) FROM PlayerStatLines WHERE NFLWeek = {} AND PlayerId = {} and SeasonId = {} and ProjectedStat = {}".format(
                    currentWeek, translate_team_code_to_id(homeTeam) * -1, seasonId, 0)
                self.cursor.execute(sqlq)
                if self.cursor.fetchone()[0]:
                    self.cursor.execute(
                        "UPDATE PlayerStatLines SET [PointsAllowed] = ?, [YardsAllowed] = ?, [Sacks] = ?, [DefensiveTD] = ?, [DefensiveInt] = ?, [DefensiveFumbleRecovery] = ? WHERE [NFLWeek] = ? AND [PlayerId] = ? AND [SeasonId] = ? AND [ProjectedStat] = ?",
                        away_points_allowed, homeYardsAllowed, homeSack, homeTd, homeInt, homeFR, currentWeek,
                        translate_team_code_to_id(homeTeam) * -1, seasonId, False)
                    self.cursor.commit()
                    print("UPDATE")
                else:
                    self.cursor.execute(
                        "INSERT INTO PlayerStatLines ([PointsAllowed],[YardsAllowed],[Sacks],[DefensiveTD],[DefensiveInt],[DefensiveFumbleRecovery],[NFLWeek],[PlayerId], [SeasonId], [ProjectedStat]) VALUES(?,?,?,?,?,?,?,?,?,?)",
                        away_points_allowed, homeYardsAllowed, homeSack, homeTd, homeInt, homeFR, currentWeek,
                        translate_team_code_to_id(homeTeam) * -1, seasonId, False)
                    self.cursor.commit()
                    print("INSERT")

                sqlq = "SELECT COUNT(1) FROM PlayerStatLines WHERE NFLWeek = {} AND PlayerId = {} and SeasonId = {} and ProjectedStat = {}".format(
                    currentWeek, translate_team_code_to_id(awayTeam) * -1, seasonId, 0)
                self.cursor.execute(sqlq)
                if self.cursor.fetchone()[0]:
                    self.cursor.execute(
                        "UPDATE PlayerStatLines SET [PointsAllowed] = ?, [YardsAllowed] = ?, [Sacks] = ?, [DefensiveTD] = ?, [DefensiveInt] = ?, [DefensiveFumbleRecovery] = ? WHERE [NFLWeek] = ? AND [PlayerId] = ? AND [SeasonId] = ? AND [ProjectedStat] = ?",
                        home_points_allowed, awayYardsAllowed, awaySack, awayTd, awayInt, awayFR, currentWeek,
                        translate_team_code_to_id(awayTeam) * -1, seasonId, False)
                    self.cursor.commit()
                    print("UPDATE")
                else:
                    self.cursor.execute(
                        "INSERT INTO PlayerStatLines ([PointsAllowed],[YardsAllowed],[Sacks],[DefensiveTD],[DefensiveInt],[DefensiveFumbleRecovery],[NFLWeek],[PlayerId], [SeasonId], [ProjectedStat]) VALUES(?,?,?,?,?,?,?,?,?,?)",
                        home_points_allowed, awayYardsAllowed, awaySack, awayTd, awayInt, awayFR, currentWeek,
                        translate_team_code_to_id(awayTeam) * -1, seasonId, False)
                    self.cursor.commit()
                    print("INSERT")

                driver.close()
