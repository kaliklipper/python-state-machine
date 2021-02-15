"""Custom Exceptions for the state machine"""


class ActivationOutOfPhase(Exception):

    def __init(self, message='Attempt to activate action out of correct phase'):
        self.message = message
        super().__init__(self.message)


class PropertyKeyNotRecognised(Exception):

    def __init__(self, message='Property Key not recognised'):
        self.message = message
        super().__init__(self.message)


class DuplicateDataInControlDatabase(Exception):

    def __init(self, message='Duplicate records found in control database'):
        self.message = message
        super().__init__(self.message)


class MissingDataInControlDatabase(Exception):

    def __init(self, message='Record not found in control database'):
        self.message = message
        super().__init__(self.message)


class RDBMSNotRecognised(Exception):

    def __init__(self, message='RDBMS not recognised / supported'):
        self.message = message
        super().__init__(self.message)


class TimestampFormatNotRecognised(Exception):

    def __init__(self, message='Timestamp format not recognised'):
        self.message = message
        super().__init__(self.message)
