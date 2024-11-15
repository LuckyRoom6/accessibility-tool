const postHTML = async () => {
  // 全てのスクリプトタグを取得
  let scripts = document.querySelectorAll("script");
  let scriptsContent = "";

  // 各スクリプトタグの内容を取得
  scripts.forEach((script) => {
    if (script.src) {
      // 外部スクリプトの場合は、ソースURLを取得
      scriptsContent += `External script source: ${script.src}\n`;
    } else {
      // インラインスクリプトの場合は、その内容を取得
      scriptsContent += `${script.innerHTML}\n`;
    }
  });

  // 全てのスタイルタグとリンクタグ（スタイルシートを指しているもの）を取得
  let styleTags = document.querySelectorAll("style");
  let linkTags = document.querySelectorAll("link[rel='stylesheet']");
  let stylesContent = "";

  // インラインスタイルの内容を取得
  styleTags.forEach((style) => {
    stylesContent += `${style.innerHTML}\n`;
  });

  // 外部スタイルシートのリンクを取得
  linkTags.forEach((link) => {
    stylesContent += `External stylesheet source: ${link.href}\n`;
  });

  // ローカルホストにPOSTリクエストを送信
  const res = await fetch("http://localhost:8000/", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      // 開いているページのHTML、スクリプト、スタイルを送信
      page: document.querySelector("html").innerHTML,
      scripts: scriptsContent,
      styles: stylesContent,
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
      z-index: 100000;
      background-color: white;
      padding: 20px;
      max-height: 80%;
      width: 80%;
      overflow-y: auto;
      font-family: 'Noto Sans JP', 'Hiragino Sans';
      line-height: 1.5;
      border-radius: 1.0rem;
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
      border-radius: 1.0rem;
      box-shadow: 0 10px 15px -3px #0000001a, 0 4px 6px -4px #0000001a;
    }
    .custom-modal button:hover {
      background-color: #0056b3;
    }
    .custom-modal .modal-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
    .custom-modal .modal-header h2 {
      margin: 0;
    }
    .custom-modal .modal-content {
      margin-top: 20px;
    }
    .custom-modal .close-button {
      cursor: pointer;
      font-size: 24px;
    }
    .custom-modal h1,
    .custom-modal h2,
    .custom-modal h3,
    .custom-modal h4,
    .custom-modal h5,
    .custom-modal h6 {
      margin: 5px;
    }
    .custom-modal h1 {
      font-size: 20px;
      font-weight: 700;
    }
    .custom-modal h2 {
      font-size: 17px;
      font-weight: 600;
      position: relative;
      display: inline-block;
      font-weight:bold;
      background: linear-gradient(transparent 50%, yellow 50%);
      margin: 0 auto 20px;
      padding: 0 10px 0 10px;
    }
    .custom-modal h3 {
      font-size: 16px;
      font-weight: 600;
      position: relative;
      display: inline-block;
      font-weight: bold;
      background: linear-gradient(transparent 50%, rgba(0, 123, 255, 0.5) 50%);
      margin: 0 auto 20px;
      padding: 0 10px 0 10px;
    }
    .custom-modal h4 {
      font-size: 16px;
      font-weight: 700;
      background-color: #eee;
      color: #17194c;
      padding: 15px;
      line-height: 1.3;
    }
    .custom-modal h5 {
      font-size: 1em;
    }
    .custom-modal p {
      font-size: 12px;
      color: #000;
    }
    .custom-modal ul {
      list-style: disc;
      padding-left: 20px;
    }
    .custom-modal code {
      display: block;
      background-color: #f4f4f4;
      border-left: 4px solid #007bff;
      padding: 10px;
      margin: 15px 0;
      border-radius: 5px;
      font-size: 13px;
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
    .custom-modal li {
      list-style: disc;
      font-size: 12px;
      color: #000;
      margin: 0 25px;
    }
    .custom-modal, .custom-modal * {
      font-family: 'Noto Sans JP', 'Hiragino Sans', sans-serif;
    }
  `;
  shadowRoot.appendChild(style);

  // モーダルのコンテンツを作成し、Shadow DOMに追加
  const modalContent = document.createElement("div");
  modalContent.className = "custom-modal";
  modalContent.innerHTML = `
    <div>${content}</div>
    <button id="closeModal">閉じる</button>
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
      <h2>アクセシビリティ評価</h2>
      <div>${ret.description}</div>
      <h3>ARIAタグの提案</h3>
      <ul>
        ${ret.aria_tags
          .map(
            (tag) =>
              `<li>${tag.suggested_aria_tag}</li><br><li>${tag.info}</li>`
          )
          .join("")}
      </ul>
      <h3>Altタグがない画像</h3>
      ${ret.alt_message ? `<p>${ret.alt_message}</p>` : ""}
      <ul>
        ${ret.images_without_alt
          .map(
            (img) =>
              `<li>
                <strong>画像:</strong><br><img src="${img.src}" alt="${img.description}" style="max-width: 40%; height: auto;" /><br>
                <strong>Altタグの提案:</strong> ${img.description}
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
