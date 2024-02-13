document.addEventListener("DOMContentLoaded", () => {
  const uploadForm = document.getElementById("uploadForm");
  const textContainer = document.getElementById("textContainer");
  const questionInput = document.getElementById("questionInput");
  const askButton = document.getElementById("askButton");
  const answerContainer = document.getElementById("answerContainer");

  uploadForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const formData = new FormData();
    formData.append("pdf_file", uploadForm.elements.pdfFile.files[0]);
    const response = await fetch("/api/pdf/upload/", {
      method: "POST",
      body: formData,
    });
    const data = await response.json();
    textContainer.textContent = data.pdf_text;
  });

  askButton.addEventListener("click", async () => {
    const question = questionInput.value.trim();
    if (question) {
      const response = await fetch("/api/qa/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ question }),
      });
      const data = await response.json();
      answerContainer.textContent = `Answer: ${data.answer}`;
    }
  });
});
