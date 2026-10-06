# GT-ZHS — Locale layer evidence base: zh-Hant-TW → zh-Hans (mainland) for *Five Hours Apart*

Lane: GT-ZHS (read-only ground-truth lane). Date anchored: 2026-10-06. Scope: the Simplified edition is DERIVED from the ratified Taiwan text by OpenCC `tw2sp`, then a lexicon pass driven by this layer, then a human mainland-register review. This file is the evidence base for that lexicon pass and review. It does not translate the story.

## 0. Method, sources reachable, legend

The whole story was read in three slices (lines 1–400, 401–800, 801–1202). Every term below was checked against at least one of the following corpora, all pulled live on 2026-10-06 (the egress proxy blocked zh.wikipedia.org, terms.naer.edu.tw, chinese-linguipedia.org, moedict.tw, data.gov.tw, moe.gov.cn, language.moe.gov.tw, thepaper.cn, w3.org, wikiwand, baike.baidu.com, every zhwiki mirror and every Taiwan/mainland news site I tried; raw.githubusercontent.com and github.com were open, and the web-search tool returned snippets from the blocked sites, which I cite as "WEB-snippet"):

| tag | source | what it proves |
|---|---|---|
| **OCC** | OpenCC `tw2sp` run locally (pip `opencc` 1.4.2, bundled dictionaries; plus a sparse clone of `BYVoid/OpenCC` master: `data/dictionary/TWPhrases.txt` 824 entries (the former TWPhrasesIT/Name/Other, now merged), `TSPhrases.txt` 487, `TSCharacters.txt` 5062, `config/tw2sp.json`). Two test corpora (≈620 TW items) were converted; every "tw2sp gives …" statement below is observed output, not assumption. | exactly what the converter will and will not do |
| **CSLD** | 《兩岸常用詞典》(中華語文知識庫) data via `g0v/moedict-data-csld`: `dict-csld.json` (99,187 entries, with 陸⃝/臺⃝ usage notes), `=同實異名.json` (753 same-thing-different-name pairs), `=同名異實.json`, `=臺灣特有.json` (801), `=大陸特有.json` (3,299) | the cross-strait dictionary's own ruling |
| **MW** | MediaWiki zh-conversion tables (zh2CN/zh2Hans) via `gumblex/zhconv` `zhcdict.json` | zh.wikipedia's own TW→CN word pairs |
| **XH-P / XH-G** | 新华社译名室《世界人名翻译大辞典》/《世界地名翻译大辞典》Excel backups via `karedoea/Global-name-translation` (人名翻译.xlsx 676,876 rows; 地名翻译.xlsx 177,322 rows) | the mainland standard name forms |
| **CLREQ** | W3C 中文排版需求 (`w3c/clreq` gh-pages source) | punctuation forms by region, spacing |
| **GB15834** | GB/T 15834-2011《标点符号用法》as quoted (with clause numbers) in `mizzlelover/biaodian` references | mainland punctuation rules |
| **STYLE** | `ruanyf/document-style-guide` (CN), `sparanoid/chinese-copywriting-guidelines` (TW) | web/tech spacing and numeral habits (NOT print norms) |
| **WEB** | a named URL whose text I saw (snippet or page) | usage evidence |
| **CORPUS** | this lane's own usage knowledge, not verified live today | lowest weight |

Confidence: **H** = standard or converter-verified; **M** = well-attested usage, not a standard; **L** = inference.

Columns in §a: `en | tw | hans | forbidden | cat | conf | evidence | notes`. "forbidden" = a form the converter leaves or a Taiwan writer would write that a mainland editor strikes. "—" in `forbidden` means the pair is the same in both editions once the script is converted: **do not over-convert these**.

Three architectural facts the layer must be built on (all converter-verified, §d has the detail):

1. **`tw2sp` has almost no aviation, automotive, hotel/food, unit, physics or everyday coverage.** Of 230 story-domain items tested, it changed the computing ones and left 航廈/空橋/進場/登機門/班機/航管/後照鏡/煞車/後車廂/雙黃燈/飯店/櫃檯/服務生/自動販賣機/鋁罐/起司/便利商店/呎/哩/吋/公尺/美金/克耳文/重整化/雜訊/計程車→(converted)/公車/捷運/機車/保全/手扶梯/透過/蠻/捐血/鐵捲門/磨石子/霧面玻璃/尖峰時間/日光節約時間/世界協調時間/識別證/束帶/語音助理/筆電 … untouched. The lexicon pass is therefore load-bearing, not cosmetic.
2. **`tw2sp` over-converts several polysemous words everywhere they occur** (核心→内核, 程序→进程, 設定→设置, 資料→数据, 檔案→文件, 物件→对象, 影片→视频 (even inside 投影片→投视频), 陣列→数组 (even 超導體陣列), 複製→拷贝, 執行→运行, 存取→访问, 排程→调度, 簡報→演示文稿) and it fires inside proper names and quoted labels (國立臺灣大學資訊工程學系→…信息工程学系, 《數位時代》→《数字时代》).
3. **`tw2sp` leaves residues a mainland editor always strikes**: 甚么, 妳/牠/祂, 帐 (帐单/转帐/记帐/结帐/对帐单), 纪录 (for "record"), 姓钟 (should be 锺), 乱数, 笔电, 杂讯, 智能型手机, 当机, 重开机, 脱机, 存盘, 捷径, 工具列, 领台, 蓝芽.

---

## (a) TW → CN lexicon

### a.1 Computing (the machine, the test, the log)

| en | tw | hans | forbidden | cat | conf | evidence | notes |
|---|---|---|---|---|---|---|---|
| software | 軟體 | 软件 | 软体 | comp | H | OCC 软件; CSLD 軟體[臺] 陸⃝即「軟件」; MW | |
| hardware / firmware | 硬體 / 韌體 | 硬件 / 固件 | 硬体 / 韧体 | comp | H | OCC | |
| program | 程式 | 程序 | 程式 | comp | H | OCC; CSLD 程式 臺⃝…陸⃝即「程序」 | but see 程序→进程 trap (§d) |
| process (OS; "Two processes, each convinced it got there first") | 行程 / 處理程序 | 进程 | 行程 (CN = itinerary) | comp | H | OCC 兩個行程→两个进程; 處理程序 left as 处理程序 | if the TW text uses 程序 for "process", tw2sp gives 进程 (right here, wrong elsewhere) |
| code / source code | 程式碼 / 原始碼 | 代码 / 源代码 | 程式码 / 原始码 | comp | H | OCC; CSLD 原始碼[臺] 陸⃝即「源代碼」 | "The fix is four lines" → 四行代码 |
| programmer / engineer | 程式設計師 / 工程師 | 程序员 / 工程师 | 程式设计师 | comp | H | OCC; CSLD 程式員→程序員 | |
| data (ML/computing sense) | 資料 | 数据 | — (資料 itself is fine in the "materials/info" sense) | comp | H | OCC 資料→数据 everywhere (over-converts 個人資料→个人数据); CSLD 資料 (both sides share the "materials" sense) | guard: 個人資料→个人资料/个人信息, 背景資料→背景资料 |
| database / data pipeline | 資料庫 / 資料管線 | 数据库 / 数据管道 (数据流水线) | 数据管线 (OCC residue) | comp | M | OCC 数据库 ✓, 資料管線→数据管线 ✗; CORPUS | |
| screen (monitor/phone screen) | 螢幕 | 屏幕 | 萤幕 | comp | H | OCC; CSLD 螢幕[臺] 陸⃝即「屏幕」 | |
| monitor (device) | 顯示器 | 显示器 | — | comp | H | OCC unchanged | the folding-table monitor |
| server | 伺服器 | 服务器 | 伺服器 | comp | H | OCC; CSLD; MW | |
| network / the internet | 網路 / 網際網路 | 网络 / 互联网 | 网路 / 网际网路 | comp | H | OCC; CSLD 網路[臺] 陸⃝即「網絡」, 網際網路→互聯網 | fires inside names: guard (§d) |
| memory (RAM) | 記憶體 | 内存 | 记忆体 / 存储器 | comp | H | OCC 内存; CSLD 主記憶體→內存 | |
| hard drive; "a drive in his desk" | 硬碟 / 隨身碟 / 外接硬碟 | 硬盘 / U盘 / 移动硬盘 | 硬碟 / 随身碟 | comp | H | OCC 硬盘, 隨身碟→U盘; CSLD 隨身碟[臺] 陸⃝即「優盤」「閃存盤」… | for the father's copy prefer 硬盘/移动硬盘, not U盘 |
| GPU card; "eight cards", "four cards" | 顯示卡 / 卡 | 显卡 / 卡 | 显示卡 | comp | H | OCC; CSLD 顯示卡 也作「顯卡」 | classifier: TW 一張卡; CN 一块显卡 is commoner than 一张 (OCC keeps 张) — editor's call, M |
| cache | 快取 | 缓存 | 快取 | comp | H | OCC; CSLD 快取 陸⃝也作「高速緩存」 | |
| hash ("hash 9b3e… = 9b3e…") | 雜湊 | 哈希 | 杂凑 | comp | H | OCC 哈希 | 散列 is the formal CN term; 哈希 is what engineers say |
| kernel ("the same kernel, in the other order") | 核心 | 内核 (OS) / 核函数 (GPU kernel) | 内核 in every non-computing sense | comp | H | OCC 核心→内核 everywhere (核心價值→内核价值, 核心區→内核区, 問題的核心 kept) | guard: convert only 作業系統核心/核心函式; keep 核心 elsewhere ("out of the core" = downtown) |
| bit; "to the bit", "bit for bit" | 位元 | 比特 / 位 | 位元 | comp | H | OCC 位元→比特, 一位元不差→一比特不差; CSLD 位元[臺] 陸⃝即「比特」 | literary CN usually "一位不差/逐位", 比特 is fine in a machine-talk sentence |
| byte ("four bytes a tile", "to the byte") | 位元組 | 字节 | 位元组 | comp | H | OCC; CSLD; MW | |
| thread | 執行緒 | 线程 | 执行绪 | comp | H | OCC | |
| interface | 介面 | 界面 (UI) / 接口 (API, network) | 介面 | comp | H | OCC 介面→界面 (網路介面→网络界面 ✗ should be 网络接口); CSLD 介面[臺] 陸⃝即「界面」 | |
| digital | 數位 | 数字 / 数码 | 数位 | comp | H | OCC 数字; CSLD 數位 陸⃝即「數字」「數碼」 | |
| print / printer | 列印 / 印表機 | 打印 / 打印机 | 列印 / 印表机 | comp | H | OCC; CSLD; MW | |
| information | 資訊 | 信息 | 资讯 | comp | H | OCC; CSLD 資訊[臺] 陸⃝即「信息」 | fires inside institution names: guard |
| message (chat/text) | 訊息 | 消息 (信息) | 讯息 | comp | H | OCC 訊息→消息 | |
| SMS | 簡訊 | 短信 | 简讯 | comp | H | OCC; CSLD 簡訊 陸⃝即「短信」 | |
| to text ("Text me what it does", "You dictate two words back") | 傳訊息 / 傳簡訊 | 发消息 / 发短信 / 发信息 | 传消息 / 传短信 (OCC output) | comp | H | OCC 傳訊息→传消息 (verb survives) | lexicon must rewrite the verb 傳→发 |
| mobile phone | 行動電話 / 手機 | 手机 (移动电话 only in formal register) | 行动电话 | comp | H | OCC 移动电话; CSLD 行動電話[臺] 陸⃝即「移動電話」「手機」 | 手機 is identical both sides |
| smartphone | 智慧型手機 | 智能手机 | 智能型手机 (OCC output) | comp | H | OCC gives 智能型手机; CSLD 陸⃝即「智能手機」 | |
| video ("people post videos of it threading garages") | 影片 | 视频 | — (影片 = film is fine in CN) | comp | H | OCC 影片→视频 everywhere; CSLD 影片 = 電影 | guard against 投影片→投视频 (§d) |
| file (computer) | 檔案 | 文件 | 档案 in computing sense; but 檔案 = archive/records must STAY 档案 | comp | H | OCC 檔案→文件 everywhere (人事檔案→人事文件 ✗, 檔案室→文件室 ✗); CSLD 檔案 = records (shared) | |
| folder | 資料夾 | 文件夹 | 资料夹 | comp | H | OCC; CSLD 資料夾[臺] 陸⃝即「文件夾」 | |
| page table ("a copy of the page table") | 分頁表 | 页表 | 分页表 (OCC residue) | comp | M | OCC unchanged; CORPUS (CN OS literature: 页表) | |
| page (memory page) | 分頁 / 頁 | 页 / 页面 | — | comp | M | OCC unchanged | |
| checkpoint ("ckpt") | 檢查點 | 检查点 | — | comp | H | OCC unchanged, same both sides | |
| seed (random seed; log "seed 9e40…") | 種子 / 亂數種子 | 种子 / 随机数种子 | 乱数 (OCC residue) | comp | H | OCC 亂數→乱数 unchanged; CORPUS 随机数 | |
| random number | 亂數 | 随机数 | 乱数 | comp | H | OCC unchanged; CORPUS | |
| fork ("You fork it", "fork #8812") | 分叉 / 分支 | 分叉 (分支) | — | comp | M | OCC unchanged; CORPUS (复刻 only for repo forks) | |
| rewind ("rewind #8812 … exact") | 倒帶 / 回溯 | 倒带 / 回退 (回滚) | — | comp | M | OCC unchanged | 倒带 understood both sides |
| replay ("fork C replay from 10-27") | 重播 / 回放 | 回放 | 重播 (CN = rebroadcast) | comp | M | CSLD 回放[陸]; OCC unchanged | |
| laptop | 筆電 / 筆記型電腦 | 笔记本电脑 / 笔记本 | 笔电 (OCC residue) | comp | H | OCC 筆電→笔电, 筆記型電腦→笔记本电脑; CSLD 筆電[臺] 陸⃝即「筆記本電腦」 | "I could run its whole life again on your laptop" |
| mouse / keyboard | 滑鼠 / 鍵盤 | 鼠标 / 键盘 | 滑鼠 | comp | H | OCC; CSLD; MW | |
| rack / cabinet / fan / watt | 機架 / 機櫃 / 風扇 / 瓦 | 机架 / 机柜 / 风扇 / 瓦 | — | comp | H | OCC unchanged | "Idle 790 W" |
| algorithm | 演算法 | 算法 | 演算法 | comp | H | OCC; MW | |
| array (computing) | 陣列 | 数组 | — | comp | H | OCC | |
| array (physics: "arrays of superconductors") | 陣列 | 阵列 | 数组 (OCC output ✗) | phys | H | OCC 超導體陣列→超导体数组 ✗, 天線陣列→天线数组 ✗ | must be 超导体阵列 |
| queue | 佇列 | 队列 | 伫列 (only with plain t2s) | comp | H | OCC tw2sp 队列 ✓; t2s 伫列 ✗ | the brief's 佇列→伫列 fear applies to t2s/t2cn, not tw2sp |
| variable / function / loop / recursion / stack | 變數 / 函式 / 迴圈 / 遞迴 / 堆疊 | 变量 / 函数 / 循环 / 递归 / 堆栈 | 变数 / 函式 / 回圈 | comp | H | OCC | "the loop that keeps every region just inside the edge" is a control loop → 回路/控制环 (M), not 循环 |
| object (OOP) | 物件 | 对象 | 物件 only if it means "item" | comp | H | OCC 物件→对象 everywhere (這件物件→这件对象 ✗) | |
| operating system | 作業系統 | 操作系统 | 作业系统 | comp | H | OCC; MW | |
| configuration file ("a configuration file nobody had opened since May") | 設定檔 | 配置文件 | 设置档 (OCC output ✗) | comp | H | OCC 設定檔→设置档; CORPUS | |
| setting ("there's a setting for it somewhere") | 設定 | 设置 | 设定 is correct for narrative "setting" (故事設定) | comp | H | OCC 設定→设置 everywhere (故事設定→故事设置 ✗) | |
| default | 預設 | 默认 (computing) / 预设 (presuppose) | — | comp | M | OCC leaves 预设 | |
| sandbox ("It's a sandbox.") | 沙盒 | 沙箱 (沙盒 also current) | — | comp | M | OCC unchanged; CORPUS (security/dev: 沙箱; games: 沙盒) | recommend 沙箱 |
| schedule (booking: "It's on the schedule under my name") | 排程 | 排期 / 日程 / 预约 | 调度 (OCC output, wrong in this sense) | comp | H | OCC 排程→调度 | |
| scheduler / scheduling (OS) | 排程 / 排程器 | 调度 / 调度器 | — | comp | H | OCC | |
| version | 版本 | 版本 | — | comp | H | same | |
| bug / error | 錯誤 / bug | 错误 / 漏洞 / bug | — | comp | M | same chars | |
| fix / patch | 修補 / 修正 / 修復 | 修复 / 修改 / 补丁 | 修补 (OCC residue, weak) | comp | M | OCC 修補 unchanged, 修補程式→修补程序 (CN: 补丁) | |
| test / model / evaluation | 測試 / 模型 / 評估 | 测试 / 模型 / 评估 | — | comp | H | same | |
| go live ("We went live in May") | 上線 | 上线 | — | comp | H | same (CSLD lists unrelated 陸 senses; IT sense shared) | |
| test and dev | 測試與開發 | 测试与开发 | — | comp | H | same | |
| open-source ("small open models") | 開源 / 開放原始碼 | 开源 / 开放源代码 | 开放原始码 | comp | H | OCC | |
| AI / ML / feature / retrain | 人工智慧 / 機器學習 / 特徵 / 重新訓練 | 人工智能 / 机器学习 / 特征 / 重新训练 | 人工智慧 | comp | H | OCC; CSLD; MW | 徵→征 is script only |
| language model | 語言模型 | 语言模型 | — | comp | H | same | |
| voice assistant ("The assistant answers") | 語音助理 | 语音助手 | 语音助理 (OCC residue) | comp | H | OCC unchanged; CORPUS (Siri/小爱 = 语音助手) | |
| profile photo ("the size of a postage stamp") | 大頭貼 / 大頭照 / 個人照片 | 头像 | 大头贴 | comp | M | OCC unchanged; CORPUS | |
| motion sensor | 感應器 / 感測器 | 传感器 (感应器 acceptable for motion sensors) | — | comp | M | OCC 感測器→传感器, 感應器 unchanged; CORPUS (红外感应器 is normal CN) | |
| receiver (the thumb-sized ADS-B dongle) | 接收器 | 接收器 (接收机) | — | comp | M | OCC unchanged | |
| antenna | 天線 | 天线 | — | comp | H | same | |
| cables / "a loom of cables" / zip ties | 線材(纜線) / 線束 / 束帶(束線帶) | 线缆 / 线束 / 扎带 | 束带 | comp | M | OCC unchanged; CORPUS | |
| label maker / label strip | 標籤機 / 標籤 | 标签机 / 标签 | — | comp | M | same | |
| podcast | Podcast / 播客 | 播客 | — | comp | M | same | |
| UTC ("You could feed it UTC") | 世界協調時間 / UTC | 协调世界时 / UTC | 世界协调时间 | comp | H | OCC unchanged; CORPUS (GB/T 7408 name 协调世界时) | keep "UTC" in Latin in both and the trap vanishes |
| daylight saving (implied by "clocks went back") | 日光節約時間 | 夏令时 | 日光节约时间 | comp | H | OCC unchanged; CSLD 日光節約時間[臺] 陸⃝即「夏令時」「夏時制」 | |
| clocks go back / fall back | 時鐘撥慢(調回)一小時 | 时钟拨回(调回)一小时 | — | comp | H | same | |
| local time ("Local.") | 當地時間 / 本地時間 | 本地时间 | — | comp | H | same | |
| record / the log / rows ("Everything the field has ever concluded is a row") | 紀錄 / 記錄 / 日誌 | 记录 / 日志 | 纪录 (CN: only 纪录片, 世界纪录) | comp | H | OCC 紀錄→纪录 ✗; TW spelling rule 紀錄 (noun) vs 記錄 (verb) does not exist in CN | the single most frequent residue risk in Part Two/Three |
| recording ("bring up a recording"; "It's a recording when it's stopped") | 錄影 / 錄音 / 紀錄 | 录像 / 录音 / 记录 | 录影 | comp | H | OCC 錄影→录像; CSLD 錄影[臺] 陸⃝即「錄像」 | |
| crash | 當機 | 死机 / 宕机 | 当机 | comp | H | CSLD 當機[臺] 陸⃝即「死機」; OCC unchanged | |
| reboot | 重開機 | 重启 | 重开机 | comp | H | OCC unchanged; CORPUS | |
| download / upload / search / link / click | 下載 / 上傳 / 搜尋 / 連結 / 點選 | 下载 / 上传 / 搜索 / 链接 / 点击 | 搜寻 / 连结 / 点选 | comp | H | OCC | |
| log in / log out | 登入 / 登出 | 登录 / 注销(退出) | 登入 | comp | H | OCC | |
| online / offline | 線上 / 離線 | 在线 / 离线 | 脱机 (OCC output, dated) | comp | H | OCC 線上→在线, 離線→脱机; CSLD 離線 陸⃝也作「脫機」 | prefer 离线 |
| bandwidth / latency | 頻寬 / 延遲 | 带宽 / 延迟 | 频宽 | comp | H | OCC; CSLD 帶寬[陸] | |
| Bluetooth / Wi-Fi / hotspot | 藍牙(藍芽) / Wi-Fi / 熱點 | 蓝牙 / Wi-Fi / 热点 | 蓝芽 | comp | H | OCC leaves 蓝芽 | |
| cloud / cloud computing | 雲端 / 雲端運算 | 云端 / 云计算 | 云端运算 | comp | H | OCC unchanged; CSLD 雲端運算→雲計算 | |
| chip / silicon / IC / transistor | 晶片 / 矽 / 積體電路 / 電晶體 | 芯片 / 硅 / 集成电路 / 晶体管 | 晶片 / 矽 | comp | H | OCC; CSLD 矽[臺] 陸⃝即「硅」 | "in silicon or in meat" → 硅 |
| window / menu / shortcut / icon / toolbar / status bar | 視窗 / 選單 / 捷徑 / 圖示 / 工具列 / 狀態列 | 窗口 / 菜单 / 快捷方式 / 图标 / 工具栏 / 状态栏 | 捷径, 工具列 (OCC residues) | comp | H | OCC; CSLD 視窗/選單 | |
| access / read / write / execute | 存取 / 讀取 / 寫入 / 執行 | 访问 / 读取 / 写入 / 运行(执行) | — | comp | M | OCC 存取→访问, 執行→运行 (over-converts 執行計畫→运行计划 ✗) | guard 執行 outside computing |
| copy (noun/verb; "a copy of the page table", "He has a copy") | 複製 / 副本 | 复制 / 副本 | 拷贝 (OCC output; colloquial) | comp | H | OCC 複製→拷贝 | mainland editors prefer 复制 |
| save (file) | 存檔 / 儲存 | 保存 / 存档 | 存盘 (OCC output, dated) | comp | M | OCC 存檔→存盘 | |
| restore / revert | 復原 / 還原 / 回復 | 恢复 / 还原 | 回复 (= reply) | comp | H | OCC 回復原狀→回复原状 ✗ | |
| permutation / integers / reversible | 排列(置換) / 整數 / 可逆 | 置换(排列) / 整数 / 可逆 | — | comp | M | same chars | "an exact permutation of integers" → 整数的精确置换 |
| noise ("It's noise. Content-free, on purpose.") | 雜訊 | 噪声 | 杂讯 (OCC residue) | comp | H | OCC 雜訊→杂讯 unchanged ✗; MW 雜訊→噪声; CSLD 噪聲[陸] 臺⃝即「噪音」 | |
| signal | 訊號 | 信号 | 讯号 | comp | H | OCC 信号 | |
| frequency | 頻率 | 频率 | — | comp | H | same | |
| shielding | 遮蔽 / 屏蔽 | 屏蔽 | — | comp | H | OCC 遮蔽→屏蔽 | |
| stereogram | 立體圖 / 3D立體圖 | 立体图 / 三维立体画 | — | comp | L | CORPUS | |
| lava lamp | 熔岩燈 | 熔岩灯 | — | comp | M | same | |
| "the tape" (the unbroken record) | 磁帶 / 紀錄帶 | 磁带 / 记录 | — | comp | M | OCC same; 磁碟→磁盘 | |
| Frontier / Idle / Quiet (screen labels) | 前沿 / 閒置 / 靜止 | 前沿 / 空闲(闲置) / 静止 | — | comp | M | CORPUS | keep Latin labels identical in both editions if the TW edition keeps them |
| bookkeeping ("Night is when it does its bookkeeping") | 記帳 | 记账 | 记帐 (OCC output ✗) | fin | H | OCC 帳→帐 everywhere | CN uses 账 for money, 帐 only for 帐篷/蚊帐 |
| bank statement ("the way you'd scroll a bank statement") | 銀行對帳單 | 银行对账单 | 对帐单 (OCC ✗) | fin | H | OCC | |
| transfers (money; "the transfers moving between the London systems and yours") | 轉帳 | 转账 | 转帐 (OCC ✗) | fin | H | OCC 轉帳→转帐; MW 帳單→账单 | |
| account / bill | 帳戶 / 帳號 / 帳單 | 账户 / 账号 / 账单 | 帐户 / 帐号 / 帐单 (OCC ✗) | fin | H | OCC; MW | |
| rent ("A knot stays while it earns its keep"; log "rent … balance +") | 租金 / 房租 | 租金 / 房租 | — | fin | H | same | |

### a.2 Aviation

| en | tw | hans | forbidden | cat | conf | evidence | notes |
|---|---|---|---|---|---|---|---|
| terminal ("Terminal D") | 航廈 (第D航廈) | 航站楼 (D航站楼) | 航厦 | avi | H | OCC unchanged; CSLD 航廈[臺] 陸⃝即「航站樓」「候機樓」 | |
| jet bridge ("The walk off the jet bridge") | 空橋 | 廊桥 / 登机桥 | 空桥 | avi | H | CSLD 空橋 陸⃝也作「廊橋」「登機廊橋」; OCC unchanged | |
| approach (the arrival/approach; "on final") | 進場 / 進場程序 | 进近 | 进场 (CN = entering a venue) | avi | H | OCC unchanged; CORPUS (CN 民航: 进近, 最后进近) | "The approach is the only part that's ever interested you" → 进近 |
| final (leg) | 五邊 / 最後進場 | 五边 / 最后进近 | — | avi | M | same chars; CORPUS | 五边 is used by CN GA pilots too |
| land / landing / "cleared to land" | 落地 / 降落 / 著陸 ; 可以落地 | 落地 / 降落 / 着陆 ; 可以落地 | 著陆 (t2s residue only) | avi | H | OCC tw2sp 着陆 ✓ | |
| passport control ("The lines at passport control") | 證照查驗 / 護照查驗 | 边检 / 边防检查 / 护照检查 | 证照查验 | avi | H | OCC unchanged; CORPUS | |
| carousel | 行李轉盤 | 行李转盘 | — | avi | H | same | |
| baggage claim | 行李提領區 | 行李提取处 | 行李提领 | avi | M | OCC unchanged; CORPUS | |
| gate ("AT GATE") | 登機門 | 登机口 | 登机门 | avi | H | CSLD 登機門[臺] 陸⃝即「登機口」 | |
| flight ("the last London flight of the night") | 班機 / 航班 | 航班 | 班机 (understood, TW-flavoured) | avi | H | OCC unchanged; CORPUS | |
| flight (the act), ATC | 飛航 / 飛航管制 | 飞行 / 空中交通管制 (空管) | 飞航 | avi | H | OCC unchanged; CORPUS | |
| ATC (short) | 航管 | 空管 | 航管 | avi | H | OCC unchanged; CORPUS | |
| tower ("the speakers play the tower") | 塔台 | 塔台 | — | avi | H | same | |
| heavy (wake category; the father's word) | 重型機 / 重型 | 重型机 / 重型 | — | avi | M | same chars; CORPUS | do not render as 重機 (TW = big motorcycle) |
| runway / "the seventeens and eighteens" / 27L | 跑道 / 17、18跑道 / 27左 | 跑道 / 17、18号跑道 / 27左 | — | avi | M | same | |
| crosswind / westerly / south wind | 側風 / 西風 / 南風 | 侧风 / 西风 / 南风 | — | avi | H | same | |
| transponder ("Every aircraft … broadcasts where it is") | 應答機 / 詢答機 (TW CAA) / 應答器 | 应答机 | 询答机 | avi | H | OCC unchanged; WEB interpreting.hku.hk glossary "transponder 應答器;詢答機"; CORPUS CN 民航 应答机 | |
| receiver (radio) | 接收器 / 接收機 | 接收机 / 接收器 | — | avi | M | OCC unchanged | |
| airport / airline | 機場 / 航空公司 | 机场 / 航空公司 | — | avi | H | same | |
| economy class / middle seat | 經濟艙 / 中間座位 | 经济舱 / 中间座位 | — | avi | H | same | |
| jet lag / "It's four in the morning in me" | 時差 | 时差 | — | avi | H | same | |
| connection | 轉機 | 转机 / 中转 | — | avi | H | same | |
| arrivals / departures ("International arrivals come out downstairs"; "the ramp for departures") | 入境(大廳) / 出境(層) | 到达 / 出发 (国际到达/国际出发) | — | avi | M | OCC same chars; CORPUS | CN airports sign 国际到达/国际出发 |
| arrivals board ("Up on the board") | 航班顯示看板 / 班機資訊 | 航班显示屏 / 航班信息屏 | 看板 | avi | M | CORPUS | |
| DELAYED / LANDED / AT GATE | 延誤 / 已降落 / 已抵達登機門 | 延误 / 已降落 / 已到达登机口 | — | avi | M | CORPUS | |
| shuttle ("between a shuttle and a family") | 接駁車 | 摆渡车 / 班车 / 穿梭巴士 | 接驳车 | avi | H | OCC unchanged; CSLD 接駁車 (no 陸 equivalent listed); CORPUS | |
| cell lot | 手機等候區 | 手机等候区 / 等候停车场 | — | avi | L | CORPUS | |
| toll plaza ("the south toll plaza") | 收費站 | 收费站 | — | avi | H | same | |
| taxiway / apron / "the field" | 滑行道 / 停機坪 / 機場場面 | 滑行道 / 停机坪 / 机场 | — | avi | H | same | |
| boarding pass / lounge | 登機證 / 候機室 | 登机牌 / 候机室 | 登机证 | avi | M | OCC unchanged; CORPUS | |
| flight attendant / captain | 空服員 / 機長 | 乘务员(空乘) / 机长 | 空服员 | avi | M | OCC unchanged | |
| engine / jet (aircraft) | 引擎 / 噴射機 | 发动机 (引擎 ok) / 喷气式飞机 | 喷射机 | avi | H | CSLD 噴射機→噴氣式飛機 (同實異名) | |
| landing gear / flaps / winglets / raked wingtips | 起落架 / 襟翼 / 翼尖小翼 / 斜削翼尖 | 起落架 / 襟翼 / 翼梢小翼 / 斜削式翼梢 | — | avi | M | same; CORPUS | |
| cargo (flights) | 貨機 | 货机 | — | avi | H | same | |
| go-around / holding / delayed / on time | 重飛 / 等待航線 / 延誤(誤點) / 準點 | 复飞 / 等待航线 / 延误(晚点) / 准点 | 重飞 / 误点 | avi | H | OCC unchanged; CORPUS | |
| knots / nautical miles | 節 / 浬(海浬) | 节 / 海里 | 浬 / 海浬 | avi | H | OCC unchanged; CSLD 臺灣特有 海浬 | |
| window seat / blind | 靠窗座位 / 遮光板 | 靠窗座位 / 遮光板 | — | avi | H | same | |
| yoke / throttle quadrant | 駕駛盤(操縱桿) / 油門象限(油門座) | 驾驶盘 / 油门台 | — | avi | L | CORPUS | |
| flight simulator | 飛行模擬器 | 飞行模拟器 | — | avi | H | same | |
| flight path ("We were on the flight path") | 航道 / 飛行路徑 / 航線下方 | 航线 / 飞行路径 | — | avi | M | same | |
| jet fuel | 航空燃油 | 航空煤油 / 航油 | — | avi | M | CORPUS | |
| triple-seven / 737 | 波音777 (七七七) / 737 | 波音777 / 737 | — | avi | H | same | |

### a.3 Cars, roads, parking

| en | tw | hans | forbidden | cat | conf | evidence | notes |
|---|---|---|---|---|---|---|---|
| self-driving / autopilot / supervising | 自動駕駛 / 監督 | 自动驾驶 / 监督 | — | car | H | same | |
| steering wheel ("you give the car the wheel") | 方向盤 | 方向盘 | — | car | H | same | |
| side mirrors ("its mirrors unfold") | 後照鏡 | 后视镜 | 后照镜 | car | H | CSLD 後照鏡[臺] 陸⃝即「後視鏡」; OCC unchanged | |
| navigation / HOME / the blue ribbon | 導航 / 回家 / 藍色路徑 | 导航 / 回家 / 蓝色路线 | — | car | H | same | keep "HOME" Latin in both if TW does |
| valet | 代客泊車 / 泊車員 | 代客泊车 / 泊车员 | — | car | H | CSLD 代客泊車[臺]; same chars, used in CN | |
| garage (parking; P4) | 停車場 / 停車塔 | 停车场 / 车库 | — | car | H | same | "four levels under the street" → 地下四层 (CN) vs 地下四樓 (TW): 樓→层 M |
| spiral ramp / ramps | 螺旋坡道 / 坡道 | 螺旋坡道 / 坡道 | — | car | H | same | |
| ticket arm / garage arm | 柵欄 / 閘門 / 擋車桿 | 道闸 / 挡车杆 | 栅栏 (CN = fence) | car | M | OCC unchanged; CSLD 柵欄 = fence on both sides; CORPUS | |
| toll / toll booth | 過路費(通行費) / 收費站 | 过路费(通行费) / 收费站 | — | car | H | same | |
| freeway ("Stemmons", "the Carpenter Freeway") | 高速公路 | 高速公路 (高速) | — | car | H | CSLD 高速公路 陸⃝簡稱「高速」 | |
| interchange / exit | 交流道 / 出口 | 立交 / 互通 / 出口 | 交流道 | car | H | CSLD 交流道[臺] 陸⃝即「匝道」; OCC unchanged | |
| ramp (on/off) | 匝道 | 匝道 | — | car | H | same | |
| lane | 車道 | 车道 | — | car | H | same | |
| accelerator / brake / horn | 油門 / 煞車 / 喇叭 | 油门 / 刹车 / 喇叭 | 煞车 (OCC residue) | car | H | OCC 煞車 unchanged ✗; MW 煞車→刹车; CSLD 煞車 也作「剎車」 | |
| brake lights | 煞車燈 | 刹车灯 | 煞车灯 | car | H | OCC unchanged | |
| trunk ("You fit the suitcase in the back") | 後車廂 | 后备箱 | 后车厢 | car | H | CSLD 後車廂 陸⃝也作「後備廂」; OCC unchanged | |
| car (colloquial) | 車子 | 车 / 车子 | — | car | M | same; 车子 is fine but less frequent in CN | |
| hazard lights ("with its hazards on") | 雙黃燈 / 警示燈 | 双闪 | 双黄灯 | car | H | OCC unchanged; CORPUS | |
| turn signal | 方向燈 | 转向灯 | 方向灯 | car | H | OCC unchanged; CORPUS | |
| heat (car: "You turn on the heat") | 暖氣 | 暖风 (暖气 ok) | — | car | M | CSLD 暖氣機→暖風機 | house heating "heat on" = 暖气 both |
| air-conditioning | 冷氣 | 空调 | 冷气 (CN = cold air) | car | H | CSLD 空調 vs 冷氣 (臺); CORPUS | |
| dashboard ("The dashboard says 11:31") | 儀表板 | 仪表盘 | 仪表板 | car | M | OCC unchanged; CORPUS | |
| hood ("sit on the hood of the car") | 引擎蓋 | 引擎盖 / 发动机盖 | — | car | H | same | |
| minivan / sedan | 休旅車(廂型車) / 轎車 | MPV / 商务车 / 轿车 | 休旅车 | car | M | OCC unchanged; CORPUS | |
| windshield / wipers / plate | 擋風玻璃 / 雨刷 / 車牌 | 挡风玻璃 / 雨刮器 / 车牌 | — | car | H | same; CORPUS | |
| car service ("Her car service gave up") | 接送服務 / 車行 | 专车 / 接机服务 / 约好的车 | — | car | M | CORPUS | |
| book a car / "a car booked" | 訂車 / 預約車 | 约车 / 订车 | — | car | H | same | |
| give someone a ride ("gave a colleague a ride") | 載一程 / 載 | 送一程 / 捎 / 载一程 | — | car | M | same | |
| levee / floodway | 堤防 / 洩洪道 | 堤坝(河堤) / 泄洪道 | — | car | M | OCC 泄洪道; CORPUS | |
| curb ("stops itself at the hotel's curb") | 路邊 | 路边 | — | car | H | same | |
| tires / the hum of the freeway | 輪胎 / 高速公路的嗡嗡聲 | 轮胎 / 高速公路的嗡嗡声 | — | car | H | same | |
| lower the window | 搖下車窗 | 摇下车窗 | — | car | H | same | |
| train (DART light rail on Pacific) | 輕軌列車 / 列車 / 捷運 | 轻轨列车 / 列车 / 地铁 | 捷运 | car | H | CSLD 捷運[臺]; OCC unchanged | two cars = 兩節車廂 / 两节车厢 |
| platform | 月台 | 站台 | 月台 | car | H | OCC unchanged; CORPUS | not in story |

### a.4 Office and finance

| en | tw | hans | forbidden | cat | conf | evidence | notes |
|---|---|---|---|---|---|---|---|
| company / office / "the forty-first floor" | 公司 / 辦公室 / 四十一樓 | 公司 / 办公室 / 四十一楼(层) | — | off | H | same | |
| manager ("Dana, who runs your group") | 主管 / 組長 | 主管 / 上司 / 组长 | 领导 is CN-only flavour, do not add | off | H | same | |
| project | 專案 | 项目 | 专案 (CN = special case) | off | H | OCC 專案→项目; CSLD 專案 臺⃝ research-project sense | |
| presentation ("The presentation has a hole in it"; "I present at nine") | 簡報 | 汇报 / 演示 / 报告 | 简报 (CN = briefing/bulletin); 演示文稿 (OCC output = the PPT file) | off | H | OCC 簡報→演示文稿; CSLD 簡報 = brief report | |
| slide ("a slide titled *What we learned*") | 投影片 | 幻灯片 | 投视频 (OCC bug) | off | H | OCC 投影片→投视频; CSLD 幻燈片 | |
| meeting / meetings | 會議 | 会议 | — | off | H | same | |
| review council | 審查委員會 / 評審委員會 | 评审委员会 / 审议委员会 | — | off | M | OCC same chars; CORPUS | |
| group / team | 小組 / 團隊 | 组 / 团队 | — | off | H | same | |
| documents ("a name at the top of documents") | 文件 | 文件 | — | off | H | same | |
| badge / badge in ("You badge in."; "the garage arm lifts for your badge") | 識別證 / 門禁卡 ; 刷卡進入 | 工牌 / 门禁卡 ; 刷工牌(刷卡)进门 | 识别证 | off | H | OCC unchanged; CORPUS | |
| swipe card | 刷卡 | 刷卡 | — | off | H | same | |
| company card ("you hand over the company card") | 公司卡 / 公司信用卡 | 公司卡 / 公务卡 | — | off | M | same | |
| configuration file / one line / fourteen sixes | 設定檔 / 一行 / 十四個六 | 配置文件 / 一行 / 十四个六 | 设置档 | off | H | OCC | |
| retrain / check the features / data twice | 重新訓練 / 檢查特徵 / 資料 | 重新训练 / 检查特征 / 数据 | — | off | H | OCC | |
| rush hour ("since Sunday it looks like rush hour") | 尖峰時間(時段) | 高峰时段 / 早晚高峰 | 尖峰时间 | off | H | OCC unchanged; CORPUS | |
| move money / transfers | 轉帳 / 匯款 | 转账 / 汇款 | 转帐 | fin | H | OCC 帐 residue | |
| evaluation ("Dana said evaluation") | 評估 | 评估 | — | off | H | same | |
| cleaning crews | 清潔人員 | 保洁员 / 清洁工 | — | off | M | CSLD 保潔[陸]; OCC unchanged | |
| security guard / lobby guard | 保全 / 警衛 | 保安 | 保全 (CN = equipment maintenance) | off | H | CSLD 保全 臺⃝…陸⃝即「保安」「保安員」 | |
| tenants / rents the smallest room | 租戶 / 租 | 租户 / 租 | — | off | H | same | |
| staff door / "no number" | 員工專用 / 沒有門牌 | 员工专用 / 没有门牌 | — | off | H | same | |
| motion sensors / the lights go to sleep | 感應器 / 感應燈 | 感应器 / 感应灯 | — | off | M | see a.1 | |

### a.5 Hotel and food

| en | tw | hans | forbidden | cat | conf | evidence | notes |
|---|---|---|---|---|---|---|---|
| hotel ("the hotel on Elm") | 飯店 | 酒店 | 饭店 (CN reads as restaurant) | hot | H | OCC unchanged; CORPUS | |
| lobby | 大廳 | 大厅 | — | hot | H | same | |
| bellman | 行李員 | 行李员 / 门童 | — | hot | M | same | |
| front desk ("Her bag is already at the front desk") | 櫃檯 | 前台 | 柜台 (OCC output; CN = shop counter) | hot | H | OCC 櫃檯→柜台; CORPUS | |
| host (restaurant) | 領檯 / 帶位 | 领位员 / 迎宾 | 领台 (OCC output) | hot | H | OCC 領檯→领台; CORPUS | |
| waiter | 服務生 | 服务员 | 服务生 (understood, TW-flavoured) | hot | H | OCC unchanged; CORPUS | |
| the check / bill | 帳單 | 账单 | 帐单 (OCC ✗) | hot | H | OCC; MW 帳單→账单 | |
| pay / settle ("The check comes") | 買單 / 結帳 | 买单 / 结账 | 结帐 (OCC ✗) | hot | H | OCC 結帳→结帐 | |
| vending machines | 自動販賣機 | 自动售货机 | 自动贩卖机 | hot | H | CSLD 自動販賣機 陸⃝也作「自動售貨機」; OCC unchanged | |
| can ("the orange can") | 鋁罐 / 易開罐 | 易拉罐 | 易开罐 | hot | H | CSLD 易開罐[臺] 陸⃝即「易拉罐」 | |
| orange (colour) | 橘色 | 橙色 (橘色 acceptable) | — | hot | M | OCC unchanged; CORPUS | |
| energy drink / Ultra Sunrise | 能量飲料 / Ultra Sunrise | 能量饮料(功能饮料) / Ultra Sunrise | — | hot | H | same; keep brand Latin | |
| pretzels ("nothing but pretzels since somewhere over Ireland") | 椒鹽捲餅 / 蝴蝶餅 | 椒盐卷饼 / 椒盐脆饼 | — | hot | M | OCC 椒盐卷饼; CORPUS | |
| bread / dessert | 麵包 / 甜點 | 面包 / 甜点(甜品) | — | hot | H | OCC | |
| cheese | 起司 | 奶酪 | 起司 | hot | H | CSLD 起司 也作「奶酪」「芝士」; OCC unchanged | not in story |
| coffee / bad coffee | 咖啡 / 難喝的咖啡 | 咖啡 / 难喝的咖啡 | — | hot | H | same | |
| convenience store | 便利商店 / 超商 | 便利店 | 便利商店 / 超商 | hot | H | OCC unchanged; CORPUS | not in story |
| butter / cream | 奶油 / 鮮奶油 | 黄油 / 奶油 | 奶油 for butter (CN 奶油 = cream) | hot | H | CSLD 奶油 = butter sense; CORPUS CN 黄油 | not in story; classic trap |
| restaurant at the top / "terribly fancy" | 頂樓餐廳 / 非常高級 | 顶层餐厅 / 特别高档 | — | hot | H | same | |
| menu / tablecloth / linen / glass | 菜單 / 桌布 / 亞麻 / 酒杯 | 菜单 / 桌布 / 亚麻 / 酒杯 | — | hot | H | same | |
| revolving doors / marble / mirrored elevator | 旋轉門 / 大理石 / 鏡面電梯 | 旋转门 / 大理石 / 镜面电梯 | — | hot | H | same | |
| nightstand / curtains / bed still made | 床頭櫃 / 窗簾 / 床沒動過 | 床头柜 / 窗帘 / 床没动过 | — | hot | H | OCC 窗帘 | |
| phone face down / "at two percent" | 螢幕朝下 / 剩百分之二 | 屏幕朝下 / 只剩百分之二 | 萤幕 | hot | H | OCC | |
| laundry ("I did laundry") | 洗衣服 | 洗衣服 | — | hot | H | same | |

### a.6 Weather and units

| en | tw | hans | forbidden | cat | conf | evidence | notes |
|---|---|---|---|---|---|---|---|
| north wind / "the first norther of the year" | 北風 / 入秋第一道冷鋒(北風) | 北风 / 入秋第一股寒潮(冷空气) | — | wx | M | same chars; CORPUS | "norther" has no fixed term either side |
| cold snap | 寒流 | 寒潮 (寒流 ok) | — | wx | M | OCC unchanged; CORPUS (CN meteorology 寒潮) | |
| cold front / flags point south | 冷鋒 / 旗子指向南方 | 冷锋 / 旗子指向南方 | — | wx | H | same | |
| Fahrenheit / Celsius ("seventy-one degrees", "79, 71, 64, 57", "Fifty-five degrees") | 華氏 / 攝氏 | 华氏 / 摄氏 | — | wx | H | same | keep Fahrenheit in both editions or convert in both; never diverge |
| feet ("three thousand feet", "forty feet") | 呎 / 英呎 / 英尺 | 英尺 | 呎 / 英呎 | unit | H | OCC unchanged; CORPUS | |
| miles ("a hundred and fifty miles") | 哩 / 英里 | 英里 | 哩 | unit | H | CSLD 哩 臺⃝ 陸⃝即「英里」 | |
| yards ("two hundred yards") | 碼 | 码 | — | unit | H | same | |
| inches | 吋 / 英吋 | 英寸 | 吋 | unit | H | OCC unchanged; CORPUS | |
| pounds / kilometres / degrees | 磅 / 公里 / 度 | 磅 / 公里 / 度 | — | unit | H | same | |
| metres / centimetres | 公尺 / 公分 | 米 / 厘米 | 公尺 / 公分 | unit | H | MW 公尺→米; CSLD 公尺 也作「米」 | |
| dollars ("Two dollars", "Nine dollars", "Thirty dollars") | 美元 / 美金 / 塊 | 美元 / 块 | 美金 | unit | H | OCC unchanged; CORPUS | |
| watts ("790 W") | 瓦 | 瓦 | — | unit | H | same | |
| kelvin ("290 K", "0.003 K") | 克耳文 / K | 开尔文 / K | 克耳文 | unit | H | OCC unchanged; CORPUS (GB 3100 SI unit name 开尔文) | keep "K" and the trap vanishes |
| nickel (sky "the color of a nickel") | 鎳幣的顏色 / 五分硬幣 | 镍币的颜色 | — | wx | L | CORPUS | |
| a billion and change / ten trillion years | 十億多 / 十兆年 | 十亿多 / 十万亿年 | 兆 (CN 兆 = mega/10^6 in SI contexts; 万亿 is 10^12) | unit | H | CORPUS (GB 3102: 兆 = 10^6; TW 兆 = 10^12) | "ten trillion years" = 1e13 → TW 十兆年, CN 十万亿年. Real trap. |

### a.7 Physics (KELVIN, BKT, the log)

| en | tw | hans | forbidden | cat | conf | evidence | notes |
|---|---|---|---|---|---|---|---|
| kelvin (unit) / Lord Kelvin | 克耳文 | 开尔文 | 克耳文 | phys | H | OCC unchanged; XH-P "Kelvin (英) 凯尔文" is the generic person form; CORPUS: Lord Kelvin & the unit = 开尔文 by convention | door label "KELVIN" stays Latin in both |
| vortex / vortex pair ("knots … only in pairs") | 渦旋 / 渦旋對 | 涡旋 / 涡旋对 | — | phys | H | same | |
| pinning ("pin E/1931") | 釘扎 | 钉扎 | — | phys | H | same | |
| renormalization / "level six, very coarse" | 重整化 / 第六層 | 重正化 / 第六层 | 重整化 | phys | H | OCC unchanged; CORPUS (全国科技名词 重正化 vs NAER 重整化) | |
| silicon | 矽 | 硅 | 矽 | phys | H | OCC; CSLD | |
| helium / thin films of helium | 氦 / 氦薄膜 | 氦 / 氦薄膜 | — | phys | H | same | |
| superconductor / arrays of superconductors | 超導體 / 超導體陣列 | 超导体 / 超导体阵列 | 超导体数组 (OCC ✗) | phys | H | OCC | |
| lattice / phase transition / temperature / entropy | 晶格 / 相變 / 溫度 / 熵 | 晶格 / 相变 / 温度 / 熵 | — | phys | H | same | |
| noise / signal / frequency / shielding | 雜訊 / 訊號 / 頻率 / 屏蔽 | 噪声 / 信号 / 频率 / 屏蔽 | 杂讯 / 讯号 | phys | H | see a.1 | |
| nucleation ("nucleate … certified") / annihilation | 成核 / 湮滅 | 成核 / 湮灭 | — | phys | H | same | |
| red dwarf / star / galaxy / planet / sun | 紅矮星 / 恆星 / 星系 / 行星 / 太陽 | 红矮星 / 恒星 / 星系 / 行星 / 太阳 | — | phys | H | same | |
| mass ("mass 0.08 sun") | 質量 | 质量 | — | phys | H | CSLD 質量 physics sense shared | the same characters mean "quality" in CN prose — see §e |
| compass needle / "which way it's pointing" | 指南針的針 / 羅盤針 | 指南针 / 罗盘指针 | — | phys | H | same | |
| per unit area / free knots | 單位面積 / 自由渦旋(自由結) | 单位面积 / 自由涡旋 | — | phys | H | same | |
| XY model / spin | XY模型 / 自旋 | XY模型 / 自旋 | — | phys | H | same | |
| critical point / "just inside the edge" | 臨界點 / 剛好在邊緣內側 | 临界点 / 刚好在边缘内侧 | — | phys | H | same | |
| wake-sleep / "it dreams" | 清醒—睡眠 / 作夢 | 清醒—睡眠 / 做梦 | 作梦 (TW spelling) | phys | M | CORPUS (CN standard 做梦) | OCC does not normalise 作夢→做梦: check |
| Kosterlitz–Thouless–Berezinskii | see §c | | | | | | |

### a.8 Everyday (time, city, body, objects)

| en | tw | hans | forbidden | cat | conf | evidence | notes |
|---|---|---|---|---|---|---|---|
| week / a week / Tuesday / the odd week | 週 / 一週 / 週二(星期二) / 奇數週 | 周 / 一周 / 周二(星期二) / 单周 | 礼拜 is colloquial both sides | day | H | OCC 週→周; CSLD 一週 | 禮拜二 → 周二/星期二 in narration |
| what time / minutes / "a quarter past" | 幾點 / 分鐘 / 一刻 | 几点 / 分钟 / 一刻 | — | day | H | OCC | |
| taxi | 計程車 | 出租车 | 计程车 | day | H | OCC 出租车; CSLD 陸⃝也作「的士」 | |
| bus | 公車 | 公交车 | 公车 (CN = company car) | day | H | CSLD 公車 臺⃝/陸⃝ senses differ (同名異實 list); OCC unchanged | "the bus runs outside security" |
| metro / light rail | 捷運 | 地铁 / 轻轨 | 捷运 | day | H | CSLD 捷運[臺] | |
| motorcycle | 機車 | 摩托车 | 机车 (CN = locomotive) | day | H | CSLD 機車 臺⃝…陸⃝即「摩托車」 | not in story |
| bicycle | 腳踏車 | 自行车 | 脚踏车 | day | H | OCC; CSLD | |
| AC / space heater | 冷氣 / 電暖器 | 空调 / 电暖器(取暖器) | 冷气 | day | H | see a.3 | |
| security guard / lobby guard | 保全 / 警衛 | 保安 | 保全 | day | H | CSLD | |
| building / floor / elevator | 大樓 / 樓層 / 電梯 | 大楼 / 楼层 / 电梯 | — | day | H | same | |
| escalator | 手扶梯 / 電扶梯 | 自动扶梯 / 扶梯 | 手扶梯 | day | H | CSLD 手扶梯 (臺灣特有) 也作「自動扶梯」 | |
| curtains / suitcase / wheel | 窗簾 / 行李箱 / 輪子 | 窗帘 / 行李箱 / 轮子 | — | day | H | OCC | |
| coat / jacket / scarf / wool coat | 大衣 / 外套(夾克) / 圍巾 / 羊毛大衣 | 大衣 / 外套(夹克) / 围巾 / 羊毛大衣 | — | day | H | same | |
| phone / signal / call / reply | 手機 / 訊號 / 打電話 / 回覆 | 手机 / 信号 / 打电话 / 回复 | 讯号 | day | H | OCC | |
| through/via ("It reaches you through her") | 透過 | 通过 | 透过 only for physical "light through" | day | H | CSLD 透過 臺⃝介詞 陸⃝即「通過」; OCC unchanged | |
| quality | 品質 | 质量 (品质 acceptable) | — | day | H | CSLD 品質 陸⃝也作「質量」 | |
| level / standard | 水準 | 水平 | 水准 (understood, rarer) | day | H | CSLD 水準 也作「水平」; OCC unchanged | |
| local / relatively / a bit | 當地(本地) / 比較 / 一下 | 当地(本地) / 比较 / 一下 | — | day | H | same | |
| quite ("蠻/滿") | 蠻好 / 滿好 | 挺好 / 很好 | 蛮 / 满 | reg | H | CSLD 蠻 has no adverb sense (TW colloquial), 挺 has "程度較高" sense; OCC unchanged | see §e |
| plastic / plastic sleeve | 塑膠 / 塑膠套 | 塑料 / 塑料套 | 塑胶 | day | H | OCC; CSLD 塑膠 陸⃝即「塑料」 | |
| give blood ("the needle when you give blood") | 捐血 | 献血 | 捐血 | day | H | CSLD 捐血 陸⃝也作「獻血」; OCC unchanged | |
| shop grilles ("pulling down their grilles") | 鐵捲門 | 卷帘门 | 铁卷门 | day | H | OCC unchanged; CORPUS | |
| terrazzo | 磨石子(地) | 水磨石 | 磨石子 | day | H | OCC unchanged; CORPUS | |
| frosted doors / frosted glass | 霧面玻璃門 / 毛玻璃 | 磨砂玻璃门 (毛玻璃 ok) | 雾面玻璃 | day | H | OCC unchanged; CORPUS | |
| fence (airport perimeter) | 圍籬 | 围栏 / 围墙 | 围篱 | day | M | OCC unchanged; CORPUS | |
| convention center | 會議中心 | 会展中心 / 会议中心 | — | day | M | CORPUS | |
| observation plaza | 觀景台 / 觀機平台 | 观景台 / 观景平台 | — | day | H | same | |
| porch / stadium / levee | 門廊 / 體育場(球場) / 堤防 | 门廊 / 体育场(球场) / 堤坝 | — | day | H | same | |
| tunnels under downtown / bricked up | 地下通道(地下街) / 砌起來 | 地下通道 / 砌起来 | — | day | H | same | |
| fluorescent tubes that hum | 日光燈管 | 日光灯管(荧光灯管) | — | day | H | same | |
| bread box / folding table / space heater / sheet of paper taped | 麵包箱 / 折疊桌 / 電暖器 / 貼著一張紙 | 面包箱 / 折叠桌 / 电暖器 / 贴着一张纸 | — | day | H | OCC | |
| vacuum / gym / shower | 吸塵器 / 健身房 / 洗澡(淋浴) | 吸尘器 / 健身房 / 洗澡(淋浴) | — | day | H | same | |
| balloon / glitter sign / grocery-store flowers / plastic sleeve | 氣球 / 亮粉標語 / 超市買的花 / 塑膠套 | 气球 / 闪粉标语 / 超市买的花 / 塑料套 | — | day | M | OCC 塑料 | |
| handshake "of exactly the right length" | 握手 | 握手 | — | day | H | same | |
| piano / siren / neon / derrick / Pegasus | 鋼琴 / 警笛 / 霓虹 / 井架 / 飛馬 | 钢琴 / 警笛 / 霓虹 / 井架 / 飞马 | — | day | H | same | |
| oil company / "the tallest thing in town" | 石油公司 / 全城最高 | 石油公司 / 全城最高 | — | day | H | same | |
| shed ("found the original in a shed") | 倉庫 / 棚子 | 仓库 / 棚子 | — | day | H | same | |
| two fingers lifted / "Night, son." / "Night, Dad." | 舉起兩根手指 / 晚安，兒子。/ 晚安，爸。 | 举起两根手指 / 晚安，儿子。/ 晚安，爸。 | — | day | H | same | |
| "Hey Grok" / Grok | 嘿，Grok | 嘿，Grok | — | day | H | keep Latin both | |
| dreams / "does it dream" | 作夢 / 夢 | 做梦 / 梦 | 作梦 | day | M | CORPUS (CN 做梦) | |
| sign ("It's a sign.") | 牌子 / 接機牌 | 牌子 / 接机牌 | — | day | H | same | |
| phone note app ("open a blank note") | 備忘錄 / 記事本 | 备忘录 | — | day | H | same | |
| speakers (observation plaza) | 擴音器 / 喇叭 | 扬声器 / 喇叭 | — | day | H | same | |

---

## (b) Punctuation TW → CN for a novel

Evidence base: CLREQ (`w3c/clreq`, which states its punctuation section "is mainly based on … GB/T 15834—2011 … as well as the Punctuation Guidance (2008 revised edition) issued by the Ministry of Education in Taiwan"), GB/T 15834-2011 clauses as cited in `mizzlelover/biaodian` (`references/confusable-pairs.md`), and the two web style guides for what NOT to carry into print. OpenCC touches none of this: `tw2sp` output kept 「」, 《》 and spacing unchanged in every test.

| item | TW form (as a Taiwan writer types it) | CN form to print | rule / evidence | conf |
|---|---|---|---|---|
| quotation marks | 「…」 outer, 『…』 inner | “…” outer, ‘…’ inner | GB/T 15834 §4.8 (引号 forms “ ” ‘ ’); CLREQ: mainland "引号（横排使用弯引号，直排使用直角引号）", i.e. 「」 is reserved for vertical setting on the mainland | H |
| nesting | 「…『…』…」 | “…‘…’…” | nesting order inverts with the glyph swap; a regex that maps 「→“ 」→” 『→‘ 』→’ is sufficient (OpenCC will not do it) | H |
| dash 破折號 | ——, but TW manuscripts frequently carry ──(U+2500×2), — (single U+2014), or –(U+2013) | —— (two U+2014; CLREQ recommends U+2E3A ⸺ but notes two U+2014 are what is used; occupies two character cells, never broken across lines) | CLREQ 破折号; GB/T 15834 §4.10 | H (form) / M (TW habit) |
| ellipsis 刪節號/省略号 | ……, but TW manuscripts also carry ⋯⋯ (U+22EF×2), … (single), or "..." | …… (two U+2026, six dots, two cells, not broken across lines) | CLREQ 省略号; GB/T 15834 §4.11; `sparanoid … discussions/218` documents the TW ⋯⋯ habit | H |
| the story's own "…" inside log rows (ckpt 2c71…, "03:11:59.999999…") | keep single U+2026 inside code blocks | same — code blocks are not prose | both editions must agree; CN prose rule does not apply inside monospace blocks | H |
| full-width ，。、；： | identical characters | identical | TW sets them centred in the em box, CN at the lower-left; CLREQ: "港台的標點多位於字面正中；中國大陸的標點多位於…末端" — this is a font/typesetting difference, not a text change | H |
| enumeration comma 、 | used | used | GB/T 15834 §4.4; `ruanyf` marks.md "并列词…用全角顿号" | H |
| 《》 book-title marks | 《》 (and 〈〉 for 篇名) | 《》 (〈〉 inside 《》 only) | GB/T 15834 §4.15 (quoted in biaodian §13: 书名号 for 书、篇、刊、影视、音乐、软件 names; 活动/课程/主题 take 引号) | H |
| "a slide titled *What we learned*" | 題為「我們學到了什麼」的投影片 (TW uses 「」) | 题为“我们学到了什么”的幻灯片 — 引号, not 书名号 (a slide title is a 主题) | biaodian §13 "题是作品名→书名号；题是主题→引号" | M |
| 着重号 (emphasis dots) | not in the TW handbook; TW emphasis is 「」, 楷體/黑體, or nothing | GB/T 15834 §4.12 着重号 exists and is normal in mainland fiction for spoken stress; CLREQ: dots under characters in horizontal text | For the source's italics: *heavy*, *On it*, *is*, the screen captions *Quiet. Frontier 0. Idle 790 W.* — recommend 楷体 for machine captions and screen text in both editions, 着重号 (CN) / 「」 (TW) only for spoken stress ("Why *is* that worth pointing at?") | M |
| sentence-final mark vs closing quote | 「……。」 when the quotation is a complete sentence; 「……」他說。 when the carrier continues | “……。” / “……”他说。 — identical rule | GB/T 15834 B.2.1 (引文完整独立→句末点号在引号内；引文为句子成分→引号外); biaodian table "“我真的很期待。”他说。" | H — only the glyphs change, never the position |
| dialogue colon | 他說：「…」 | 他说：“…” | GB/T 15834 §4.5 (冒号 before quoted speech) | H |
| 間隔號 in foreign names (艾丽斯·雷恩) | TW types ‧ (U+2027), ・ (U+30FB) or ． (U+FF0E) | · U+00B7 only | GB/T 15834 §4.14 间隔号; `ethantw/Han` issue #43 notes the national standard treats it as a half-width mark | H |
| numerals | TW literary print mostly Chinese numerals; some houses allow Arabic for clock times; full-width digits (６：５２) still occur | half-width Arabic digits always (GB/T 15835-2011; `ruanyf` number.md "阿拉伯数字一律使用半角形式"); Chinese numerals for 概数 (三四個→三四个), idioms, and in dialogue if the TW text uses them | GB/T 15835-2011 §4–5 (not fetched; cited from memory — M); ruanyf STYLE | M |
| clock times in narration ("At 6:52 you find it", "11:31", "4:31") | 六點五十二分 or 6:52 | 6点52分 / 六点五十二分 — follow whatever the TW edition chose, but normalise the colon to ASCII ":" and digits to half-width | GB/T 15835 allows both; consistency is the rule | M |
| ranges / log rows ("18:30–19:00", "10-27", "27L", "+89 min") | ASCII in code blocks | ASCII in code blocks; in prose CN uses 一字线 — (U+2014) for ranges (北京—上海) and 波浪线 ～ for numeric ranges (ruanyf number.md) | GB/T 15834 §4.13 连接号 | M |
| space between CJK and Latin/digits | TW web guides (sparanoid) insist on a U+0020 space; TW print does not | CN web guides (ruanyf text.md "全角中文字符与半角英文字符之间，应有一个半角空格") insist on it; CN print does not. CLREQ: "汉字与西文字母、阿拉伯数字间使用不多于四分之一个汉字宽的字距或空白" — a typesetter's gap, not a character | Recommendation: strip U+0020 between CJK and Latin/digits in prose in BOTH editions before typesetting; keep inside code blocks. | H |
| parentheses | （） | （） | identical | H |
| italic text-message block (Dana's text) | layout | layout | identical | H |
| 專名號 (proper-noun underline) | listed in TW handbook, unused in modern print | GB/T 15834 §4.16 reserves it for 古籍 | do not introduce | H |

One further scripted check: TW manuscripts sometimes carry U+FF5E "～" and U+FF0D "－" where CN wants ～ (U+FF5E is fine) and "—"; and the TW 連接號 "－" between numbers (6－9) should become "—" or "～".

---

## (c) Name forms (新华社 standard beside the Taiwan form)

Sources: **XH-P** = 《世界人名翻译大辞典》, **XH-G** = 《世界地名翻译大辞典》 (both 新华社译名室; Excel backups in `karedoea/Global-name-translation`, looked up on 2026-10-06); TW forms from CNA/LTN/NTU usage and the 兩岸 corpus; zh.wikipedia itself was unreachable, so where I cite a zhwiki title it is from a search snippet of a mirror and marked M.

| en | tw (zh-Hant-TW) | hans (to print) | evidence | conf | notes |
|---|---|---|---|---|---|
| Iris (woman) | 艾瑞絲 (TW literary practice, e.g. 艾瑞絲·梅鐸 for Iris Murdoch) | **艾丽斯** (XH-P: "Iris (英) 艾里斯;艾丽斯 (女名)" — the (女名) form); mainland literary houses also use 艾丽丝 (艾丽丝·默多克) | XH-P row verbatim; WEB snippet for 艾丽丝·默多克 / 艾瑞絲 | H (艾丽斯 is the standard; 艾丽丝 is tolerated usage) | the character's surname follows: 艾丽斯·雷恩 |
| Wren | 雷恩 | **雷恩** (XH-P: "Wren (英) 雷恩") | XH-P; Christopher Wren = 克里斯托弗·雷恩 (CN) / 克里斯多佛·雷恩 (TW) | H | identical both sides |
| Dana (woman) | 黛娜 (TW practice; 丹娜 also seen) | **达娜** (XH-P: "Dana (英…) 达娜(女名);达纳") | XH-P verbatim; WEB snippets show 黛娜·史卡莉 (TW) vs 丹娜·斯卡莉 (CN fan usage) for Dana Scully | H | do not use 达纳 (male/generic) for her |
| Kelvin (Lord Kelvin, "a man who thought atoms were knots in a fluid") | 克耳文 (克耳文男爵; NAER unit name 克耳文) | **开尔文** (开尔文勋爵; the unit 开尔文) | XH-P gives "Kelvin (英) 凯尔文" for ordinary people; Lord Kelvin and the SI unit are 约定俗成 开尔文 (GB 3100 unit names) — CORPUS | H for 开尔文 as person+unit; the label "KELVIN" stays Latin | if the TW edition romanises the door label, both editions should keep KELVIN in Latin |
| Kosterlitz | 科斯特利茲 (CNA 2016) / 柯斯特利茲 (other TW press) / 科斯特利茨 (NTU thesis) | **科斯特利茨** (XH-P: "Kosterlitz (德) 科斯特利茨"; mainland 2016 Nobel coverage 迈克尔·科斯特利茨) | XH-P; WEB cna.com.tw/news/firstnews/201610040413.aspx; WEB thepaper.cn/newsDetail_forward_1538583 (snippet); WEB tdr.lib.ntu.edu.tw/handle/123456789/60716 | H | |
| Thouless | 杜列斯 (CNA 2016; zh-tw wiki title 大衛·杜列斯) / 索利斯 (NTU thesis) | **索利斯** (XH-P: "Thouless (英) 索利斯"; 大卫·索利斯 in mainland coverage) | XH-P; CNA; thepaper snippet; NTU thesis | H | TW form is unsettled — flag to the TW lane |
| Berezinskii | 別列津斯基 (NTU thesis "別列津斯基-科斯特利茨-索利斯相變"); 貝瑞津斯基 also seen in TW popular science (L) | **别列津斯基** (XH-P Russian entries: "Berezinski (俄) 别列津斯基", "Berezinskiy (俄) 别列津斯基") | XH-P; NTU thesis | H | mainland physics prose also writes BKT相变; recommend 别列津斯基—科斯特利茨—索利斯 on first mention, BKT after |
| Dallas | 達拉斯 | **达拉斯** (XH-G "Dallas (加、美、英) 达拉斯") | XH-G | H | identical |
| Fort Worth | 沃斯堡 (TW press); 福和 (Taiwanese community in DFW) | **沃思堡** (XH-G "Fort Worth (美) 沃思堡") | XH-G; WEB snippets show both 沃思堡/沃斯堡 in circulation | H | the highway-sign row "FORT WORTH a word on a sign" is best left in Latin in both editions |
| Irving | 歐文 | **欧文** (XH-G "Irving (美) 欧文") | XH-G | H | identical |
| Arlington | 阿靈頓 | **阿灵顿** (XH-G "Arlington (英) 阿灵顿"; "Arlington County (美) 阿灵顿县") | XH-G | H | identical |
| Grapevine | 葡萄藤 (Taiwanese community / commercial usage 葡萄藤市) | **格雷普韦恩** (XH-G "Grapevine (美) 格雷普韦恩") | XH-G; WEB expedia.com/cn "葡萄藤城" shows the commercial calque | H for the standard; M that a mainland editor would accept 葡萄藤 as a literary calque | "coming in over Grapevine" — the standard form is unlovely; moderator may prefer 格雷普韦恩 with no gloss |
| Euless | 尤利斯 | **尤利斯** (XH-G "Euless (美) 尤利斯") | XH-G | H | identical |
| Las Colinas | 拉斯科利納斯 | **拉斯科利纳斯** (XH-G has "Colinas (巴西) 科利纳斯"; Las→拉斯 by the 新华社 rule; cvent.com zh-CN uses 拉斯科利纳斯) | XH-G partial; WEB cvent.com/venues/zh-CN/results/Dallas--Texas--USA/hotel-venues?p=21 | M | |
| Leeds | 里茲 (TW; zh-tw wiki title 里茲市) | **利兹** (XH-G "Leeds (美、英) 利兹") | XH-G; WEB snippet zhwiki.oracleblog.org/wiki/里茲市 | H | real divergence |
| London | 倫敦 | **伦敦** | XH-G | H | identical |
| Heathrow | 希斯洛 (LTN "倫敦希斯洛機場"; CNA 201701120416); 希斯羅 in some TW outlets | **希思罗** (XH-G "Heathrow Airport (英) 希思罗机场"; "London (Heathrow) Airport 伦敦希思罗机场") | XH-G; WEB news.ltn.com.tw/news/world/breakingnews/4987098; cna.com.tw/news/aopl/201701120416.aspx | H | real divergence; tw2sp leaves 希斯洛 |
| Singapore | 新加坡 | **新加坡** | XH-G | H | identical |
| Texas | 德州 / 德克薩斯 | **得克萨斯** (XH-G "Texas, State of (美) 得克萨斯州"); 德州 is tolerated colloquially but editors restore 得克萨斯 | XH-G | H | "It's the end of October in Texas" → 得克萨斯; tw2sp leaves 德克萨斯 |
| Trinity River | 三一河 (semantic; TW usage unverified) / 特里尼蒂河 | **特里尼蒂河** (XH-G "Trinity R. (美) 特里尼蒂河") | XH-G | H (CN) / L (TW) | TW lane to decide 三一河 vs 特里尼蒂河 |
| Love Field | 愛田機場 (zh-wiki title 達拉斯愛田機場; TW usage) | **爱田机场** (established usage; the strict transliteration would be 洛夫菲尔德机场: XH-P "Love (英) 洛夫") | XH-P for 洛夫; WEB snippets for 爱田机场 | M | recommend 爱田机场 (both editions agree, only script differs) |
| Reunion Tower | 重逢塔 (TW) / 團圓塔 | **重逢塔** (ctrip "重逢塔位于美国达拉斯市中心…156米") | WEB gs.ctrip.com/html5/you/sight/Grandview38977/5126224.html | M | |
| Deep Ellum | 深艾倫區 (TW community usage, unverified) | **迪普埃勒姆** by the 新华社 rule (XH-G "Deep … 迪普…" for every Deep- place name; Ellum→埃勒姆) — no attested usage found | XH-G pattern | L | recommend keeping "Deep Ellum" in Latin in both editions, or 迪普埃勒姆区 with no gloss |
| the Metroplex | 大都會區 / 達福都會區 | **达拉斯—沃思堡都会区** (都会区 / 都市圈); in the log row "every aircraft over the Metroplex" → 整个都会区 | CORPUS | M | |
| Stemmons (Freeway) | 史丹蒙斯 / 斯特蒙斯 | **斯特蒙斯高速公路** (by rule; not in XH-P/G) | XH pattern | L | consider keeping "Stemmons" Latin in both |
| Carpenter Freeway | 卡本特高速公路 | **卡彭特高速公路** (XH-P/G "Carpenter 卡彭特") | XH-G "Carpenter (美) 卡彭特" | H | real divergence 卡本特/卡彭特 |
| Bachman Lake | 巴克曼湖 | **巴克曼湖** (XH-P "Bachman (英…) 巴克曼") | XH-P | H | identical |
| Elm Street / Commerce Street / Pacific Avenue | 榆樹街 / 商業街 / 太平洋大道 (semantic, TW literary habit) | strict 新华社: 埃尔姆街 / 科默斯街 / 帕西菲克大道 (XH-G "Elm 埃尔姆", "Commerce (美) 科默斯", "Pacific (美) 帕西菲克"); literary mainland practice: 榆树街 / 商业街 / 太平洋大道 | XH-G | M | recommend the semantic forms in both editions (one decision, both editions), note the strict forms in the TW lane's record |
| International Parkway | 國際公園大道 | 国际大道 / 国际公园大道 | CORPUS | L | |
| Magnolia Building / the red Pegasus | 木蘭大樓 / 紅色飛馬 | 马格诺利亚大楼 (XH-G "Magnolia (美) 马格诺利亚") or 木兰大楼 / 红色飞马 | XH-G | M | |
| the West End / Design District / Mid-Cities | 西區 / 設計區 / 中城區 | 西区 / 设计区 / 中城区 (strict XH-G "West End 韦斯滕德" is for towns named West End, not districts) | XH-G | M | |
| Manhattan / Ireland / the Channel / the Atlantic | 曼哈頓 / 愛爾蘭 / 英吉利海峽 / 大西洋 | 曼哈顿 / 爱尔兰 / 英吉利海峡 / 大西洋 (XH-G) | XH-G | H | identical |
| DART / DFW / LHR / Grok / Ultra Sunrise / KELVIN | Latin | Latin | — | H | keep identical |

Haldane (not in the story) for completeness: TW 哈爾丹 (CNA) / CN 霍尔丹.

---

## (d) OpenCC `tw2sp` residue traps and over-conversions (observed, with guards)

All rows are from the two local runs (pip OpenCC 1.4.2 bundled dictionaries; master `TWPhrases.txt` cloned the same day). "t2s" notes mark traps that only occur if someone runs the plain `t2s`/`t2cn` profile instead of `tw2sp`. The guard column is what the lexicon pass should do after `tw2sp`.

### d.1 One-to-many characters — what tw2sp gets right (no action) and where it fails

| trap | tw2sp result | correct mainland form | guard |
|---|---|---|---|
| 佇列 | 队列 ✓ (t2s gives 伫列 ✗) | 队列 | none for tw2sp; never use t2s |
| 髮/發 | 头发 发型 理发师 发现 ✓ | — | none |
| 乾/幹/干 | 干净 干燥 饼干 干杯 干部 干活 干扰 天干 ✓; 乾坤 乾隆 kept ✓ | — | none |
| 後/后 | 后面 以后 皇后 后羿 ✓ | — | none |
| 鬆/松, 隻/只, 於/于 | ✓ | — | none |
| 瞭解/瞭望 | 了解 ✓, 瞭望 kept ✓, 明了 一目了然 ✓ | — | none |
| 甚麼 | **甚么 ✗** (什麼→什么 ✓) | 什么 | regex 甚么→什么, 甚麼→什么 |
| 麼 | 这么 怎么 要么 多么 ✓ | — | none |
| 著/着 | tw2sp: 看着 著名 着陆 睡着 执着 显著 ✓ (t2s leaves 看著 睡著 ✗) | — | none for tw2sp |
| 裡/里 | 这里 心里 公里 里程 邻里 ✓ | — | none |
| 週/周 | 周末 一周 周期 周二 ✓ | — | none |
| 唸/念 | 念书 念出来 ✓ | — | none |
| 檯/臺/颱/台 | 台灯 柜台 台湾 舞台 台风 塔台 ✓ | — | none; but 櫃檯 (hotel desk) → 前台, see §a |
| 鐘/鍾 | 时钟 钟头 钟爱 一见钟情 ✓; 鍾馗→锺馗 ✓; **姓鍾→姓钟 ✗** | surname 锺 (2013《通用规范汉字表》restores 锺 for the surname) | if a Chinese surname 鍾 occurs → 锺 |
| 覆/復/複 | 回复 答复 覆盖 复原 恢复 复杂 重复 复印 ✓; **複製→拷贝 ✗** | 复制 | regex 拷贝→复制 |
| 回復 (restore) | **回復原狀→回复原状 ✗** | 恢复原状 | 回復 + 原狀/正常/到 → 恢复 |
| 瀋/沈 | 沈阳 ✓; 沈默→沉默 ✓ | — | none |
| 餘/余, 捲/卷, 鬥/斗, 麵/面, 徵/征, 鬱/郁, 籲/吁, 鹹/咸 | all ✓ (泡麵→方便面 also fires) | — | none |
| 繫/係/系 | 联系 关系 系数 系统 系鞋带 ✓ | — | none |
| 準/准, 製/制, 幾/几 | 标准 准备 批准 制造 制度 几点 茶几 ✓; 機率→概率, 幾率→几率 | 概率 preferred | none |
| 計畫/計劃 | both → 计划 ✓ (CSLD: TW splits 計畫 noun / 計劃 verb; CN only 计划) | — | none |
| 影響, 瀏覽, 歷/曆, 蘋, 範, 鬚, 彆, 嚥, 盃, 傢俱, 煙/菸, 讚 | all ✓ (按讚→按赞; CN says 点赞) | — | 按赞→点赞 |
| 牠 / 妳 / 祂 | **unchanged ✗** (牠 牠们 妳 妳们 祂) | 它 / 你 / 他(祂→他 or 上帝) | regex: 牠→它, 妳→你, 祂→他 (whole text; mainland print does not use any of the three) — critical for this story, where a TW translator will write 妳 for Iris throughout |
| 帳 | **帐 everywhere ✗** (帐单 帐户 帐号 转帐 记帐 结帐 对帐单 帐面) | 账单 账户 账号 转账 记账 结账 对账单 账面; keep 帐 only in 帐篷 蚊帐 营帐 | regex 帐→账 except the tent/curtain set |
| 紀錄 | **纪录 ✗** (纪录 纪录档 行车纪录器) | 记录 (纪录 only in 纪录片, 世界纪录) | regex 纪录→记录 except 纪录片/世界纪录/刷新纪录 |
| 作夢 / 作出 | not normalised | 做梦 / 做出 | regex 作梦→做梦 |
| 智慧型手機 | 智能型手机 ✗ | 智能手机 | regex |
| 當機 / 重開機 / 離線 / 存檔 / 捷徑 / 工具列 / 領檯 / 藍芽 / 筆電 / 亂數 / 雜訊 / 雲端運算 / 語音助理 / 識別證 / 束帶 | 当机 / 重开机 / 脱机 / 存盘 / 捷径 / 工具列 / 领台 / 蓝芽 / 笔电 / 乱数 / 杂讯 / 云端运算 / 语音助理 / 识别证 / 束带 — all residues | 死机 / 重启 / 离线 / 保存 / 快捷方式 / 工具栏 / 领位员 / 蓝牙 / 笔记本电脑 / 随机数 / 噪声 / 云计算 / 语音助手 / 工牌 / 扎带 | lexicon rows in §a |

### d.2 Phrase over-conversions (tw2sp fires where it must not)

| TW input | tw2sp output | correct | guard |
|---|---|---|---|
| 核心價值 / 核心問題 / 核心區 / 核心人物 / 核心 (alone) | 内核价值 / 内核问题 / 内核区 / 内核人物 / 内核 ✗ (問題的核心 kept) | 核心… | convert 核心→内核 ONLY after 作業系統/系統/Linux or before 函式/程式/模組; else restore 核心 |
| 法律程序 / 作業程序 / 標準作業程序 / 行程表 | 法律进程 / 作业进程 / 标准作业进程 / 进程表 ✗ | 法律程序 / 作业程序 / 标准作业程序 / 行程表(日程表) | restore 程序 when preceded by 法律/作業/標準/行政/司法/正當; 行程表→日程表 |
| 個人資料 / 資料來源 | 个人数据 / 数据源 ✗ | 个人资料(信息) / 资料来源 | 資料→数据 only in computing/ML collocations (資料庫, 訓練資料, 資料管線, 資料集); else 资料 |
| 人事檔案 / 檔案室 / 存檔 | 人事文件 / 文件室 / 存盘 ✗ | 人事档案 / 档案室 / 保存 | 檔案→文件 only for computer files |
| 這件物件 | 这件对象 ✗ | 这件物件/物品 | 物件→对象 only in 物件導向 / programming |
| 故事設定 / 設定檔 | 故事设置 / 设置档 ✗ | 故事设定 / 配置文件 | 設定檔→配置文件; 設定→设定 in narrative senses |
| 投影片 | **投视频 ✗** (影片→视频 fires inside the word) | 幻灯片 | lexicon row must run BEFORE or override; regex 投视频→幻灯片 |
| 電影影片 / 這部影片 (a film) | 电影视频 / 这部视频 ✗ | 电影 / 这部影片 | 影片→视频 only for online/short video |
| 超導體陣列 / 天線陣列 | 超导体数组 / 天线数组 ✗ | 超导体阵列 / 天线阵列 | 陣列→数组 only in programming |
| 執行計畫 / 執行 (carry out) | 运行计划 ✗ | 执行计划 | 執行→运行 only for programs/進程 |
| 存取 (general "access") | 访问 | 存取/访问 both exist in CN | low priority |
| 排程 ("on the schedule") | 调度 ✗ | 排期 / 日程 | lexicon |
| 簡報 (a presentation) | 演示文稿 ✗ | 汇报 / 演示 | lexicon |
| 複製 | 拷贝 ✗ | 复制 | regex |
| 泡麵 / 機率 | 方便面 / 概率 (fine) | — | none |
| 行動電話 / 行動裝置 / 行動電源 | 移动电话 ✓ / 行动设备 ✗ / 行动电源 ✗ | 手机 / 移动设备 / 充电宝 | 行動 (mobile) → 移动 in device collocations; 行動 (action) stays 行动 |
| 介面 (network/API) | 界面 ✗ | 接口 | 網路介面→网络接口, API 介面→接口 |
| 網路卡 / 網路線 | 网络卡 / 网络线 ✗ | 网卡 / 网线 | lexicon |
| 傳訊息 / 傳簡訊 | 传消息 / 传短信 ✗ (verb left) | 发消息 / 发短信 | lexicon with verb |
| 柵欄 (ticket arm) / 煞車 / 後照鏡 / 雙黃燈 / 冷氣 / 暖氣 (car) | unchanged (栅栏 煞车 后照镜 双黄灯 冷气 暖气) | 道闸 / 刹车 / 后视镜 / 双闪 / 空调 / 暖风 | lexicon (tw2sp has no automotive dictionary) |
| every aviation term in §a.2 | unchanged | §a.2 | lexicon (tw2sp has no aviation dictionary) |
| every unit in §a.6 (呎 哩 吋 公尺 公分 美金 克耳文 兆) | unchanged | §a.6 | lexicon; note 兆 = 10^12 (TW) vs 10^6/万亿 (CN) |

### d.3 Substitutions that must NOT fire inside proper names or quoted labels

Observed: `國立臺灣大學資訊工程學系` → `国立台湾大学信息工程学系` (official name is 資訊工程學系 and a mainland editor keeps 资讯 inside a Taiwan institution's name); `《數位時代》` → `《数字时代》` (the magazine's registered name is 數位時代); `「網路大學」`/`「資訊」`/`「網路」` inside 「」 all converted; `中華電信網路` → `中华电信网络`. The brief's worry about 倫/貞 inside names is not an OpenCC phrase problem: 倫→伦 and 貞→贞 are plain character mappings (艾倫→艾伦, 貞子→贞子, 倫敦→伦敦 all ✓). The real name problems are (1) phrase substitutions inside institution/product names and quoted labels, and (2) the TW-vs-CN transliteration conventions that OpenCC never touches (希斯洛, 里茲, 德克薩斯, 沃斯堡, 卡本特, 艾瑞絲, 黛娜, 杜列斯 all survive tw2sp unchanged — verified).

Guard design (recommended order of operations for the pipeline):

1. **Mask before converting.** Tokenise and protect: everything inside code blocks (the log rows), every string inside 《…》, every all-caps Latin label (KELVIN, HOME, DELAYED, LANDED, AT GATE, IRIS WREN, SKY, ORGAN, WORLD, BADGE), every brand/product (Grok, Ultra Sunrise, DART, DFW, LHR), and a name list exported from the TW lane's name register. Convert the masked text with `tw2sp`, then unmask and apply the §c name table to the names explicitly (the TW form → the 新华社 form), rather than letting character conversion produce a half-converted name.
2. **Lexicon pass with context rules** (§a rows with a `forbidden` entry) — longest match first; the context-sensitive rows (核心, 程序, 資料, 檔案, 物件, 設定, 影片, 陣列, 執行, 行動, 介面) need the collocation guards in d.2 rather than bare word replacement.
3. **Residue regexes** (d.1): 甚么, 拷贝, 投视频, 牠/妳/祂, 帐 (outside 帐篷/蚊帐), 纪录 (outside 纪录片/世界纪录), 作梦, 姓钟, 按赞, 蓝芽, 智能型手机, 内核 followed by 价值/问题/区/人物, 进程 preceded by 法律/作业/标准/行政, 设置档, 这件对象, 回复原状, 传消息, 传短信.
4. **Punctuation normalisation** (§b): 「」『』 → “”‘’; ──/⋯⋯/‧/・/．/full-width digits → ——/……/·/half-width; strip CJK–Latin spaces in prose.
5. **Pin the OpenCC version.** The pip wheel (1.4.2 here) and master `TWPhrases.txt` (824 entries, merged from the three former files; `ver.1.1.9` still ships `TWPhrasesIT.txt` separately) can differ; record the dictionary commit in the build log so the human review is reproducible.

### d.4 Known tw2sp dictionary choices that are wrong or too aggressive for fiction (summary)

複製→拷贝; 程序→进程 (unconditional); 核心→内核 (unconditional); 設定→设置 (unconditional); 檔案→文件 (unconditional); 物件→对象 (unconditional); 影片→视频 (unconditional, breaks 投影片); 陣列→数组 (unconditional); 執行→运行 (unconditional); 存取→访问; 排程→调度; 簡報→演示文稿; 離線→脱机; 存檔→存盘; 行動裝置→行动设备 (half-converted); 智慧型手機→智能型手机 (half-converted); 回復→回复 (loses the restore sense); 帳→帐 (OpenCC's TSCharacters choice; CN finance uses 账); 紀錄→纪录 (TW spelling preserved where CN spells 记录); 甚麼→甚么 (not normalised); 牠/妳/祂 untouched. None of these are bugs from OpenCC's point of view (it is a general-purpose converter), which is exactly why a lexicon pass with context rules is required.

---

## (e) Register: what a mainland literary editor flags in a Taiwanese translation

Evidence: the 兩岸常用詞典 entries quoted (CSLD), the 同名異實 list (words with different meanings on the two sides), and corpus observation for the particles, which the dictionary does not cover (喔/耶/齁 have no sentence-final-particle entries in CSLD; 蠻 has no adverb sense; 不會 has no "you're welcome" sense — those absences are themselves the evidence that these are Taiwan colloquialisms). Conf M unless marked.

| TW usage | what it signals to a mainland editor | recommended mainland equivalent | evidence |
|---|---|---|---|
| sentence-final 喔 ("好喔", "知道了喔") | Taiwan/Hokkien-coloured softener; CSLD lists 喔 only as 擬聲詞 and 嘆詞 (表示了解), not as a final particle | 哦 / 啊, or drop; in this story's dry dialogue, drop | CSLD 喔 entry; CORPUS |
| sentence-final 耶 ("好厲害耶") | pure Taiwan particle; CSLD lists 耶 only as transliteration/文言 particle | 呀 / 诶 / drop | CSLD 耶 entry |
| 啦 | shared (CSLD: 了+啊 合音, both sides) but overused in TW text; fine in CN at low density | keep sparingly | CSLD 啦 |
| 齁 / 吼 ("對齁") | Taiwanese-only tag ("right?") | 是吧 / 对吧 / drop | CORPUS |
| 欸 / 誒 (attention-getter) | TW spelling habit | 哎 / 诶 | CSLD lists 欸 only as a surname (臺) |
| 阿 for 啊 ("好阿") | TW internet spelling | 啊 | CORPUS; mainland copy-editors strike 阿 |
| 蠻 / 滿 + adj ("蠻好的", "滿有趣的") | 蠻 as a degree adverb is Taiwanese colloquial (CSLD gives 蠻 no adverb sense); 蛮 survives in CN only as a regional (吴语) colloquialism; 满 as adverb reads as TW | 挺 (CSLD 挺: "表示程度較高") / 很 / 相当 | CSLD 蠻, 挺 |
| 超 + adj ("超好", "超累") | youth slang both sides, but TW uses it in adult narration | 特别 / 太…了 / 非常; 特 is northern colloquial — avoid in a Dallas narrator's mouth | CSLD 超 (no adverb sense); CORPUS |
| 很棒 / 好棒 | TW praise default; CN reads as cheerful/childish | 真好 / 不错 / 很好 ("Good." in the story → 好/行) | CORPUS |
| 謝啦 | TW casual thanks | 谢了 / 谢谢 | CORPUS |
| 不會 as "you're welcome" ("謝謝" — "不會") | Taiwan calque of Hokkien 袂; CSLD 不會 has only "cannot/won't" senses | 不客气 / 不用谢 / 没事 | CSLD 不會 entry |
| 沒差 | TW "no difference / doesn't matter" | 无所谓 / 没区别 / 都行 | CORPUS |
| 好的 vs 行 | both fine in CN; 行 is the casual mainland "okay"; 好啊/好喔 are TW | 好的 (formal) / 行 (casual) / 好 | CORPUS |
| 的確 vs 確實 | both standard on both sides (CSLD 的確 = 確實) | keep either | CSLD 的確 |
| 一下下 | TW diminutive | 一会儿 / 一下 | CORPUS |
| 車子 | fine both sides; CN narration prefers bare 车 | 车 | CSLD (no flag) |
| 和 pronounced hàn | TW spoken only (CSLD: "臺⃝口語連詞義音ㄏㄢˋ") — no written trace; irrelevant to print | — | CSLD 和 |
| 包含 vs 包括 | both standard; CN lists prefer 包括, TW over-uses 包含 for "including" | 包括 for lists, 包含 for containment | CSLD 包含 (no flag) |
| 質量 | CN: quality (CSLD "陸⃝物品或工作等優劣程度"); TW: mass (physics) or quality-and-quantity. In this story 質量 appears only as physics mass ("mass 0.08 sun") → 质量 is correct in both; but any TW sentence using 品質 for "quality" should become 质量/品质 and never 水準 | 质量 (quality) / 品质 (acceptable) | CSLD 質量, 品質 (同名異實) |
| 水準 | TW "level/standard"; CN reads as slightly dated/Taiwan | 水平 | CSLD 水準 也作「水平」 |
| 土豆 | TW = peanut, CN = potato (CSLD 同名異實) — not in the story; keep out | 花生 / 土豆(马铃薯) | CSLD 土豆 |
| 窩心 | TW = warmed/touched; CN = aggrieved (CSLD 同名異實) — not in the story, but a TW translator could reach for it in VI ("It's warmer than that") → must be 暖心/贴心 in CN | 暖心 / 贴心 | CSLD 窩心 |
| 影響 | identical meaning both sides; no action (listed in the brief; CSLD shows no divergence) | 影响 | CSLD 影響 |
| 透過 (preposition "through/by means of") | CSLD marks the preposition sense 臺⃝, 陸⃝即「通過」; mainland editors change it reflexively | 通过 (keep 透过 only for light/physical passage: "the lights of downtown showing through it" → 透过她的倒影) | CSLD 透過 |
| 公車 / 捷運 / 計程車 / 機車 / 腳踏車 / 保全 / 冷氣 / 便當 / 宵夜 / 奶油 | the ten words that identify a text as Taiwanese at a glance | 公交车 / 地铁 / 出租车 / 摩托车 / 自行车 / 保安 / 空调 / 盒饭 / 夜宵 / 黄油 | CSLD entries quoted in §a |
| 妳 | marks the text as Taiwan/HK at a glance; mainland print uses 你 for both sexes | 你 | OCC leaves 妳 (verified) |
| 牠 (animals) / 祂 (deities) | same; and a TW translator might be tempted to use 牠 for the machine — do not | 它 | OCC leaves 牠/祂 (verified) |
| 您 in a boss's text message | both sides use 您; mainland office register would have Dana write 你 to a subordinate | 你 | CORPUS |
| 「您好」/「不好意思」 as openers | 不好意思 is shared; TW over-uses it for "excuse me/sorry" | 不好意思 / 抱歉 / 对不起 (Iris's "And I'm so sorry." → 真对不起/非常抱歉) | CORPUS |
| 歐巴桑 / 阿嬤 / 阿公 | Taiwan kinship/colloquial — none in the story; the father is 爸/爸爸 both sides | — | CSLD 臺灣特有 lists 阿嬤 |
| classifier 張 for a card | TW 一張顯示卡; CN 一块显卡 | 块 (or 张 — editor's call) | OCC leaves 张 |
| floor counting 四十一樓 | identical; CN also says 41层 for a storey count ("takes you down forty-one floors" → 下了四十一层) | 层 for counting storeys, 楼 for the floor name | CORPUS |

### Unresolved and hand-off notes

1. **Berezinskii's Taiwan form** is unsettled (別列津斯基 in an NTU thesis; 貝瑞津斯基 in popular writing); the mainland form 别列津斯基 is settled (XH-P). Thouless's Taiwan form is likewise split (杜列斯 in CNA, 索利斯 in academia). The TW lane should pick; the CN edition does not depend on it.
2. **Deep Ellum, Stemmons, Las Colinas, International Parkway, the Metroplex** have no 新华社 dictionary entry; the forms given are rule-derived (L–M). Recommend the moderator decide once for both editions whether such Dallas micro-toponyms stay in Latin (as the log rows do) or are transliterated; mixing the two policies inside one story reads as carelessness in either edition.
3. **Fahrenheit, feet, miles, dollars**: keep the source units in both editions (the narrator is a Texan) — the divergence is only in the unit *word* (呎/英尺, 哩/英里, 美金/美元), handled in §a.6.
4. **"ten trillion years" = 十兆年 (TW) vs 十万亿年 (CN)**: a genuine semantic trap (兆 = 10^12 in Taiwan, 10^6 in mainland SI usage; mainland prose counts 万亿). `tw2sp` does nothing here.
5. **GB/T 15835-2011 (numerals)** could not be fetched; its rules are cited from memory (M). GB/T 15834-2011 clauses are cited through a secondary source (`mizzlelover/biaodian` references, which quote clause numbers B.2.1, 4.5.3.5); CLREQ was read in source. NAER's 兩岸對照 lists and the Wikipedia conversion groups (Template:CGroup/IT, /Aviation, /Physics) were unreachable; their role is covered by CSLD + OCC + MW, but a maintainer with open network access should diff this lexicon against NAER 兩岸對照名詞-計算機 (data.gov.tw dataset 15275) and Template:CGroup/Aviation before freezing it.
6. **The register table's particle rows are corpus observations**, not dictionary rulings (the dictionary's silence is the evidence). A mainland copy-editor should read every line of dialogue once for 喔/耶/齁/蠻/超/不會/謝啦 after the lexicon pass; none of them can be caught mechanically without false positives (喔 as an interjection and 耶 inside 耶稣 are legitimate).
7. Not verified live: the zh.wikipedia zh-cn/zh-tw title pairs. Every name form in §c therefore rests on the 新华社 dictionaries (H) plus press usage (M), not on Wikipedia.
