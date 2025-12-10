#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
関西弁アクセント辞書をMeCab形式に変換するスクリプト

Usage:
    python3 convert_to_mecab.py
"""

import csv
import sys
from pathlib import Path


def convert_accent_to_mecab_format(accent):
    """
    京阪式アクセント記法をMeCab形式に変換
    
    Args:
        accent (str): 京阪式アクセント（例: H00, L02, H01）
    
    Returns:
        str: MeCab形式のアクセント情報
    """
    if not accent or accent == '-':
        return '0'
    
    # H/Lと数字を分離
    if accent.startswith('H') or accent.startswith('L'):
        onset = accent[0]  # H or L
        pattern = accent[1:]  # 数字列
        
        # 核の位置を特定（最後の非0の数字の位置）
        nucleus = 0
        for i, char in enumerate(pattern):
            if char != '0':
                nucleus = i + 1
        
        # MeCab形式: 核の位置（0=核なし）
        return str(nucleus)
    
    return '0'


def convert_pos_to_mecab(pos):
    """
    品詞情報をMeCab形式に変換
    
    Args:
        pos (str): 品詞（例: 名、動、形）
    
    Returns:
        tuple: (品詞, 品詞細分類1, 品詞細分類2, 品詞細分類3)
    """
    pos_map = {
        '名': ('名詞', '一般', '*', '*'),
        '動': ('動詞', '自立', '*', '*'),
        '形': ('形容詞', '自立', '*', '*'),
        '副': ('副詞', '一般', '*', '*'),
        '連語': ('名詞', '一般', '*', '*'),
        '感': ('感動詞', '*', '*', '*'),
        '接続': ('接続詞', '*', '*', '*'),
        '助': ('助詞', '*', '*', '*'),
    }
    
    return pos_map.get(pos, ('名詞', '一般', '*', '*'))


def main():
    # パスの設定
    script_dir = Path(__file__).parent
    project_dir = script_dir.parent
    input_file = project_dir / 'data' / 'kansai_accent_dict.csv'
    output_file = project_dir / 'mecab' / 'kansai_accent.csv'
    
    print(f"入力ファイル: {input_file}")
    print(f"出力ファイル: {output_file}")
    
    # 入力ファイルの確認
    if not input_file.exists():
        print(f"エラー: 入力ファイルが見つかりません: {input_file}", file=sys.stderr)
        sys.exit(1)
    
    # 出力ディレクトリの作成
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    # 変換処理
    converted_count = 0
    
    with open(input_file, 'r', encoding='utf-8') as infile, \
         open(output_file, 'w', encoding='utf-8') as outfile:
        
        reader = csv.DictReader(infile)
        
        for row in reader:
            word = row['word']
            original = row.get('original', '')
            pos = row.get('pos', '名')
            accent = row.get('accent', '0')
            
            # 品詞情報の変換
            pos1, pos2, pos3, pos4 = convert_pos_to_mecab(pos)
            
            # アクセント情報の変換
            accent_mecab = convert_accent_to_mecab_format(accent)
            
            # 表層形（ひらがな）
            surface = word
            
            # 読み（カタカナに変換、簡易版）
            # 本来はひらがな→カタカナ変換が必要
            reading = word
            
            # 発音（読みと同じ）
            pronunciation = reading
            
            # MeCab形式で出力
            # 形式: 表層形,左文脈ID,右文脈ID,コスト,品詞,品詞細分類1,品詞細分類2,品詞細分類3,活用型,活用形,原形,読み,発音,アクセント
            mecab_line = f"{surface},0,0,1,{pos1},{pos2},{pos3},{pos4},*,*,{original if original else surface},{reading},{pronunciation},{accent_mecab}"
            
            outfile.write(mecab_line + '\n')
            converted_count += 1
    
    print(f"変換完了: {converted_count}語をMeCab形式に変換しました")
    print(f"出力先: {output_file}")


if __name__ == '__main__':
    main()
