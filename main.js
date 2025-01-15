// CSSの内容を取得する関数
const fetchCSSContent = async (url) => {
  try {
    const response = await fetch(url);
    if (!response.ok)
      throw new Error(`Failed to fetch CSS: ${response.statusText}`);
    return await response.text();
  } catch (error) {
    console.error(`Error fetching CSS from ${url}:`, error);
    return "";
  }
};

// すべてのCSSコンテンツを収集する関数
const getAllCSSContent = async () => {
  let stylesContent = "";

  // インラインスタイルの取得
  const styleTags = document.querySelectorAll("style");
  styleTags.forEach((style) => {
    stylesContent += `/* Inline Style */\n${style.innerHTML}\n`;
  });

  // 外部スタイルシートの取得
  const linkTags = document.querySelectorAll("link[rel='stylesheet']");
  const cssPromises = Array.from(linkTags).map(async (link) => {
    const href = link.href;
    if (href) {
      try {
        // Same-Origin Policyに違反しないURLのみ処理
        const url = new URL(href);
        if (url.origin === window.location.origin) {
          const cssContent = await fetchCSSContent(href);
          return `/* External Style: ${href} */\n${cssContent}\n`;
        }
        return `/* External stylesheet (not fetched due to CORS): ${href} */\n`;
      } catch (error) {
        console.error(`Error processing CSS from ${href}:`, error);
        return "";
      }
    }
    return "";
  });

  // すべてのCSSを結合
  const cssContents = await Promise.all(cssPromises);
  stylesContent += cssContents.join("\n");

  return stylesContent;
};

// main.jsのpostHTML関数を修正
const postHTML = async () => {
  // スクリプトの取得（既存のコード）
  let scripts = document.querySelectorAll("script");
  let scriptsContent = "";
  scripts.forEach((script) => {
    if (script.src) {
      scriptsContent += `External script source: ${script.src}\n`;
    } else {
      scriptsContent += `${script.innerHTML}\n`;
    }
  });

  // CSSコンテンツの取得（新しい実装）
  const stylesContent = await getAllCSSContent();

  // 現在のページのベースURLを取得
  const baseUrl = window.location.origin + window.location.pathname;

  // ローカルホストにPOSTリクエストを送信
  const res = await fetch("http://localhost:8000/", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      page: document.querySelector("html").innerHTML,
      scripts: scriptsContent,
      styles: stylesContent,
      url: baseUrl,
    }),
  });

  const data = await res.json();
  return data;
};

// モーダルを作成して表示する関数
const showModal = (content) => {
  // モーダルのための Shadow DOM を作成
  const modalWrapper = document.createElement("div");
  const shadowRoot = modalWrapper.attachShadow({ mode: "open" });

  // スタイルタグを作成し、Shadow DOMに追加
  const style = document.createElement("style");
  style.textContent = `
    .custom-modal {
      position: fixed;
      top: 50%;
      left: 50%;
      transform: translate(-50%, -50%);
      z-index: 1000;
      background-color: white;
      padding: 30px 40px;
      max-height: 80vh;
      width: 80%;
      overflow-y: auto;
      font-family: 'Noto Sans JP', 'Hiragino Sans', sans-serif;
      line-height: 1.5;
      border-radius: 1rem;
      box-shadow: 0 0 10px rgba(0, 0, 0, 0.3);
    }

    .custom-modal button {
      display: block;
      margin: 20px auto 0;
      padding: 10px 20px;
      background-color: #007bff;
      color: white;
      border: none;
      cursor: pointer;
      border-radius: 1rem;
      transition: background-color 0.3s ease;
      box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -4px rgba(0, 0, 0, 0.1);
    }

    .custom-modal button:hover {
      background-color: #0056b3;
    }

    .custom-modal .modal-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 20px;
    }

    .custom-modal .modal-header h2 {
      margin: 0;
    }

    .custom-modal .close-button {
      cursor: pointer;
      font-size: 24px;
      background: none;
      border: none;
      color: #666;
    }

    .custom-modal h1 {
      font-size: 20px;
      font-weight: 700;
      margin: 5px 0;
    }

    .custom-modal h2 {
      font-size: 17px;
      font-weight: 600;
      position: relative;
      display: inline-block;
      background: linear-gradient(transparent 50%, yellow 50%);
      padding: 0 10px;
      margin: 0 0 20px;
    }

    .custom-modal h3 {
      font-size: 16px;
      font-weight: 600;
      position: relative;
      display: inline-block;
      background: linear-gradient(transparent 50%, rgba(0, 123, 255, 0.5) 50%);
      padding: 0 10px;
      margin: 0 0 20px;
    }

    .custom-modal h4 {
      font-size: 16px;
      font-weight: 700;
      line-height: 1.3;
      padding:0 .4em .2em;
      border-bottom: 3px dashed #aad3f3;
      background-color: #ffffff;
      color: #000000;
    }

    .custom-modal p,
    .custom-modal li {
      font-size: 14px;
      color: #000;
    }

    .custom-modal ul {
      list-style-type: disc;
      padding-left: 20px;
    }

    .custom-modal li {
      margin: 10px 0;
    }

    .custom-modal code {
      display: block;
      background-color: #f4f4f4;
      border-left: 4px solid #007bff;
      padding: 10px;
      margin: 15px 0;
      border-radius: 5px;
      font-size: 14px;
      color: #007bff;
      white-space: pre-wrap;
      font-family: 'Courier New', Courier, monospace;
      overflow-x: auto;
      max-width: 100%;
    }

    .custom-modal pre code {
      background: none;
      padding: 0;
      border: none;
    }

    .report pre code {
      background-color: #333;
      color: #00ff00;
      padding: 10px;
      margin: 15px 0;
      border-radius: 5px;
      white-space: pre-wrap;
      font-family: 'Courier New', Courier, monospace;
      overflow-x: auto;
      max-width: 100%;
    }

    .alt-suggest {
      display: block;
      background-color: #ffe6e9;
      border-left: 4px solid #dc143c;
      padding: 10px;
      margin: 15px 0;
      border-radius: 5px;
      font-size: 13px;
      white-space: pre-wrap;
      font-family: 'Courier New', Courier, monospace;
      overflow-x: auto;
      max-width: 100%;
    }

    img {
      max-width: 50%;
      height: auto;
    }
  `;
  shadowRoot.appendChild(style);

  // モーダルのコンテンツを作成し、Shadow DOMに追加
  const modalContent = document.createElement("div");
  modalContent.className = "custom-modal";
  modalContent.innerHTML = `
    <div>${content}</div>
    <button id="closeModal" aria-label="モーダルを閉じる">閉じる</button>
  `;
  shadowRoot.appendChild(modalContent);

  // モーダルを閉じるイベント
  modalContent.querySelector("#closeModal").addEventListener("click", () => {
    modalWrapper.remove();
  });

  // モーダルをDOMに追加
  document.body.appendChild(modalWrapper);
};

// ボタンを作成し、クリックイベントを設定する関数
function createButton() {
  const button = document.createElement("button");
  button.textContent = "アクセシビリティチェック開始";
  // ARIA属性を追加
  button.setAttribute("role", "button");
  button.setAttribute("aria-label", "アクセシビリティチェックを開始するボタン");
  button.setAttribute("aria-pressed", "false");
  // スタイル設定
  button.style.position = "fixed";
  button.style.bottom = "10px";
  button.style.left = "10px";
  button.style.zIndex = "100000";
  button.style.backgroundColor = "#095DAD";
  button.style.border = "3px solid #095DAD";
  button.style.color = "#fff";
  button.style.padding = "8px";
  button.style.cursor = "pointer";
  button.style.borderRadius = "1.0rem";
  button.style.fontWeight = "700";
  button.style.boxShadow =
    "0 10px 15px -3px #0000001a, 0 4px 6px -4px #0000001a";
  button.style.transition = "background-color 0.3s, color 0.3s";
  button.style.fontFamily = "'Noto Sans JP', 'Hiragino Sans', sans-serif";

  // ホバー時のスタイル設定
  button.addEventListener("mouseenter", () => {
    button.style.backgroundColor = "#fff";
    button.style.color = "#095DAD";
  });
  button.addEventListener("mouseleave", () => {
    button.style.backgroundColor = "#095DAD";
    button.style.color = "#fff";
  });

  return button;
}

// リロードマークを作成する関数
const createLoadingSpinner = () => {
  const spinner = document.createElement("div");
  spinner.className = "loading-spinner";
  spinner.innerHTML = `
    <style>
      .loading-spinner {
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        z-index: 100001;
        border: 8px solid #f3f3f3;
        border-top: 8px solid #3498db;
        border-radius: 50%;
        width: 60px;
        height: 60px;
        animation: spin 1s linear infinite;
      }
      @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
      }
    </style>
  `;
  document.body.appendChild(spinner);
  return spinner;
};

// ボタンを作成してクリックイベントを設定
const button = createButton();
button.addEventListener("click", async () => {
  // リロードマークを表示
  const spinner = createLoadingSpinner();

  try {
    // POSTリクエストを送信し、レスポンスを取得
    const ret = await postHTML();
    console.log(ret); // Log the response to check its structure and data

    // モーダルを表示
    showModal(`
      <h1>アクセシビリティ評価</h1>
      <div class="report">${ret.description}</div>
      <h3>ARIAタグの提案</h3>
      ${
        ret.aria_message
          ? `<p class="aria-all-tagged">${ret.aria_message}</p>`
          : `<ul>
          ${ret.aria_tags
            .map(
              (tag) =>
                `<li>
                  <strong>要素タイプ:</strong> ${tag.element}<br>
                  <strong>提案:</strong> ${tag.suggested_aria_tag}<br>
                  <strong>説明:</strong> ${tag.info}<br>
                  <strong>該当箇所のコード:</strong>
                  <code>${tag.html_snippet
                    .replace(/</g, "&lt;")
                    .replace(/>/g, "&gt;")}</code>
                </li>`
            )
            .join("")}
        </ul>`
      }
      </ul>
      <h3>Altタグがない画像</h3>
      ${ret.alt_message ? `<p>${ret.alt_message}</p>` : ""}
      <ul>
        ${ret.images_without_alt
          .map(
            (img) =>
              `<li>
                <strong>画像:</strong><br><img src="${img.src}" alt="${img.description}" style="max-width: 40%; height: auto;" /><br>
                <strong>画像の説明:</strong> ${img.description}<br>
                <p class="alt-suggest">Altタグの提案: ${img.alt}</p>
              </li>`
          )
          .join("")}
      </ul>
    `);
  } catch (error) {
    console.error("Error fetching data:", error);
    alert("データの取得中にエラーが発生しました。");
  } finally {
    // リロードマークを非表示にする
    spinner.remove();
  }
});
document.body.appendChild(button);
