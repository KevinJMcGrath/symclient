
import sym_session

from rest_admin import Admin


class BotClient:
    """
    Creates a client associated with a Symphony service user account.
    """
    def __init__(self, symphony_config: dict):
        self.config = symphony_config
        self.session = sym_session.Session(self.config)

        self.Admin = Admin(self.session)
