# Mock logger to help with validating log code branches
# in testing
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
