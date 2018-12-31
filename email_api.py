import logging
import smtplib
import email.utils
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


class EmailApi(object):
    def __init__(self,
                 username,
                 password,
                 to_email,
                 from_email) -> None:
        super().__init__()
        self._username = username
        self._password = password
        self._to = to_email
        self._from = from_email
        self._host = "email-smtp.eu-west-1.amazonaws.com"
        self._port = 587
        self._logger = logging.getLogger()
        self._logger.setLevel(logging.INFO)

    def send_email(self, from_name, subject, body):
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = email.utils.formataddr((from_name, self._from))
        msg['To'] = self._to
        part1 = MIMEText(body, 'plain')
        msg.attach(part1)

        # CONFIGURATION_SET = "ConfigSet"
        # msg.add_header('X-SES-CONFIGURATION-SET',CONFIGURATION_SET)
        # part2 = MIMEText(BODY_HTML, 'html')
        # msg.attach(part2)

        try:
            server = smtplib.SMTP(self._host, self._port)
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(self._username, self._password)
            server.sendmail(self._from, self._to, msg.as_string())
            server.close()
        except Exception as e:
            self._logger.error('failed to send email to {} with exception {}'.format(self._to, e))
        else:
            self._logger.info('successfully sent email to {}'.format(self._to))