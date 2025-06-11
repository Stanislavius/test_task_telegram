# Telegram Manager Performance Analyzer

A tool for analyzing manager performance in Telegram by tracking response times, service quality metrics, and customer interaction patterns.

## Project Structure
telegram-manager-analyzer/
│── main.py              # Main script with Telegram client setup and analysis flow
│── manager_performance.py  # Performance metrics calculation and reporting
│── gemini_wrapper.py    # Wrapper for Google's Gemini AI API integration
│── settings.py          # Configuration and environment variables
├── tests/
│   └── test_gemini_queries.py  # Unit tests for Gemini AI functionality
├── .env.s                    # Environment variables (API keys, credentials)
├── .gitignore             # Git ignore file
├── requirements.txt        # Project dependencies
└── README.md              # Project documentation


## Requirements

- Python 3.12+
- Telegram API credentials (api_id and api_hash)
- Google Cloud credentials for Gemini AI

## Installation

1. Clone the repository:
2. Install dependencies:
3. Create `.env` file in the project root or pass them as environmental variables the same way as in .env.sample
4. Run "main.py"

## Setting up Telegram API

1. Get `api_id` and `api_hash` from [my.telegram.org](https://my.telegram.org/):
   - Log in to your account
   - Go to "API development tools"
   - Create a new application
   - Copy API ID and API Hash

2. Set up Google Cloud credentials for Gemini AI:
   - Create a project in [Google Cloud Console](https://console.cloud.google.com/)
   - Enable Gemini API
   - Create service account key and download JSON file
   - Set path to file in .env

## Running the Application

1. Ensure virtual environment is activated

First run will require Telegram authorization:
- Enter phone number
- Enter verification code
- Enter 2FA password if enabled

## Output

After execution, the following reports will be generated in `reports/` directory:
- `summary.html/.csv` - summary metrics table
- `detailed_metrics.html/.csv` - detailed analysis

## Analysis Metrics

- Total message count
- Manager/client message ratio
- Average response time
- Quick/slow responses count
- Service quality analysis
- Unfulfilled promises detection