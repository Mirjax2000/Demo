from django.core.mail import EmailMessage


class CustomEmail:
    def __init__(self, subject, body, to_email: list, attachments: list) -> None:
        self.subject = subject
        self.body = body
        self.from_email = "miroslav.viktorin@seznam.cz"
        self.to_email: list = to_email
        self.attachments: list = attachments

    def send_email(self) -> None:
        email = EmailMessage(self.subject, self.body, self.from_email, self.to_email)
        email.send()

    def send_email_with_pdf(self):
        email = EmailMessage(self.subject, self.body, self.from_email, self.to_email)

        for file_path in self.attachments:
            with open(file_path, "rb") as f:
                email.attach(
                    filename=file_path.split("/")[-1],
                    content=f.read(),
                    mimetype="application/pdf",
                )

        email.send()


if __name__ == "__main__":
    ...
