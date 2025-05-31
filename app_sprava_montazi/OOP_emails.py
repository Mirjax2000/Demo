from django.core.mail import EmailMessage


class CustomEmail:
    def __init__(self, subject, body, to_email: list, attachments: list) -> None:
        self.subject = subject
        self.body = body
        self.from_email = "tvuj.email@gmail.com"
        self.to_email: list = to_email
        self.attachments: list = attachments

    def send_email(self) -> None:
        email = EmailMessage(self.subject, self.body, self.from_email, self.to_email)
        email.send()

    # def send_email_with_pdf(self):
    #     subject = self.subject
    #     body = self.body
    #     from_email = self.from_email
    #     to_email = self.to_email

    #     email = EmailMessage(subject, body, from_email, to_email)

    #     email.attach(self.attachments)

    #     email.send()


if __name__ == "__main__":
    ...
