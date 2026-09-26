document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll(".flash-close").forEach((button) => {
    button.addEventListener("click", () => button.parentElement.remove());
  });

  const fileInput = document.querySelector("#image");
  const fileName = document.querySelector("#file-name");
  if (fileInput && fileName) {
    fileInput.addEventListener("change", () => {
      fileName.textContent = fileInput.files.length ? fileInput.files[0].name : "Choose file";
    });
  }

  document.querySelectorAll("[data-confirm-update]").forEach((form) => {
    form.addEventListener("submit", (event) => {
      if (!window.confirm("Update this complaint for the citizen?")) event.preventDefault();
    });
  });

  const menuToggle = document.querySelector(".menu-toggle");
  const navLinks = document.querySelector(".nav-links");
  if (menuToggle && navLinks) {
    menuToggle.addEventListener("click", () => navLinks.classList.toggle("is-open"));
  }
});