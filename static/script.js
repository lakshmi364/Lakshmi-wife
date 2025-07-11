async function getStrategy() {
  const res = await fetch('/strategy');
  const data = await res.json();
  document.getElementById('strategy').innerText = data.strategy || "No strategy today.";
}

async function getIndicator() {
  const res = await fetch('/indicator');
  const data = await res.json();
  document.getElementById('indicator').innerText = data.indicator || "No indicator today.";
}

document.getElementById("chat-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const input = document.getElementById("message");
  const msg = input.value.trim();
  if (!msg) return;

  const chatBox = document.getElementById("chat-box");
  chatBox.innerHTML += `<div><strong>You:</strong> ${msg}</div>`;

  const res = await fetch("/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message: msg })
  });
  const data = await res.json();
  chatBox.innerHTML += `<div><strong>Lakshmi:</strong> ${data.response}</div>`;
  chatBox.scrollTop = chatBox.scrollHeight;
  input.value = "";
});
