function searchFunction() {
    const input = document.getElementById('searchBar');
    const filter = input.value.toUpperCase();
    const ul = document.getElementById('itemsList');
    const li = ul.getElementsByTagName('li');

    // Show all items if the search bar is empty
    if (filter === "") {
        for (let i = 0; i < li.length; i++) {
            li[i].style.display = "";
        }
        return; // Exit if there's no search term
    }

    // Filter the list based on the search term
    for (let i = 0; i < li.length; i++) {
        const item = li[i];
        const text = item.textContent || item.innerText;

        if (text.toUpperCase().indexOf(filter) > -1) {
            item.style.display = "";
        } else {
            item.style.display = "none";
        }
    }
}

// Show the list when the search bar is focused
function showList() {
    const ul = document.getElementById('itemsList');
    ul.style.display = "block"; // Show the list
}

// Hide the list when the search bar loses focus (if nothing is typed)
function hideList() {
    const input = document.getElementById('searchBar');
    const ul = document.getElementById('itemsList');

    // Only hide the list if the input is empty
    if (input.value === "") {
        ul.style.display = "none";
    }
}
