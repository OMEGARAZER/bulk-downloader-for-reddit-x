import configparser


class SiteAuthenticator:
    def __init__(self, cfg: configparser.ConfigParser) -> None:
        self.imgur_authentication = None
