import os
import json
import shutil
from flask import Flask, send_from_directory, request, jsonify

# --- Configuration ---
CONFIG_DIR = '/app/config'
DATA_DIR = os.path.join(CONFIG_DIR, 'data')
STATIC_DIR = os.path.join(CONFIG_DIR, 'static')
LINKS_FILE = os.path.join(DATA_DIR, 'links.json')
SETTINGS_FILE = os.path.join(DATA_DIR, 'settings.json')

# --- Default File Content ---
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
            <h1 id="page-title">My Homepage</h1>
            <div class="controls">
                <button id="settings-button">Settings</button>
                <button id="edit-button">Edit Links</button>
                <button id="save-button" class="hidden">Save Changes</button>
            </div>
        </header>
        <main id="links-container">
            <!-- Links will be dynamically loaded here -->
        </main>
    </div>

    <!-- Settings Modal -->
    <div id="settings-modal" class="modal-overlay">
        <div class="modal-content">
            <h2>Settings</h2>
            <form id="settings-form">
                <div class="form-group">
                    <label for="page-title-input">Page Title</label>
                    <input type="text" id="page-title-input" name="pageTitle">
                </div>
                <div class="form-group">
                    <label for="link-columns-input">Link Columns</label>
                    <input type="number" id="link-columns-input" name="linkColumns" min="1" max="6" value="2">
                </div>
                <div class="form-group">
                    <label>
                        <input type="checkbox" id="new-tab-checkbox" name="openLinksInNewTab">
                        Open links in a new tab
                    </label>
                </div>
                <hr>
                <div class="form-group">
                    <label>
                        <input type="checkbox" id="overwrite-static-checkbox" name="forceOverwriteStaticFiles">
                        <span class="warning-text">Force overwrite static files on next restart (for testing)</span>
                    </label>
                </div>
            </form>
            <div class="modal-actions">
                <button id="cancel-settings-button">Cancel</button>
                <button id="save-settings-button">Save Settings</button>
            </div>
        </div>
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
    transition: background-color 0.3s, color 0.3s;
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
header h1 { margin: 0; font-size: 1.8rem; }
.controls button { background-color: #007bff; color: white; border: none; padding: 0.5rem 1rem; border-radius: 5px; cursor: pointer; transition: background-color 0.2s; margin-left: 0.5rem; }
.controls button:hover { background-color: #0056b3; }
.controls button#settings-button { background-color: #6c757d; }
.controls button#settings-button:hover { background-color: #5a6268; }
.hidden { display: none; }
.section { margin-bottom: 2rem; }
.section h2 { color: #00aaff; border-bottom: 1px solid #444; padding-bottom: 0.5rem; margin-bottom: 1rem; }
.links {
    list-style: none;
    padding: 0;
    display: grid;
    /* This variable will be set by JavaScript based on settings */
    grid-template-columns: repeat(var(--link-columns, 2), 1fr);
    gap: 1rem;
}
.links a { color: #8ab4f8; text-decoration: none; font-size: 1.1em; }
.links a:hover { text-decoration: underline; }

/* Edit Mode Styles */
.edit-mode .section-header { display: flex; justify-content: space-between; align-items: center; }
.edit-mode input[type="text"] { background-color: #333; color: #eee; border: 1px solid #555; padding: 0.5rem; border-radius: 4px; margin-bottom: 0.5rem; width: calc(100% - 1.2rem); }
.edit-mode .link-item { display: flex; flex-direction: column; background-color: #2a2a2a; padding: 1rem; border-radius: 5px; }
.edit-mode .remove-btn { background-color: #dc3545; color: white; border: none; padding: 0.3rem 0.6rem; border-radius: 4px; cursor: pointer; align-self: flex-end; }
.edit-mode .add-btn { background-color: #28a745; color: white; border: none; padding: 0.5rem; border-radius: 4px; cursor: pointer; margin-top: 0.5rem; }

/* Modal Styles */
.modal-overlay { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background-color: rgba(0, 0, 0, 0.7); justify-content: center; align-items: center; z-index: 1000; display: none; }
.modal-overlay.visible { display: flex; }
.modal-content { background-color: #2c2c2c; padding: 2rem; border-radius: 8px; width: 90%; max-width: 500px; box-shadow: 0 5px 15px rgba(0,0,0,0.5); }
.modal-content h2 { margin-top: 0; color: #00aaff;}
.form-group { margin-bottom: 1rem; }
.form-group label { display: block; margin-bottom: 0.5rem; }
.form-group input[type="text"], .form-group input[type="number"] { width: calc(100% - 1rem); background-color: #333; border: 1px solid #555; color: #eee; padding: 0.5rem; border-radius: 4px;}
.form-group input[type="checkbox"] { margin-right: 0.5rem; }
.modal-actions { margin-top: 1.5rem; display: flex; justify-content: flex-end; gap: 0.5rem; }
.modal-actions button { background-color: #6c757d; color: white; border: none; padding: 0.6rem 1.2rem; border-radius: 5px; cursor: pointer; }
.modal-actions button#save-settings-button { background-color: #007bff; }
hr { border: 1px solid #444; margin: 1.5rem 0;}
.warning-text { color: #ffc107; }
"""

DEFAULT_JS = """
document.addEventListener('DOMContentLoaded', () => {
    // --- Global State ---
    let isEditMode = false;
    let currentLinks = {};
    let currentSettings = {};

    // --- DOM Elements ---
    const root = document.documentElement;
    const pageTitleElement = document.getElementById('page-title');
    const editButton = document.getElementById('edit-button');
    const saveButton = document.getElementById('save-button');
    const linksContainer = document.getElementById('links-container');
    const settingsButton = document.getElementById('settings-button');
    const settingsModal = document.getElementById('settings-modal');
    const saveSettingsButton = document.getElementById('save-settings-button');
    const cancelSettingsButton = document.getElementById('cancel-settings-button');
    const pageTitleInput = document.getElementById('page-title-input');
    const newTabCheckbox = document.getElementById('new-tab-checkbox');
    const linkColumnsInput = document.getElementById('link-columns-input');
    const overwriteStaticCheckbox = document.getElementById('overwrite-static-checkbox');
    

    // --- Data Fetching ---
    const fetchAllData = async () => {
        try {
            const [linksResponse, settingsResponse] = await Promise.all([
                fetch('/api/links'),
                fetch('/api/settings')
            ]);
            if (!linksResponse.ok || !settingsResponse.ok) throw new Error('Network response was not ok');
            currentLinks = await linksResponse.json();
            currentSettings = await settingsResponse.json();
            
            applySettings();
            renderLinks();

        } catch (error) {
            linksContainer.innerHTML = `<p style="color:red;">Error loading data: ${error.message}</p>`;
        }
    };

    // --- Rendering ---
    const applySettings = () => {
        document.title = currentSettings.pageTitle || 'Homepage';
        pageTitleElement.textContent = currentSettings.pageTitle || 'Homepage';
        root.style.setProperty('--link-columns', currentSettings.linkColumns || 2);
    };

    const renderLinks = () => {
        linksContainer.innerHTML = '';
        const linkTarget = currentSettings.openLinksInNewTab ? '_blank' : '_self';

        (currentLinks.sections || []).forEach((section, sectionIndex) => {
            const sectionDiv = document.createElement('div');
            sectionDiv.className = 'section';
            
            let sectionHeaderHTML = isEditMode
                ? `<div class="section-header"><input type="text" value="${section.title}" class="section-title-input" data-section-index="${sectionIndex}"><button class="remove-btn remove-section-btn" data-section-index="${sectionIndex}">X</button></div>`
                : `<h2>${section.title}</h2>`;
            sectionDiv.innerHTML = sectionHeaderHTML;

            const linksUl = document.createElement('ul');
            linksUl.className = 'links';

            (section.links || []).forEach((link, linkIndex) => {
                const li = document.createElement('li');
                li.className = 'link-item';
                if (isEditMode) {
                    li.innerHTML = `<input type="text" placeholder="Name" value="${link.name}" class="link-name-input" data-section-index="${sectionIndex}" data-link-index="${linkIndex}"><input type="text" placeholder="URL" value="${link.url}" class="link-url-input" data-section-index="${sectionIndex}" data-link-index="${linkIndex}"><button class="remove-btn remove-link-btn" data-section-index="${sectionIndex}" data-link-index="${linkIndex}">X</button>`;
                } else {
                    li.innerHTML = `<a href="${link.url}" target="${linkTarget}">${link.name}</a>`;
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
        
        addDynamicEventListeners();
    };
    
    // --- Edit Mode Logic ---
    const toggleEditMode = () => {
        isEditMode = !isEditMode;
        document.body.classList.toggle('edit-mode', isEditMode);
        editButton.classList.toggle('hidden', isEditMode);
        settingsButton.classList.toggle('hidden', isEditMode);
        saveButton.classList.toggle('hidden', !isEditMode);
        renderLinks();
    };

    const saveLinkChanges = async () => {
        const sections = [];
        document.querySelectorAll('.section').forEach(sectionDiv => {
            const titleInput = sectionDiv.querySelector('.section-title-input');
            if (!titleInput) return;
            
            const newSection = { title: titleInput.value, links: [] };
            sectionDiv.querySelectorAll('.link-item').forEach(linkItem => {
                const nameInput = linkItem.querySelector('.link-name-input');
                const urlInput = linkItem.querySelector('.link-url-input');
                if (nameInput && urlInput && nameInput.value && urlInput.value) {
                    newSection.links.push({ name: nameInput.value, url: urlInput.value });
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
            if (!response.ok) throw new Error('Failed to save link changes');
            currentLinks = { sections };
            toggleEditMode();
        } catch (error) {
            console.error('Error saving links:', error);
        }
    };

    // --- Settings Modal Logic ---
    const openSettingsModal = () => {
        pageTitleInput.value = currentSettings.pageTitle;
        newTabCheckbox.checked = currentSettings.openLinksInNewTab;
        linkColumnsInput.value = currentSettings.linkColumns;
        overwriteStaticCheckbox.checked = currentSettings.forceOverwriteStaticFiles;
        settingsModal.classList.add('visible');
    };

    const closeSettingsModal = () => {
        settingsModal.classList.remove('visible');
    };

    const saveSettingsChanges = async () => {
        const newSettings = {
            pageTitle: pageTitleInput.value,
            openLinksInNewTab: newTabCheckbox.checked,
            linkColumns: parseInt(linkColumnsInput.value, 10),
            forceOverwriteStaticFiles: overwriteStaticCheckbox.checked
        };
        try {
            const response = await fetch('/api/settings', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(newSettings)
            });
            if (!response.ok) throw new Error('Failed to save settings');
            currentSettings = newSettings;
            applySettings();
            renderLinks();
            closeSettingsModal();
        } catch (error) {
            console.error('Error saving settings:', error);
        }
    };

    // --- Event Listeners ---
    function addDynamicEventListeners() {
        linksContainer.addEventListener('click', (e) => {
            if (e.target.matches('.remove-link-btn')) e.target.closest('.link-item').remove();
            if (e.target.matches('.remove-section-btn')) e.target.closest('.section').remove();
            if (e.target.matches('.add-link-btn')) {
                const linksUl = e.target.previousElementSibling;
                const newLinkLi = document.createElement('li');
                newLinkLi.className = 'link-item';
                newLinkLi.innerHTML = `<input type="text" placeholder="Name" class="link-name-input"><input type="text" placeholder="URL" class="link-url-input"><button class="remove-btn remove-link-btn">X</button>`;
                linksUl.appendChild(newLinkLi);
            }
            if(e.target.matches('.add-section-btn')) {
                 const newSectionDiv = document.createElement('div');
                 newSectionDiv.className = 'section';
                 newSectionDiv.innerHTML = `<div class="section-header"><input type="text" value="New Section" class="section-title-input"><button class="remove-btn remove-section-btn">X</button></div><ul class="links"></ul><button class="add-btn add-link-btn">Add Link</button>`;
                 linksContainer.insertBefore(newSectionDiv, e.target);
            }
        });
    }
    
    editButton.addEventListener('click', toggleEditMode);
    saveButton.addEventListener('click', saveLinkChanges);
    settingsButton.addEventListener('click', openSettingsModal);
    cancelSettingsButton.addEventListener('click', closeSettingsModal);
    saveSettingsButton.addEventListener('click', saveSettingsChanges);
    settingsModal.addEventListener('click', (e) => {
        if (e.target === settingsModal) closeSettingsModal();
    });

    fetchAllData();
});
"""

DEFAULT_LINKS = {
    "sections": [
        {
            "title": "Getting Started",
            "links": [
                {"name": "Edit Links", "url": "#"},
                {"name": "Google", "url": "https://google.com"}
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

DEFAULT_SETTINGS = {
    "pageTitle": "My Homepage",
    "openLinksInNewTab": True,
    "linkColumns": 2,
    "forceOverwriteStaticFiles": False
}


def initialize_app():
    """Checks for required files and directories, creating or overwriting them based on settings."""
    print("Initializing application...")
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(STATIC_DIR, exist_ok=True)

    # --- Settings File Handling ---
    should_overwrite_static = False
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, 'r') as f:
                existing_settings = json.load(f)
            if existing_settings.get('forceOverwriteStaticFiles', False):
                should_overwrite_static = True
                print("Setting 'forceOverwriteStaticFiles' is true. Static files will be overwritten.")
        except (json.JSONDecodeError, IOError) as e:
            print(f"Warning: Could not read settings file, defaulting to not overwrite. Error: {e}")
    else:
        print(f"'{SETTINGS_FILE}' not found, creating with default content.")
        with open(SETTINGS_FILE, 'w') as f:
            json.dump(DEFAULT_SETTINGS, f, indent=4)
    
    # --- Static File Handling ---
    files_to_create = {
        os.path.join(STATIC_DIR, 'index.html'): DEFAULT_HTML,
        os.path.join(STATIC_DIR, 'style.css'): DEFAULT_CSS,
        os.path.join(STATIC_DIR, 'scripts.js'): DEFAULT_JS
    }
    
    if should_overwrite_static:
        print("Overwriting static files...")
        for fpath in files_to_create.keys():
            if os.path.exists(fpath):
                os.remove(fpath)
    
    for fpath, content in files_to_create.items():
        if not os.path.exists(fpath):
            print(f"Creating '{os.path.basename(fpath)}'.")
            with open(fpath, 'w') as f:
                f.write(content)

    # --- Links File Handling ---
    if not os.path.exists(LINKS_FILE):
        print(f"'{LINKS_FILE}' not found, creating with default content.")
        with open(LINKS_FILE, 'w') as f:
            json.dump(DEFAULT_LINKS, f, indent=4)

    print("Initialization complete.")


# --- App Initialization & Routes ---
initialize_app()
app = Flask(__name__, static_url_path='/static', static_folder=STATIC_DIR)

@app.route('/')
def index():
    return send_from_directory(STATIC_DIR, 'index.html')

@app.route('/api/links', methods=['GET'])
def get_links():
    try:
        with open(LINKS_FILE, 'r') as f:
            data = json.load(f)
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": f"Could not read links file: {e}"}), 500

@app.route('/api/links', methods=['POST'])
def save_links():
    try:
        new_data = request.get_json()
        with open(LINKS_FILE, 'w') as f:
            json.dump(new_data, f, indent=4)
        return jsonify({"message": "Links saved"}), 200
    except Exception as e:
        return jsonify({"error": f"Failed to save links: {e}"}), 500

@app.route('/api/settings', methods=['GET'])
def get_settings():
    try:
        with open(SETTINGS_FILE, 'r') as f:
            data = json.load(f)
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": f"Could not read settings file: {e}"}), 500

@app.route('/api/settings', methods=['POST'])
def save_settings():
    try:
        new_data = request.get_json()
        with open(SETTINGS_FILE, 'w') as f:
            json.dump(new_data, f, indent=4)
        return jsonify({"message": "Settings saved"}), 200
    except Exception as e:
        return jsonify({"error": f"Failed to save settings: {e}"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
