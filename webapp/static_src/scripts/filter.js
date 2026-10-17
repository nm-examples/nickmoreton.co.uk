document.querySelectorAll("[data-filter]").forEach((section) => {
  const input = section.querySelector("[data-filter-input]");
  const controls = section.querySelector("[data-filter-controls]");
  const status = section.querySelector("[data-filter-status]");
  const reset = section.querySelector("[data-filter-reset]");
  const empty = section.querySelector("[data-filter-empty]");
  const items = [...section.querySelectorAll("[data-search-item]")];
  if (!input || !controls || !status || !reset || !empty || !items.length)
    return;
  controls.hidden = false;
  const filter = () => {
    const query = input.value.trim().toLocaleLowerCase();
    let count = 0;
    items.forEach((item) => {
      const text = item.dataset.searchText || item.textContent;
      const match = text.toLocaleLowerCase().includes(query);
      item.hidden = !match;
      if (match) count++;
    });
    empty.hidden = count !== 0;
    reset.hidden = !query;
    status.textContent = query
      ? `${count} result${count === 1 ? "" : "s"} found`
      : "";
  };
  input.addEventListener("input", filter);
  reset.addEventListener("click", () => {
    input.value = "";
    filter();
    input.focus();
  });
  filter();
});
