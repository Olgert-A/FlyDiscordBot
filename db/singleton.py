class SingletonDB:
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'instance'):
            cls.instance = super(SingletonDB, cls).__new__(cls)
        return cls.instance

    def __init__(self, database_url):
        self.DATABASE_URL = database_url
