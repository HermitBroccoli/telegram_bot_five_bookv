from dotenv import dotenv_values

class EnvVariables:
    def __init__(self, file_path=".env"):
        self.file_path = file_path
        self.variables = self.load_variables()

    def load_variables(self):
        return dotenv_values(self.file_path)

    def get_value(self, key, default=None):
        value = self.variables.get(key)
        return value if value is not None and value != '' else default