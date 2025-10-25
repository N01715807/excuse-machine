// ==== 配置区域 ====
const API_BASE = "http://localhost:3000";  // 你的 FastAPI 后端地址
const ENDPOINT = `${API_BASE}/excuse`;     // 对应 app.py 里的 /excuse

// ==== DOM 元素 ====
const form = document.querySelector("form");
const userInput = document.getElementById("userInput");
const styleSelect = document.getElementById("styleSelect");
const outputBox = document.getElementById("outputBox");
const copyBtn = document.querySelector('button[type="button"]');

// ==== 表单提交逻辑 ====
form.addEventListener("submit", async (event) => {
  event.preventDefault();  // 阻止默认刷新页面

  const text = userInput.value.trim();
  const style = styleSelect.value;

  if (!text) {
    outputBox.value = "⚠️ 请输入你的情况再生成。";
    return;
  }

  outputBox.value = "⏳ 正在生成中，请稍候...";

  try {
    const response = await fetch(ENDPOINT, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text, style }),
    });

    if (!response.ok) {
      throw new Error(`Server error: ${response.status}`);
    }

    const data = await response.json();

    if (data.error) {
      outputBox.value = `❌ 出错：${data.error}`;
    } else {
      outputBox.value = data.excuse || data.output || "（无返回内容）";
    }
  } catch (err) {
    console.error(err);
    outputBox.value = "🚨 网络或服务器错误，请稍后再试。";
  }
});

// ==== 复制按钮逻辑 ====
copyBtn.addEventListener("click", async () => {
  const text = outputBox.value.trim();
  if (!text) return;

  try {
    await navigator.clipboard.writeText(text);
    copyBtn.textContent = "✅ 已复制";
    setTimeout(() => (copyBtn.textContent = "Copy Output"), 1500);
  } catch (err) {
    console.error(err);
    copyBtn.textContent = "❌ 复制失败";
  }
});
