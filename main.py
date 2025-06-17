from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from dotenv import load_dotenv
from openai import OpenAI, OpenAIError
from PIL import Image, ImageDraw, ImageFont
from nltk.tokenize import sent_tokenize
import nltk

import os
import json
import datetime

# -------------- Load Environment + NLTK --------------
load_dotenv()
nltk.download('punkt', force=True)
client = OpenAI()  # Uses OPENAI_API_KEY from environment

# -------------- App Initialization --------------
app = FastAPI()

# Enable CORS (for frontend development use "*"; restrict in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update to specific domains in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create required directories
os.makedirs("stories", exist_ok=True)
os.makedirs("slides", exist_ok=True)

# -------------- Data Models --------------
class Character(BaseModel):
    name: str
    description: Optional[str] = ""
    traits: Optional[str] = ""
    backstory: Optional[str] = ""

class StorySetup(BaseModel):
    title: str
    setting: str
    characters: List[Character]

class ContinueStoryInput(BaseModel):
    story_filename: str
    prompt: Optional[str] = "Continue the story."

# -------------- Utility Functions --------------
def get_story_filepath(title: str) -> str:
    safe_title = title.lower().replace(" ", "_").replace("/", "-")
    return f"stories/{safe_title}.json"

def save_story_file(filename: str, data: dict):
    with open(f"stories/{filename}", "w") as f:
        json.dump(data, f, indent=4)

def load_story_file(filename: str) -> dict:
    path = f"stories/{filename}"
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Story not found")
    with open(path, "r") as f:
        return json.load(f)

def summarize_chapter(chapter_text: str, chapter_num: int) -> str:
    summary_prompt = (
        f"Summarize Chapter {chapter_num} of the story below in a clear and concise narrative style. "
        f"Focus on major events, emotional developments, and character progression:\n\n"
        f"{chapter_text}"
    )
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that summarizes fiction chapters."},
                {"role": "user", "content": summary_prompt}
            ]
        )
        return response.choices[0].message.content.strip()
    except OpenAIError as e:
        raise HTTPException(status_code=500, detail=f"Summary generation failed: {str(e)}")

# -------------- API Routes: Story Management --------------
@app.post("/start-story")
def start_story(story: StorySetup):
    created = datetime.datetime.now().isoformat()
    story_data = {
        "title": story.title,
        "setting": story.setting,
        "created_at": created,
        "summary": "",
        "characters": [char.dict() for char in story.characters],
        "chapters": []
    }
    filename = get_story_filepath(story.title).split("/")[-1]
    save_story_file(filename, story_data)
    return {"story_filename": filename}

@app.post("/generate-chapter")
def generate_chapter(input: ContinueStoryInput):
    story_data = load_story_file(input.story_filename)
    title = story_data["title"]
    setting = story_data["setting"]
    summary = story_data.get("summary", "").strip()
    characters = story_data.get("characters", [])
    chapter_num = len(story_data["chapters"]) + 1

    # Compose character descriptions
    char_descriptions = "\n".join([
        f"{char['name']} - {char.get('description', '')} {char.get('traits', '')} {char.get('backstory', '')}"
        for char in characters
    ])

    # Prompt to generate story content
    prompt = (
        f"You are an AI storyteller. Write Chapter {chapter_num} of the story titled '{title}'.\n"
        f"Setting: {setting}\n"
        f"Characters:\n{char_descriptions}\n"
        f"Story so far:\n{summary}\n\n"
        f"{input.prompt}"
    )

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a helpful storyteller AI."},
                {"role": "user", "content": prompt}
            ]
        )
        chapter_text = response.choices[0].message.content.strip()
    except OpenAIError as e:
        raise HTTPException(status_code=500, detail=f"OpenAI API error: {str(e)}")

    # Summarize the generated chapter
    chapter_summary = summarize_chapter(chapter_text, chapter_num)

    # Save the chapter
    created = datetime.datetime.now().isoformat()
    story_data["chapters"].append({
        "created_at": created,
        "chapter_number": chapter_num,
        "content": chapter_text,
        "summary": chapter_summary
    })
    story_data["summary"] += f"\nChapter {chapter_num} summary: {chapter_summary}"

    save_story_file(input.story_filename, story_data)

    return {"chapter": chapter_text, "summary": chapter_summary}

@app.get("/get-story/{filename}")
def get_story(filename: str):
    return load_story_file(filename)

@app.get("/stories")
def list_stories():
    return [f for f in os.listdir("stories") if f.endswith(".json")]

# -------------- Slide Generator --------------
def split_text_into_slides(text: str, max_chars=400) -> List[str]:
    sentences = sent_tokenize(text)
    slides = []
    current_slide = ""

    for sentence in sentences:
        if len(current_slide) + len(sentence) <= max_chars:
            current_slide += " " + sentence
        else:
            slides.append(current_slide.strip())
            current_slide = sentence
    if current_slide:
        slides.append(current_slide.strip())

    return slides

def generate_slide_image(text: str, output_path: str):
    width, height = 1080, 1920
    image = Image.new("RGB", (width, height), "black")
    draw = ImageDraw.Draw(image)

    try:
        font = ImageFont.truetype("arial.ttf", 50)
    except:
        font = ImageFont.load_default()

    margin = 60
    current_y = height // 3

    lines = []
    words = text.split()
    line = ""
    for word in words:
        test_line = f"{line} {word}".strip()
        if draw.textlength(test_line, font=font) < (width - 2 * margin):
            line = test_line
        else:
            lines.append(line)
            line = word
    lines.append(line)

    for line in lines:
        bbox = font.getbbox(line)
        line_height = bbox[3] - bbox[1]
        draw.text((margin, current_y), line, font=font, fill="white")
        current_y += line_height + 10

    image.save(output_path)

@app.post("/generate-slides")
def generate_slides(story_filename: str, chapter_number: int):
    story_data = load_story_file(story_filename)
    try:
        chapter = next(ch for ch in story_data["chapters"] if ch["chapter_number"] == chapter_number)
    except StopIteration:
        raise HTTPException(status_code=404, detail="Chapter not found")

    text = chapter["content"]
    slides = split_text_into_slides(text)

    slides_dir = f"slides/{story_filename.replace('.json', '')}/chapter{chapter_number}"
    os.makedirs(slides_dir, exist_ok=True)

    generated_files = []
    for i, slide_text in enumerate(slides):
        slide_path = f"{slides_dir}/slide_{i+1}.png"
        generate_slide_image(slide_text, slide_path)
        generated_files.append(slide_path)

    return {"slides": generated_files}

@app.get("/slides/{filename}")
def get_slide(filename: str):
    file_path = os.path.join("slides", filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Slide not found")
    return FileResponse(file_path)
