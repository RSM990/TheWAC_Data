from Tools.Settings import Settings
from Tools.BeautifulSoup import get_soup
import pyodbc
from Tools.TeamCodes import translate_team_name_to_id

class ProjectionStatBuilder:
    def __init__(self, season_id, week):
        print('Building Season Stat Projection')
        settings = Settings()

        self.connection = pyodbc.connect(settings.CURRENT_CONNECTION_STRING)
        self.cursor = self.connection.cursor()
        self.load_qbs(season_id, week)
        self.load_rbs(season_id, week)
        self.load_wrs(season_id, week)
        self.load_tes(season_id, week)
        self.load_kickers(season_id, week)



    def load_qbs(self, season_id, week):
        url = f'https://www.fantasypros.com/nfl/projections/qb.php?week={week}'
        soup = get_soup(url)
        rows = soup.find_all("table")[0].find_all('tbody')[0].find_all('tr')
        print(url)
        passingCursor = self.connection.cursor()

        for data in rows:
            cols = data.find_all('td')
            nameLink = cols[0].find("a", href=True)
            fullName = nameLink.get_text()
            names = nameLink.get_text().split(" ")
            first = names[0]
            last = ''
            for name in names[1:]:
                if name == 'II':
                    continue
                last = last + ' ' + name

            last = last.strip()
            nflTeam = cols[0].getText().split(' ')[-1]
            passAttempt = float(cols[1].getText().replace(',', ''))
            complete = float(cols[2].getText().replace(',', ''))
            passYards = float(cols[3].getText().replace(',', ''))
            passTD = float(cols[4].getText().replace(',', ''))
            passInt = float(cols[5].getText().replace(',', ''))
            rushAtt = float(cols[6].getText().replace(',', ''))
            rushYards = float(cols[7].getText().replace(',', ''))
            rushTD = float(cols[8].getText().replace(',', ''))
            fumLost = float(cols[9].getText().replace(',', ''))

            sql = "SELECT * FROM Players WHERE FirstName  LIKE ? AND LastName LIKE ? AND NFLTeamId = ? AND Position = 'QB' "
            firstNameParam = f'%{first}%'
            lastNameParam = f'%{last}%'
            print(firstNameParam, lastNameParam, nflTeam)
            nflTeamId = translate_team_name_to_id(nflTeam)
            dbPlayer = passingCursor.execute(sql, firstNameParam, lastNameParam, nflTeamId)
            for row in dbPlayer.fetchall():
                playerId = row[0]
            print(fullName)

            updateDB = True

            nflWeek = week
            if week == 'draft':
                nflWeek = 0

            sqlCheck = "SELECT * FROM PlayerStatLines WHERE PlayerId = ? AND SeasonId = ? AND NFLWeek = ? AND ProjectedStat = ?"
            statCheck = passingCursor.execute(sqlCheck, playerId, season_id, nflWeek, True)
            for row in statCheck.fetchall():
                print(row[0])
                updateDB = False

            if updateDB:
                passingCursor.execute(
                    "INSERT INTO PlayerStatLines ([SeasonId], [ProjectedStat], [NFLWeek], [PlayerId],[PassYards],"
                    " [Completions],[PassTDs],[Interceptions],[PassAttempts],[RushYards],[RushTDs],"
                    "[Fumbles]) "
                    "VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
                    season_id, True, nflWeek, playerId, passYards, complete, passTD, passInt, passAttempt, rushYards, rushTD, fumLost)
                passingCursor.commit()

            print(translate_team_name_to_id(nflTeam))

        passingCursor.close()


    def load_rbs(self, season_id, week):
        url = f'https://www.fantasypros.com/nfl/projections/rb.php?week={week}'
        soup = get_soup(url)
        rows = soup.find_all("table")[0].find_all('tbody')[0].find_all('tr')

        cursor = self.connection.cursor()

        for data in rows:
            cols = data.find_all('td')
            nameLink = cols[0].find("a", href=True)
            fullName = nameLink.get_text()
            names = nameLink.get_text().split(" ")
            first = names[0]
            last = ''
            for name in names[1:]:
                if (name == 'II'):
                    continue
                last = last + ' ' + name

            last = last.strip()

            nflTeam = cols[0].getText().split(' ')[-1]
            rushAttempt = float(cols[1].getText().replace(',', ''))
            rushYards = float(cols[2].getText().replace(',', ''))
            rushTD = float(cols[3].getText().replace(',', ''))
            rec = float(cols[4].getText().replace(',', ''))
            recYards = float(cols[5].getText().replace(',', ''))
            recTD = float(cols[6].getText().replace(',', ''))
            fumbles = float(cols[7].getText().replace(',', ''))

            sql = "SELECT * FROM Players WHERE FirstName  LIKE ? AND LastName LIKE ? AND NFLTeamId = ? AND Position = 'RB' "
            firstNameParam = f'%{first}%'
            lastNameParam = f'%{last}%'
            nflTeamId = translate_team_name_to_id(nflTeam)
            dbPlayer = cursor.execute(sql, firstNameParam, lastNameParam, nflTeamId)
            for row in dbPlayer.fetchall():
                playerId = row[0]
            print(fullName)
            print("{} {} {} {}".format(rushAttempt, rushYards, rec, fumbles))
            updateDB = True

            nflWeek = week
            if week == 'draft':
                nflWeek = 0
            sqlCheck = "SELECT * FROM PlayerStatLines WHERE PlayerId = ? AND SeasonId = ? AND NFlWeek = ? AND ProjectedStat = ?"
            statCheck = cursor.execute(sqlCheck, playerId, season_id, nflWeek, True)
            for row in statCheck.fetchall():
                updateDB = False

            if updateDB:
                cursor.execute(
                    "INSERT INTO PlayerStatLines ([SeasonId], [ProjectedStat], [NFLWeek], [PlayerId],[RushAttempts],"
                    "[RushYards],[RushTDs],[Receptions],[RecYards],[RecTDs],[Fumbles]) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                    season_id, True, nflWeek, playerId, rushAttempt, rushYards, rushTD, rec, recYards, recTD, fumbles)
                cursor.commit()
            print(translate_team_name_to_id(nflTeam))

        cursor.close()

    def load_wrs(self, season_id, week):
        url = f'https://www.fantasypros.com/nfl/projections/wr.php?week={week}'
        soup = get_soup(url)
        rows = soup.find_all("table")[0].find_all('tbody')[0].find_all('tr')

        cursor = self.connection.cursor()

        for data in rows:
            cols = data.find_all('td')
            nameLink = cols[0].find("a", href=True)
            fullName = nameLink.get_text()
            names = nameLink.get_text().split(" ")
            first = names[0]
            last = ''
            for name in names[1:]:
                if (name == 'II'):
                    continue
                last = last + ' ' + name

            last = last.strip()

            nflTeam = cols[0].getText().split(' ')[-1]
            rec = float(cols[1].getText().replace(',', ''))
            recYards = float(cols[2].getText().replace(',', ''))
            recTD = float(cols[3].getText().replace(',', ''))
            rushAttempt = float(cols[4].getText().replace(',', ''))
            rushYards = float(cols[5].getText().replace(',', ''))
            rushTD = float(cols[6].getText().replace(',', ''))

            fumbles = float(cols[7].getText().replace(',', ''))

            sql = "SELECT * FROM Players WHERE FirstName  LIKE ? AND LastName LIKE ? AND NFLTeamId = ? AND Position = 'WR' "
            firstNameParam = f'%{first}%'
            lastNameParam = f'%{last}%'
            nflTeamId = translate_team_name_to_id(nflTeam)
            dbPlayer = cursor.execute(sql, firstNameParam, lastNameParam, nflTeamId)
            for row in dbPlayer.fetchall():
                playerId = row[0]
            print(fullName)
            print("{} {} {} {}".format(rec, recYards, recTD, fumbles))
            updateDB = True

            nflWeek = week
            if week == 'draft':
                nflWeek = 0
            sqlCheck = "SELECT * FROM PlayerStatLines WHERE PlayerId = ? AND SeasonId = ? AND NFLWeek = ? AND ProjectedStat = ?"
            statCheck = cursor.execute(sqlCheck, playerId, season_id, nflWeek, True)
            for row in statCheck.fetchall():
                updateDB = False

            if updateDB:
                cursor.execute(
                    "INSERT INTO PlayerStatLines ([SeasonId], [ProjectedStat], [NFLWeek], [PlayerId],[RushAttempts], [RushYards],[RushTDs],[Receptions],[RecYards],[RecTDs],[Fumbles]) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                    season_id, True, nflWeek, playerId, rushAttempt, rushYards, rushTD, rec, recYards, recTD, fumbles)
                cursor.commit()
            print(translate_team_name_to_id(nflTeam))

        cursor.close()

    def load_tes(self, season_id, week):
        url = f'https://www.fantasypros.com/nfl/projections/te.php?week={week}'
        soup = get_soup(url)
        rows = soup.find_all("table")[0].find_all('tbody')[0].find_all('tr')

        cursor = self.connection.cursor()

        for data in rows:
            cols = data.find_all('td')
            nameLink = cols[0].find("a", href=True)
            fullName = nameLink.get_text()
            names = nameLink.get_text().split(" ")
            first = names[0]
            last = ''
            for name in names[1:]:
                if (name == 'II'):
                    continue
                last = last + ' ' + name

            last = last.strip()

            nflTeam = cols[0].getText().split(' ')[-1]
            rec = float(cols[1].getText().replace(',', ''))
            recYards = float(cols[2].getText().replace(',', ''))
            recTD = float(cols[3].getText().replace(',', ''))

            fumbles = float(cols[4].getText().replace(',', ''))

            sql = "SELECT * FROM Players WHERE FirstName  LIKE ? AND LastName LIKE ? AND NFLTeamId = ? AND Position = 'TE' "
            firstNameParam = f'%{first}%'
            lastNameParam = f'%{last}%'
            nflTeamId = translate_team_name_to_id(nflTeam)
            dbPlayer = cursor.execute(sql, firstNameParam, lastNameParam, nflTeamId)
            for row in dbPlayer.fetchall():
                playerId = row[0]
            print(fullName)
            print("{} {} {} {}".format(rec, recYards, recTD, fumbles))
            updateDB = True

            nflWeek = week
            if week == 'draft':
                nflWeek = 0
            sqlCheck = "SELECT * FROM PlayerStatLines WHERE PlayerId = ? AND SeasonId = ? AND NFLWeek = ? AND ProjectedStat = ?"
            statCheck = cursor.execute(sqlCheck, playerId, season_id, nflWeek, True)
            for row in statCheck.fetchall():
                updateDB = False

            if updateDB:
                cursor.execute(
                    "INSERT INTO PlayerStatLines ([SeasonId], [ProjectedStat], [NFLWeek], [PlayerId],[Receptions],[RecYards],[RecTDs],[Fumbles]) VALUES (?,?,?,?,?,?,?,?)",
                    season_id, True, nflWeek, playerId, rec, recYards, recTD, fumbles)
                cursor.commit()

            print(translate_team_name_to_id(nflTeam))

        cursor.close()

    def load_kickers(self, season_id, week):
        url = f'https://www.fantasypros.com/nfl/projections/k.php?week={week}'
        soup = get_soup(url)
        rows = soup.find_all("table")[0].find_all('tbody')[0].find_all('tr')

        cursor = self.connection.cursor()

        for data in rows:
            cols = data.find_all('td')
            nameLink = cols[0].find("a", href=True)
            fullName = nameLink.get_text()
            names = nameLink.get_text().split(" ")
            first = names[0]
            last = ''
            for name in names[1:]:
                if (name == 'II'):
                    continue
                last = last + ' ' + name

            last = last.strip()

            nflTeam = cols[0].getText().split(' ')[-1]
            fg = float(cols[1].getText().replace(',', ''))
            fga = float(cols[2].getText().replace(',', ''))
            xp = float(cols[3].getText().replace(',', ''))

            points = float(cols[4].getText().replace(',', ''))

            sql = "SELECT * FROM Players WHERE FirstName  LIKE ? AND LastName LIKE ? AND NFLTeamId = ? AND Position = 'K' "
            firstNameParam = f'%{first}%'
            lastNameParam = f'%{last}%'
            nflTeamId = translate_team_name_to_id(nflTeam)
            dbPlayer = cursor.execute(sql, firstNameParam, lastNameParam, nflTeamId)
            playerId = 0
            for row in dbPlayer.fetchall():
                playerId = row[0]

            if playerId == 0:
                continue

            print(fullName)
            updateDB = True

            nflWeek = week
            if week == 'draft':
                nflWeek = 0
            sqlCheck = "SELECT * FROM PlayerStatLines WHERE PlayerId = ? AND SeasonId = ? AND NFLWeek = ? AND ProjectedStat = ?"
            statCheck = cursor.execute(sqlCheck, playerId, season_id, nflWeek, True)
            for row in statCheck.fetchall():
                updateDB = False

            if updateDB:
                cursor.execute(
                    "INSERT INTO PlayerStatLines ([SeasonId], [ProjectedStat], [NFLWeek], [PlayerId],[FieldGoalsMade],[FieldGoalsAttempted],[PATMade],[ProjectedKickingPoints]) VALUES (?,?,?,?,?,?,?,?)",
                    season_id, True, nflWeek, playerId, fg, fga, xp, points)
                cursor.commit()

            print(translate_team_name_to_id(nflTeam))

        cursor.close()