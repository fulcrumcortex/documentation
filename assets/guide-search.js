"use strict";
const filter = document.getElementById("guide-filter");
const guideNav = document.getElementById("docs-nav");
if (filter && guideNav) filter.addEventListener("input", () => {
  const query = filter.value.trim().toLocaleLowerCase();
  let found = 0;
  for (const list of guideNav.querySelectorAll(":scope > ul")) {
    let sectionMatches = 0;
    for (const row of list.children) {
      const matches = !query || row.textContent.toLocaleLowerCase().includes(query);
      row.hidden = !matches;
      if (matches) sectionMatches++;
    }
    const heading = list.previousElementSibling;
    if (heading?.classList.contains("nav-section")) heading.hidden = sectionMatches === 0;
    list.hidden = sectionMatches === 0;
    found += sectionMatches;
  }
  document.getElementById("guide-filter-status").textContent = query ? `${found} matching guides` : "";
});
