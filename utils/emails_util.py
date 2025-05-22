import smtplib
from email.mime.text import MIMEText

from settings.config import GMAIL_PASSWORD, GMAIL
from utils.logger_util import logger

async def send_email(to_email, login, operator):
    with open("resources/subject.html", "r", encoding="utf-8") as file:
        html_content = file.read()

    html_content = html_content.replace("{nick}", login).replace("{operator}", operator)

    msg = MIMEText(html_content, "html", "utf-8")
    msg["Subject"] = "我们注意到您的帐户已登录使用 Steam 身份验证的第三方网站"
    msg["To"] = to_email

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(GMAIL, GMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        logger("The letter has been sent")
    except Exception as e:
        logger("Error sending:" + f"{e}")
