import pickle
from ex_server import Mailbox, MAILBOX_FILE

def main():
    try:
        with open(MAILBOX_FILE, 'rb') as file:
            mailboxes = pickle.load(file)
    except FileNotFoundError:
        mailboxes = {}

    user = input("Enter the username: ")
    if user in mailboxes:
        mailbox = mailboxes[user]
    else:
        mailbox = Mailbox(user)
        mailboxes[user] = mailbox

    print("Enter the email details:")
    sender = input("From: ")
    subject = input("Subject: ")
    body = input("Body: ")

    mailbox.add_email(sender, subject, body)

    with open(MAILBOX_FILE, 'wb') as file:
        pickle.dump(mailboxes, file)

    print("Email added successfully!")

if __name__ == "__main__":
    main()