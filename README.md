# taxi-card — 把酒店地址变成司机看得懂的卡片

外国人在中国旅行时，最难的不是找到地方，而是**说清楚是哪一个**。
booking 网站给你一个英文名和一张地图；中国司机会看着导航说「不是这家」。

这个工具把一家酒店的中文名与中文地址排成一张可以直接出示的卡片：

```
请司机带我到这里：
  北京饭店
  Beijing Hotel
  地址：北京市东长安街33号
  城市：北京
```

## 用法

```bash
# 按 ID 从 D1 取
python3 taxi_card.py --id 9003

# 按名称
python3 taxi_card.py --name "北京饭店"

# 无网络：从本地 JSON 读
python3 taxi_card.py --json hotels_export.json --name "北京饭店"

# 存成 HTML（可打印 / 可存 PDF）
python3 taxi_card.py --id 9003 --out card.html
```

## 为什么中文名和中文地址要分开

酒店的中文名往往带品牌和专名（「北京饭店」而不是「北京市某某路 33 号酒店」），
司机的认知里前者是检索词，后者是定位。卡片两个都给。

## 数据来源

酒店记录来自 [SinoStay](https://sinostay.com) 的公开目录 —— 该站只收录
**确实接待外国护照**的住宿单位，并保留中文名、中文地址与真实访客评价。
免费浏览，无需注册：https://sinostay.com/hotel/

## 许可

MIT。数据本身归 SinoStay 所有。
