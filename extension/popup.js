const BACKEND = "http://127.0.0.1:8001/api";

function setStatus(type, msg) {
  const el = document.getElementById("status");
  el.className = "status " + type;
  el.textContent = msg;
}

function showPreview(text) {
  const el = document.getElementById("preview");
  el.style.display = "block";
  el.textContent = text.slice(0, 500);
}

async function extractContent() {
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  const results = await chrome.scripting.executeScript({
    target: { tabId: tab.id },
    func: () => {
      const selectors = [
        "article", "main", ".job-detail", ".jd-content",
        ".job-description", ".post-content", "#job-detail",
        ".detail-content", ".job-desc",
      ];
      for (const sel of selectors) {
        const el = document.querySelector(sel);
        if (el && el.textContent.trim().length > 200) {
          return { title: document.title, content: el.textContent.trim(), url: location.href };
        }
      }
      const body = document.body.cloneNode(true);
      const exclude = body.querySelectorAll("nav, header, footer, script, style, .nav, .header, .footer, .sidebar, .comment");
      exclude.forEach((e) => e.remove());
      const text = body.textContent.trim();
      return { title: document.title, content: text, url: location.href };
    },
  });
  return results[0].result;
}

document.getElementById("extractBtn").addEventListener("click", async () => {
  const btn = document.getElementById("extractBtn");
  btn.disabled = true;
  btn.textContent = "提取中...";

  try {
    const data = await extractContent();
    if (!data.content || data.content.length < 100) {
      setStatus("err", "未能提取到足够内容，请确保在招聘详情页打开");
      btn.disabled = false;
      btn.textContent = "提取 JD 并发送到 JobPilot";
      return;
    }

    showPreview(data.content);
    setStatus("info", "已提取 " + data.content.length + " 字符，正在发送...");

    const res = await fetch(`${BACKEND}/jobs/parse`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ jd_text: data.content, url: data.url, source: "extension" }),
    });

    if (!res.ok) throw new Error(await res.text());

    const result = await res.json();
    setStatus("ok", "已解析: " + (result.parsed_jd?.title || result.title || "成功"));

    setTimeout(() => {
      window.open("http://127.0.0.1:8001/jobs/match/", "_blank");
    }, 500);
  } catch (e) {
    setStatus("err", "失败: " + (e.message || "请确保 JobPilot 已启动"));
  } finally {
    btn.disabled = false;
    btn.textContent = "提取 JD 并发送到 JobPilot";
  }
});

document.getElementById("openBtn").addEventListener("click", () => {
  window.open("http://127.0.0.1:8001", "_blank");
});
