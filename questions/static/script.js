document.addEventListener("DOMContentLoaded", () => {
  const uploadForm = document.getElementById("uploadForm");
  const textContainer = document.getElementById("textContainer");
  const questionInput = document.getElementById("questionInput");
  const askButton = document.getElementById("askButton");
  const answerContainer = document.getElementById("answerContainer");
  const summarizeButton = document.getElementById("summarizeButton");

  uploadForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const formData = new FormData();
    formData.append("pdf_file", uploadForm.elements.pdfFile.files[0]);
    const response = await fetch("/api/pdf/", {
      method: "POST",
      body: formData,
    });
    const data = await response.json();
    textContainer.textContent = data.pdf_text;
  });

  summarizeButton.addEventListener("click", async () => {
    console.log("Summarize button clicked"); // Log button click for debugging
    const text = textContainer.value.trim(); // Use value property for textarea

    if (text) {
      const response = await fetch("/api/summarize/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ input_text: text }), // Send text for summarization
      });
      const data = await response.json();
      answerContainer.textContent = `Summarized Text: ${data.summarized_text}`; // Display summarized text
    } else {
      answerContainer.textContent = "No text to summarize"; // Inform user if no text is available
    }
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
