const API_URL = "http://localhost:8000"; // Change to your actual backend URL if deployed

const storyListDiv = document.getElementById("story-list");
const chapterListDiv = document.getElementById("chapter-list");
const chapterContentDiv = document.getElementById("chapter-content");

let currentStory = null;

// Fetch list of stories
async function fetchStories() {
  try {
    const res = await fetch(`${API_URL}/stories`);
    const stories = await res.json();

    storyListDiv.innerHTML = `<h4>Stories:</h4>`;
    stories.forEach(filename => {
      const btn = document.createElement("button");
      btn.className = "btn btn-outline-primary btn-sm me-2 mb-2";
      btn.innerText = filename.replace(".json", "").replace(/_/g, " ");
      btn.onclick = () => loadStory(filename);
      storyListDiv.appendChild(btn);
    });
  } catch (err) {
    storyListDiv.innerHTML = `<div class="text-danger">Error loading stories</div>`;
    console.error(err);
  }
}

// Load story and show chapters
async function loadStory(filename) {
  try {
    const res = await fetch(`${API_URL}/get-story/${filename}`);
    const data = await res.json();
    currentStory = data;

    chapterListDiv.innerHTML = `<h4>${data.title}</h4><p class="text-muted">${data.setting}</p><hr/><h5>Chapters:</h5>`;
    data.chapters.forEach((ch, i) => {
      const btn = document.createElement("button");
      btn.className = "btn btn-outline-dark btn-sm me-2 mb-2";
      btn.innerText = `Chapter ${i + 1}`;
      btn.onclick = () => showChapter(i);
      chapterListDiv.appendChild(btn);
    });

    chapterContentDiv.classList.add("d-none");
  } catch (err) {
    chapterListDiv.innerHTML = `<div class="text-danger">Error loading story</div>`;
    console.error(err);
  }
}

// Show specific chapter
function showChapter(index) {
  const chapter = currentStory.chapters[index];
  chapterContentDiv.innerHTML = `
    <h5 class="mb-2">Chapter ${index + 1}</h5>
    <p class="text-muted">${new Date(chapter.created_at).toLocaleString()}</p>
    <hr/>
    <div>${chapter.content.replace(/\n/g, "<br>")}</div>
  `;
  chapterContentDiv.classList.remove("d-none");
}

// Load stories on start
fetchStories();
