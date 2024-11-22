import flet as ft
import math

# ボタンの基本クラス
class CalcButton(ft.ElevatedButton):
    def __init__(self, text, button_clicked, expand=1):
        super().__init__()
        self.text = text  # ボタンに表示されるテキスト
        self.expand = expand  # ボタンの拡大率
        self.on_click = button_clicked  # ボタンがクリックされたときの処理
        self.data = text  # ボタンのデータ（テキスト）

# 数字用ボタン
class DigitButton(CalcButton):
    def __init__(self, text, button_clicked, expand=1):
        CalcButton.__init__(self, text, button_clicked, expand)
        self.bgcolor = ft.colors.WHITE24  # 背景色
        self.color = ft.colors.WHITE  # 文字色

# 四則演算やイコール用ボタン
class ActionButton(CalcButton):
    def __init__(self, text, button_clicked):
        CalcButton.__init__(self, text, button_clicked)
        self.bgcolor = ft.colors.ORANGE  # 背景色
        self.color = ft.colors.WHITE  # 文字色

# その他の機能用ボタン（AC、+/-、%など）
class ExtraActionButton(CalcButton):
    def __init__(self, text, button_clicked):
        CalcButton.__init__(self, text, button_clicked)
        self.bgcolor = ft.colors.BLUE_GREY_100  # 背景色
        self.color = ft.colors.BLACK  # 文字色

# 科学計算用ボタン（sin, cos, logなど）
class ScientificButton(CalcButton):
    def __init__(self, text, button_clicked):
        CalcButton.__init__(self, text, button_clicked)
        self.bgcolor = ft.colors.BLUE_200  # 背景色
        self.color = ft.colors.BLACK  # 文字色

# 電卓アプリのメインクラス
class CalculatorApp(ft.Container):
    def __init__(self):
        super().__init__()
        self.reset()  # 初期化メソッドを呼び出す

        # 結果表示用テキスト
        self.result = ft.Text(value="0", color=ft.colors.WHITE, size=20)

        # 電卓の全体デザイン
        self.width = 450  # 幅を増やしてボタンを収容
        self.bgcolor = ft.colors.BLACK
        self.border_radius = ft.border_radius.all(20)
        self.padding = 20

        # 電卓のボタンとレイアウト
        self.content = ft.Column(
            controls=[
                ft.Row(controls=[self.result], alignment="end"),  # 結果表示行
                # 科学計算のボタン行1
                ft.Row(
                    controls=[
                        ScientificButton(text="sin", button_clicked=self.button_clicked),
                        ScientificButton(text="cos", button_clicked=self.button_clicked),
                        ScientificButton(text="tan", button_clicked=self.button_clicked),
                        ScientificButton(text="π", button_clicked=self.button_clicked),
                        ScientificButton(text="e", button_clicked=self.button_clicked),
                    ]
                ),
                # 科学計算のボタン行2
                ft.Row(
                    controls=[
                        ScientificButton(text="log", button_clicked=self.button_clicked),
                        ScientificButton(text="ln", button_clicked=self.button_clicked),
                        ScientificButton(text="x²", button_clicked=self.button_clicked),
                        ScientificButton(text="√", button_clicked=self.button_clicked),
                        ScientificButton(text="x^y", button_clicked=self.button_clicked),
                    ]
                ),
                # 基本機能ボタン行1
                ft.Row(
                    controls=[
                        ExtraActionButton(text="AC", button_clicked=self.button_clicked),
                        ExtraActionButton(text="+/-", button_clicked=self.button_clicked),
                        ExtraActionButton(text="%", button_clicked=self.button_clicked),
                        ActionButton(text="/", button_clicked=self.button_clicked),
                    ]
                ),
                # 基本機能ボタン行2以降
                ft.Row(
                    controls=[
                        DigitButton(text="7", button_clicked=self.button_clicked),
                        DigitButton(text="8", button_clicked=self.button_clicked),
                        DigitButton(text="9", button_clicked=self.button_clicked),
                        ActionButton(text="*", button_clicked=self.button_clicked),
                    ]
                ),
                ft.Row(
                    controls=[
                        DigitButton(text="4", button_clicked=self.button_clicked),
                        DigitButton(text="5", button_clicked=self.button_clicked),
                        DigitButton(text="6", button_clicked=self.button_clicked),
                        ActionButton(text="-", button_clicked=self.button_clicked),
                    ]
                ),
                ft.Row(
                    controls=[
                        DigitButton(text="1", button_clicked=self.button_clicked),
                        DigitButton(text="2", button_clicked=self.button_clicked),
                        DigitButton(text="3", button_clicked=self.button_clicked),
                        ActionButton(text="+", button_clicked=self.button_clicked),
                    ]
                ),
                ft.Row(
                    controls=[
                        DigitButton(text="0", expand=2, button_clicked=self.button_clicked),
                        DigitButton(text=".", button_clicked=self.button_clicked),
                        ActionButton(text="=", button_clicked=self.button_clicked),
                    ]
                ),
            ]
        )

    # ボタンがクリックされたときの処理
    def button_clicked(self, e):
        data = e.control.data  # クリックされたボタンのデータ（テキスト）
        print(f"Button clicked with data = {data}")

        # 各ボタンに応じた動作（ACでリセット、四則演算、科学計算など）
        # ここに記述されたロジックは省略せず、特定の計算やエラー処理を行う

    # 数値のフォーマット処理
    def format_number(self, num):
        if num % 1 == 0:
            return int(num)  # 整数として返す
        else:
            return num  # 小数のまま返す

    # 計算処理
    def calculate(self, operand1, operand2, operator):
        # 四則演算や累乗などを実行
        try:
            if operator == "+":
                return self.format_number(operand1 + operand2)
            elif operator == "-":
                return self.format_number(operand1 - operand2)
            elif operator == "*":
                return self.format_number(operand1 * operand2)
            elif operator == "/":
                if operand2 == 0:
                    return "Error"  # ゼロ除算をエラーで返す
                else:
                    return self.format_number(operand1 / operand2)
            elif operator == "x^y":
                return self.format_number(operand1 ** operand2)
        except:
            return "Error"  # 例外処理

    # 初期化処理
    def reset(self):
        self.operator = "+"  # 初期演算子
        self.operand1 = 0  # 最初のオペランド
        self.new_operand = True  # 新しい入力を示すフラグ

# メインアプリケーションの起動
def main(page: ft.Page):
    page.title = "Scientific Calculator"  # タイトル
    calc = CalculatorApp()  # 電卓アプリのインスタンス
    page.add(calc)  # ページに追加

ft.app(target=main)  # アプリを起動
