import os
import json
import shutil
import requests
import sys
from flask import Flask, send_from_directory, request, jsonify

# --- Configuration ---
CONFIG_DIR = '/app/config'
DATA_DIR = os.path.join(CONFIG_DIR, 'data')
STATIC_DIR = os.path.join(CONFIG_DIR, 'static')
LINKS_FILE = os.path.join(DATA_DIR, 'links.json')
SETTINGS_FILE = os.path.join(DATA_DIR, 'settings.json')
NOTES_FILE = os.path.join(DATA_DIR, 'notes.json')

# --- Default File Content ---
DEFAULT_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Homepage</title>
    <link rel="stylesheet" href="/static/style.css">
    <script src="https://cdn.jsdelivr.net/npm/sortablejs@latest/Sortable.min.js"></script>
</head>
<body>
    <div class="container">
        <header>
            <h1 id="page-title">My Homepage</h1>
            <div id="status-indicator-container"></div>
            <div class="search-wrapper">
                <input type="search" id="search-input" placeholder="Search links...">
            </div>
            <div class="controls">
                <button id="notepad-button" title="Scratchpad">
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
                        <path d="M8 1.5A1.5 1.5 0 0 1 9.5 0H11a.5.5 0 0 1 .5.5v2A1.5 1.5 0 0 1 10 4H4a2 2 0 0 0-2 2v8a2 2 0 0 0 2 2h8a2 2 0 0 0 2-2V9.5a1.5 1.5 0 0 1 3 0V14a3 3 0 0 1-3 3H4a3 3 0 0 1-3-3V6a3 3 0 0 1 3-3h1.5a2.5 2.5 0 0 1 2.5 2.5V6h1.5A1.5 1.5 0 0 1 10 4.5z"/>
                        <path d="M12.5 0a.5.5 0 0 1 .5.5v2a.5.5 0 0 1-.5-.5h-2a.5.5 0 0 1-.5-.5v-2a.5.5 0 0 1 .5-.5zM12 3.5a.5.5 0 0 1 .5-.5h2a.5.5 0 0 1 0 1h-2a.5.5 0 0 1-.5-.5"/>
                    </svg>
                </button>
                <button id="settings-button" title="Settings">
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
                      <path d="M9.405 1.05c-.413-1.4-2.397-1.4-2.81 0l-.1.34a1.464 1.464 0 0 1-2.105.872l-.31-.17c-1.283-.698-2.686.705-1.987 1.987l.169.311a1.464 1.464 0 0 1-.872 2.105l-.34.1c-1.4.413-1.4 2.397 0 2.81l.34.1a1.464 1.464 0 0 1 .872 2.105l-.17.31c-.698 1.283.705 2.686 1.987 1.987l.311-.169a1.464 1.464 0 0 1 2.105.872l.1.34c.413 1.4 2.397 1.4 2.81 0l.1-.34a1.464 1.464 0 0 1 2.105-.872l.31.17c1.283.698 2.686-.705 1.987-1.987l-.169-.311a1.464 1.464 0 0 1 .872-2.105l.34-.1c-1.4-.413-1.4-2.397 0-2.81l.34-.1a1.464 1.464 0 0 1 .872-2.105l.17-.31c.698-1.283-.705-2.686-1.987-1.987l-.311.169a1.464 1.464 0 0 1-2.105-.872l-.1-.34zM8 10.93a2.929 2.929 0 1 1 0-5.858 2.929 2.929 0 0 1 0 5.858z"/>
                    </svg>
                </button>
                <button id="edit-button" title="Edit Links">
                     <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
                        <path d="M12.854.146a.5.5 0 0 0-.707 0L10.5 1.793 14.207 5.5l1.647-1.646a.5.5 0 0 0 0-.708l-3-3zm.646 6.061L9.793 2.5 3.293 9H3.5a.5.5 0 0 1 .5.5v.5h.5a.5.5 0 0 1 .5.5v.5h.5a.5.5 0 0 1 .5.5v.5h.5a.5.5 0 0 1 .5.5v.207l6.5-6.5zm-7.468 7.468A.5.5 0 0 1 6 13.5V13h-.5a.5.5 0 0 1-.5-.5V12h-.5a.5.5 0 0 1-.5-.5V11h-.5a.5.5 0 0 1-.5-.5V10h-.5a.499.499 0 0 1-.175-.032l-.179.178a.5.5 0 0 0-.11.168l-2 5a.5.5 0 0 0 .65.65l5-2a.5.5 0 0 0 .168-.11l.178-.178z"/>
                    </svg>
                </button>
                <button id="discard-button" class="hidden">Discard</button>
                <button id="save-button" class="hidden">Save Changes</button>
            </div>
        </header>
        <main id="links-container">
            <!-- Links will be dynamically loaded here -->
        </main>
    </div>

    <!-- Scratchpad Modal -->
    <div id="notepad-modal" class="modal-overlay">
        <div class="modal-content">
            <h2>Scratchpad</h2>
            <textarea id="notepad-textarea" placeholder="Type your notes here..."></textarea>
            <div class="modal-actions">
                <button id="delete-all-notes-button" class="button-danger">Delete All</button>
                <div style="flex-grow: 1;"></div> <!-- Spacer -->
                <button id="discard-notepad-button">Discard Changes</button>
                <button id="save-notepad-button">Save</button>
            </div>
        </div>
    </div>

    <!-- Delete Confirmation Modal -->
    <div id="delete-confirm-modal" class="modal-overlay">
        <div class="modal-content">
            <h2>Delete All Notes?</h2>
            <p>This action cannot be undone.</p>
            <div class="modal-actions">
                <button id="confirm-delete-cancel">Cancel</button>
                <button id="confirm-delete-all" class="button-danger">Delete All</button>
                <button id="confirm-delete-all-close" class="button-danger">Delete All & Close</button>
            </div>
        </div>
    </div>


    <!-- Drag Overlay -->
    <div id="drag-overlay" class="hidden">
        <div class="drag-overlay-content">
            <h2>Drop Link Here</h2>
        </div>
    </div>

    <!-- Add Link Modal (for drag & drop) -->
    <div id="add-link-modal" class="modal-overlay">
        <div class="modal-content">
            <h2>Add New Link</h2>
            <form id="add-link-form">
                <div class="form-group">
                    <label for="link-name-input">Link Name</label>
                    <input type="text" id="link-name-input" required>
                </div>
                <div class="form-group">
                    <label for="link-url-input">Link URL</label>
                    <input type="text" id="link-url-input" required readonly>
                </div>
                <div class="form-group">
                    <label for="link-section-select">Section</label>
                    <select id="link-section-select">
                        <!-- Options will be populated by JS -->
                    </select>
                </div>
                <div class="form-group hidden" id="new-section-group">
                    <label for="new-section-title-input">New Section Title</label>
                    <input type="text" id="new-section-title-input">
                </div>
            </form>
            <div class="modal-actions">
                <button id="cancel-add-link-button">Cancel</button>
                <button id="save-add-link-button">Save Link</button>
            </div>
        </div>
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
    flex-wrap: nowrap;
    gap: 1rem;
}
header h1 { margin: 0; font-size: 1.8rem; flex-shrink: 0; white-space: nowrap; }
.search-wrapper { flex-grow: 1; max-width: 250px; min-width: 150px; }
#search-input {
    width: 100%;
    background-color: #333;
    color: #eee;
    border: 1px solid #555;
    padding: 0.5rem;
    border-radius: 4px;
    font-size: 1rem;
}
.controls { display: flex; flex-shrink: 0; }
.controls button {
    background-color: #007bff;
    color: white;
    border: none;
    padding: 0.5rem 1rem;
    border-radius: 5px;
    cursor: pointer;
    transition: background-color 0.2s;
    margin-left: 0.5rem;
    display: flex;
    align-items: center;
    justify-content: center;
}
.controls button:hover { background-color: #0056b3; }
.controls button#settings-button, .controls button#discard-button, .controls button#notepad-button { background-color: #6c757d; }
.controls button#settings-button:hover, .controls button#discard-button:hover, .controls button#notepad-button:hover { background-color: #5a6268; }
.controls button#edit-button { background-color: #007bff; }
.controls button#edit-button:hover { background-color: #0056b3; }
.controls button#notepad-button, .controls button#settings-button, .controls button#edit-button {
    width: 40px;
    height: 36px;
    padding: 0;
}
.hidden { display: none !important; }
.search-hidden { display: none !important; }

.section {
    margin-bottom: 2rem;
    background-color: #1c1c1c;
    padding: 1rem;
    border-radius: 8px;
    border: 1px solid transparent;
}
.section h2 { color: #00aaff; border-bottom: 1px solid #444; padding-bottom: 0.5rem; margin-bottom: 1rem; }
.links {
    list-style: none;
    padding: 0;
    display: grid;
    grid-template-columns: repeat(var(--link-columns, 2), 1fr);
    gap: 1rem;
    min-height: 50px;
}
.links a { color: #8ab4f8; text-decoration: none; font-size: 1.1em; }
.links a:hover { text-decoration: underline; }

/* Edit Mode Styles */
.edit-mode .section { border: 1px dashed #555; }
.edit-mode .section-header { display: flex; justify-content: space-between; align-items: center; }
.edit-mode .section-header-title { display: flex; align-items: center; flex-grow: 1; }
.edit-mode input[type="text"] { background-color: #333; color: #eee; border: 1px solid #555; padding: 0.5rem; border-radius: 4px; margin-bottom: 0.5rem; width: 100%; }
.edit-mode .link-item { display: flex; align-items: center; background-color: #2a2a2a; padding: 0.5rem 1rem; border-radius: 5px; }
.edit-mode .link-item-content { flex-grow: 1; }
.edit-mode .remove-btn { background-color: #dc3545; color: white; border: none; padding: 0.3rem 0.6rem; border-radius: 4px; cursor: pointer; align-self: center; margin-left: 0.5rem; flex-shrink: 0; }
.edit-mode .add-btn { background-color: #28a745; color: white; border: none; padding: 0.5rem; border-radius: 4px; cursor: pointer; margin-top: 0.5rem; }
.drag-handle { cursor: grab; color: #888; margin-right: 10px; font-size: 1.2rem; line-height: 1; }
.drag-handle:active { cursor: grabbing; }
.sortable-ghost { background-color: #007bff; opacity: 0.4; }
.sortable-chosen { background-color: #2a2a2a; }
.section.sortable-ghost { background-color: #00aaff; }

/* Modal Styles */
.modal-overlay { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background-color: rgba(0, 0, 0, 0.7); justify-content: center; align-items: center; z-index: 1000; display: none; }
.modal-overlay.visible { display: flex; }
.modal-content { background-color: #2c2c2c; padding: 2rem; border-radius: 8px; width: 90%; max-width: 500px; box-shadow: 0 5px 15px rgba(0,0,0,0.5); }
#notepad-modal .modal-content { max-width: 800px; }
.modal-content h2 { margin-top: 0; color: #00aaff;}
.form-group { margin-bottom: 1rem; }
.form-group label { display: block; margin-bottom: 0.5rem; }
.form-group input[type="text"], .form-group input[type="number"], .form-group select { width: 100%; box-sizing: border-box; background-color: #333; border: 1px solid #555; color: #eee; padding: 0.5rem; border-radius: 4px;}
.form-group input[type="checkbox"] { margin-right: 0.5rem; width: auto; }
.modal-actions { margin-top: 1.5rem; display: flex; justify-content: flex-end; gap: 0.5rem; align-items: center; }
.modal-actions button { background-color: #6c757d; color: white; border: none; padding: 0.6rem 1.2rem; border-radius: 5px; cursor: pointer; }
.modal-actions button.button-danger { background-color: #dc3545; }
.modal-actions button.button-danger:hover { background-color: #c82333; }
.modal-actions button#save-settings-button, .modal-actions button#save-add-link-button, .modal-actions button#save-notepad-button { background-color: #007bff; }
hr { border: 1px solid #444; margin: 1.5rem 0;}
.warning-text { color: #ffc107; }

/* Scratchpad Styles */
#notepad-textarea {
    width: 100%;
    height: 60vh;
    background-color: #333;
    border: 1px solid #555;
    color: #eee;
    padding: 0.5rem;
    border-radius: 4px;
    resize: vertical;
    box-sizing: border-box;
}

/* Drag Overlay Styles */
#drag-overlay {
    position: fixed; top: 0; left: 0; width: 100%; height: 100%;
    background-color: rgba(0, 170, 255, 0.2);
    border: 3px dashed #00aaff;
    box-sizing: border-box;
    z-index: 2000;
}
#drag-overlay .drag-overlay-content {
    display: flex; justify-content: center; align-items: center;
    width: 100%; height: 100%; font-size: 2rem; color: #e0e0e0;
    text-shadow: 0 0 10px #121212;
}

/* Status Indicator Styles */
#status-indicator-container {
    flex-grow: 1;
    display: flex;
    justify-content: center;
    min-width: 150px;
}
#status-indicator {
    display: block;
    padding: 0.5rem 1rem;
    border-radius: 5px;
    font-size: 0.9rem;
    font-weight: bold;
    color: white;
    text-align: center;
    transition: background-color 0.3s;
    white-space: nowrap;
    text-decoration: none;
}
#status-indicator:hover {
    color: white; /* Maintain text color on hover */
    filter: brightness(110%);
}
#status-indicator.ok { background-color: #28a745; }
#status-indicator.investigate { background-color: #ff9800; }
#status-indicator.error { background-color: #dc3545; }
"""

DEFAULT_JS = """
document.addEventListener('DOMContentLoaded', () => {
    // --- Global State ---
    let isEditMode = false;
    let currentLinks = {};
    let currentSettings = {};
    let sortableInstances = [];
    let currentNotepadContent = '';

    // --- DOM Elements ---
    const root = document.documentElement;
    const pageTitleElement = document.getElementById('page-title');
    const searchInput = document.getElementById('search-input');
    const searchWrapper = document.querySelector('.search-wrapper');
    const editButton = document.getElementById('edit-button');
    const saveButton = document.getElementById('save-button');
    const discardButton = document.getElementById('discard-button');
    const linksContainer = document.getElementById('links-container');
    const settingsButton = document.getElementById('settings-button');
    const statusIndicatorContainer = document.getElementById('status-indicator-container');

    // Notepad Modal
    const notepadButton = document.getElementById('notepad-button');
    const notepadModal = document.getElementById('notepad-modal');
    const notepadTextarea = document.getElementById('notepad-textarea');
    const saveNotepadButton = document.getElementById('save-notepad-button');
    const discardNotepadButton = document.getElementById('discard-notepad-button');
    const deleteAllNotesButton = document.getElementById('delete-all-notes-button');

    // Delete Confirm Modal
    const deleteConfirmModal = document.getElementById('delete-confirm-modal');
    const confirmDeleteCancelButton = document.getElementById('confirm-delete-cancel');
    const confirmDeleteAllButton = document.getElementById('confirm-delete-all');
    const confirmDeleteAllCloseButton = document.getElementById('confirm-delete-all-close');


    // Settings Modal
    const settingsModal = document.getElementById('settings-modal');
    const saveSettingsButton = document.getElementById('save-settings-button');
    const cancelSettingsButton = document.getElementById('cancel-settings-button');
    const pageTitleInput = document.getElementById('page-title-input');
    const newTabCheckbox = document.getElementById('new-tab-checkbox');
    const linkColumnsInput = document.getElementById('link-columns-input');
    const overwriteStaticCheckbox = document.getElementById('overwrite-static-checkbox');

    // Add Link Modal
    const addLinkModal = document.getElementById('add-link-modal');
    const dragOverlay = document.getElementById('drag-overlay');
    const addLinkForm = document.getElementById('add-link-form');
    const linkNameInput = document.getElementById('link-name-input');
    const linkUrlInput = document.getElementById('link-url-input');
    const linkSectionSelect = document.getElementById('link-section-select');
    const newSectionGroup = document.getElementById('new-section-group');
    const newSectionTitleInput = document.getElementById('new-section-title-input');
    const saveAddLinkButton = document.getElementById('save-add-link-button');
    const cancelAddLinkButton = document.getElementById('cancel-add-link-button');

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

    const fetchUptimeKumaStatus = async () => {
        try {
            const response = await fetch('/api/uptime-kuma-status');
            const data = await response.json();

            if (!data.enabled) {
                statusIndicatorContainer.innerHTML = '';
                return;
            }

            let indicator;
            if (data.url) {
                indicator = document.createElement('a');
                indicator.href = data.url;
                indicator.target = '_blank';
                indicator.rel = 'noopener noreferrer';
            } else {
                indicator = document.createElement('div');
            }

            indicator.id = 'status-indicator';
            
            if (data.status === 'ok') {
                indicator.className = 'ok';
                indicator.title = 'All services are online.';
                indicator.textContent = 'All Systems Online';
            } else if (data.status === 'investigate') {
                indicator.className = 'investigate';
                indicator.title = 'One or more services requires attention.';
                indicator.textContent = 'Investigate Services';
            } else { // Handles 'error' state
                indicator.className = 'error';
                const errorMessage = data.message || 'Could not retrieve status.';
                indicator.title = errorMessage;
                indicator.textContent = 'Status Unavailable';
            }
            
            statusIndicatorContainer.innerHTML = ''; // Clear previous indicator
            statusIndicatorContainer.appendChild(indicator);

        } catch (error) {
            console.error('Error fetching Uptime Kuma status:', error);
            statusIndicatorContainer.innerHTML = `<div id="status-indicator" class="error" title="Client-side error fetching status.">Status Unavailable</div>`;
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

        (currentLinks.sections || []).forEach((section) => {
            const sectionDiv = document.createElement('div');
            sectionDiv.className = 'section';

            let sectionHeader;
            if (isEditMode) {
                sectionHeader = `
                    <div class="section-header">
                        <div class="section-header-title">
                           <span class="drag-handle section-drag-handle">☰</span>
                           <input type="text" value="${section.title}" class="section-title-input">
                        </div>
                        <button class="remove-btn remove-section-btn">X</button>
                    </div>`;
            } else {
                sectionHeader = `<h2>${section.title}</h2>`;
            }
            sectionDiv.innerHTML = sectionHeader;


            const linksUl = document.createElement('ul');
            linksUl.className = 'links';
            sectionDiv.appendChild(linksUl);

            (section.links || []).forEach((link) => {
                const li = document.createElement('li');
                li.className = 'link-item';
                if (isEditMode) {
                    li.innerHTML = `
                        <span class="drag-handle link-drag-handle">☰</span>
                        <div class="link-item-content">
                            <input type="text" placeholder="Name" value="${link.name}" class="link-name-input">
                            <input type="text" placeholder="URL" value="${link.url}" class="link-url-input">
                        </div>
                        <button class="remove-btn remove-link-btn">X</button>
                    `;
                } else {
                    const linkAnchor = document.createElement('a');
                    linkAnchor.href = link.url;
                    linkAnchor.target = linkTarget;
                    linkAnchor.textContent = link.name;
                    linkAnchor.setAttribute('data-name', link.name.toLowerCase());
                    linkAnchor.setAttribute('data-url', link.url.toLowerCase());
                    li.appendChild(linkAnchor);
                }
                linksUl.appendChild(li);
            });

            if(isEditMode) {
                const addLinkBtn = document.createElement('button');
                addLinkBtn.textContent = 'Add Link';
                addLinkBtn.className = 'add-btn add-link-btn';
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

    // --- Search Logic ---
    const handleSearch = () => {
        const searchTerm = searchInput.value.toLowerCase();

        document.querySelectorAll('.section').forEach(section => {
            let sectionHasVisibleLink = false;
            section.querySelectorAll('.link-item').forEach(item => {
                const link = item.querySelector('a');
                if (link) {
                    const name = link.getAttribute('data-name');
                    const url = link.getAttribute('data-url');
                    const isVisible = name.includes(searchTerm) || url.includes(searchTerm);
                    item.classList.toggle('search-hidden', !isVisible);
                    if (isVisible) sectionHasVisibleLink = true;
                }
            });
            section.classList.toggle('search-hidden', !sectionHasVisibleLink);
        });
    };

    // --- Drag and Drop Sorting Logic ---
    const initializeSortable = () => {
        const sectionsContainer = document.getElementById('links-container');
        sortableInstances.push(new Sortable(sectionsContainer, {
            group: 'sections', animation: 150, handle: '.section-drag-handle', ghostClass: 'sortable-ghost',
        }));
        document.querySelectorAll('.links').forEach(list => {
            sortableInstances.push(new Sortable(list, {
                group: 'links', animation: 150, handle: '.link-drag-handle', ghostClass: 'sortable-ghost',
            }));
        });
    };

    const destroySortable = () => {
        sortableInstances.forEach(instance => instance.destroy());
        sortableInstances = [];
    };

    // --- Edit Mode Logic ---
    const toggleEditMode = () => {
        isEditMode = !isEditMode;
        document.body.classList.toggle('edit-mode', isEditMode);

        // Hide/show main controls when entering/exiting edit mode
        searchWrapper.classList.toggle('hidden', isEditMode);
        settingsButton.classList.toggle('hidden', isEditMode);
        notepadButton.classList.toggle('hidden', isEditMode);
        editButton.classList.toggle('hidden', isEditMode);

        // Hide/show edit-specific controls
        saveButton.classList.toggle('hidden', !isEditMode);
        discardButton.classList.toggle('hidden', !isEditMode);
        
        destroySortable();
        renderLinks(); // Re-render the links to apply/remove edit controls
        
        if (isEditMode) {
            initializeSortable();
        } else {
            // Clear search when exiting edit mode
            searchInput.value = '';
            handleSearch();
        }
    };

    const saveAllLinkChanges = async (newLinkData) => {
        try {
            const response = await fetch('/api/links', {
                method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(newLinkData)
            });
            if (!response.ok) throw new Error('Failed to save link changes');
            currentLinks = newLinkData;
            toggleEditMode(); // Exit edit mode and re-render
        } catch (error) {
            console.error('Error saving links:', error);
        }
    };

    const saveLinkChangesFromEditMode = () => {
        const newSections = [];
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
            newSections.push(newSection);
        });
        saveAllLinkChanges({ sections: newSections });
    };

    // --- Settings Modal Logic ---
    const openSettingsModal = () => {
        pageTitleInput.value = currentSettings.pageTitle || 'My Homepage';
        newTabCheckbox.checked = currentSettings.openLinksInNewTab;
        linkColumnsInput.value = currentSettings.linkColumns || 2;
        overwriteStaticCheckbox.checked = currentSettings.forceOverwriteStaticFiles || false;
        settingsModal.classList.add('visible');
    };

    const closeSettingsModal = () => settingsModal.classList.remove('visible');

    const saveSettingsChanges = async () => {
        const newSettings = {
            pageTitle: pageTitleInput.value,
            openLinksInNewTab: newTabCheckbox.checked,
            linkColumns: parseInt(linkColumnsInput.value, 10),
            forceOverwriteStaticFiles: overwriteStaticCheckbox.checked
        };
        try {
            const response = await fetch('/api/settings', {
                method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(newSettings)
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

    // --- Scratchpad Modal Logic ---
    const openNotepadModal = async () => {
        try {
            const response = await fetch('/api/notes');
            if (!response.ok) throw new Error('Failed to fetch notes');
            const data = await response.json();
            currentNotepadContent = data.content;
            notepadTextarea.value = currentNotepadContent;
            notepadModal.classList.add('visible');
        } catch (error) {
            console.error('Error opening notepad:', error);
        }
    };

    const closeNotepadModal = () => notepadModal.classList.remove('visible');

    const saveNotepadChanges = async (content = null, andClose = false) => {
        const newContent = content !== null ? content : notepadTextarea.value;
        try {
            const response = await fetch('/api/notes', {
                method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ content: newContent })
            });
            if (!response.ok) throw new Error('Failed to save notes');
            currentNotepadContent = newContent;
            notepadTextarea.value = newContent;
            if (andClose) {
                closeNotepadModal();
            }
        } catch (error) {
            console.error('Error saving notepad:', error);
        }
    };

    // --- Add Link Modal Logic ---
    const openAddLinkModal = (url) => {
        addLinkForm.reset();
        newSectionGroup.classList.add('hidden');
        linkUrlInput.value = url;
        let urlForParsing = url;
        if (!urlForParsing.startsWith('http')) urlForParsing = 'http://' + urlForParsing;
        try {
            linkNameInput.value = new URL(urlForParsing).hostname.replace(/^www./, '');
        } catch (e) {
            linkNameInput.value = url;
        }
        linkSectionSelect.innerHTML = '';
        currentLinks.sections.forEach((section, index) => {
            const option = document.createElement('option');
            option.value = index;
            option.textContent = section.title;
            linkSectionSelect.appendChild(option);
        });
        const newSectionOption = document.createElement('option');
        newSectionOption.value = '--new-section--';
        newSectionOption.textContent = 'Create a new section...';
        linkSectionSelect.appendChild(newSectionOption);
        addLinkModal.classList.add('visible');
    };

    const closeAddLinkModal = () => addLinkModal.classList.remove('visible');

    const saveLinkFromModal = () => {
        const name = linkNameInput.value.trim();
        const url = linkUrlInput.value.trim();
        const sectionChoice = linkSectionSelect.value;
        const newSectionTitle = newSectionTitleInput.value.trim();
        if (!name || !url) return;
        const newLink = { name, url };
        let updatedLinks = JSON.parse(JSON.stringify(currentLinks));
        if (sectionChoice === '--new-section--') {
            if (!newSectionTitle) return;
            updatedLinks.sections.push({ title: newSectionTitle, links: [newLink] });
        } else {
            updatedLinks.sections[parseInt(sectionChoice, 10)].links.push(newLink);
        }
        // This is a bit abrupt. Instead of calling the full save, let's just update the local data
        // and re-render. This is better UX for drag-drop.
        currentLinks = updatedLinks;
        renderLinks();
        // Now save in the background
        fetch('/api/links', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(currentLinks)
        }).catch(err => console.error("Failed to save new link in background:", err));

        closeAddLinkModal();
    };

    // --- Event Listener Setup ---
    function addDynamicEventListeners() {
        linksContainer.addEventListener('click', (e) => {
            if (e.target.matches('.remove-btn')) {
                if (e.target.matches('.remove-link-btn')) e.target.closest('.link-item').remove();
                if (e.target.matches('.remove-section-btn')) e.target.closest('.section').remove();
            }
            if (e.target.matches('.add-link-btn')) {
                const linksUl = e.target.parentElement.querySelector('.links');
                
                // Create elements programmatically to ensure properties are set correctly
                const newLinkLi = document.createElement('li');
                newLinkLi.className = 'link-item';

                const dragHandle = document.createElement('span');
                dragHandle.className = 'drag-handle link-drag-handle';
                dragHandle.textContent = '☰';
                
                const contentDiv = document.createElement('div');
                contentDiv.className = 'link-item-content';

                const nameInput = document.createElement('input');
                nameInput.type = 'text';
                nameInput.placeholder = 'Name';
                nameInput.className = 'link-name-input'; // Crucial for saving
                
                const urlInput = document.createElement('input');
                urlInput.type = 'text';
                urlInput.placeholder = 'URL';
                urlInput.className = 'link-url-input'; // Crucial for saving

                const removeBtn = document.createElement('button');
                removeBtn.className = 'remove-btn remove-link-btn';
                removeBtn.textContent = 'X';

                contentDiv.appendChild(nameInput);
                contentDiv.appendChild(urlInput);
                newLinkLi.appendChild(dragHandle);
                newLinkLi.appendChild(contentDiv);
                newLinkLi.appendChild(removeBtn);
                
                linksUl.appendChild(newLinkLi);
            }
            if(e.target.matches('.add-section-btn')) {
                 const newSectionDiv = document.createElement('div');
                 newSectionDiv.className = 'section';
                 
                 const newLinksUl = document.createElement('ul');
                 newLinksUl.className = 'links';

                 const addLinkBtn = document.createElement('button');
                 addLinkBtn.textContent = 'Add Link';
                 addLinkBtn.className = 'add-btn add-link-btn';

                 newSectionDiv.innerHTML = `
                    <div class="section-header">
                        <div class="section-header-title">
                           <span class="drag-handle section-drag-handle">☰</span>
                           <input type="text" value="New Section" class="section-title-input">
                        </div>
                        <button class="remove-btn remove-section-btn">X</button>
                    </div>`;
                 
                 newSectionDiv.appendChild(newLinksUl);
                 newSectionDiv.appendChild(addLinkBtn);

                 linksContainer.insertBefore(newSectionDiv, e.target);
                 destroySortable();
                 initializeSortable();
            }
        });
    }

    addDynamicEventListeners();
    searchInput.addEventListener('input', handleSearch);
    editButton.addEventListener('click', toggleEditMode);
    saveButton.addEventListener('click', saveLinkChangesFromEditMode);
    discardButton.addEventListener('click', () => {
        toggleEditMode(); // Simply exit edit mode without saving
    });
    settingsButton.addEventListener('click', openSettingsModal);
    cancelSettingsButton.addEventListener('click', closeSettingsModal);
    saveSettingsButton.addEventListener('click', saveSettingsChanges);

    // Notepad Listeners
    notepadButton.addEventListener('click', openNotepadModal);
    saveNotepadButton.addEventListener('click', () => saveNotepadChanges(null, true));
    discardNotepadButton.addEventListener('click', () => {
        notepadTextarea.value = currentNotepadContent;
        closeNotepadModal();
    });
    deleteAllNotesButton.addEventListener('click', () => deleteConfirmModal.classList.add('visible'));

    // Delete Confirmation Listeners
    confirmDeleteCancelButton.addEventListener('click', () => deleteConfirmModal.classList.remove('visible'));
    confirmDeleteAllButton.addEventListener('click', () => {
        saveNotepadChanges('', false);
        deleteConfirmModal.classList.remove('visible');
    });
    confirmDeleteAllCloseButton.addEventListener('click', () => {
        saveNotepadChanges('', true);
        deleteConfirmModal.classList.remove('visible');
    });

    // Drag and Drop Listeners
    let dragCounter = 0;
    window.addEventListener('dragenter', (e) => {
        e.preventDefault();
        if (!isEditMode && (e.dataTransfer.types.includes('text/uri-list') || e.dataTransfer.types.includes('text/plain'))) {
            dragCounter++;
            dragOverlay.classList.remove('hidden');
        }
    });
    window.addEventListener('dragleave', (e) => {
        e.preventDefault();
        dragCounter--;
        if (dragCounter === 0) dragOverlay.classList.add('hidden');
    });
    window.addEventListener('dragover', (e) => e.preventDefault());
    window.addEventListener('drop', (e) => {
        e.preventDefault();
        if (isEditMode) return;
        dragCounter = 0;
        dragOverlay.classList.add('hidden');
        const droppedText = e.dataTransfer.getData('text/uri-list') || e.dataTransfer.getData('text/plain');
        if (!droppedText) return;
        let urlToTest = droppedText.trim();
        if (!urlToTest.startsWith('http')) urlToTest = 'http://' + urlToTest;
        try {
            new URL(urlToTest);
            openAddLinkModal(droppedText.trim());
        } catch (err) {
            console.warn('Dropped item is not a valid URL:', droppedText);
        }
    });

    // Add Link Modal Listeners
    linkSectionSelect.addEventListener('change', () => {
        newSectionGroup.classList.toggle('hidden', linkSectionSelect.value !== '--new-section--');
    });
    cancelAddLinkButton.addEventListener('click', closeAddLinkModal);
    saveAddLinkButton.addEventListener('click', saveLinkFromModal);

    // --- Initial Load ---
    fetchAllData();
    fetchUptimeKumaStatus();

    // --- Set up refresh interval ---
    setInterval(fetchUptimeKumaStatus, 60000); // 60000ms = 1 minute
});
"""

DEFAULT_NOTES = {"content": ""}

DEFAULT_LINKS = {
    "sections": [
        { "title": "Getting Started", "links": [ {"name": "Edit Links", "url": "#"}, {"name": "Google", "url": "https://google.com"} ] },
        { "title": "News", "links": [ {"name": "Hacker News", "url": "https://news.ycombinator.com"}, {"name": "Reddit", "url": "https://reddit.com"} ] }
    ]
}

DEFAULT_SETTINGS = {
    "pageTitle": "My Homepage", "openLinksInNewTab": True, "linkColumns": 2, "forceOverwriteStaticFiles": False
}


def initialize_app():
    """Ensures that all necessary directories and default configuration files are created."""
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(STATIC_DIR, exist_ok=True)

    should_overwrite_static = False
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, 'r') as f:
                settings = json.load(f)
                if settings.get('forceOverwriteStaticFiles', False):
                    should_overwrite_static = True
                    log_message("Setting 'forceOverwriteStaticFiles' is true. Static files will be overwritten.")
        except (json.JSONDecodeError, IOError) as e:
            log_message(f"Warning: Could not read settings file during init: {e}")
    else:
        with open(SETTINGS_FILE, 'w') as f: json.dump(DEFAULT_SETTINGS, f, indent=4)

    files_to_create = {
        os.path.join(STATIC_DIR, 'index.html'): DEFAULT_HTML,
        os.path.join(STATIC_DIR, 'style.css'): DEFAULT_CSS,
        os.path.join(STATIC_DIR, 'scripts.js'): DEFAULT_JS
    }

    for fpath, content in files_to_create.items():
        if not os.path.exists(fpath) or should_overwrite_static:
            log_message(f"Creating or overwriting '{os.path.basename(fpath)}'.")
            with open(fpath, 'w', encoding='utf-8') as f: f.write(content)

    if not os.path.exists(LINKS_FILE):
        with open(LINKS_FILE, 'w') as f: json.dump(DEFAULT_LINKS, f, indent=4)

    if not os.path.exists(NOTES_FILE):
        with open(NOTES_FILE, 'w') as f: json.dump(DEFAULT_NOTES, f, indent=4)


# --- App Definition ---
app = Flask(__name__, static_url_path='/static', static_folder=STATIC_DIR)

# Helper function to print to stderr for Docker logs
def log_message(message):
    print(message, file=sys.stderr, flush=True)

@app.route('/')
def index():
    """Serves the main index.html file."""
    return send_from_directory(STATIC_DIR, 'index.html')

@app.route('/health')
def health_check():
    """Provides a simple health check endpoint."""
    return jsonify({"status": "ok"}), 200

def get_json_file(file_path):
    """Helper function to read and serve a JSON file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return jsonify(json.load(f))
    except Exception as e:
        return jsonify({"error": f"Could not read file: {e}"}), 500

def save_json_file(file_path):
    """Helper function to save JSON data from a request to a file."""
    try:
        data = request.get_json()
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)
        return jsonify({"message": "Saved"}), 200
    except Exception as e:
        return jsonify({"error": f"Failed to save file: {e}"}), 500

# --- API Routes ---
@app.route('/api/links', methods=['GET', 'POST'])
def handle_links():
    if request.method == 'POST':
        return save_json_file(LINKS_FILE)
    return get_json_file(LINKS_FILE)

@app.route('/api/settings', methods=['GET', 'POST'])
def handle_settings():
    if request.method == 'POST':
        return save_json_file(SETTINGS_FILE)
    return get_json_file(SETTINGS_FILE)

@app.route('/api/notes', methods=['GET', 'POST'])
def handle_notes():
    if request.method == 'POST':
        return save_json_file(NOTES_FILE)
    return get_json_file(NOTES_FILE)

@app.route('/api/uptime-kuma-status')
def get_uptime_kuma_status():
    """
    Fetches and processes the status from an Uptime Kuma instance.
    Includes detailed logging for debugging purposes.
    """
    uk_url = os.environ.get('UK_URL')
    if not uk_url:
        return jsonify({"enabled": False})

    clean_uk_url = uk_url.rstrip('/')
    heartbeat_api_url = f"{clean_uk_url}/api/status-page/heartbeat/all-checks"

    log_message("\n--- [Uptime Kuma] Starting status fetch ---")
    log_message(f"[Uptime Kuma] Requesting URL: {heartbeat_api_url}")

    try:
        response = requests.get(heartbeat_api_url, timeout=10)
        log_message(f"[Uptime Kuma] Received HTTP status code: {response.status_code}")
        response.raise_for_status()
        data = response.json()

        overall_status = "ok"
        heartbeat_list = data.get("heartbeatList", {})

        if not heartbeat_list:
            log_message("[Uptime Kuma] Warning: heartbeatList is empty or missing in the response.")
        
        for monitor_id, heartbeats in heartbeat_list.items():
            if heartbeats:
                heartbeats.sort(key=lambda x: x.get('time', ''), reverse=True)
                
                latest_heartbeat = heartbeats[0]
                latest_status = latest_heartbeat.get("status")
                
                if latest_status != 1:
                    overall_status = "investigate"
                    log_message(f"[Uptime Kuma] !! Monitor '{monitor_id}' triggered 'investigate' state with status '{latest_status}'. Halting checks.")
                    log_message(f"[Uptime Kuma] !! Failing heartbeat data: {latest_heartbeat}")
                    break 
                else:
                    log_message(f"[Uptime Kuma] Monitor '{monitor_id}' latest status is OK (1)")
            else:
                log_message(f"[Uptime Kuma] Warning: Monitor '{monitor_id}' has an empty heartbeat list.")

        log_message(f"[Uptime Kuma] Final determined overall_status: '{overall_status}'")
        log_message("--- [Uptime Kuma] Finished status fetch ---\n")
        
        return jsonify({
            "enabled": True,
            "status": overall_status,
            "url": clean_uk_url
        })

    except requests.exceptions.RequestException as e:
        log_message(f"[Uptime Kuma] ERROR: Could not connect to Uptime Kuma. Details: {e}")
        return jsonify({"enabled": True, "status": "error", "message": f"Could not connect to Uptime Kuma: {e}", "url": clean_uk_url}), 500
    except Exception as e:
        log_message(f"[Uptime Kuma] ERROR: An unexpected error occurred. Details: {e}")
        return jsonify({"enabled": True, "status": "error", "message": f"An unexpected error occurred: {e}", "url": clean_uk_url}), 500

def main():
    """Main function to run initialization."""
    log_message("--- Running initialization ---")
    initialize_app()
    log_message("--- Initialization complete ---")

if __name__ == '__main__':
    main()
    log_message("--- Starting Flask development server ---")
    app.run(host='0.0.0.0', port=8000, debug=True)
