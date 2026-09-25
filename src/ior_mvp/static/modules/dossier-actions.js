export function printDossier() {
  window.print();
}

const printButton = document.querySelector("[data-dossier-print]");
if (printButton) printButton.addEventListener("click", printDossier);
