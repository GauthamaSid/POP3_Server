# add_messages.py

import pickle
from pop3_server import Mailbox, Email  # Import the Mailbox and Email classes from your existing POP3 server script

def add_messages():
    # Create or load the mailbox
    try:
        with open('mailbox.pkl', 'rb') as file:
            mailbox = pickle.load(file)
    except FileNotFoundError:
        mailbox = Mailbox()

    # Add new messages
    mailbox.add_email("new_user@example.com", "New Message 1", "This is a new message.")
    mailbox.add_email("another_user@example.com", "New Message 2", "This is another new message.")

    # Save the updated mailbox
    with open('mailbox.pkl', 'wb') as file:
        pickle.dump(mailbox, file)

if __name__ == "__main__":
    add_messages()
