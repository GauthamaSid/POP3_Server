import pickle
from datetime import datetime

MAILBOX_FILE = 'mailbox.pkl'

class Email:
    def __init__(self, sender, subject, body, to_del):
        self.sender = sender
        self.subject = subject
        self.body = body
        self.to_del = to_del

class Mailbox:
    def __init__(self, user):
        self.user = user
        self.emails = []

    def add_email(self, sender, subject, body):
        email = Email(sender, subject, body, 0)
        self.emails.append(email)

def load_mailbox(user):
    try:
        with open(f'{MAILBOX_FILE}_{user}', 'rb') as file:
            return pickle.load(file)
    except FileNotFoundError:
        mailbox = Mailbox(user)
        return mailbox

def save_mailbox(user, mailbox):
    with open(f'{MAILBOX_FILE}_{user}', 'wb') as file:
        pickle.dump(mailbox, file)

def add_email(user, sender, subject, body):
    mailbox = load_mailbox(user)
    mailbox.add_email(sender, subject, body)
    save_mailbox(user, mailbox)
    print(f"Email added to {user}'s mailbox.")

if __name__ == "__main__":
    while True:
        print("1. Add email")
        print("2. Exit")
        choice = input("Enter your choice: ")

        if choice == "1":
            user = input("Enter the username: ")
            sender = input("Enter the sender's email address: ")
            subject = input("Enter the email subject: ")
            body = input("Enter the email body: ")
            add_email(user, sender, subject, body)
        elif choice == "2":
            break
        else:
            print("Invalid choice. Please try again.")