# Drug Price File Automation Tool

This Streamlit app automates the process of generating drug price information sheets. It uses data stored in public Google Drive files and allows users to select compounds and generate Excel files with detailed drug information.

## Features

- Select compounds from a pre-populated list or input compound IDs directly
- Generate Excel files with formatted drug information
- Access data stored in public Google Drive files

## Setup

1. Clone this repository
2. Install the required packages:
   ```
   pip install -r requirements.txt
   ```
3. Update the `file_ids` dictionary in `app.py` with your public Google Drive file IDs

## Running the App Locally

To run the app locally:

```
streamlit run app.py
```

## Deploying to Streamlit Sharing

1. Push your code to a GitHub repository
2. Connect your GitHub account to Streamlit Sharing
3. Deploy your app by selecting the repository and branch

## Usage

1. Open the app
2. Choose whether to select compounds from the list or input IDs directly
3. Select or input the desired compound IDs
4. Click "Generate Excel File"
5. Download the generated Excel file

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License.