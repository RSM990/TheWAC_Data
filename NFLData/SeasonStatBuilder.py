from Tools.Settings import Settings
from Tools.BeautifulSoup import get_soup
import pyodbc


class SeasonStatBuilder:

    def __init__(self, data_year, season_id):
        print('Loading Season Stats')
        settings = Settings()

        self.connection = pyodbc.connect(settings.CURRENT_CONNECTION_STRING)
        self.cursor = self.connection.cursor()

        self.load_passing(data_year, season_id)
        self.load_rushing(data_year, season_id)
        self.load_receiving(data_year, season_id)
        self.load_returns(data_year, season_id)
        self.load_scoring(data_year, season_id)
        self.load_kicking(data_year, season_id)


    def load_passing(self, year, season_id):
        url = 'https://www.pro-football-reference.com/years/{}/passing.htm'.format(year)
        soup = get_soup(url)

        rows = soup.find_all("table")[0].find_all('tbody')[0].find_all('tr')
        passing_cursor = self.connection.cursor()
        for data in rows:
            cols = data.find_all('td')
            if len(cols) > 0:
                name_link = cols[0].find_all('a', href=True)[0];
                name = name_link.get_text()

                player_id = name_link['href'].split('/')[3].split('.')[0]

                passing_cursor.execute("SELECT Id FROM Players WHERE ProReferenceKey = ?", player_id)
                for row in passing_cursor.fetchall():
                    player_id = row[0]

                games_played = cols[4].get_text()
                games_started = cols[5].get_text()

                comp = cols[7].get_text()
                attempts = cols[8].get_text()
                yards = cols[10].get_text()
                td = cols[11].get_text()
                inter = cols[13].get_text()
                qbr = cols[22].get_text()

                if isinstance(player_id, int):
                    stat_id = -1
                    passing_cursor.execute(
                        "SELECT * FROM PlayerStatLines WHERE SeasonId = ? AND PlayerId = ? AND NFLWeek = 0 AND ProjectedStat = 0", season_id,
                        player_id)
                    for row in passing_cursor.fetchall():
                        stat_id = row[0]
                    if stat_id > 0:
                        # update
                        passing_cursor.execute(
                            "UPDATE PlayerStatLines SET [GamesStarted] = ?,[GamesPlayed] = ?, [PassYards] = ?,[Completions] = ?,[PassTDs] = ?,[Interceptions] = ?,[PassAttempts] = ?, [QBRating] = ? WHERE SeasonId = ? AND PlayerId = ? AND ProjectedStat = 0 AND NFLWeek = 0",
                            games_started, games_played, yards, comp, td, inter, attempts, qbr, season_id, player_id)

                        passing_cursor.commit()
                    else:
                        # add
                        passing_cursor.execute(
                            "INSERT INTO PlayerStatLines ([SeasonId], [ProjectedStat], [NFLWeek], [PlayerId], [GamesPlayed], [GamesStarted], [PassYards], [Completions],[PassTDs],[Interceptions],[PassAttempts],[QBRating]) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
                            season_id, 0, 0, player_id, games_played, games_started, yards, comp, td, inter, attempts, qbr)
                        passing_cursor.commit()
                print(
                    "Name: {} ({}) - Games: ({}/{})  Comp: {}  Attempt: {}  Yards: {} TDs: {} INTs: {} QBR: {}".format(
                        name.strip(), player_id, games_started, games_played, comp, attempts, yards, td, inter, qbr))

        passing_cursor.close()


    def load_rushing(self, year, season_id):
        url = 'https://www.pro-football-reference.com/years/{}/rushing.htm'.format(year)
        soup = get_soup(url)
        rows = soup.find_all("table")[0].find_all('tbody')[0].find_all('tr')

        rushingCursor = self.connection.cursor()

        for data in rows:
            cols = data.find_all('td')
            if len(cols) > 0:
                link = cols[0].find_all('a', href=True)[0];
                name = link.get_text()

                player_id = link['href'].split('/')[3].split('.')[0]

                rushingCursor.execute("SELECT Id FROM Players WHERE ProReferenceKey = ?", player_id)
                for row in rushingCursor.fetchall():
                    player_id = row[0]

                games_played = cols[4].get_text()
                games_started = cols[5].get_text()

                attempts = cols[6].get_text()
                yards = cols[7].get_text()
                td = cols[8].get_text()
                average = cols[12].get_text()
                fumbles = cols[14].get_text()
                print(
                    "Name: {} ({}) - Games: ({}/{})  Rush Attempts: {} Yards: {} TDs: {} Fumbles: {} Average: {}".format(
                        name.strip(), player_id, games_started, games_played, attempts, yards, td, fumbles, average))
                if isinstance(player_id, int):
                    stat_id = -1
                    rushingCursor.execute(
                        "SELECT * FROM PlayerStatLines WHERE SeasonId = ? AND PlayerId = ? AND ProjectedStat = 0 AND NFLWeek = 0", season_id,
                        player_id)
                    for row in rushingCursor.fetchall():
                        stat_id = row[0]
                    if stat_id > 0:
                        #                 update
                        rushingCursor.execute(
                            "UPDATE PlayerStatLines SET [GamesStarted] = ?,[GamesPlayed] = ?, [RushAttempts] = ?,[RushYards] = ?,[RushTDs] = ?,[Fumbles] = ?,[RushAverage] = ? WHERE SeasonId = ? AND PlayerId = ? AND ProjectedStat = 0 AND NFLWeek = 0",
                            games_started, games_played, attempts, yards, td, fumbles, average, season_id, player_id)
                        rushingCursor.commit()
                    else:
                        #                 add
                        rushingCursor.execute(
                            "INSERT INTO PlayerStatLines ([SeasonId], [NFLWeek], [ProjectedStat], [PlayerId],[GamesStarted],[GamesPlayed], [RushAttempts],[RushYards],[RushTDs],[Fumbles],[RushAverage]) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                            season_id, 0, 0, player_id, games_started, games_played, attempts, yards, td, fumbles, average)
                        rushingCursor.commit()


        rushingCursor.close()


    def load_receiving(self, year, season_id):
        url = 'https://www.pro-football-reference.com/years/{}/receiving.htm'.format(year)
        soup = get_soup(url)
        rows = soup.find_all("table")[0].find_all('tbody')[0].find_all('tr')

        rec_cursor = self.connection.cursor()

        for data in rows:
            cols = data.find_all('td')
            if len(cols) > 0:
                link = cols[0].find_all('a', href=True)[0];
                name = link.get_text()

                player_id = link['href'].split('/')[3].split('.')[0]

                rec_cursor.execute("SELECT Id FROM Players WHERE ProReferenceKey = ?", player_id)
                for row in rec_cursor.fetchall():
                    player_id = row[0]

                games_played = cols[4].get_text()
                games_started = cols[5].get_text()

                targets = cols[6].get_text()
                rec = cols[7].get_text()
                yards = cols[9].get_text()
                td = cols[11].get_text()
                average = cols[16].get_text()
                fumbles = cols[18].get_text()
                print(
                    "Name: {} ({}) - Games: ({}/{})  Targets: {} Catches: {} Yards: {} TDs: {} Fumbles: {} Average: {}".format(
                        name.strip(), player_id, games_started, games_played, targets, rec, yards, td, fumbles,
                        average))
                if isinstance(player_id, int):
                    stat_id = -1
                    rec_cursor.execute(
                        "SELECT * FROM PlayerStatLines WHERE SeasonId = ? AND PlayerId = ? AND ProjectedStat = 0 AND NFLWeek = 0", season_id,
                        player_id)
                    for row in rec_cursor.fetchall():
                        stat_id = row[0]
                    if stat_id > 0:
                        #                 update
                        rec_cursor.execute(
                            "UPDATE PlayerStatLines SET [GamesStarted] = ?,[GamesPlayed] = ?, [Targets] = ?, [Receptions] = ?, [RecYards] = ?,[RecTDs] = ?,[Fumbles] = ?,[RecAverage] = ? WHERE SeasonId = ? AND PlayerId = ? AND ProjectedStat = 0 AND NFLWeek = 0",
                            games_started, games_played, targets, rec, yards, td, fumbles, average, season_id, player_id)
                        rec_cursor.commit()
                    else:
                        #                 add
                        rec_cursor.execute(
                            "INSERT INTO PlayerStatLines ([SeasonId], [NFLWeek], [ProjectedStat], [PlayerId],[GamesStarted],[GamesPlayed], [Targets],[Receptions],[RecYards],[RecTDs],[Fumbles],[RecAverage]) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
                            season_id, 0, 0, player_id, games_started, games_played, targets, rec, yards, td, fumbles, average)
                        rec_cursor.commit()


        rec_cursor.close()


    def load_returns(self, year, season_id):
        url = 'https://www.pro-football-reference.com/years/{}/returns.htm'.format(year)
        soup = get_soup(url)
        rows = soup.find_all("table")[0].find_all('tbody')[0].find_all('tr')

        return_cursor = self.connection.cursor()

        for data in rows:
            cols = data.find_all('td')
            if len(cols) > 0:
                link = cols[0].find_all('a', href=True)[0]
                name = link.get_text()

                player_id = link['href'].split('/')[3].split('.')[0]

                return_cursor.execute("SELECT Id FROM Players WHERE ProReferenceKey = ?", player_id)
                for row in return_cursor.fetchall():
                    player_id = row[0]

                games_played = cols[4].get_text()
                games_started = cols[5].get_text()

                punt_attempts = cols[6].get_text()
                punt_yards = cols[7].get_text()
                punt_tds = cols[8].get_text()

                kick_attempts = cols[11].get_text()
                kick_yards = cols[12].get_text()
                kick_tds = cols[13].get_text()

                if isinstance(player_id, int):
                    stat_id = -1
                    return_cursor.execute(
                        "SELECT * FROM PlayerStatLines WHERE SeasonId = ? AND PlayerId = ? AND ProjectedStat = 0 AND NFLWeek = 0", season_id,
                        player_id)
                    for row in return_cursor.fetchall():
                        stat_id = row[0]
                    if stat_id > 0:
                        #                 update
                        return_cursor.execute(
                            "UPDATE PlayerStatLines SET [GamesStarted] = ?,[GamesPlayed] = ?, [PRAttempted] = ?,[PRYards] = ?,[PRTDs] = ?,[KRAttempted] = ?,[KRYards] = ?, [KRTDs] = ? WHERE SeasonId = ? AND PlayerId = ? AND ProjectedStat = 0 AND NFLWeek = 0",
                            games_started, games_played, punt_attempts, punt_yards, punt_tds, kick_attempts, kick_yards,
                            kick_tds, season_id, player_id)
                        return_cursor.commit()
                    else:
                        #                 add
                        return_cursor.execute(
                            "INSERT INTO PlayerStatLines ([SeasonId], [NFLWeek], [ProjectedStat], [PlayerId],[GamesStarted],[GamesPlayed], [PRAttempted],[PRYards],[PRTDs],[KRAttempted],[KRYards], [KRTDs]) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
                            season_id, 0, 0, player_id, games_started, games_played, punt_attempts, punt_yards, punt_tds,
                            kick_attempts, kick_yards, kick_tds)
                        return_cursor.commit()
                print(
                    "Name: {} ({}) - Games: ({}/{})  Punts: {} Attempts, {} Yards, {} TDs  Kick: {} Attempts, {} Yards, {} TDs".format(
                        name.strip(), player_id, games_started, games_played, punt_attempts, punt_yards, punt_tds, kick_attempts,
                        kick_yards, kick_tds))

        return_cursor.close()

    def load_scoring(self, year, season_id):
        url = 'https://www.pro-football-reference.com/years/{}/scoring.htm'.format(year)
        soup = get_soup(url)
        rows = soup.find_all("table")[0].find_all('tbody')[0].find_all('tr')

        scoring_cursor = self.connection.cursor()

        for data in rows:
            cols = data.find_all('td')
            if len(cols) > 0:
                link = cols[0].find_all('a', href=True)[0];
                name = link.get_text()

                player_id = link['href'].split('/')[3].split('.')[0]

                scoring_cursor.execute("SELECT Id FROM Players WHERE ProReferenceKey = ?", player_id)
                for row in scoring_cursor.fetchall():
                    player_id = row[0]

                games_played = cols[4].get_text()
                games_started = cols[5].get_text()
                made = cols[14].get_text()

                if isinstance(player_id, int):
                    stat_id = -1
                    scoring_cursor.execute(
                        "SELECT * FROM PlayerStatLines WHERE SeasonId = ? AND PlayerId = ? AND ProjectedStat = 0 AND NFLWeek = 0", season_id,
                        player_id)
                    for row in scoring_cursor.fetchall():
                        stat_id = row[0]
                    if stat_id > 0:
                        #                 update
                        scoring_cursor.execute(
                            "UPDATE PlayerStatLines SET [GamesStarted] = ?,[GamesPlayed] = ?, [TwoPointConv] = ? WHERE SeasonId = ? AND PlayerId = ? AND ProjectedStat = 0 AND NFLWeek = 0",
                            games_started, games_played, made, season_id, player_id)
                        scoring_cursor.commit()
                    else:
                        #                 add
                        scoring_cursor.execute(
                            "INSERT INTO PlayerStatLines ([SeasonId], [NFLWeek], [ProjectedStat], [PlayerId],[GamesStarted],[GamesPlayed], [TwoPointConv]) VALUES (?,?,?,?,?,?,?)",
                            season_id, 0, 0, player_id, games_started, games_played, made)
                        scoring_cursor.commit()
                print("Name: {} ({}) Games ({}/{}) - Made:{}".format(name.strip(), player_id, games_started,
                                                                     games_played, made))

        scoring_cursor.close()


    def load_kicking(self, year, season_id):
        url = 'https://www.pro-football-reference.com/years/{}/kicking.htm'.format(year)
        soup = get_soup(url)
        rows = soup.find_all("table")[0].find_all('tbody')[0].find_all('tr')

        kicking_cursor = self.connection.cursor()

        for data in rows:
            cols = data.find_all('td')
            if len(cols) > 0:
                link = cols[0].find_all('a', href=True)[0];
                name = link.get_text()

                player_id = link['href'].split('/')[3].split('.')[0]

                kicking_cursor.execute("SELECT Id FROM Players WHERE ProReferenceKey = ?", player_id)
                for row in kicking_cursor.fetchall():
                    player_id = row[0]

                games_played = cols[4].get_text()
                games_started = cols[5].get_text()

                fg_attempt = cols[16].get_text()
                fg_made = cols[17].get_text()

                xp_attempt = cols[20].get_text()
                xp_made = cols[21].get_text()

                fg50Att = cols[14].get_text()
                fg50Made = cols[15].get_text()

                fg40Att = cols[12].get_text()
                fg40Made = cols[13].get_text()

                fg30Att = cols[10].get_text()
                fg30Made = cols[11].get_text()

                fg20Att = cols[8].get_text()
                fg20Made = cols[9].get_text()

                fg19Att = cols[6].get_text()
                fg19Made = cols[7].get_text()

                if isinstance(player_id, int):
                    stat_id = -1
                    kicking_cursor.execute(
                        "SELECT * FROM PlayerStatLines WHERE SeasonId = ? AND PlayerId = ? AND ProjectedStat = 0 AND NFLWeek = 0", season_id,
                        player_id)
                    for row in kicking_cursor.fetchall():
                        stat_id = row[0]
                    if stat_id > 0:
                        #                 update
                        kicking_cursor.execute(
                            "UPDATE PlayerStatLines SET [GamesStarted] = ?,[GamesPlayed] = ?, [FieldGoalsMade] = ?, [FieldGoalsAttempted] = ?, [FieldGoals1to19Attempted] = ?,[FieldGoals1to19Made] = ?,[FieldGoals20to29Attempted] = ?,[FieldGoals20to29Made] = ?,[FieldGoals30to39Attempted] = ?,[FieldGoals30to39Made] = ?,[FieldGoals40to49Attempted] = ?,[FieldGoals40to49Made] = ?,[FieldGoals50PlusAttempted] = ?,[FieldGoals50PlusMade] = ?,[PATAttempted] = ?,[PATMade] = ?  WHERE SeasonId = ? AND PlayerId = ? AND ProjectedStat = 0 AND NFLWeek = 0",
                            games_started, games_played, fg_made, fg_attempt, fg19Att, fg19Made, fg20Att, fg20Made, fg30Att,
                            fg30Made, fg40Att, fg40Made, fg50Att, fg50Made, xp_attempt, xp_made, season_id, player_id)
                        kicking_cursor.commit()
                    else:
                        #                 add
                        kicking_cursor.execute(
                            "INSERT INTO PlayerStatLines ([SeasonId], [NFLWeek], [ProjectedStat], [PlayerId],[GamesStarted],[GamesPlayed],[FieldGoalsMade],[FieldGoalsAttempted],[FieldGoals1to19Attempted],[FieldGoals1to19Made],[FieldGoals20to29Attempted],[FieldGoals20to29Made],[FieldGoals30to39Attempted],[FieldGoals30to39Made],[FieldGoals40to49Attempted],[FieldGoals40to49Made],[FieldGoals50PlusAttempted],[FieldGoals50PlusMade],[PATAttempted] ,[PATMade]) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                            season_id, 0, 0, player_id, games_started, games_played, fg_made, fg_attempt, fg19Att, fg19Made,
                            fg20Att, fg20Made, fg30Att, fg30Made, fg40Att, fg40Made, fg50Att, fg50Made, xp_attempt,
                            xp_made)
                        kicking_cursor.commit()
                print(
                    "Name: {} ({}) Games ({}/{}) - FG:{}/{}  XP:{}/{} 1-19:{}/{} 20-29:{}/{} 30-39:{}/{} 40-49:{}/{} 50+:{}/{}".format(
                        name.strip(), player_id, games_started, games_played, fg_made, fg_attempt, xp_attempt, xp_made,
                        fg19Made, fg19Att, fg20Made, fg20Att, fg30Made, fg30Att, fg40Made, fg40Att, fg50Made, fg50Att))

        kicking_cursor.close()
