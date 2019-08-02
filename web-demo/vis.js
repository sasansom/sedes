const ALL_STYLES = [
  "shade-text",
  "shade-bubbles",
  "size-bubbles",
  "shade-background",
];

const BOOL_GRID = document.getElementById("bool-grid");
const GROUP_STYLE = document.getElementById("group-style");
const GRID_MARKERS = document.getElementById("gridmarkers");
const TEXT = document.getElementById("text");

function setClass(elem, className, cond) {
  if (cond) {
    elem.classList.add(className);
  } else {
    elem.classList.remove(className);
  }
}

BOOL_GRID.addEventListener("change", event => {
  setClass(TEXT, "grid", event.target.checked);
  setClass(GRID_MARKERS, "visible", event.target.checked);
});
setClass(TEXT, "grid", BOOL_GRID.checked);
setClass(GRID_MARKERS, "visible", BOOL_GRID.checked);

GROUP_STYLE.addEventListener("change", event => {
  TEXT.classList.remove(...ALL_STYLES);
  TEXT.classList.add(event.target.value);
});
TEXT.classList.add(GROUP_STYLE.value);
