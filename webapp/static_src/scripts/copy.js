document.querySelectorAll("[data-copy]").forEach((button) => {
  const container = button.closest("[data-copy-container]");
  const source = container?.querySelector("[data-code-source]");
  if (!source) return;
  button.hidden = false;
  const label = button.textContent;
  let resetTimer;
  const status = document.createElement("span");
  status.className = "visually-hidden";
  status.setAttribute("role", "status");
  container.append(status);
  button.addEventListener("click", async () => {
    clearTimeout(resetTimer);
    try {
      await navigator.clipboard.writeText(source.value);
      button.textContent = "Copied ✓";
      status.textContent = "Copied to clipboard";
    } catch {
      button.textContent = "Select code to copy";
      status.textContent =
        "Copy failed. Select the displayed code to copy it manually.";
    }
    resetTimer = setTimeout(() => {
      button.textContent = label;
      status.textContent = "";
    }, 2200);
  });
});
