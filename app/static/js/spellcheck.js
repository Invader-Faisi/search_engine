const input = document.querySelector("#search_input");
const backdrop = document.querySelector("#highlighted_text");

const menu = document.createElement("div");
menu.className = "spellcheck-menu";
document.body.appendChild(menu);

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

    const rect = event.target.getBoundingClientRect();
    menu.style.display = "block";
    menu.style.left = `${rect.left + window.scrollX}px`;
    menu.style.top = `${rect.bottom + window.scrollY + 5}px`;
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