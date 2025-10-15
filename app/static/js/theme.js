document.addEventListener("DOMContentLoaded", () => {
  const body = document.getElementById("main-body");
  const switchEl = document.getElementById("darkModeSwitch");

  function applyTheme(dark) {
    body.setAttribute("data-bs-theme", dark ? "dark" : "light");
    localStorage.setItem("theme", dark ? "dark" : "light");
  }

  const savedTheme = localStorage.getItem("theme");
  if (savedTheme) {
    applyTheme(savedTheme === "dark");
    if (switchEl) switchEl.checked = savedTheme === "dark";
  } else {
    applyTheme(false);
  }

  if (switchEl) {
    switchEl.addEventListener("change", (e) =>
      applyTheme(e.target.checked)
    );
  }
});
