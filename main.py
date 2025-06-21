import os
import json
from flask import Flask, send_from_directory, request, jsonify

# --- Configuration ---
# The single volume you mount from your host (e.g., Unraid appdata)
CONFIG_DIR = '/app/config'
DATA_DIR = os.path.join(CONFIG_DIR, 'data')
STATIC_DIR = os.path.join(CONFIG_DIR, 'static')
LINKS_FILE = os.path.join(DATA_DIR, 'links.json')

# --- Default File Content ---
# (Content is unchanged, but included for completeness)
DEFAULT_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Homepage</title>
    <link rel="stylesheet" href="/static/style.css">
</head>
<body>
    <div class="container">
        <header>
            <h1>My Homepage</h1>
            <div class="controls">
                <button id="edit-button">Edit Links</button>
                <button id="save-button" class="hidden">Save Changes</button>
            </div>
        </header>
        <main id="links-container">
            <!-- Links will be dynamically loaded here -->
        </main>
    </div>
    <script src="/static/scripts.js"></script>
</body>
</html>
"""

DEFAULT_CSS = """
body {
    background-color: #121212;
    color: #e0e0e0;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
    margin: 0;
    padding: 2rem;
}
.container {
    max-width: 900px;
    margin: 0 auto;
}
header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 2px solid #333;
    padding-bottom: 1rem;
    margin-bottom: 2rem;
}
header h1 {
    margin: 0;
}
.controls button {
    background-color: #007bff;
    color: white;
    border: none;
    padding: 0.5rem 1rem;
    border-radius: 5px;
    cursor: pointer;
    transition: background-color 0.2s;
}
.controls button:hover {
    background-color: #0056b3;
}
.hidden {
    display: none;
}
.section {
    margin-bottom: 2rem;
}
.section h2 {
    color: #00aaff;
    border-bottom: 1px solid #444;
    padding-bottom: 0.5rem;
    margin-bottom: 1rem;
}
.links {
    list-style: none;
    padding: 0;
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
    gap: 1rem;
}
.links a {
    color: #8ab4f8;
    text-decoration: none;
    font-size: 1.1em;
}
.links a:hover {
    text-decoration: underline;
}
/* Edit Mode Styles */
.edit-mode .section-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
}
.edit-mode input {
    background-color: #333;
    color: #eee;
    border: 1px solid #555;
    padding: 0.5rem;
    border-radius: 4px;
    margin-bottom: 0.5rem;
    width: calc(100% - 1.2rem);
}
.edit-mode .link-item {
    display: flex;
    flex-direction: column;
    background-color: #2a2a2a;
    padding: 1rem;
    border-radius: 5px;
}
.edit-mode .remove-btn {
    background-color: #dc3545;
    color: white;
    border: none;
    padding: 0.3rem 0.6rem;
    border-radius: 4px;
    cursor: pointer;
    align-self: flex-end;
}
.edit-mode .add-btn {
    background-color: #28a745;
    color: white;
    border: none;
    padding: 0.5rem;
    border-radius: 4px;
    cursor: pointer;
    margin-top: 0.5rem;
}
"""

DEFAULT_JS = """
document.addEventListener('DOMContentLoaded', () => {
    const editButton = document.getElementById('edit-button');
    const saveButton = document.getElementById('save-button');
    const linksContainer = document.getElementById('links-container');
    let isEditMode = false;

    const fetchAndRenderLinks = async () => {
        try {
            const response = await fetch('/api/links');
            if (!response.ok) throw new Error('Network response was not ok');
            const data = await response.json();
            render(data);
        } catch (error) {
            linksContainer.innerHTML = `<p style="color:red;">Error loading links: ${error.message}</p>`;
            console.error('Fetch error:', error);
        }
    };

    const render = (data) => {
        linksContainer.innerHTML = '';
        data.sections.forEach((section, sectionIndex) => {
            const sectionDiv = document.createElement('div');
            sectionDiv.className = 'section';
            
            let sectionHeaderHTML = isEditMode
                ? `<div class="section-header">
                       <input type="text" value="${section.title}" data-section-index="${sectionIndex}" class="section-title-input">
                       <button class="remove-btn remove-section-btn" data-section-index="${sectionIndex}">Remove Section</button>
                   </div>`
                : `<h2>${section.title}</h2>`;

            sectionDiv.innerHTML = sectionHeaderHTML;

            const linksUl = document.createElement('ul');
            linksUl.className = 'links';

            section.links.forEach((link, linkIndex) => {
                const li = document.createElement('li');
                li.className = 'link-item';
                if (isEditMode) {
                    li.innerHTML = `
                        <input type="text" placeholder="Name" value="${link.name}" data-section-index="${sectionIndex}" data-link-index="${linkIndex}" class="link-name-input">
                        <input type="text" placeholder="URL" value="${link.url}" data-section-index="${sectionIndex}" data-link-index="${linkIndex}" class="link-url-input">
                        <button class="remove-btn remove-link-btn" data-section-index="${sectionIndex}" data-link-index="${linkIndex}">Remove Link</button>
                    `;
                } else {
                    li.innerHTML = `<a href="${link.url}" target="_blank">${link.name}</a>`;
                }
                linksUl.appendChild(li);
            });
            sectionDiv.appendChild(linksUl);
            
            if(isEditMode) {
                const addLinkBtn = document.createElement('button');
                addLinkBtn.textContent = 'Add Link';
                addLinkBtn.className = 'add-btn add-link-btn';
                addLinkBtn.dataset.sectionIndex = sectionIndex;
                sectionDiv.appendChild(addLinkBtn);
            }

            linksContainer.appendChild(sectionDiv);
        });

        if (isEditMode) {
             const addSectionBtn = document.createElement('button');
             addSectionBtn.textContent = 'Add Section';
             addSectionBtn.className = 'add-btn add-section-btn';
             linksContainer.appendChild(addSectionBtn);
        }
        
        addEventListeners();
    };
    
    const toggleEditMode = () => {
        isEditMode = !isEditMode;
        document.body.classList.toggle('edit-mode', isEditMode);
        editButton.classList.toggle('hidden', isEditMode);
        saveButton.classList.toggle('hidden', !isEditMode);
        fetchAndRenderLinks();
    };

    const saveChanges = async () => {
        const sections = [];
        document.querySelectorAll('.section').forEach((sectionDiv, sectionIndex) => {
            const titleInput = sectionDiv.querySelector('.section-title-input');
            if (!titleInput) return; // Skip if section is already gone
            
            const newSection = {
                title: titleInput.value,
                links: []
            };

            sectionDiv.querySelectorAll('.link-item').forEach(linkItem => {
                const nameInput = linkItem.querySelector('.link-name-input');
                const urlInput = linkItem.querySelector('.link-url-input');
                if (nameInput && urlInput && nameInput.value && urlInput.value) {
                    newSection.links.push({
                        name: nameInput.value,
                        url: urlInput.value
                    });
                }
            });
            sections.push(newSection);
        });

        try {
            const response = await fetch('/api/links', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ sections })
            });
            if (!response.ok) throw new Error('Failed to save');
            toggleEditMode(); // Exit edit mode on successful save
        } catch (error) {
            alert(`Error saving: ${error.message}`);
            console.error('Save error:', error);
        }
    };
    
    function addEventListeners() {
        // Use event delegation for dynamically added elements
        linksContainer.addEventListener('click', (e) => {
            if (e.target.matches('.remove-link-btn')) {
                e.target.closest('.link-item').remove();
            }
            if (e.target.matches('.remove-section-btn')) {
                e.target.closest('.section').remove();
            }
            if (e.target.matches('.add-link-btn')) {
                const sectionIndex = e.target.dataset.sectionIndex;
                const linksUl = e.target.previousElementSibling;
                const newLinkLi = document.createElement('li');
                newLinkLi.className = 'link-item';
                newLinkLi.innerHTML = `
                    <input type="text" placeholder="Name" class="link-name-input">
                    <input type="text" placeholder="URL" class="link-url-input">
                    <button class="remove-btn remove-link-btn">Remove Link</button>
                `;
                linksUl.appendChild(newLinkLi);
            }
            if(e.target.matches('.add-section-btn')) {
                 const newSectionDiv = document.createElement('div');
                 newSectionDiv.className = 'section';
                 newSectionDiv.innerHTML = `
                    <div class="section-header">
                       <input type="text" value="New Section" class="section-title-input">
                       <button class="remove-btn remove-section-btn">Remove Section</button>
                    </div>
                    <ul class="links"></ul>
                    <button class="add-btn add-link-btn">Add Link</button>
                 `;
                 // Insert before the "Add Section" button itself
                 linksContainer.insertBefore(newSectionDiv, e.target);
            }
        });
    }

    editButton.addEventListener('click', toggleEditMode);
    saveButton.addEventListener('click', saveChanges);

    // Initial load
    fetchAndRenderLinks();
});
"""

DEFAULT_LINKS = {
    "sections": [
        {
            "title": "Getting Started",
            "links": [
                {"name": "Edit Links", "url": "#"},
                {"name": "Google", "url": "https://google.com"},
                {"name": "GitHub", "url": "https://github.com"}
            ]
        },
        {
            "title": "News",
            "links": [
                {"name": "Hacker News", "url": "https://news.ycombinator.com"},
                {"name": "Reddit", "url": "https://reddit.com"}
            ]
        }
    ]
}


def initialize_app():
    """Checks for required directories and files, creates them if missing."""
    print("Initializing application...")
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(STATIC_DIR, exist_ok=True)

    if not os.path.exists(LINKS_FILE):
        print(f"'{LINKS_FILE}' not found, creating with default content.")
        with open(LINKS_FILE, 'w') as f:
            json.dump(DEFAULT_LINKS, f, indent=4)

    files_to_check = {
        os.path.join(STATIC_DIR, 'index.html'): DEFAULT_HTML,
        os.path.join(STATIC_DIR, 'style.css'): DEFAULT_CSS,
        os.path.join(STATIC_DIR, 'scripts.js'): DEFAULT_JS
    }

    for fpath, content in files_to_check.items():
        if not os.path.exists(fpath):
            print(f"'{fpath}' not found, creating with default content.")
            with open(fpath, 'w') as f:
                f.write(content)
    print("Initialization complete.")


# --- App Initialization ---
# 1. Initialize file structure *before* creating the app object
initialize_app()

# 2. Create the Flask app, explicitly telling it where the static files are.
#    This is more robust than a custom route.
app = Flask(__name__, static_url_path='/static', static_folder=STATIC_DIR)


# --- Flask Routes ---
@app.route('/')
def index():
    """Serve the main index.html file."""
    return send_from_directory(STATIC_DIR, 'index.html')

# The custom static file route is no longer needed, as Flask handles it now.
# @app.route('/static/<path:path>') ...

@app.route('/api/links', methods=['GET'])
def get_links():
    """API endpoint to get the current links configuration."""
    try:
        with open(LINKS_FILE, 'r') as f:
            data = json.load(f)
        return jsonify(data)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        return jsonify({"error": f"Could not read or parse links file: {e}"}), 500

@app.route('/api/links', methods=['POST'])
def save_links():
    """API endpoint to save the links configuration."""
    try:
        new_data = request.get_json()
        if 'sections' not in new_data:
             return jsonify({"error": "Invalid data format"}), 400
        with open(LINKS_FILE, 'w') as f:
            json.dump(new_data, f, indent=4)
        return jsonify({"message": "Links saved successfully"}), 200
    except Exception as e:
        return jsonify({"error": f"Failed to save links: {e}"}), 500


if __name__ == '__main__':
    # This block is only for local development (e.g., `python main.py`)
    # It will not run when using Gunicorn.
    app.run(host='0.0.0.0', port=8000, debug=True)