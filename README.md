# Email to Audio Transcription Script

## Introduction

This Python script automates the process of converting email text to audio files using OpenAI's transcription services. The script:
- Retrieves and processes unread emails with a specific subject.
- Uses OpenAI's API to transcribe the email content to audio.
- Sends the transcribed audio file back to the sender.

## Prerequisites

Before using this script, ensure you have the following:
- Python 3.7 or higher
- An OpenAI API key

## Installation

1. **Clone the Repository:**
   ```sh
   git clone https://github.com/yourusername/your-repo.git
   cd your-repo
   ```

2. **Install Dependencies:**
   - Create a virtual environment (optional but recommended):
     ```sh
     python -m venv env
     source env/bin/activate  # On Windows use `env\Scripts ctivate`
     ```
   - Install required packages:
     ```sh
     pip install -r requirements.txt
     ```

## Configuration

### Environment Variables

Set the following environment variables for the script to function correctly:

- `AITOOLS_IMAP_SERVER`: Your IMAP server (e.g., imap.example.com)
- `AITOOLS_IMAP_PORT`: Your IMAP server port (e.g., 993)
- `AITOOLS_SMTP_SERVER`: Your SMTP server (e.g., smtp.example.com)
- `AITOOLS_SMTP_PORT`: Your SMTP server port (e.g., 587)
- `AITOOLS_EMAIL_ACCOUNT`: Your email account
- `AITOOLS_EMAIL_PASSWORD`: Your email account password
- `OPENAI_API_KEY`: Your OpenAI API key

Example configuration in a `.env` file:
```env
AITOOLS_IMAP_SERVER=
AITOOLS_IMAP_PORT=993
AITOOLS_SMTP_SERVER=
AITOOLS_SMTP_PORT=587
AITOOLS_EMAIL_ACCOUNT=your-email@example.com
AITOOLS_EMAIL_PASSWORD=yourpassword
OPENAI_API_KEY=your-openai-api-key
```

### Setting Environment Variables

On Unix-based systems, you can set environment variables like this:
```sh
export AITOOLS_IMAP_SERVER=
export AITOOLS_IMAP_PORT=993
export AITOOLS_SMTP_SERVER=
export AITOOLS_SMTP_PORT=587
export AITOOLS_EMAIL_ACCOUNT=your-email@example.com
export AITOOLS_EMAIL_PASSWORD=yourpassword
export OPENAI_API_KEY=your-openai-api-key
```

## Usage

Run the Script:
```sh
python tts_email.py
```

### Email Subject Format

The script looks for emails with the subject "TTS".
You can specify the voice model in the subject (e.g., "TTS: onyx"). Available models are:
- alloy
- echo
- fable
- onyx (default)
- nova
- shimmer

## Security Considerations

- **Handling Sensitive Information**: Ensure that your environment variables, especially those containing passwords and API keys, are kept secure and not hard-coded in the script.
- **Best Practices**: Use environment variable management tools like dotenv for secure and convenient handling.

## Troubleshooting

### Common Issues

- **Missing Environment Variables**: Ensure all required environment variables are set.
- **Connection Errors**: Verify your email server details and internet connection.
- **Processing Failures**: Check logs for any errors related to the OpenAI API or email processing.

### Log Messages

Check the log output for detailed error messages and follow the recommendations.

## Future Development Ideas

- Enhanced Error Handling: Improve robustness with more granular error handling.
- Multiple Email Accounts: Support multiple email accounts.
- Web Interface: Develop a web-based interface for easier management.
- Scheduled Transcriptions: Add the ability to schedule transcription jobs.
- Content Moderation: Use OpenAI's moderation endpoint to filter and classify email content before processing.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

If you would like to contribute to this project, please fork the repository and submit a pull request. For major changes, please open an issue first to discuss what you would like to change.
