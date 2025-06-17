# 📖 AI Storyteller API

This FastAPI-based backend lets you create, continue, and summarize fictional stories using OpenAI's GPT models. It also generates vertical slide images from each chapter for visual storytelling or social media sharing.

## 🚀 Features

- ✅ Start a story with a title, setting, and characters
- ✅ Generate new chapters using GPT-4o
- ✅ Auto-summarize each chapter and maintain a story-wide summary
- ✅ Create slide images for each chapter (1080x1920) from the text
- ✅ RESTful API with CORS enabled for frontend integration

## 🧠 Tech Stack

- [FastAPI](https://fastapi.tiangolo.com/)
- [OpenAI GPT-4o](https://platform.openai.com/)
- [Pillow](https://pillow.readthedocs.io/) for image generation
- [nltk](https://www.nltk.org/) for sentence tokenization

## 📦 Installation

1. **Clone the repo**:
   git clone https://github.com/yourusername/ai-storyteller-api.git
   cd ai-storyteller-api

Install dependencies:
pip install -r requirements.txt

Create .env file:
OPENAI_API_KEY=your_openai_key_here

Run the API:
uvicorn main:app --reload
The API will be available at: http://localhost:8000

🧪 Example Endpoints
➕ Start a new story
POST /start-story
{
  "title": "The Lost Kingdom",
  "setting": "Ancient magical world",
  "characters": [
    { "name": "Aria", "description": "Brave warrior", "traits": "Loyal, Fearless" }
  ]
}

✍️ Generate next chapter
POST /generate-chapter
{
  "story_filename": "the_lost_kingdom.json",
  "prompt": "Describe Aria's encounter with the fire dragon."
}

🖼️ Generate slides for a chapter
POST /generate-slides?story_filename=the_lost_kingdom.json&chapter_number=1

Returns a list of generated PNG file paths.

📄 Get full story JSON
GET /get-story/the_lost_kingdom.json

🗂️ List all saved stories
GET /stories

📷 Get a slide image
GET /slides/the_lost_kingdom/chapter1/slide_1.png

🗂️ Project Structure
.
├── main.py              # FastAPI application
├── stories/             # Folder to store story JSON files
├── slides/              # Folder to store generated slide images
├── fonts/               # Optional: store TTF fonts here
├── .env                 # Your OpenAI key (not committed)
└── requirements.txt     # Python dependencies

🔐 Environment Variables
Make sure to set your .env file with:
OPENAI_API_KEY=your_openai_key_here

📝 License
MIT License. See LICENSE file for details.

👨‍💻 Author
Developed by Jeffrey Manuel

Contributions, issues, and stars are welcome! 🌟