const sendButton = document.querySelector(".send-icon");
const textarea = document.getElementById("email-fieldtext");
const fileInput = document.getElementById("input-file");

sendButton.addEventListener("click", async () => {
  const text = textarea.value.trim();
  if (!text) return alert("Cole um texto para classificar!");

  const formData = new FormData();
  formData.append("text", text);

  const response = await fetch("/classify-text", {
    method: "POST",
    body: formData,
  });

  const result = await response.json();
  alert(`Categoria: ${result.classification}\nConfiança: ${(result.confidence*100).toFixed(2)}%\nResposta: ${result.response}`);
});

fileInput.addEventListener("change", async (e) => {
  const file = e.target.files[0];
  if (!file) return;

  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch("/classify-file", {
    method: "POST",
    body: formData,
  });

  const result = await response.json();
  alert(`Categoria: ${result.classification}\nConfiança: ${(result.confidence*100).toFixed(2)}%\nResposta: ${result.response}`);
});
