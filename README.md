# 📚 Canvas Course Extractor

A modern web application that allows teachers to extract and download their Canvas course content as structured JSON files.

## Features

- 🔗 **Easy Authentication**: Connect using your Canvas API credentials
- 📋 **Course Selection**: Browse and select from all your available courses
- ⚙️ **Smart Extraction**: Automatically parses modules, assignments, pages, discussions, quizzes, and files
- 📥 **JSON Export**: Download structured course data for offline access or analysis
- 🎨 **Modern UI**: Clean, responsive interface with step-by-step workflow
- ⚠️ **Error Handling**: Comprehensive error handling and user feedback

## Project Structure

```
canvas-course-extractor/
├── backend/
│   ├── app.py                 # Flask web server
│   ├── canvas.py              # Canvas API parsing logic
│   ├── requirements.txt       # Python dependencies
│   └── downloads/             # Generated JSON files
├── frontend/
│   ├── index.html            # Main web interface
│   ├── styles.css            # Modern CSS styling
│   └── script.js             # Frontend JavaScript logic
└── README.md
```

## Setup Instructions

### Prerequisites

- Python 3.7 or higher
- Canvas API access token
- Modern web browser

### Installation

1. **Clone or download this project**
   ```bash
   cd canvas-course-extractor
   ```

2. **Install Python dependencies**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

3. **Start the web server**
   ```bash
   python app.py
   ```

4. **Open your browser**
   - Navigate to `http://localhost:5000`
   - The application will load automatically

## Usage Guide

### Step 1: Get Your Canvas API Token

1. Log into your Canvas account
2. Go to **Account** → **Settings**
3. Scroll down to **Approved Integrations**
4. Click **+ New Access Token**
5. Give it a purpose (e.g., "Course Extractor")
6. Copy the generated token

### Step 2: Connect to Canvas

1. Enter your Canvas API URL (e.g., `https://yourschool.instructure.com`)
2. Paste your API access token
3. Click **Connect to Canvas**

### Step 3: Select Course

1. Browse your available courses
2. Click on the course you want to extract
3. Click **Continue with Selected Course**

### Step 4: Download Results

1. Wait for the extraction to complete
2. Review the extraction summary
3. Click **Download JSON File**

## JSON Output Format

The extracted course data follows this structure:

```json
{
  "course_name": "Course Name",
  "course_id": 12345,
  "modules": [
    {
      "title": "Module Name",
      "items": [
        {
          "type": "Assignment",
          "title": "Assignment Title",
          "description": "Assignment description text",
          "due_date": "2024-01-15T23:59:59",
          "download_link": "NA",
          "file_type": "NA"
        },
        {
          "type": "Page",
          "title": "Page Title",
          "description": "Page content text",
          "due_date": "NA",
          "download_link": "NA",
          "file_type": "NA"
        },
        {
          "type": "File",
          "title": "document.pdf",
          "description": null,
          "due_date": "NA",
          "download_link": "https://canvas.../files/123/download",
          "file_type": "NA"
        }
      ]
    }
  ]
}
```

## Supported Content Types

- ✅ **Assignments**: Title, description, due dates
- ✅ **Pages**: Title and content text
- ✅ **Discussions**: Title and message content
- ✅ **Quizzes**: Title and description
- ✅ **Files**: Title and download links
- ✅ **Modules**: Organization and structure

## Technical Details

### Backend (Python/Flask)

- **Flask**: Web server and API endpoints
- **canvasapi**: Official Canvas API Python library
- **BeautifulSoup**: HTML content parsing
- **Flask-CORS**: Cross-origin request handling

### Frontend (HTML/CSS/JavaScript)

- **Modern CSS**: Responsive design with smooth animations
- **Vanilla JavaScript**: No external dependencies
- **Progressive Web App**: Step-by-step user flow
- **Error Handling**: User-friendly error messages

### Security Features

- Session-based authentication
- Input validation and sanitization
- Automatic file cleanup
- CORS protection

## Troubleshooting

### Common Issues

**"Connection failed"**
- Verify your Canvas API URL format
- Check that your API token is valid
- Ensure Canvas allows API access

**"No courses found"**
- Make sure you have teacher/admin access to courses
- Check if your account has the necessary permissions

**"Parsing failed"**
- Large courses may take longer to process
- Some course content might be inaccessible
- Check server logs for specific errors

### Getting Help

1. Check that all dependencies are installed correctly
2. Verify your Canvas API credentials
3. Look at the browser developer console for errors
4. Check the Flask server logs for backend issues

## Development

### Running in Development Mode

```bash
# Backend with auto-reload
cd backend
python app.py

# Access at http://localhost:5000
```

### Code Structure

- **canvas.py**: Core parsing logic with error handling
- **app.py**: Flask web server with REST API
- **frontend/**: Static files served by Flask
- **downloads/**: Temporary storage for generated files

## License

This project is provided as-is for educational purposes. Make sure to comply with your institution's Canvas API usage policies.

## Contributing

Feel free to submit issues, feature requests, or pull requests to improve the Canvas Course Extractor.

---

**Made with ❤️ for educators who want to backup and analyze their course content.** 