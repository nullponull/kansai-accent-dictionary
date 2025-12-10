# MeCab形式の関西弁アクセント辞書

本ディレクトリには、関西弁アクセント辞書のMeCab形式版が含まれています。

## ファイル

- `kansai_accent.csv`: MeCab形式の辞書ファイル（4,615語）

## MeCab形式について

MeCab形式の辞書は、以下のフィールドで構成されています：

```
表層形,左文脈ID,右文脈ID,コスト,品詞,品詞細分類1,品詞細分類2,品詞細分類3,活用型,活用形,原形,読み,発音,アクセント
```

### アクセント情報

本辞書では、最後のフィールド（14番目）にアクセント核の位置を記録しています：

- `0`: アクセント核なし
- `1`: 1拍目に核
- `2`: 2拍目に核
- `3`: 3拍目に核
- （以下同様）

**例**:
```
はな,0,0,1,名詞,一般,*,*,*,*,鼻,はな,はな,0
あめ,0,0,1,名詞,一般,*,*,*,*,雨,あめ,あめ,2
はし,0,0,1,名詞,一般,*,*,*,*,橋,はし,はし,1
```

## 使用方法

### 1. MeCabユーザー辞書としてコンパイル

MeCabのユーザー辞書としてコンパイルするには、以下の手順を実行します：

```bash
# MeCabのインストール（Ubuntu/Debian）
sudo apt-get install mecab mecab-ipadic-utf8

# 辞書のコンパイル
/usr/lib/mecab/mecab-dict-index \
  -d /usr/share/mecab/dic/ipadic \
  -u kansai_accent.dic \
  -f utf-8 \
  -t utf-8 \
  kansai_accent.csv

# MeCabで使用
mecab -u kansai_accent.dic
```

### 2. Pythonから使用

```python
import MeCab

# ユーザー辞書を指定してMeCabを初期化
tagger = MeCab.Tagger('-u kansai_accent.dic')

# 形態素解析
text = "はなが咲いた"
result = tagger.parse(text)
print(result)
```

### 3. 音声合成での使用

音声合成エンジン（OpenJTalk等）でアクセント情報を使用する場合：

```python
import csv

# 辞書を読み込む
accent_dict = {}
with open('kansai_accent.csv', 'r', encoding='utf-8') as f:
    for line in f:
        fields = line.strip().split(',')
        surface = fields[0]
        accent = fields[13]  # アクセント情報
        accent_dict[surface] = accent

# 単語のアクセントを取得
word = "はな"
accent = accent_dict.get(word, '0')
print(f"{word}のアクセント核: {accent}")
```

## 注意事項

### 左文脈ID・右文脈IDについて

現在の辞書では、左文脈ID・右文脈IDを`0`に設定しています。これは簡易的な実装であり、実際の運用では以下の対応が必要です：

1. **MeCabの辞書ファイルから適切なIDを取得**
2. **コスト値の調整**（現在は`1`に固定）

より正確な形態素解析を行う場合は、これらの値を適切に設定してください。

### 読み・発音について

現在の辞書では、読みと発音をひらがなのまま記録しています。本来は以下の変換が必要です：

- **読み**: カタカナに変換
- **発音**: 実際の発音に合わせた表記

将来のバージョンで対応予定です。

## 変換スクリプト

MeCab形式への変換は、`tools/convert_to_mecab.py`スクリプトで行っています。

```bash
# 変換スクリプトの実行
python3 tools/convert_to_mecab.py
```

## トラブルシューティング

### コンパイルエラーが発生する

MeCabの辞書ファイルのパスが正しいか確認してください：

```bash
# MeCabの辞書ディレクトリを確認
mecab-config --dicdir
```

### アクセント情報が取得できない

MeCabの出力形式を確認してください：

```bash
# 出力形式を指定
mecab -u kansai_accent.dic -O wakati
```

## 今後の改善予定

- [ ] 左文脈ID・右文脈IDの適切な設定
- [ ] コスト値の最適化
- [ ] 読み・発音のカタカナ変換
- [ ] コンパイル済みバイナリの提供

## ライセンス

本辞書は、元データのライセンスに従います。詳細は`docs/data_sources.md`を参照してください。
