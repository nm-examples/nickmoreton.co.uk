document.querySelectorAll(".code-copy").forEach((b) =>
  b.addEventListener("click", async () => {
    try {
      await navigator.clipboard.writeText(
        b.closest(".code-block").querySelector("code").textContent,
      );
      b.textContent = "Copied ✓";
    } catch {
      b.textContent = "Select code to copy";
    }
    setTimeout(() => (b.textContent = "Copy code"), 2000);
  }),
);
