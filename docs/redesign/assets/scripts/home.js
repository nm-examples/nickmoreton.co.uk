const items = [...document.querySelectorAll(".article-item")],
  search = document.querySelector("#search");
search.addEventListener("input", () => {
  const q = search.value.trim().toLowerCase();
  let count = 0;
  items.forEach((item) => {
    const match = item.textContent.toLowerCase().includes(q);
    item.hidden = !match;
    if (match) count++;
  });
  document.querySelector(".empty").hidden = count !== 0;
  document.querySelector("#results").textContent = q
    ? `${count} article${count === 1 ? "" : "s"} found`
    : "";
});
const copy = document.querySelector(".copy");
copy.addEventListener("click", async () => {
  const yaml =
    'who_am_i:\n  name: "Nick Moreton"\n  works_at: https://torchbox.com\n  preferred_cms: https://wagtail.org';
  try {
    await navigator.clipboard.writeText(yaml);
    copy.textContent = "Copied ✓";
  } catch {
    copy.textContent = "Select code to copy";
  }
  setTimeout(() => {
    copy.textContent = "Copy ⧉";
  }, 2200);
});
