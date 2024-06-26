"""
AI Tools Email Processor
Version: 0.3

This script processes emails with the subject 'TTS', checks for content safety using OpenAI's moderation endpoint,
transcribes the email content to audio using OpenAI's TTS model, and sends an email with the transcribed audio file attached.

Features:
- Checks for new emails with subject 'TTS'.
- Provides word character limit per email.
- Moderates email content to ensure safety.
- Transcribes email content to audio.
- Sends an email with the transcribed audio file attached.
- Provides links to LinkedIn, Flickr, and Etsy pages in the email.

Requirements:
- imaplib
- smtplib
- email
- openai
- logging
- argparse
- python-dotenv

GitHub Repository: https://github.com/adrianhensler/ajh_ai_tools

Author: Adrian Hensler
"""
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders
from pathlib import Path
import openai
import os
import logging
import time
import argparse
from dotenv import load_dotenv
import warnings

# Ignore DeprecationWarning to get rid of "DeprecationWarning: Due to a bug, this method doesn't actually stream the response content, .with_streaming_response.method() should be used instead"
warnings.filterwarnings("ignore", category=DeprecationWarning)

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Email credentials and server details from environment variables
IMAP_SERVER = os.getenv('AITOOLS_IMAP_SERVER')
IMAP_PORT = int(os.getenv('AITOOLS_IMAP_PORT'))
SMTP_SERVER = os.getenv('AITOOLS_SMTP_SERVER')
SMTP_PORT = int(os.getenv('AITOOLS_SMTP_PORT'))
EMAIL_ACCOUNT = os.getenv('AITOOLS_EMAIL_ACCOUNT')
EMAIL_PASSWORD = os.getenv('AITOOLS_EMAIL_PASSWORD')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
FORCE_MODERATION = os.getenv('FORCE_MODERATION', 'true').lower() == 'true'
DISABLE_MODERATION = os.getenv('DISABLE_MODERATION', 'false').lower() == 'false'

# Define maximum character count for email body
MAX_CHARACTER_COUNT = 2000  # Set your desired limit

# Validate environment variables
if not EMAIL_ACCOUNT or not EMAIL_PASSWORD or not OPENAI_API_KEY:
    logging.error("Missing essential environment variables. Please check your .env file.")
    exit(1)

# Log the loaded environment variables (except sensitive information)
logging.info(f"IMAP_SERVER: {IMAP_SERVER}")
logging.info(f"IMAP_PORT: {IMAP_PORT}")
logging.info(f"SMTP_SERVER: {SMTP_SERVER}")
logging.info(f"SMTP_PORT: {SMTP_PORT}")

# Initialize OpenAI API key
openai.api_key = OPENAI_API_KEY

def check_email():
    """Check the email inbox for new messages with the subject 'TTS'."""
    try:
        mail = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT)
        mail.login(EMAIL_ACCOUNT, EMAIL_PASSWORD)
        mail.select('inbox')

        result, data = mail.search(None, '(UNSEEN SUBJECT "TTS")')
        email_ids = data[0].split()

        if not email_ids:
            logging.info("No new emails found.")
            return

        for email_id in email_ids:
            result, data = mail.fetch(email_id, '(RFC822)')
            raw_email = data[0][1]
            msg = email.message_from_bytes(raw_email)

            from_email = msg['From']
            subject = msg['Subject']
            email_body = extract_email_body(msg)

            if email_body:
                char_count = len(email_body)
                if char_count > MAX_CHARACTER_COUNT:
                    logging.warning(f"Email from {from_email} exceeds the character count limit and was not processed.")
                    continue

                moderate_content = not DISABLE_MODERATION and (FORCE_MODERATION or 'NO_MODERATION' not in subject.upper())

                if not moderate_content or is_content_safe(email_body):
                    voice_model = extract_voice_model(subject)
                    transcribed_audio_path = transcribe_text_to_audio(email_body, voice_model)
                    if transcribed_audio_path:
                        send_email(from_email, subject, transcribed_audio_path)
                        mail.store(email_id, '+FLAGS', '\\Seen')
                    else:
                        logging.error(f"Failed to transcribe and send email for {from_email}")
                else:
                    logging.warning(f"Email from {from_email} contained inappropriate content and was not processed.")
    except Exception as e:
        logging.error(f"Error checking email: {e}")
    finally:
        try:
            mail.logout()
        except Exception as e:
            logging.error(f"Error logging out from email server: {e}")

def extract_email_body(msg):
    """Extract the body of the email."""
    try:
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/plain":
                    return part.get_payload(decode=True).decode('utf-8')
        else:
            return msg.get_payload(decode=True).decode('utf-8')
    except Exception as e:
        logging.error(f"Error extracting email body: {e}")
    return None

def extract_voice_model(subject):
    """Extract the voice model from the email subject."""
    models = ['alloy', 'echo', 'fable', 'onyx', 'nova', 'shimmer']
    for model in models:
        if model in subject.lower():
            return model
    return 'onyx'  # Default voice model

def is_content_safe(text):
    """Check if the email content is safe using OpenAI's moderation endpoint."""
    try:
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        response = client.moderations.create(input=text)
        results = response.results[0]  # Use dot notation to access results
        if results.flagged:  # Use dot notation to access flagged attribute
            return False
        return True
    except Exception as e:
        logging.error(f"Error checking content safety: {e}")
        return False

def transcribe_text_to_audio(text, voice_model='onyx'):
    """Transcribe text to audio using OpenAI's TTS model."""
    try:
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        speech_file_path = Path(__file__).parent / "speech.mp3"
        response = client.audio.speech.create(
            model="tts-1",
            voice=voice_model,
            input=text
        )
        response.stream_to_file(speech_file_path)
        return speech_file_path
    except Exception as e:
        logging.error(f"Error transcribing text to audio: {e}")
        return None

def send_email(to_email, subject, audio_file_path):
    """Send an email with the transcribed audio file as an attachment."""
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_ACCOUNT
        msg['To'] = to_email
        msg['Subject'] = subject

        # Adding the body text to the email with HTML content
        body = """
        <html>
        <body>
            <p>Dear {to_email},</p>
            <p>Thank you for using <strong>ajh_ai_tools</strong>. Please find the transcribed audio file attached.</p>
            <p>Best regards,<br>Adrian Hensler</p>
            <hr>
            <p>Connect with me:</p>
            <ul>
                <li><a href="https://www.linkedin.com/in/adrian-hensler/">Please visit my LinkedIn</a></li>
                <li><a href="https://www.flickr.com/photos/adrianhensler/">Please enjoy my photography on Flickr</a></li>
            </ul>
        </body>
        </html>
        """.format(to_email=to_email)

        msg.attach(MIMEText(body, 'html'))

        # Adding the audio attachment
        with open(audio_file_path, 'rb') as audio_file:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(audio_file.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', 'attachment', filename='transcribed_audio.mp3')
            msg.attach(part)

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_ACCOUNT, EMAIL_PASSWORD)
            server.sendmail(EMAIL_ACCOUNT, to_email, msg.as_string())
            logging.info(f"Email sent to {to_email}")
    except Exception as e:
        logging.error(f"Error sending email: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process emails and transcribe to audio.")
    parser.add_argument('--loop', action='store_true', help="Run the script in a loop.")
    args = parser.parse_args()

    if args.loop:
        try:
            while True:
                check_email()
                time.sleep(60)  # Check for new emails every minute
        except KeyboardInterrupt:
            logging.info("Service interrupted by user.")
        except Exception as e:
            logging.error(f"Unexpected error: {e}")
    else:
        check_email()
