// script.js

async function getStrategy() {
  const res = await fetch('/strategy');
  const data = await res.json();
  document.getElementById('strategy').innerText = JSON.stringify(data, null, 2);
}

async function getIndicator() {
  const res = await fetch('/indicators');
  const data = await res.json();
  document.getElementById('indicator').innerText = JSON.stringify(data, null, 2);
}

async function sendMsg() {
  const msg = document.getElementById("msgInput").value.trim();
  if (!msg) return;
  const messages = document.getElementById("messages");

  const userMsg = document.createElement("div");
  userMsg.innerHTML = `<strong>You:</strong> ${msg}`;
  messages.appendChild(userMsg);

  const res = await fetch("/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message: msg, username: "user" })
  });
  const data = await res.json();

  const botMsg = document.createElement("div");
  botMsg.innerHTML = `<strong>Lakshmi:</strong> ${data.reply}`;
  messages.appendChild(botMsg);

  messages.scrollTop = messages.scrollHeight;
  document.getElementById("msgInput").value = "";
}
