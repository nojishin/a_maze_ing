*This project has been created as part of the 42 curriculum by shshimiz, snoji.*

# A-Maze-ing

## Description

設定ファイルを受け取って迷路を生成し、壁を16進数の表現でファイルに書き出す、迷路生成器です。
入口と出口の間の経路が1本だけになる完全迷路も生成できます。
迷路の視覚的な表現も提供し、生成ロジックは後で再利用できるように整理しています。

## Instructions

### インストール

### 操作コマンド

| コマンド | 内容 |
|---|---|
| `generate` (`g`) | 新しい迷路を生成する |
| `route` (`r`) | 解の経路を表示 / 非表示にする |
| `exit` (`e`) | 終了する |

### Lint

## Architecture
### 処理の流れ
### フォルダー構成
### 主なクラス

## Configuration
1行に1つ、`KEY=VALUE` の形式で書く。
SEEDのみ任意。

| キー | 必須 | 内容 |
|---|---|---|
| `WIDTH` | ○ | 迷路の幅（1〜100） |
| `HEIGHT` | ○ | 迷路の高さ（1〜100） |
| `ENTRY` | ○ | 入口の座標（`x,y`）。迷路の範囲内で、`EXIT` とは別の座標 |
| `EXIT` | ○ | 出口の座標（`x,y`）。迷路の範囲内で、`ENTRY` とは別の座標 |
| `OUTPUT_FILE` | ○ | 出力先のパス。空と、設定ファイルと同じパスは不可 |
| `PERFECT` | ○ | 完全迷路にするかどうか（真偽値） |
| `SEED` | 任意 | 乱数のシード（整数） |

## Maze generation algorithm
### 採用したアルゴリズム
    Recursive Divison
### 選んだ理由
- 
### 迷路生成の流れ
Recursive Divisionで迷路を作り、そのあとで42パターンの配置と経路の調整をします。

```text
外周の壁だけを作る
      ↓
42パターンの位置を決める
      ↓
Recursive Divisionで壁を作る
      ↓
42パターンのセルを壁で閉じる
      ↓
分断された領域をつなぎ直す
      ↓
PERFECT=False のときだけループを追加する
```
#### 1. 外周の壁だけを作る
```py
def parse_grid(width: int, height: int) -> list[list[int]]:
```
迷路全体を、外周にだけ壁がある1つの広い部屋とする。

#### 2. 42パターンの位置を決める
```py
def make_blocked(width: int, height: int) -> set[tuple[int, int]]:
```

7×5マスの42パターンを、迷路の中央に置くセルを求める。
幅が9未満、または高さが7未満の迷路には置けないため、エラーにする。
このあと `SEED` で乱数を初期化する。

#### 3. Recursive Divisionで壁を作る
```py
def divide(
    grid: list[list[int]],
    x: int,
    y: int,
    width: int,
    height: int,
) -> None:
```

次の手順を、部屋の幅か高さが1マスになるまで繰り返す。

1. 部屋の長い辺を横切る向きに壁を引きます。正方形なら向きはランダム。
2. 壁の位置と、壁に1か所だけ開ける通路の位置をランダムに決める。
3. 壁で分かれた2つの部屋に、同じ処理をする。

2つの部屋は必ず1か所の通路だけでつながるので、この時点の迷路はループのない完全迷路になる。

#### 4. 42パターンのセルを壁で閉じる
```py
def close_blocked(grid: list[list[int]], blocked: set[tuple[int, int]]) -> None:
```

42パターンのセルを四方の壁で囲む。
この操作により元の通路がふさがれ、迷路が複数の領域に分断されることがある。

#### 5. 分断された領域をつなぎ直す
```py
def repair(grid: list[list[int]], blocked: set[tuple[int, int]]) -> None:
```

1. `(0, 0)` から到達できるセルをBFSで調べる。
2. 到達済みのセルと未到達のセルの境界にある壁を、ランダムに1枚壊します。42パターンのセルに接する壁は壊さない。
3. 壊した先から到達できるセルを調べ、未到達のセルがなくなるまで繰り返す。

別々の領域を1か所ずつつなぐだけなのでループはできず、完全迷路のままになる。
### nonperfect迷路
`PERFECT=False` のときだけ実行する。
```py
def add_loops(grid: list[list[int]], blocked: set[tuple[int, int]]) -> None:
```
行き止まりのセルをランダムな順に調べ、壁を1枚壊してループを作る。
隣も行き止まりになる壁を優先して壊し、2×2の空間ができる壁と42パターンのセルに接する壁は壊さない。

## Reusable code

## Team and project management
### 役割分担
| 担当者 | 担当範囲 | 主なファイル |
|---|---|---|
| shshimiz | 迷路生成アルゴリズム（Recursive Division）、nonperfect迷路の生成 | `mazegen/generate/` |
| snoji | 設定ファイルの読み込みと検証、エラー処理、`MazeGenerator` の設計、迷路の描画、対話式コマンド、パッケージ化と開発環境の整備 | `input/`, `models/`, `errors/`, `mazegen/generator.py`, `visualizer/`, `pyproject.toml` |
### 計画と実際の進み方

### うまくいった点と改善できる点

### 使用したツール

## Resources
### 参考資料
### AIの利用
