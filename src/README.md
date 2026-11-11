*This project has been created as part of the 42 curriculum by shshimiz, snoji.*

# A-Maze-ing

## Description

設定ファイルを受け取って迷路を生成し、壁を16進数の表現でファイルに書き出す、迷路生成器である。
入口と出口の間の経路が1本だけになる完全迷路も生成できる。
迷路の視覚的な表現も提供し、生成ロジックは後で再利用できるように整理している。

## Instructions

### makeコマンド
```sh
make install
```
パッケージのインストールを行います。

```sh
make run # uv run a_maze_ing.py config.txt
make debug # uv run python -m pdb a_maze_ing.py config.txt
```
`config.txt`を読み込み`a_maze_ingg.py`を実行する

```sh
make lint
```
`mypy`と`flake8`を確認します。

```sh
make clean
```
`__pycache__` やキャッシュを削除する

### 操作コマンド

| コマンド | 内容 |
|---|---|
| `generate` (`g`) | 新しい迷路を生成する |
| `path` (`p`) | 解の経路を表示 / 非表示にする |
| `color`(`c`) | 壁の色を変える |
| `help`(`h`)  | 操作コマンドを表示する|
| `exit` (`q`) | 終了する |

## Architecture
### 処理の流れ
```text
設定ファイルを読み込み、値を検証する（input/, models/）
      ↓
検証した値を MazeGenerator に渡す（mazegen/generator.py）
      ↓
Recursive Divisionで迷路を生成する（mazegen/generate/）
      ↓
迷路を16進数の表現で OUTPUT_FILE に書き出す
      ↓
迷路を描画し、コマンドの入力を待つ（visualizer/, a_maze_ing.py）
```
設定ファイルやパラメータに誤りがある場合は、その時点でエラーを表示して終了する（errors/）。
迷路生成の詳しい手順は [Maze generation algorithm](#maze-generation-algorithm) にまとめている。
### フォルダー構成
```
.
├── a_maze_ing.py
├── config.txt
├── errors
│   ├── __init__.py
│   ├── exceptions.py
│   └── handler.py
├── input
│   ├── __init__.py
│   ├── cli.py
│   └── maze_config.py
├── LICENSE.md
├── Makefile
├── mazegen
│   ├── __init__.py
│   ├── errors.py
│   ├── generate
│   │   ├── __init__.py
│   │   ├── gen_maze.py
│   │   ├── maze_utils.py
│   │   ├── non_perfect.py
│   │   └── pattern42.py
│   ├── generator.py
│   ├── models.py
│   └── solve
│       ├── __init__.py
│       └── solver.py
├── mazegen-1.0.0-py3-none-any.whl
├── mazegen-1.0.0.tar.gz
├── models
│   ├── __init__.py
│   └── config.py
├── pyproject.toml
├── README.md
├── uv.lock
└── visualizer
    ├── __init__.py
    └── renderder.py
```
## Configuration
1行に1つ、`KEY=VALUE` の形式で書く。
SEEDのみ任意。
#で始まる行がコメントとして無視される。

| キー | 必須 | 内容 |
|---|---|---|
| `WIDTH` | ○ | 迷路の幅（3〜100） |
| `HEIGHT` | ○ | 迷路の高さ（3〜100） |
| `ENTRY` | ○ | 入口の座標（`x,y`）。迷路の範囲内で、`EXIT` とは別の座標 |
| `EXIT` | ○ | 出口の座標（`x,y`）。迷路の範囲内で、`ENTRY` とは別の座標 |
| `OUTPUT_FILE` | ○ | 出力先のパス。空と、設定ファイルと同じパスは不可 |
| `PERFECT` | ○ | 完全迷路にするかどうか（真偽値） |
| `SEED` | 任意 | 乱数のシード（整数） |

## Maze generation algorithm
### 採用したアルゴリズム
    Recursive Division
### 選んだ理由
- よくある迷路生成のアルゴリズムBacktrackingとは別のアルゴリズムで実装しようと考えていた。
- 壁がないところから迷路を生成するアルゴリズムをやろうと思っていたから。
- 面白そうだったから
### 迷路生成の流れ
Recursive Divisionで迷路を作り、そのあとで42パターンの配置と経路の調整をする。

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
def init_grid(width: int, height: int) -> list[list[int]]:
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

1. 部屋の長い辺を横切る向きに壁を引く。正方形なら向きはランダム。
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
2. 到達済みのセルと未到達のセルの境界にある壁を、ランダムに1枚壊す。42パターンのセルに接する壁は壊さない。
3. 壊した先から到達できるセルを調べ、未到達のセルがなくなるまで繰り返す。

別々の領域を1か所ずつつなぐだけなのでループはできず、完全迷路のままになる。
### nonperfect迷路
`PERFECT=False` のときだけ実行する。
```py
def add_loops(grid: list[list[int]], blocked: set[tuple[int, int]]) -> None:
```
行き止まりのセルをランダムな順に調べ、壁を1枚壊してループを作る。
隣も行き止まりになる壁を優先して壊し、3×3の空間ができる壁と42パターンのセルに接する壁は壊さない。

## Reusable code
### クラス
```py
class MazeGenerator:
    """Generate a maze and find its solution path."""

    def __init__(  # noqa: PLR0913 - public API, mirrors MazeParams fields
        self,
        *,
        width: int,
        height: int,
        entry: tuple[int, int],
        exit: tuple[int, int],  # noqa: A002 - pairs with `entry`
        is_perfect: bool,
        seed: int | None = None,
    ) -> None:
        """Validate and store the maze parameters.

        Args:
            width: Maze width in cells.
            height: Maze height in cells.
            entry: The ``(x, y)`` entry cell.
            exit: The ``(x, y)`` exit cell.
            is_perfect: Whether exactly one path joins any two cells.
            seed: Random seed. ``None`` gives a different maze each time.

        Raises:
            ParamsValidationError: If a parameter is invalid.

        """
        try:
            self._params = MazeParams(
                width=width,
                height=height,
                entry=entry,
                exit=exit,
                is_perfect=is_perfect,
                seed=seed,
            )
        except ValidationError as e:
            raise ParamsValidationError(e) from e
        self._grid: list[list[int]] | None = None

    def generate(self) -> list[list[int]]:
        """Generate a new maze.

        Returns:
            A grid of wall bitmasks, indexed as ``grid[y][x]``.

        """
        self._grid = generate(self._params)
        return self._grid

    def solve(self) -> PathResult:
        """Find the shortest path from the entry to the exit.

        Returns:
            The path cells and directions.

        Raises:
            MazeNotGeneratedError: If ``generate()`` has not been called.
            PathNotFoundError: If the exit cannot be reached.

        """
        if self._grid is None:
            raise MazeNotGeneratedError
        return solve(self._grid, self._params.entry, self._params.exit)

    def has_42pattern(self) -> bool:
        """Check whether the maze is large enough to embed the 42 pattern.

        Returns:
            ``True`` if the width and height meet the minimum size for
            the 42 pattern, ``False`` otherwise.

        """
        if self._grid is None:
            raise MazeNotGeneratedError
        return (
            self._params.width >= MIN_WIDTH
            and self._params.height >= MIN_HEIGHT
        )
```
### 引数

| 引数 | 型 | 内容 |
|---|---|---|
| `width` | `int` | 迷路の幅（セル数） |
| `height` | `int` | 迷路の高さ（セル数） |
| `entry` | `tuple[int, int]` | 入口のセル `(x, y)` |
| `exit` | `tuple[int, int]` | 出口のセル `(x, y)` |
| `is_perfect` | `bool` | `True` なら任意の2セル間の経路が1本だけの完全迷路にする |
| `seed` | `int \| None` | 乱数のシード。同じ値なら同じ迷路になる |

不正な値を渡すと `ParamsValidationError`が送られる

### メソッド
| メソッド | 戻り値 | 内容 |
|---|---|---|
| `generate()` | `list[list[int]]` | 新しい迷路を生成して返す。形式は [迷路のデータ形式](#迷路のデータ形式) を参照 |
| `solve()` | `PathResult` | 入口から出口までの最短経路を返す。`coord` は通るセルの座標のリスト、`directions` は `N` `E` `S` `W` で表した移動の文字列 |
| `has_42pattern()` | `bool` | 迷路が42パターンを埋め込める大きさかどうかを返す |

`generate()` より前に `solve()` か `has_42pattern()` を呼ぶと `MazeNotGeneratedError` が送出され、出口に到達できない場合は `PathNotFoundError` が送出される。
例外はすべて `MazeGenError` を継承しているので、まとめて捕捉することもできる。

### 迷路のデータ形式
迷路は `grid[y][x]` でアクセスする2次元リストで、各セルの壁を4ビットで表す。

| ビット | 値 | 壁の向き |
|---|---|---|
| 0 | `0b0001` (1) | 北 |
| 1 | `0b0010` (2) | 東 |
| 2 | `0b0100` (4) | 南 |
| 3 | `0b1000` (8) | 西 |

例えば値が `0b1001`（16進数で `9`）のセルは、北と西に壁がある。
隣り合うセルの壁は両側のセルに同じように記録しているので、どちらのセルから見ても壁の有無が一致する。

## Team and project management
### 役割分担
| 担当者 | 担当範囲 | 主なファイル |
|---|---|---|
| shshimiz | 迷路生成アルゴリズム（Recursive Division）、nonperfect迷路の生成 | `mazegen/generate/` |
| snoji | 設定ファイルの読み込みと検証、エラー処理、`MazeGenerator` の設計、迷路の描画、対話式コマンド、パッケージ化と開発環境の整備 | `input/`, `models/`, `errors/`, `mazegen/generator.py`, `visualizer/`, `pyproject.toml` |
### 計画と実際の進み方
当初の計画ではPERFECT=True,Falseでアルゴリズムを変えてBonusまで実装する計画だったが、subjectの
```txt
Support multiple maze generation algorithms.
```
から各アルゴリズムを両方の場合で切り替えることができないとBonusに含まれないのではないかと判断し実装をやめた
### うまくいった点と改善できる点
うまくいった点
42パターンを閉じる処理などで通路がふさがれ、どこからも到達できないセルができても、repair 関数でつなぎ直せるようにした。そのため細かいことを気にせず、試行錯誤しながら実装を進められた。

改善できる点
毎回、到達済みのセルすべてから候補を探し直しているので大きすぎる迷路を生成する場合に遅くなってしまう。
### 使用したツール
claude ai、uv(仮想環境)、mypy(型ヒントのチェック)、flake8(フォーマッター)、ruff(開発用フォーマッター)
## Resources
### 参考資料
- [Maze Algorithms](https://www.jamisbuck.org/mazes/)
- [Python ビット演算 超入門 #Python - Qiita](https://qiita.com/7shi/items/41d262ca11ea16d85abc)
- [Pythonのビット演算子（論理積、論理和、排他的論理和、反転、シフト） \| note.nkmk.me](https://note.nkmk.me/python-bit-operation/)
- [\[Python\]コマンドライン引数を受け取る方法 #argparse - Qiita](https://qiita.com/to-fmak/items/4b136479099826959ea6)
- [【ざっくりと解説】Pythonのsysモジュールの使い方（メモ） #Python3 - Qiita](https://qiita.com/sue-hc/items/2d93496af4b3857e80ab)
- [Python, pathlibの使い方（パスをオブジェクトとして操作・処理） \| note.nkmk.me](https://note.nkmk.me/python-pathlib-usage/)
- [Pythonの基本的なエラー一覧とその原因の確認方法 \| note.nkmk.me](https://note.nkmk.me/python-error-message/)
- [例外となかよく #Python - Qiita](https://qiita.com/yulily/items/0844e1a928a95df32a26)
- [【Python入門】Pythonにおけるclassの使い方とは? #Python3 - Qiita](https://qiita.com/Morio/items/0fe3abb58fcaff229f3d)
- [pythonで継承とsuper()を使って派生クラスをinitしてみよう #Python - Qiita](https://qiita.com/Anaakikutsushit/items/c67d4edb0c01a97f3130)
- [組み込み関数 — Python 3.14.7 ドキュメント](https://docs.python.org/ja/3/builtins/functions.html#super)
- [【完全解説！】Pythonの例外処理を基礎から実務レベルまで完全にマスターする](https://zenn.dev/tigrebiz/articles/python-try-exception)
- [組み込み例外 — Python 3.16.0a0 ドキュメント](https://docs.python.org/ja/dev/builtins/exceptions.html)
- [Pythonリスト内包表記の使い方 \| note.nkmk.me](https://note.nkmk.me/python-list-comprehension/)
- [Pythonで文字列を分割（区切り文字、改行、正規表現、文字数） \| note.nkmk.me](https://note.nkmk.me/python-split-rsplit-splitlines-re/)
- [Pydantic model\_validator について](https://blog.foresta.me/posts/pydantic-model-validator/)
- [uv エコシステムの勘所](https://zenn.dev/7shi/articles/20260302-uv-ecosystem)
- [Pythonの\_\_init\_\_.py、\_\_all\_\_とはなんなのか #Python - Qiita](https://qiita.com/okmokm422/items/3f9c5ab05f96c2795c40)
- [BFS (幅優先探索) 超入門！ 〜 キューを鮮やかに使いこなす 〜 #AtCoder - Qiita](https://qiita.com/drken/items/996d80bcae64649a6580)
- [Pythonのdequeでキュー、スタック、デック（両端キュー）を扱う \| note.nkmk.me](https://note.nkmk.me/python-collections-deque/)
### AIの利用
#### shshimiz
docstringの作成、READMEの作成補助、迷路生成コードのエラー解決、42パターンを迷路に埋め込む処理の検討
#### snoji
docstringの作成、より良い設計・読みやすいコードの検討
