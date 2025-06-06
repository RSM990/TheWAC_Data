class Settings:
    def __init__(self):
        self.POSITION_LIST = ['QB', 'RB', 'WR', 'TE', 'K']
        self.LAST_ACTIVE_YEAR_CHECK = 2016
        self.CHROME_DRIVER_PATH = 'C:/chromedriver.exe'
        self.IS_PRODUCTION = False
        self.PRODUCTION_CONNECTION_STRING = \
            'DRIVER={SQL Server Native Client 11.0};server=69.167.149.140,782;database=MLR990_TheWAC;uid=MLR990_wacuser;pwd=WACP@ssword123!@#;'
        self.QA_CONNECTION_STRING = \
            'DRIVER={SQL Server Native Client 11.0};server=69.167.149.140,782;database=MLR990_TheWACQA;uid=MLR990_wacuser;pwd=WACP@ssword123!@#;'
        self.DEV_CONNECTION_STRING = \
            'DRIVER={SQL Server Native Client 11.0};server=(localdb)\\mssqllocaldb;database=TheWAC;'

        self.CURRENT_CONNECTION_STRING = self.PRODUCTION_CONNECTION_STRING
