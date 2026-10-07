# MAINLAND — locale review of the zh-Hans edition (derived), whole book

Reviewer: the moderator, 2026-10-07, reading as a mainland literary editor. The two mainland reviewers launched on
10-06 stopped on a usage limit before writing; this review replaces both halves.
Read: the zh-Hans text derived from the ratified zh-Hant master v2 (convert v2), every prose block of all 22 units
cover to cover, then every row block; preceded by a residue sweep (≈150 Taiwan/mainland word pairs, measure words,
names) over the whole text. Brief: `../five_hours_apart_zht/_brief/QA_BRIEFS.md` §MAINLAND REVIEW.
Rule kept from the brief: the zh-Hant edition is canonical; only locale divergences are changed, never wording taste.

Every change below is made by the DERIVATION, not by hand: a registry zh-Hans cell (R35 in the zh-Hant charter) or a
line of `_key/locale_layer_zhs.txt`, each with a `forbid:` guard so the gate fails if the Taiwan form ever returns.
Re-running `convert_zhs.py` therefore reproduces the reviewed text exactly.

| unit.seq | finding | as derived | now | severity | where fixed |
|---|---|---|---|---|---|
| ch_02 … ch_18 (13 sites, prose and rows) | Iris was 艾丽斯, which Xinhua reserves for *Alice* (GT_NAMES: CN 艾丽丝, cf. 艾丽丝·默多克); the key had carried 艾丽斯 against its own ground truth. | 艾丽斯·雷恩 | 艾丽丝·雷恩 | BLOCK | registry P.iris, P.iris_rows (R35); layer; forbid:艾丽斯 |
| ch_06.059/.085, ch_16.003/.005, ch_18.006 (6 sites) | 有差 ("it makes a difference") is Taiwan colloquial; a mainland reader hears a regionalism in a locked line. 有差别 (ch_02) is standard and kept. | 会有差吗 / 对它有差 / 是有差的 / 对我会有差 | 会有区别吗 / 对它有区别 / 是有区别的 / 对我会有区别 | FIX | layer re:有差(?!别); echo in gate_zhs updated |
| ch_13.002, .009 | A car takes 辆, not 台. | 整台车 / 另一台车 | 整辆车 / 另一辆车 | FIX | layer |
| ch_06.088, ch_09.006 | A phone takes 部, not 支. | 一支手机 / 一支电量剩百分之二的手机 | 一部手机 / 一部电量只剩百分之二的手机 | FIX | layer |
| ch_13.021, ch_03.015 | Measure words. | 一颗硬盘 / 一颗气球 | 一块硬盘 / 一个气球 | FIX | layer |
| ch_05.032, ch_02.011, ch_10.004 | Businesses take 家. | 一间餐厅 / 那间酒店 | 一家餐厅 / 那家酒店 | FIX | layer |
| ch_05.018 | 有 + verb is Taiwan grammar. | 最近有找到什么好的吗？ | 最近有没有找到什么好的？ | FIX | layer |
| ch_05.036 | 资遣 is Taiwan HR language. | 就被资遣 | 就被辞退 | FIX | layer |
| ch_06.032, .043 | The click: 喀 is a Taiwan spelling of the sound. | 同一声喀 | 同一声咔嗒 | FIX | layer |
| ch_11.020 | Decades. | 七〇年代 | 七十年代 | FIX | layer |
| ch_12.003, .011, .112 | Scrolling is 滚动 on the mainland; 卷动 is the Taiwan UI verb. | 卷动 / 往下卷 / 往上卷 | 滚动 / 往下滚 / 往上滚 | FIX | layer |
| ch_02.005 | 灯号 is Taiwan. | 灯号一变 | 信号灯一变 | FIX | layer |
| ch_01.011 | Runways are numbered with 号 in mainland prose. | 17和18跑道 | 17号和18号跑道 | NIT | registry A.runways1718 (R35) |
| ch_11.040 | The schedule line read oddly. | 排期上用我的名字 | 排期表上用的是我的名字 | NIT | layer |
| rows, ch_16, ch_17 | Row columns shifted where a cell changed width (发消息 for 傳訊, 拉斯科利纳斯 for LAS COLINAS); and 传消息 itself was not mainland (the registry's 讯→消息 ran before the layer's 傳訊 rule). | 传消息, ragged columns | 发消息, rows re-padded to the zh-Hant columns | FIX | layer; `_tools_zhs/rows_zhs.py` in the converter and the gate (ROWALIGN), battery case added |

Checked and kept: 二七左 (a pilot's callout, the canonical text's choice); 七七七 (the author's word form);
重逢塔 / 特里尼蒂河 / 格雷普韦恩 / 深艾勒姆 / 拉斯科利纳斯 (the names lane's forms); 被自愿 (lands on the mainland,
where it is a known coinage); 跟 in narration (colloquial, standard); 搭 / 盖 (standard); 文档; 二〇一九年;
在海上 for "over the water"; 一间没人要的房间 (rooms take 间).

Already right in the derivation (the layer of 10-06): 屏幕, 视频, 进程, 比特, 字节, 哈希, 设置, 数据, 循环, 内核, 保安,
献血, 廊桥, 航站楼, 边检, 行李提取处, 头像, 英尺, 扎带, 播客, 水磨石, 卷帘门, 自动售货机, 开尔文, 希思罗, 得州,
卡彭特, 酒店, 进近, 汇报, 幻灯片, 配置文件, 管道, 硅, 泄洪道, 刹车灯, 保险杠, 双闪, 摆渡车, 十万亿, 账单, 桌布, 领位,
服务员, 高峰时段, 仪表盘, 空调机组, 工牌, 页表, 录像, 噪声, 记账, 回放.

Counts: BLOCK 1 · FIX 12 · NIT 2, all fixed. Gate after the fixes: 22 units, 0 FAIL; batteries ALL CASES BEHAVE
(ch_02, ch_06, ch_12, ch_13); rows check clean.
