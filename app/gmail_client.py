import email
from email.header import decode_header
import imaplib
from mimetypes import MimeTypes
import os

from drive_client import DriveClient


class GmailClient:
    def __init__(self) -> None:
        self.user = os.environ.get("WATCH_EMAIL", "contact.fuzzylabs@gmail.com")
        self.password = os.environ.get("WATCH_PASSWORD", "xjvqkodofonrhzxe")
        self.imap_url = "imap.gmail.com"

    def process_emails(self):
        imap = imaplib.IMAP4_SSL(self.imap_url)
        imap.login(self.user, self.password)
        status, messages = imap.select("INBOX")
        leaf_folder_existed = True
        is_attachment = False
        numOfMessages = int(messages[0])
        for i in range(numOfMessages, numOfMessages - 100, -1):
            res, msg = imap.fetch(str(i), "(RFC822)")
            is_attachment = False
            for response in msg:
                if isinstance(response, tuple):
                    msg = email.message_from_bytes(response[1])
                    subject, From, date = self.__obtain_header(msg)
                    if msg.is_multipart():
                        for part in msg.walk():
                            content_type = part.get_content_type()
                            print("Content_type: ", content_type)
                            content_disposition = str(part.get("Content-Disposition"))
                            print("content_disposition: ", content_disposition)
                            if "attachment" in content_disposition:
                                leaf_folder_existed = (
                                    self.__download_attachment(part, subject, date, leaf_folder_existed)
                                    and leaf_folder_existed
                                )
                                print(f"leaf_folder_existed: {leaf_folder_existed}")
                                is_attachment = True
                                if leaf_folder_existed:
                                    break
            if is_attachment:
                self.__upload_details(From, subject, date)
            print("=" * 100)
            if leaf_folder_existed and is_attachment:
                break
        imap.close()
        return f"There where {len(messages)} messages. Can you believe!"

    # clean text for creating a folder
    def __clean(self, text):
        return "".join(c if c.isalnum() else "_" for c in text)

    # decode the email subject
    def __obtain_header(self, msg):
        subject, encoding = decode_header(msg["Subject"])[0]
        if isinstance(subject, bytes):
            subject = subject.decode(encoding)
        # decode email sender
        From, encoding = decode_header(msg.get("From"))[0]
        if isinstance(From, bytes):
            From = From.decode(encoding)
        # date = datetime.strptime(msg["Date"], "%a, %d %b %Y %H:%M:%S GMT")
        date = email.utils.parsedate_to_datetime(msg["Date"]).strftime("%d-%b-%Y")
        print("Subject:", subject)
        print("From:", From)
        print("Date:", date)
        return subject, From, date

    # download attachment
    def __download_attachment(self, part, subject, date, leaf_folder_existed):
        filename = part.get_filename()
        if filename:
            folder_name = self.__clean(subject)
            if not os.path.isdir(folder_name):
                os.mkdir(folder_name)
            filepath = os.path.join(folder_name, filename)
            # download attachment and save it
            file = open(filepath, "wb")
            file.write(part.get_payload(decode=True))
            file.close()
            return DriveClient().upload_file(
                filepath,
                filename,
                date + "/" + folder_name,
                MimeTypes().guess_type(filename)[0],
                leaf_folder_existed,
            )
    
    # upload details
    def __upload_details(self, From, subject, date):
        filename = "info.txt"
        folder_name = self.__clean(subject)
        if not os.path.isdir(folder_name):
            os.mkdir(folder_name)
        filepath = os.path.join(folder_name, filename)
        file = open(filepath, "wt")
        file.write(f"From: {From}\n\nSubject: {subject}")
        file.close()
        DriveClient().upload_file(
            filepath,
            filename,
            date + "/" + folder_name,
            MimeTypes().guess_type(filename)[0],
            False,
        )

    def __get_body(self, msg):
        if msg.is_multipart():
            return self.__get_body(msg.get_payload(0))
        else:
            return msg.get_payload(None, True).decode()
