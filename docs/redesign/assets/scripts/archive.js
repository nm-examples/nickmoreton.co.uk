const search = document.querySelector("#archive-search");
if (search)
  search.addEventListener("input", () => {
    let count = 0;
    const q = search.value.trim().toLowerCase();
    document.querySelectorAll("[data-search-item]").forEach((el) => {
      const match = el.textContent.toLowerCase().includes(q);
      el.hidden = !match;
      if (match) count++;
    });
    document.querySelector(".archive-empty").hidden = count > 0;
    document.querySelector("#archive-results").textContent = q
      ? `${count} results`
      : "";
  });
