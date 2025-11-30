chrome.runtime.onInstalled.addListener(() => {
  console.log("Nitido instalado");
});

chrome.runtime.onMessage.addListener((message, sender) => {
  if (message.type === "LEGAL_DETECTED") {
    chrome.action.setBadgeText({
      text: "!",
      tabId: sender.tab.id,
    });
    chrome.action.setBadgeBackgroundColor({
      color: "#ef4444",
      tabId: sender.tab.id,
    });
  }
});
