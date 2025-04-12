// ==UserScript==
// @name         B站主评论数据抓取
// @namespace    https://tampermonkey.net/
// @version      0.1
// @description  抓取B站主评论API数据并保存到本地**不使用时请关闭，仅抓取主评论，不抓取楼中楼回复**
// @author       SunRestik
// @match        https://www.bilibili.com/*
// @grant        GM_xmlhttpRequest
// @grant        GM_download
// @grant        unsafeWindow
// @connect      api.bilibili.com
// @homepage     https://github.com/Sunbangyan233/BiliMainCommentCrawler
// @source       https://github.com/Sunbangyan233/BiliMainCommentCrawler/raw/refs/heads/main/client/browser-script.user.js
// ==/UserScript==

(function() {
    'use strict';

    // 存储抓取到的数据
    let replyMainData = [];

    // 监听fetch请求
    const originalFetch = unsafeWindow.fetch;
    unsafeWindow.fetch = function() {
        const fetchCall = originalFetch.apply(this, arguments);

        fetchCall.then(response => {
            if (!response.ok) return response;

            const url = response.url;
            const clonedResponse = response.clone();

            if (url.includes('/x/v2/reply/wbi/main')) {
                handleReplyMainResponse(clonedResponse);
            }

            return response;
        }).catch(error => {
            console.error('Fetch interception error:', error);
        });

        return fetchCall;
    };

    // 处理主评论响应
    async function handleReplyMainResponse(response) {
        try {
            const data = await response.json();
            replyMainData.push(data);
            console.log('Captured reply/main data:', data);
            saveDataIfNeeded();
        } catch (error) {
            console.error('Error processing reply/main response:', error);
        }
    }

    // 保存数据到文件
    function saveDataIfNeeded() {
        if (replyMainData.length > 0) {
            const timestamp = new Date().getTime();
            const content = JSON.stringify(replyMainData, null, 2);
            GM_download({
                url: 'data:text/plain,' + encodeURIComponent(content),
                name: `main_${timestamp}.json`,
                saveAs: false
            });
            // 清空已保存的数据
            replyMainData = [];
        }
    }

})();