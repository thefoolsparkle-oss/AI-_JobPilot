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

function showSection(sectionId) {
  document.querySelectorAll(".section").forEach(s => s.style.display = "none");
  document.getElementById(sectionId).style.display = "block";
}

async function getPageInfo() {
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  const results = await chrome.scripting.executeScript({
    target: { tabId: tab.id },
    func: () => {
      const url = location.href;
      const title = document.title;
      let pageType = "unknown";

      // Detect page type
      const formSelectors = ['input[type="text"]', 'input[type="email"]', 'textarea', 'select', 'input[name*="name"]', 'input[name*="email"]', 'input[name*="phone"]'];
      const formFields = [];
      formSelectors.forEach(sel => {
        document.querySelectorAll(sel).forEach(el => {
          const label = el.closest("label")?.textContent || el.getAttribute("placeholder") || el.getAttribute("name") || "";
          const tag = el.tagName.toLowerCase();
          const type = el.type || tag;
          const id = el.id || el.name || "";
          if (label || id) {
            formFields.push({ tag, type, label: label.trim(), id, value: el.value || "" });
          }
        });
      });

      if (formFields.length > 3) {
        pageType = "form";
      } else if (url.includes("job") || url.includes("career") || url.includes("position") || url.includes("jd")) {
        pageType = "jd";
      } else if (url.includes("apply") || url.includes("submit")) {
        pageType = "form";
      }

      // For JD pages, extract content
      let jdContent = "";
      if (pageType === "jd") {
        const jdSelectors = ["article", "main", ".job-detail", ".jd-content", ".job-description", ".post-content", "#job-detail"];
        for (const sel of jdSelectors) {
          const el = document.querySelector(sel);
          if (el && el.textContent.trim().length > 200) {
            jdContent = el.textContent.trim();
            break;
          }
        }
        if (!jdContent) {
          jdContent = document.body.textContent.trim().slice(0, 3000);
        }
      }

      return { url, title, pageType, formFields, jdContent };
    },
  });
  return results[0].result;
}

let pageInfo = null;

(async function init() {
  try {
    pageInfo = await getPageInfo();
    document.getElementById("pageType").textContent = pageInfo.pageType === "form" ? "表单页面" : pageInfo.pageType === "jd" ? "招聘页面" : "其他页面";

    if (pageInfo.pageType === "jd") {
      showSection("section-jd");
      document.getElementById("jd-title").textContent = pageInfo.title;
      if (pageInfo.jdContent) {
        showPreview(pageInfo.jdContent);
        setStatus("info", "已检测到招聘页面，可提取 JD");
      }
    } else if (pageInfo.pageType === "form") {
      showSection("section-form");
      const fieldsDiv = document.getElementById("form-fields");
      fieldsDiv.innerHTML = pageInfo.formFields.map((f, i) =>
        `<div class="field-row">
          <span class="field-label">${f.label || f.id || f.type}</span>
          <span class="field-tag">${f.type}</span>
          ${f.value ? `<span class="field-value">${f.value.slice(0, 30)}</span>` : ''}
        </div>`
      ).join("") || "未检测到表单字段";
      setStatus("info", "已检测到 " + pageInfo.formFields.length + " 个表单字段");
    } else {
      showSection("section-jd");
      setStatus("info", "未能识别页面类型，可尝试提取内容");
    }
  } catch (e) {
    setStatus("err", "初始化失败: " + e.message);
  }
})();

// JD mode: extract and send
document.getElementById("extractBtn").addEventListener("click", async () => {
  const btn = document.getElementById("extractBtn");
  btn.disabled = true;
  btn.textContent = "处理中...";
  try {
    if (!pageInfo.jdContent || pageInfo.jdContent.length < 100) {
      setStatus("err", "未提取到足够内容");
      btn.disabled = false;
      btn.textContent = "提取 JD 并发送";
      return;
    }
    const res = await fetch(`${BACKEND}/jobs/parse`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ jd_text: pageInfo.jdContent, url: pageInfo.url, source: "extension" }),
    });
    if (!res.ok) throw new Error(await res.text());
    const result = await res.json();
    setStatus("ok", "已解析: " + (result.parsed_jd?.title || "成功"));
    setTimeout(() => window.open("http://127.0.0.1:8001/jobs/match/", "_blank"), 500);
  } catch (e) {
    setStatus("err", "失败: " + e.message);
  } finally {
    btn.disabled = false;
    btn.textContent = "提取 JD 并发送";
  }
});

// Form mode: suggest answers
document.getElementById("assistBtn").addEventListener("click", async () => {
  const btn = document.getElementById("assistBtn");
  btn.disabled = true;
  btn.textContent = "分析中...";
  try {
    const fieldDescs = pageInfo.formFields.map(f => `[${f.type}] ${f.label || f.id}`).join("\n");
    const res = await fetch(`${BACKEND}/assistant/form`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ form_text: "请为以下表单字段生成填写建议:\n" + fieldDescs }),
    });
    if (!res.ok) throw new Error(await res.text());
    const data = await res.json();
    document.getElementById("form-suggestions").textContent = data.suggestion || data.natural_answer || "暂无建议";
    showSection("section-form-result");
    setStatus("ok", "填写建议已生成");
  } catch (e) {
    setStatus("err", "失败: " + e.message);
  } finally {
    btn.disabled = false;
    btn.textContent = "获取填写建议";
  }
});

document.getElementById("backBtn").addEventListener("click", () => showSection("section-form"));

document.getElementById("openBtn").addEventListener("click", () => {
  window.open("http://127.0.0.1:8001", "_blank");
});
