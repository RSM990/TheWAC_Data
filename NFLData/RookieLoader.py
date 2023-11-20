import pyodbc

from Tools.BeautifulSoup import get_soup
from Tools.Settings import Settings
from Tools.TeamCodes import translate_team_code_to_id


class RookieLoader:

    def __init__(self, year):
        print(f'Loading {year} Rookies')
        settings = Settings()

        self.connection = pyodbc.connect(settings.CURRENT_CONNECTION_STRING)
        self.cursor = self.connection.cursor()

        self.POSITION_LIST = settings.POSITION_LIST

        player_url = f'https://www.pro-football-reference.com/years/{year}/draft.htm'
        soup = get_soup(player_url)
        rows = soup.find_all("table")[0].find_all('tbody')[0].find_all('tr')
        for data in rows:
            cols = data.find_all('td')
            if len(cols) > 0:
                position = cols[3].get_text()
                if position in self.POSITION_LIST:
                    teamLink = cols[1].find("a", href=True)
                    nameLink = cols[2].find("a", href=True)
                    fullName = nameLink.get_text()
                    playerId = nameLink['href'].split('/')[3].split('.')[0]

                    names = nameLink.get_text().split(" ")
                    first = names[0]
                    last = ''
                    for name in names[1:]:
                        last = last + ' ' + name
                    print("{} {}".format(first.strip(), last.strip()))

                    playerUrl = 'https://www.pro-football-reference.com{}'.format(nameLink['href'])

                    playerSoup = get_soup(playerUrl)
                    jerseyContainer = playerSoup.find("div", {"class": "uni_holder"}).find_all('text');
                    jerseyNumber = ''
                    if len(jerseyContainer) > 0:
                        jerseyNumber = jerseyContainer[-1].get_text()

                    team = ''
                    t = teamLink.get_text()
                    team = translate_team_code_to_id(t.upper())
                    #             currentTeam = playerSoup.find("span", {"itemprop": "affiliation"})
                    #             if currentTeam is not None:
                    #                 t = currentTeam.find("a", href=True)['href'].split('/')[2]
                    #                 team = GetTeamId(t.upper())
                    birthDate = ''
                    dob = playerSoup.find("span", {"itemprop": "birthDate"})
                    if dob is not None:
                        birthDate = dob['data-birth']
                    height = ''
                    h = playerSoup.find("span", {"itemprop": "height"})
                    if h is not None:
                        height = h.get_text()
                    weight = ''
                    w = playerSoup.find("span", {"itemprop": "weight"})
                    if w is not None:
                        weight = w.get_text()

                    collegeLink = cols[26].find("a", href=True)
                    playerCollege = collegeLink.get_text()
                    #             collegeSection = playerSoup.find_all("p")[5]
                    #             college = collegeSection.find('strong',text = re.compile('College'))
                    #             playerCollege = ''
                    #             if college is not None:
                    #                 playerCollege = collegeSection.find_all('a', href=True)[0].get_text()

                    print("{} {} {} {} {} {} {} {} {} {} {} {}".format(playerId, nameLink['href'], first.strip(),
                                                                       last.strip(), team, birthDate, jerseyNumber,
                                                                       True, position, playerCollege, jerseyNumber,
                                                                       birthDate, height, weight))

                    if not team:
                        self.cursor.execute(
                            "INSERT INTO Players ([ProReferenceKey],[ProReferenceURL], [FullName],[FirstName], [LastName], [JerseyNumber], [Rookie], [Position], [College], [DateOfBirth], [Height], [Weight],[TradingBlock], [Retired],[WeeksLeftOnIR]) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                            playerId, nameLink['href'], fullName, first.strip(), last.strip(), jerseyNumber, True,
                            position, playerCollege, birthDate, height, weight, False, False, 0)
                        self.cursor.commit()
                    else:
                        self.cursor.execute(
                            "INSERT INTO Players ([ProReferenceKey],[ProReferenceURL], [FullName],[FirstName], [LastName], [NFLTeamId], [JerseyNumber], [Rookie], [Position], [College], [DateOfBirth], [Height], [Weight],[TradingBlock], [Retired],[WeeksLeftOnIR]) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                            playerId, nameLink['href'], fullName, first.strip(), last.strip(), team, jerseyNumber, True,
                            position, playerCollege, birthDate, height, weight, False, False, 0)
                        self.cursor.commit()

        self.cursor.close()
