#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成「给司机的中文地址卡」。

外国人在中国最大的实际困难不是找不到地方，而是**说不清是哪一个**。
这个工具把一家酒店的中文名与中文地址排成一张可以直接给司机看的卡片。

用法：
    # 从 D1 直接读（需要 wrangler 登录）
    python3 taxi_card.py --id 9003
    python3 taxi_card.py --name "北京饭店"

    # 从本地导出的 JSON 读（无网络环境）
    python3 taxi_card.py --json hotels_export.json --name "北京饭店"

输出：一个自包含的 HTML 卡片（可打印 / 可存成 PDF），以及纯文本版（直接发给司机）。
"""
import argparse
import json
import os
import subprocess
import sys

WRANGLER = '/Users/mac/.workbuddy/binaries/node/workspace/node_modules/.bin/wrangler'
DB = 'sinostay'


def from_d1(hotel_id=None, name=None):
    """从 D1 取一家酒店。"""
    if hotel_id:
        sql = ("SELECT nid, name_cn, name_en, addr_cn, city_cn, province_cn, rating, comment_num "
               "FROM hotels WHERE nid=%s LIMIT 1" % int(hotel_id))
    else:
        like = name.replace("'", "''")
        sql = ("SELECT nid, name_cn, name_en, addr_cn, city_cn, province_cn, rating, comment_num "
               "FROM hotels WHERE name_cn LIKE '%%%s%%' OR name_en LIKE '%%%s%%' "
               "AND COALESCE(status,'live')='live' LIMIT 1" % (like, like))
    p = subprocess.run([WRANGLER, 'd1', 'execute', DB, '--remote', '--json', '--command', sql],
                       capture_output=True, text=True)
    s = p.stdout
    if '"results"' not in s:
        sys.stderr.write('D1 查询失败：%s\n' % (s or p.stderr)[:200])
        return None
    i = s.find('"results"')
    st = s.rfind('[', 0, i)
    rows = json.JSONDecoder().raw_decode(s[st:])[0][0]['results']
    return rows[0] if rows else None


def from_json(path, name):
    data = json.load(open(path, encoding='utf-8'))
    for h in data:
        if name in (h.get('name_cn') or '') or name.lower() in (h.get('name_en') or '').lower():
            return h
    return None


def card(h):
    cn = h.get('name_cn') or ''
    en = h.get('name_en') or ''
    addr = h.get('addr_cn') or h.get('address') or ''
    city = h.get('city_cn') or ''
    prov = h.get('province_cn') or ''
    where = ' '.join(x for x in (prov, city) if x)
    text = '\n'.join([
        '请司机带我到这里：',
        '  %s' % cn,
        ('  %s' % en if en else ''),
        '  地址：%s' % addr,
        ('  城市：%s' % where if where else ''),
    ])
    html = """<!doctype html>
<html lang="zh"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>%s — 中文地址卡</title>
<style>
body{font-family:-apple-system,"PingFang SC","Microsoft YaHei",sans-serif;background:#f4f5f7;
     margin:0;padding:24px;display:flex;justify-content:center}
.card{background:#fff;border-radius:16px;padding:28px 30px;max-width:520px;width:100%%;
      box-shadow:0 2px 16px rgba(0,0,0,.08);border-top:6px solid #0f766e}
.hint{color:#6b7280;font-size:14px;margin:0 0 18px}
.cn{font-size:30px;font-weight:700;margin:0 0 4px;letter-spacing:.01em}
.en{font-size:15px;color:#6b7280;margin:0 0 20px}
.addr{font-size:21px;line-height:1.55;margin:0 0 14px}
.city{font-size:15px;color:#4b5563;margin:0}
.foot{margin-top:22px;padding-top:14px;border-top:1px solid #eee;color:#9ca3af;font-size:12px}
</style></head><body>
<div class="card">
  <p class="hint">请把这张卡片给司机看</p>
  <p class="cn">%s</p>
  <p class="en">%s</p>
  <p class="addr">%s</p>
  <p class="city">%s</p>
  <p class="foot">由 SinoStay 生成 · sinostay.com</p>
</div></body></html>
""" % (cn, cn, en, addr, where)
    return text, html


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--id', type=int)
    ap.add_argument('--name')
    ap.add_argument('--json', help='本地导出的 JSON（字段名同 D1）')
    ap.add_argument('--out', help='写出的 HTML 路径')
    args = ap.parse_args()
    if not args.id and not args.name:
        ap.error('需要 --id 或 --name')
    h = from_json(args.json, args.name) if args.json else from_d1(args.id, args.name)
    if not h:
        sys.stderr.write('没找到这家酒店\n')
        return 1
    text, html = card(h)
    print(text)
    if args.out:
        open(args.out, 'w', encoding='utf-8').write(html)
        print('\n[已写 HTML] %s' % args.out, file=sys.stderr)
    return 0


if __name__ == '__main__':
    sys.exit(main())
