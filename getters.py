import psycopg2
import smtplib
import logging


from config import EmailSettings


logging.basicConfig(filename='logs/debug.log', level=logging.INFO,
                    format="%(asctime)s %(message)s",
                    datefmt="%Y-%m-%d %H:%M:%S %p")


class DBGetter(object):
    def __init__(self, dbname):
        self.connection = psycopg2.connect(dbname=dbname)
        self.cur = self.connection.cursor()

    def insert(self, execution, values=None):
        self.cur.execute(execution, values)
        self.connection.commit()
        self.cur.close()
        self.connection.close()

    def get(self, execution):
        self.cur.execute(execution)
        rows = self.cur.fetchall()
        self.cur.close()
        self.connection.close()
        return rows


class EMailGetter:
    def __init__(self):
        self.server = smtplib.SMTP(EmailSettings.SMTP_SERVER,
                                   EmailSettings.SMTP_PORT)

    def send_email(self, subject, body):
        from_user = EmailSettings.EMAIL_ADDRESS_FROM
        pwd = EmailSettings.EMAIL_PWD
        to_user = EmailSettings.EMAIL_ADDRESS_TO
        subject = subject
        text = body

        # Prepare actual message
        message = """From: %s\nTo: %s\nSubject: %s\n\n%s
        """ % (from_user, to_user, subject, text)
        try:
            self.server.ehlo()
            self.server.starttls()
            self.server.login(from_user, pwd)
            self.server.sendmail(from_user, to_user, message)
            self.server.close()
        except Exception as error:
            logging.error("Failed to send mail: %s" % error)
