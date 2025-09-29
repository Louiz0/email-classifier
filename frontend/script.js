/*
Script que faz a comunuicação com o backend através de requisições HTTP
Funções principais:
  sendButton = async function
  fileInput = async function
*/

// Definição das váriaveis dos inputs, dados extraidos do HTML
const sendButton = document.querySelector(".send-icon");
const textarea = document.getElementById("email-fieldtext");
const fileInput = document.getElementById("input-file");

// Botão de enviar, envia a requisição classify-text
sendButton.addEventListener("click", async () => {
  const text = textarea.value.trim();
  if (!text) return alert("Cole um texto para classificar!");

  const formData = new FormData();
  formData.append("text", text);
  // Requisição HTTP ao backend
  const response = await fetch("http://127.0.0.1:8000/classify-text", {
    method: "POST",
    body: formData,
  });

  const result = await response.json();
  alert(`Categoria: ${result.classification}\nConfiança: ${(result.confidence * 100).toFixed(2)}%\nResposta: ${result.response}`);
});

// Botão de upload de um e-mail (.pdf ou .txt), envia a requisição classify-file
fileInput.addEventListener("change", async (e) => {
  const file = e.target.files[0];
  if (!file) return;

  const formData = new FormData();
  formData.append("file", file);
  // Requisição HTTP ao backend
  const response = await fetch("http://127.0.0.1:8000/classify-file", {
    method: "POST",
    body: formData,
  });

  const result = await response.json();
  alert(`Categoria: ${result.classification}\nConfiança: ${(result.confidence * 100).toFixed(2)}%\nResposta: ${result.response}`);
});