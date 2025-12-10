#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Convert Kansai Accent Dictionary to VOICEVOX/VOICEPEAK format
京阪式アクセント辞書をVOICEVOX/VOICEPEAK形式に変換
"""

import csv
import re
import jaconv

def kana_to_katakana(text):
    """ひらがなをカタカナに変換"""
    return jaconv.hira2kata(text)

def extract_reading(word, original):
    """読みを抽出（ひらがなをカタカナへ変換）"""
    reading = word
    
    # 「・」で区切られている場合は最初の部分のみを使用
    if '・' in reading:
        reading = reading.split('・')[0]
    
    # 漢字表記がある場合は単語自体が読み
    return kana_to_katakana(reading)

def parse_keihan_accent(accent_str, mora_count):
    """
    京阪式アクセント（H/L）をVOICEVOX形式のアクセント核位置に変換
    
    京阪式アクセントの基本パターン：
    - H: 高起式（最初が高い）
    - L: 低起式（最初が低い）
    - 数字: アクセント核の位置（下がり目）
    
    VOICEVOX形式：
    - 0: 平板型（下がり目なし）
    - 1以上: その位置の後で下がる（頭高型は1、中高型は2以上）
    
    例：
    - HH: 高起式で下がり目なし → 1（頭高型として扱う）
    - LL: 低起式で下がり目なし → 0（平板型）
    - H01: 高起式で1モーラ目の後に下がる → 1
    - L02: 低起式で2モーラ目の後に下がる → 2
    - HHL: 高起式から低起式へ → 1（頭高型）
    """
    
    if not accent_str or accent_str == '-':
        return 0  # デフォルトは平板型
    
    # 複数パターンがある場合は最初のパターンを使用
    if '/' in accent_str:
        accent_str = accent_str.split('/')[0].strip()
    
    # H/Lパターンを解析
    if re.match(r'^[HL]+$', accent_str):
        # 純粋なH/Lパターン
        if accent_str.startswith('H'):
            # 高起式
            if 'L' in accent_str:
                # HからLへの変化がある場合、最初のLの位置を核とする
                l_pos = accent_str.index('L')
                return l_pos
            else:
                # すべてH（HHH...）の場合は頭高型
                return 1
        else:
            # 低起式（L始まり）
            if 'H' in accent_str:
                # LからHへの変化がある場合、最初のHの位置を核とする
                h_pos = accent_str.index('H')
                return h_pos
            else:
                # すべてL（LLL...）の場合は平板型
                return 0
    
    # H/L + 数字パターン（例：H01, L02）
    match = re.match(r'^([HL])(\d+)$', accent_str)
    if match:
        onset = match.group(1)
        nucleus = int(match.group(2))
        
        if nucleus == 0:
            # 核なし
            if onset == 'H':
                return 1  # 高起式で核なし → 頭高型
            else:
                return 0  # 低起式で核なし → 平板型
        else:
            return nucleus
    
    # 数字のみのパターン
    if accent_str.isdigit():
        return int(accent_str)
    
    # その他の複雑なパターンはデフォルト
    return 0

def count_morae(katakana):
    """
    カタカナ文字列のモーラ数をカウント
    拗音（ャュョ）、促音（ッ）、長音（ー）は前の文字と合わせて1モーラ
    """
    if not katakana:
        return 0
    
    count = 0
    i = 0
    while i < len(katakana):
        char = katakana[i]
        # 小書き文字（拗音、促音）や長音は前の文字と合わせて1モーラ
        if char in 'ャュョァィゥェォッー':
            # 最初の文字の場合はカウント（エラー回避）
            if i == 0:
                count += 1
        else:
            count += 1
        i += 1
    
    return count

def convert_to_voicevox(input_csv, output_csv):
    """
    関西弁アクセント辞書をVOICEVOX形式に変換
    
    入力形式: word,original,pos,accent,note,source
    出力形式: 表記,アクセント位置,読み,優先度
    """
    
    entries = []
    skipped = 0
    seen = set()  # 重複チェック用
    
    with open(input_csv, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            word = row['word'].strip()
            original = row.get('original', '').strip()
            accent = row.get('accent', '').strip()
            
            # 接辞（-で始まる）や特殊な記号を含むものはスキップ
            if word.startswith('-') or word.startswith('・'):
                skipped += 1
                continue
            
            # 読みを抽出（カタカナに変換）
            reading = extract_reading(word, original)
            
            # モーラ数をカウント
            mora_count = count_morae(reading)
            
            if mora_count == 0:
                skipped += 1
                continue
            
            # アクセント位置を変換
            accent_pos = parse_keihan_accent(accent, mora_count)
            
            # 表記を決定（漢字表記があればそれを使用、なければ読み）
            surface = original if original else word
            
            # 表記のクリーンアップ（「・」で区切られている場合は最初の部分のみ）
            if '・' in surface:
                surface = surface.split('・')[0]
            
            # 重複チェック（表記と読みの組み合わせ）
            key = (surface, reading)
            if key in seen:
                skipped += 1
                continue
            seen.add(key)
            
            # 優先度は0（最高優先度）
            priority = 0
            
            entries.append({
                'surface': surface,
                'accent': accent_pos,
                'reading': reading,
                'priority': priority
            })
    
    # CSVに書き出し（ヘッダー行なし）
    with open(output_csv, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        # ヘッダー行は書き込まない
        for entry in entries:
            writer.writerow([
                entry['surface'],
                entry['accent'],
                entry['reading'],
                entry['priority']
            ])
    
    print(f"変換完了: {len(entries)}エントリを出力しました")
    print(f"スキップ: {skipped}エントリ")
    return len(entries)

if __name__ == '__main__':
    input_file = '../data/kansai_accent_dict.csv'
    output_file = '../voicevox/kansai_accent_voicevox.csv'
    
    count = convert_to_voicevox(input_file, output_file)
    print(f"\n出力ファイル: {output_file}")
    print(f"総エントリ数: {count}")
