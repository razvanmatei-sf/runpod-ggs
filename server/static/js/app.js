// ABOUTME: Main JavaScript for SF AI Workbench
// ABOUTME: Handles modals, navigation, and common interactions

document.addEventListener("DOMContentLoaded", function () {
  // Modal handling
  const helpBtn = document.getElementById("help-btn");
  const helpModal = document.getElementById("help-modal");

  // Open Help modal
  if (helpBtn && helpModal) {
    helpBtn.addEventListener("click", function () {
      helpModal.classList.add("active");
    });
  }

  // Close modals when clicking overlay
  document.querySelectorAll(".modal-overlay").forEach(function (overlay) {
    overlay.addEventListener("click", function (e) {
      if (e.target === overlay) {
        overlay.classList.remove("active");
      }
    });
  });

  // Close modals with Escape key
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape") {
      document
        .querySelectorAll(".modal-overlay.active")
        .forEach(function (modal) {
          modal.classList.remove("active");
        });
    }
  });

  // Collapsible sidebar sections
  document.querySelectorAll(".nav-section-header").forEach(function (header) {
    header.addEventListener("click", function () {
      const sectionName = this.dataset.section;
      const content = document.querySelector(
        '.nav-section-content[data-section="' + sectionName + '"]',
      );
      const isExpanded = this.getAttribute("aria-expanded") === "true";

      // Toggle expanded state
      this.setAttribute("aria-expanded", !isExpanded);

      // Toggle content visibility
      if (content) {
        if (isExpanded) {
          content.classList.add("collapsed");
        } else {
          content.classList.remove("collapsed");
        }
      }
    });
  });

  // Save section states to localStorage
  function saveSectionStates() {
    const states = {};
    document.querySelectorAll(".nav-section-header").forEach(function (header) {
      const sectionName = header.dataset.section;
      states[sectionName] = header.getAttribute("aria-expanded") === "true";
    });
    localStorage.setItem("sidebarSections", JSON.stringify(states));
  }

  // Restore section states from localStorage
  function restoreSectionStates() {
    const saved = localStorage.getItem("sidebarSections");
    if (saved) {
      try {
        const states = JSON.parse(saved);
        Object.keys(states).forEach(function (sectionName) {
          const header = document.querySelector(
            '.nav-section-header[data-section="' + sectionName + '"]',
          );
          const content = document.querySelector(
            '.nav-section-content[data-section="' + sectionName + '"]',
          );
          if (header && content) {
            header.setAttribute("aria-expanded", states[sectionName]);
            if (!states[sectionName]) {
              content.classList.add("collapsed");
            }
          }
        });
      } catch (e) {
        // Ignore parse errors
      }
    }
  }

  // Restore states on load
  restoreSectionStates();

  // Save states when sections are toggled
  document.querySelectorAll(".nav-section-header").forEach(function (header) {
    header.addEventListener("click", function () {
      // Small delay to ensure state is updated
      setTimeout(saveSectionStates, 10);
    });
  });
});
