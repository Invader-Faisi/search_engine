const input = document.querySelector("#search_input");
const backdrop = document.querySelector("#highlighted_text");

const menu = document.createElement("div");
menu.className = "spellcheck-menu";
document.body.appendChild(menu);

// Custom dictionary management
let customWords = [];

async function loadCustomWords() {
    try {
        const response = await fetch("/spellcheck/custom-words", {
            method: "GET",
            headers: { "Content-Type": "application/json" }
        });
        const data = await response.json();
        customWords = data.words || [];
    } catch (err) {
        console.error("Error loading custom words:", err);
    }
}

async function addToCustomDictionary(word) {
    try {
        const response = await fetch("/spellcheck/custom-words", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ words: [word] })
        });
        const data = await response.json();
        customWords = data.words || [];
        return true;
    } catch (err) {
        console.error("Error adding to custom dictionary:", err);
        return false;
    }
}

function clearSearch() {
    input.value = '';
    backdrop.innerHTML = '';
}

async function updateHighlights() {
    const text = input.value;
    if (!text) {
        backdrop.innerHTML = "";
        return;
    }

    try {
        const response = await fetch("/spellcheck", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ text })
        });
        const data = await response.json();

        backdrop.innerHTML = "";
        const words = text.split(/(\s+)/);

        words.forEach((word) => {
            const span = document.createElement("span");
            span.textContent = word;
            const cleanWord = word.trim().replace(/[.,/#!$%^&*;:{}=\-_`~()]/g,"").toLowerCase();

            if (data[cleanWord]) {
                span.className = "misspelled";
                span.onmouseenter = (e) => showMenu(e, cleanWord, data[cleanWord]);
                span.oncontextmenu = (e) => {
                    e.preventDefault();
                    showContextMenu(e, cleanWord, data[cleanWord]);
                };
            }
            backdrop.appendChild(span);
        });
    } catch (err) {
        console.error("Spellcheck error:", err);
    }
}

function showMenu(event, originalWord, suggestions) {
    menu.innerHTML = "";
    const header = document.createElement("div");
    header.textContent = "Spelling suggestions";
    header.style.cssText = "font-size: 11px; color: #70757a; padding: 5px 16px; border-bottom: 1px solid #eee;";
    menu.appendChild(header);

    suggestions.forEach(s => {
        const item = document.createElement("div");
        item.className = "suggestion-item";
        item.textContent = s;
        item.onclick = (e) => {
            const regex = new RegExp(`\\b${originalWord}\\b`, 'gi');
            input.value = input.value.replace(regex, s);
            menu.style.display = "none";
            updateHighlights();
            input.focus();
        };
        menu.appendChild(item);
    });

    // Add "Add to dictionary" option
    const addToDictItem = document.createElement("div");
    addToDictItem.className = "suggestion-item";
    addToDictItem.innerHTML = '<span style="color: #1a73e8">✓ Add "' + originalWord + '" to dictionary</span>';
    addToDictItem.onclick = async (e) => {
        const success = await addToCustomDictionary(originalWord);
        if (success) {
            menu.style.display = "none";
            updateHighlights();
            showToast(`"${originalWord}" added to custom dictionary`);
        }
    };
    menu.appendChild(addToDictItem);

    const rect = event.target.getBoundingClientRect();
    menu.style.display = "block";
    menu.style.left = `${rect.left + window.scrollX}px`;
    menu.style.top = `${rect.bottom + window.scrollY + 5}px`;
}

function showContextMenu(event, originalWord, suggestions) {
    menu.innerHTML = "";
    
    const header = document.createElement("div");
    header.textContent = "Spelling options";
    header.style.cssText = "font-size: 11px; color: #70757a; padding: 5px 16px; border-bottom: 1px solid #eee;";
    menu.appendChild(header);

    // Add suggestion items
    if (suggestions && suggestions.length > 0) {
        suggestions.forEach(s => {
            const item = document.createElement("div");
            item.className = "suggestion-item";
            item.textContent = s;
            item.onclick = (e) => {
                const regex = new RegExp(`\\b${originalWord}\\b`, 'gi');
                input.value = input.value.replace(regex, s);
                menu.style.display = "none";
                updateHighlights();
                input.focus();
            };
            menu.appendChild(item);
        });
        
        const divider = document.createElement("div");
        divider.style.cssText = "border-top: 1px solid #eee; margin: 5px 0;";
        menu.appendChild(divider);
    }

    // Add to dictionary option
    const addToDictItem = document.createElement("div");
    addToDictItem.className = "suggestion-item";
    addToDictItem.innerHTML = '<span style="color: #1a73e8">✓ Add "' + originalWord + '" to custom dictionary</span>';
    addToDictItem.onclick = async (e) => {
        const success = await addToCustomDictionary(originalWord);
        if (success) {
            menu.style.display = "none";
            updateHighlights();
            showToast(`"${originalWord}" added to custom dictionary`);
        }
    };
    menu.appendChild(addToDictItem);

    const rect = event.target.getBoundingClientRect();
    menu.style.display = "block";
    menu.style.left = `${rect.left + window.scrollX}px`;
    menu.style.top = `${rect.bottom + window.scrollY + 5}px`;
}

function showToast(message) {
    // Use Toastr if available, otherwise alert
    if (typeof toastr !== 'undefined') {
        toastr.success(message);
    } else {
        alert(message);
    }
}

let debounceTimer;
input.addEventListener("input", () => {
    backdrop.innerText = input.value;
    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(updateHighlights, 400);
});

input.addEventListener("scroll", () => {
    backdrop.scrollLeft = input.scrollLeft;
});

document.addEventListener("mousedown", (e) => {
    if (!menu.contains(e.target)) menu.style.display = "none";
});

// Load custom words on page load
document.addEventListener("DOMContentLoaded", () => {
    loadCustomWords();
});