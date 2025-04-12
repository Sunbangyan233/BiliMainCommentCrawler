# BiliMainCommentCrawler
无需配置SESSDATA，即可轻松获取主站一级评论
---
## 怎么用？
先决条件：
- 浏览器已经安装[TamperMonkey](https://tampermonkey.net)
- 已登录bilibili.com
- Python3.7+ 的运行环境（使用py脚本需要，非必须

具体用法：
1. 轻点[安装脚本](https://github.com/Sunbangyan233/BiliMainCommentCrawler/raw/refs/heads/main/browser-script.user.js)，在打开的新页面确认安装。
2. 打开你想下载评论的视频页面，检查右上角脚本打开状态，按Page Done向下滚动评论
3. 可见有一堆main_时间戳.json的文件被下载
![image](https://github.com/user-attachments/assets/4ce81069-0c21-4517-9a81-9dfe29d14b75)
4. 确保 `process_api.py` 或 `batch.py` 与 `main_*.json` 在同一目录，运行 ` python +filename `
   弹窗 两次 y ，得到json文件直接转csv
5. 运行 `batch.py` 或 `merge_csv.py`，同上，得到的comment_all.csv即为评论数据，默认包含字段 `时间` `用户UID` `昵称` `评论内容`

## 注意事项：
- 浏览器脚本使用后请及时关闭

## To Do list
- [ ] 添加对二级评论的支持
- [ ] 添加对更多评论字段处理的支持，例如`IP属地` `粉丝牌` `充电评论` 等
- [ ] 清理csv合并后的原文件
