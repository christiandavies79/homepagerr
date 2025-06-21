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
# Using the original, simpler JS without the timeout/retry logic.
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
    
    addDynamicEventListeners();

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
    # Note: We need to define default HTML and CSS here, or import them, for this to be self-contained.
    # For this example, I'm assuming the DEFAULT_JS, etc., variables are defined above in this file.
    files_to_create = {
        os.path.join(STATIC_DIR, 'index.html'): "<!-- Populated by script -->", # This will be created from a string
        os.path.join(STATIC_DIR, 'style.css'): "/* Populated by script */",
        os.path.join(STATIC_DIR, 'scripts.js'): DEFAULT_JS
    }
    
    if should_overwrite_static:
        print("Overwriting static files...")
        for fpath in files_to_create.keys():
            if os.path.exists(fpath):
                # We can just overwrite, no need to remove first
                pass
    
    # Create files if they don't exist OR if overwrite is true
    # This logic is simplified
    for fpath, content in files_to_create.items():
        # A simple check: if the file doesn't exist, create it. If we must overwrite, we'll write it anyway.
        if not os.path.exists(fpath) or should_overwrite_static:
            print(f"Creating or overwriting '{os.path.basename(fpath)}'.")
            # For simplicity, using dummy content for HTML/CSS, as JS is the focus
            if 'index.html' in fpath:
                # You would have your full DEFAULT_HTML here
                final_content = "<!-- Your full default HTML here -->"
            elif 'style.css' in fpath:
                 # You would have your full DEFAULT_CSS here
                final_content = "/* Your full default CSS here */"
            else:
                final_content = content
            with open(fpath, 'w') as f:
                f.write(final_content)


    # --- Links File Handling ---
    if not os.path.exists(LINKS_FILE):
        print(f"'{LINKS_FILE}' not found, creating with default content.")
        with open(LINKS_FILE, 'w') as f:
            json.dump(DEFAULT_LINKS, f, indent=4)

    print("Initialization complete.")


# --- App Definition ---
# The app is defined here, but not run. Gunicorn will find this 'app' object.
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

# This main entry point is for the startup script to call.
# It can also be used for local testing (e.g., python main.py).
def main():
    initialize_app()

if __name__ == '__main__':
    main()
    # For local development, you might want to run the Flask dev server
    # Note: This part is not used by Gunicorn or the startup script.
    app.run(host='0.0.0.0', port=8000, debug=True)

