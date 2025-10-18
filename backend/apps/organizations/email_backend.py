"""
Custom email backend for testing invitations.
"""
import os
from django.core.mail.backends.base import BaseEmailBackend
from django.conf import settings


class FileEmailBackend(BaseEmailBackend):
    """
    Email backend that saves emails to files for testing.
    """
    
    def __init__(self, fail_silently=False, **kwargs):
        super().__init__(fail_silently=fail_silently, **kwargs)
        self.emails_dir = os.path.join(settings.BASE_DIR, 'sent_emails')
        os.makedirs(self.emails_dir, exist_ok=True)
    
    def send_messages(self, email_messages):
        """
        Save email messages to files.
        """
        if not email_messages:
            return 0
        
        sent_count = 0
        for message in email_messages:
            try:
                # Create filename with timestamp
                import time
                timestamp = int(time.time())
                filename = f"email_{timestamp}_{sent_count}.txt"
                filepath = os.path.join(self.emails_dir, filename)
                
                # Write email content to file
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(f"To: {', '.join(message.to)}\n")
                    f.write(f"From: {message.from_email}\n")
                    f.write(f"Subject: {message.subject}\n")
                    f.write("-" * 50 + "\n")
                    f.write(message.body)
                
                sent_count += 1
                print(f"Email saved to: {filepath}")
                
            except Exception as e:
                if not self.fail_silently:
                    raise e
        
        return sent_count
