class BotSettings:
    # for the tests
    # TOKEN = ""
    # production token
    TOKEN = ""
    COMMANDS = ["/start", "/courses", "/events", "/contacts", "/about",
                "/add_event", "/delete_course", "/delete_event", "/add_course"]


class DBSettings:
    HOST = ""
    USER = ""
    PASSWORD = ""


class EmailSettings:
    SMTP_SERVER = "smtp.gmail.com"
    SMTP_PORT = 587
    EMAIL_PWD = ""
    EMAIL_ADDRESS_FROM = ""
    EMAIL_ADDRESS_TO = ""
