"use strict";

const repository = "https://github.com/Cyh29hao/shuixian-skill";
const samples = {
  folders: {
    user: "我本来想整理文件，结果整理出了三个新建文件夹。",
    reply: "文件还没归位，安置房先盖了三套。先别盖第四套了。",
    note: "从本人语料整理出的共思镜像",
    source: "corpus-onboarding-2026-10-27.md"
  },
  bakery: {
    user: "今天懒得说正事。楼下新开了一家面包店，招牌丑得很认真，我绕路过去买了个最好看的面包。",
    reply: "这家店的审美可能全用在面包上了，招牌一点没分着。你买的那个长什么样？",
    note: "公开合成样本创建的朋友镜像",
    source: "friend-runtime-2026-10-26.md"
  },
  correction: {
    user: "别每次句尾都问我问题。我今天只想随口聊两句，不想还得组织回答。",
    reply: "好，不给你留问答题了。那块招牌听着像老板亲自设计的，谁劝都没劝住。",
    note: "接续面包店话题的一次临时纠偏",
    source: "friend-runtime-2026-10-26.md"
  }
};

document.querySelectorAll("[data-sample]").forEach(button => {
  button.addEventListener("click", () => {
    const sample = samples[button.dataset.sample];
    document.querySelectorAll("[data-sample]").forEach(option => option.setAttribute("aria-pressed", String(option === button)));
    document.getElementById("sample-user").textContent = sample.user;
    document.getElementById("sample-reply").textContent = sample.reply;
    document.getElementById("sample-note").textContent = sample.note;
    document.getElementById("sample-source").href = `${repository}/blob/main/docs/experiments/${sample.source}`;
  });
});

const promptField = document.getElementById("start-prompt");
const status = document.getElementById("copy-status");
document.querySelectorAll("[data-host]").forEach(button => {
  button.addEventListener("click", () => {
    const claude = button.dataset.host === "claude";
    const host = claude ? "Claude Code" : "Codex";
    document.querySelectorAll("[data-host]").forEach(option => option.setAttribute("aria-pressed", String(option === button)));
    promptField.value = `帮我安装水仙 skill：${repository}\n我正在使用 ${host}，请安装到当前项目。\n用我选好的聊天记录或日记，整理我自己的说话方式，让我和自己的镜像聊聊。\n如果缺少文件位置、本人发言名称或导入范围，一次问清。\n已有可读文件就直接继续，只有微信原始数据库时先确认可行办法。\n先只保存抽象表达习惯，保留原件，别把聊天提交到 GitHub。\n创建后告诉我实际调用名，然后开始试聊。`;
    const prefix = claude ? ".claude" : ".agents";
    document.getElementById("install-command").textContent = `git clone ${repository} ${prefix}/skills/create-shuixian`;
    const invocation = document.getElementById("host-invocation");
    invocation.replaceChildren(document.createTextNode(`在项目目录执行，再在 ${host} 中调用 `));
    const code = document.createElement("code");
    code.textContent = `${claude ? "/" : "$"}create-shuixian`;
    invocation.append(code, document.createTextNode("。"));
    status.textContent = "";
  });
});

document.getElementById("copy-prompt").addEventListener("click", async () => {
  try {
    if (!navigator.clipboard?.writeText) throw new Error("Clipboard unavailable");
    await navigator.clipboard.writeText(promptField.value);
    status.textContent = "已复制，去你的 agent 聊天里粘贴吧。";
  } catch {
    promptField.focus();
    promptField.select();
    status.textContent = "浏览器未允许自动复制。内容已选中，请按 Ctrl+C，或长按复制。";
  }
});
