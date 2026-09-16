async function refreshStats() {
  try {
    const res = await fetch("/api/status");
    const data = await res.json();
    document.getElementById("fps").textContent = data.fps?.toFixed?.(1) ?? "—";
    document.getElementById("people").textContent = data.person_count ?? "—";
    document.getElementById("face").textContent = data.face_recognition ? "On" : "Off";
  } catch (_) {
    /* stream may restart */
  }
}

document.getElementById("source-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const message = document.getElementById("message");
  const source = document.getElementById("source").value.trim();
  message.hidden = false;
  message.className = "message";

  try {
    const res = await fetch("/api/source", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ source }),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Failed to update source");
    message.textContent = `Source updated to ${data.source}. Reloading stream...`;
    message.classList.add("ok");
    const img = document.getElementById("stream");
    img.src = `/video?ts=${Date.now()}`;
  } catch (error) {
    message.textContent = error.message;
    message.classList.add("error");
  }
});

setInterval(refreshStats, 1500);
refreshStats();
