import requests
import flet as ft
from collections import defaultdict
from datetime import datetime

# 気象庁のAPIエンドポイント
AREA_URL = "http://www.jma.go.jp/bosai/common/const/area.json"

def fetch_weather_data(region_code):
    """指定された地域コードの天気データを取得する関数"""
    try:
        weather_url = f"http://www.jma.go.jp/bosai/forecast/data/forecast/{region_code}.json"
        response = requests.get(weather_url)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"[ERROR] 天気データ取得失敗: ステータスコード {response.status_code}")
            return None
    except Exception as e:
        print(f"[EXCEPTION] 天気データ取得中にエラー発生: {e}")
        return None

def parse_weather_data(weather_data):
    """天気情報を辞書形式で解析し、日付ごとにグループ化する関数"""
    if not weather_data:
        return None
    
    weather_dict = defaultdict(list)
    
    for weather_entry in weather_data:
        publishing_office = weather_entry.get("publishingOffice", "不明")
        report_datetime = weather_entry.get("reportDatetime", "不明")
        time_series = weather_entry.get("timeSeries", [])
        
        for series in time_series:
            time_defines = series.get("timeDefines", [])
            areas = series.get("areas", [])
            
            for area in areas:
                area_name = area.get("area", {}).get("name", "不明")
                area_code = area.get("area", {}).get("code", "不明")
                
                # 各種データを取得
                weather_codes = area.get("weatherCodes", [])
                weathers = area.get("weathers", [])
                winds = area.get("winds", [])
                waves = area.get("waves", [])
                pops = area.get("pops", [])
                reliabilities = area.get("reliabilities", [])
                temps = area.get("temps", [])
                
                # 地域コードごとに情報を格納
                for idx, time_define in enumerate(time_defines):
                    # 日付部分を取得し、グループ化
                    date = time_define.split("T")[0]
                    
                    forecast = {
                        "datetime": time_define,
                        "weather_code": weather_codes[idx] if idx < len(weather_codes) else "情報なし",
                        "weather": weathers[idx] if idx < len(weathers) else "情報なし",
                        "wind": winds[idx] if idx < len(winds) else "情報なし",
                        "wave": waves[idx] if idx < len(waves) else "情報なし",
                        "pop": pops[idx] if idx < len(pops) else "情報なし",
                        "reliability": reliabilities[idx] if idx < len(reliabilities) else "情報なし",
                        "temp": temps[idx] if idx < len(temps) else "情報なし",
                    }
                    
                    # 日付ごとに予報を追加
                    weather_dict[date].append(forecast)
    
    return weather_dict

def main(page: ft.Page):
    page.title = "天気予報アプリ"
    
    # 背景色やレイアウトスタイルの調整
    page.bgcolor = "#f0f8ff"  # アクアブルー背景
    page.padding = 30  # ページ全体の余白

    # コンポーネント
    parent_dropdown = ft.Dropdown(label="地方を選択", width=350)
    child_dropdown = ft.Dropdown(label="地名を選択", disabled=True, width=350)
    result_label = ft.Text("", size=16, color="#333333", text_align="left")

    # 地域マッピング
    region_mapping = {}
    area_mapping = {}

    def update_child_dropdown(e):
        """選択された地方に基づいて地名をフィルタリング"""
        child_dropdown.options.clear()
        selected_parent = parent_dropdown.value
        
        if selected_parent in region_mapping:
            for area_name in region_mapping[selected_parent]:
                child_dropdown.options.append(ft.dropdown.Option(area_name))
        
        child_dropdown.disabled = False
        child_dropdown.update()

    parent_dropdown.on_change = update_child_dropdown

    def fetch_areas():
        """地域情報を取得し、Dropdownに地方名と地名を設定"""
        try:
            response = requests.get(AREA_URL)
            response.raise_for_status()
            areas = response.json()

            for center_code, center_data in areas.get("centers", {}).items():
                region_name = center_data["name"]
                parent_dropdown.options.append(ft.dropdown.Option(region_name))
                region_mapping[region_name] = []
                
                for child_code in center_data.get("children", []):
                    area_info = areas["offices"].get(child_code, {})
                    area_name = area_info.get("name")
                    if area_name:
                        region_mapping[region_name].append(area_name)
                        area_mapping[area_name] = {"code": child_code}
            
            parent_dropdown.update()

        except requests.RequestException as e:
            result_label.value = f"地域情報の取得に失敗しました: {e}"
            page.update()

    def fetch_weather(e):
        """選択された地域の天気を取得"""
        selected_name = child_dropdown.value
        if not selected_name:
            result_label.value = "地名を選択してください。"
            page.update()
            return

        try:
            # 選択された地域のコードを取得
            region_code = area_mapping[selected_name]["code"]
            
            # 天気データを取得
            weather_data = fetch_weather_data(region_code)
            
            # 天気データを解析
            weather_dict = parse_weather_data(weather_data)
            
            if not weather_dict:
                result_label.value = "天気情報が見つかりませんでした。"
                page.update()
                return
            
            # 選択された地域の天気情報を表示
            area_weather = weather_dict
            if not area_weather:
                result_label.value = "選択した地域の天気情報が見つかりませんでした。"
                page.update()
                return
            
            # 天気情報の詳細を表示
            weather_info = f"{selected_name} の天気情報:\n"
            weather_info += f"発表局: {area_weather.get('publishing_office', '不明')}\n"
            weather_info += f"発表日時: {area_weather.get('report_datetime', '不明')}\n\n"
            
            # 日付ごとにグループ化された天気情報を表示
            for date, forecasts in area_weather.items():
                weather_info += f"日付: {date}\n"
                for forecast in forecasts:
                    weather_info += (
                        f"  時間: {forecast['datetime']}\n"
                        f"  天気: {forecast['weather']}\n"
                        f"  気温: {forecast['temp']}℃\n"
                        f"  降水確率: {forecast['pop']}%\n"
                        f"  風: {forecast['wind']}\n"
                        f"  波: {forecast['wave']}\n"
                        f"  信頼性: {forecast['reliability']}\n\n"
                    )
            
            result_label.value = weather_info
            page.update()

        except requests.RequestException as e:
            result_label.value = f"天気情報の取得に失敗しました: {e}"
        except (KeyError, IndexError) as e:
            result_label.value = f"天気情報の解析に失敗しました: {e}"
        
        page.update()

    # ボタンのデザイン
    fetch_button = ft.ElevatedButton(
        text="天気を取得", on_click=fetch_weather,
        style=ft.ButtonStyle(color=ft.colors.WHITE, bgcolor=ft.colors.CYAN_500),
        width=350, height=50
    )

    # ページレイアウト
    page.add(
        ft.Column(
            [
                ft.Text("気象庁 天気予報アプリ", size=30, weight="bold", color="#1e3a8a"),
                ft.Text("（宮古島、大東島のみ正確に表示されます）", size=14, color="#6b7280"),
                ft.Row([parent_dropdown, child_dropdown], alignment="center", spacing=20),
                fetch_button,
                result_label,
            ],
            alignment="center",
            spacing=20
        )
    )

    # 起動時に地域情報を取得
    fetch_areas()

# アプリ実行
ft.app(target=main)
