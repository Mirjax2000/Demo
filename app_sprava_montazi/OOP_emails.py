"""Emails"""

import os
from rich.console import Console
from pypdf import PdfReader, PdfWriter
from django.core.mail import EmailMessage

# ---
cons: Console = Console()


class CustomEmail:
    def __init__(self, subject, body, to_email: list, attachments: list) -> None:
        self.subject = subject
        self.body = body
        self.from_email = "miroslav.viktorin@seznam.cz"
        self.to_email = to_email
        self.attachments = attachments

    def _encrypt_pdf(self, input_pdf_path: str, password: str) -> str:
        """
        Encryptuje pdfko
        """
        reader = PdfReader(input_pdf_path)
        writer = PdfWriter()

        for page in reader.pages:
            writer.add_page(page)

        writer.encrypt(password)

        directory, filename = os.path.split(input_pdf_path)
        name, ext = os.path.splitext(filename)
        encrypted_pdf_path = os.path.join(directory, f"{name}_encrypted{ext}")

        with open(encrypted_pdf_path, "wb") as f:
            writer.write(f)

        return encrypted_pdf_path

    def send_email_with_pdf(self, pdf_password: str):
        """
        POsle zasifrovany pdfko
        """
        email = EmailMessage(self.subject, self.body, self.from_email, self.to_email)

        for file_path in self.attachments:
            encrypted_file_path = self._encrypt_pdf(file_path, pdf_password)

            with open(encrypted_file_path, "rb") as f:
                email.attach(
                    filename=os.path.basename(encrypted_file_path),
                    content=f.read(),
                    mimetype="application/pdf",
                )
            os.remove(encrypted_file_path)

        try:
            email.send()
        except Exception as e:
            cons.log(f"Chyba při odesílání: {str(e)}", style="red")
            raise


if __name__ == "__main__":
    ...
