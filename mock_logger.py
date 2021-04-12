# Mock logger to help with validating log code branches
# in testing. Note that some logging in testing can be done
# with the caplog test fixture, but this doesn't help with
# in the case that a logger is passed in as a parameter, such
# as in `redis_connector.py`.
# See: https://docs.pytest.org/en/stable/logging.html
class MockLogger:
    def __init__(self):
        self.info_messages = []
        self.warn_messages = []
        self.error_messages = []
    
    def info(self, msg: str):
        self.info_messages.append(msg)
    
    def warn(self, msg: str):
        self.warn_messages.append(msg)

    def error(self, msg: str):
        self.error_messages.append(msg)
