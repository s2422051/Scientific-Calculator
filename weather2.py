import requests
import flet as ft
import sqlite3
from collections import defaultdict
from datetime import datetime, timedelta

# 気象庁のAPIエンドポイント
AREA_URL = "http://www.jma.go.jp/bosai/common/const/area.json"

class WeatherDatabase:
    def __init__(self, db_path='weather_forecast.db'):
        """データベース接続と初期化"""
        self.conn = sqlite3.connect(db_path)
        self.create_tables()

    def create_tables(self):
        """データベースのテーブルを作成"""
        cursor = self.conn.cursor()
        
        # エリア情報テーブル
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS areas (
            id INTEGER PRIMARY KEY,
            region_name TEXT NOT NULL,
            area_name TEXT NOT NULL,
            area_code TEXT UNIQUE NOT NULL
        )
        ''')

        # 天気予報テーブル
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS weather_forecasts (
            id INTEGER PRIMARY KEY,
            area_code TEXT NOT NULL,
            forecast_date TEXT NOT NULL,
            forecast_time TEXT NOT NULL,
            weather_code TEXT,
            weather TEXT,
            temperature TEXT,
            precipitation_probability TEXT,
            FOREIGN KEY (area_code) REFERENCES areas (area_code),
            UNIQUE (area_code, forecast_date, forecast_time)
        )
        ''')

        self.conn.commit()

    def insert_area(self, region_name, area_name, area_code):
        """エリア情報をデータベースに挿入"""
        cursor = self.conn.cursor()
        try:
            cursor.execute('''
            INSERT OR REPLACE INTO areas (region_name, area_name, area_code) 
            VALUES (?, ?, ?)
            ''', (region_name, area_name, area_code))
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"エリア情報挿入エラー: {e}")

    def insert_weather_forecast(self, area_code, forecast_date, forecast_time, 
                                weather_code, weather, temperature, precipitation_probability):
        """天気予報情報をデータベースに挿入"""
        cursor = self.conn.cursor()
        try:
            cursor.execute('''
            INSERT OR REPLACE INTO weather_forecasts 
            (area_code, forecast_date, forecast_time, weather_code, weather, temperature, precipitation_probability) 
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (area_code, forecast_date, forecast_time, weather_code, 
                weather, temperature, precipitation_probability))
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"天気予報情報挿入エラー: {e}")

    def get_weather_forecasts(self, area_code, start_date=None, end_date=None):
        """指定されたエリアと日付範囲の天気予報を取得"""
        cursor = self.conn.cursor()
        query = 'SELECT * FROM weather_forecasts WHERE area_code = ?'
        params = [area_code]

        if start_date:
            query += ' AND forecast_date >= ?'
            params.append(start_date)
        
        if end_date:
            query += ' AND forecast_date <= ?'
            params.append(end_date)
        
        try:
            cursor.execute(query, params)
            return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"天気予報取得エラー: {e}")
            return []

    def get_all_areas(self):
        """全エリア情報を取得"""
        cursor = self.conn.cursor()
        try:
            cursor.execute('SELECT DISTINCT region_name, area_name, area_code FROM areas')
            return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"エリア情報取得エラー: {e}")
            return []

    def close(self):
        """データベース接続を閉じる"""
        self.conn.close()

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
        time_series = weather_entry.get("timeSeries", [])
        for series in time_series:
            time_defines = series.get("timeDefines", [])
            areas = series.get("areas", [])
            
            for area in areas:
                area_name = area.get("area", {}).get("name", "不明")
                weather_codes = area.get("weatherCodes", [])
                weathers = area.get("weathers", [])
                temps = area.get("temps", [])
                pops = area.get("pops", [])
                
                for idx, time_define in enumerate(time_defines):
                    date = time_define.split("T")[0]
                    forecast = {
                        "datetime": time_define,
                        "weather_code": weather_codes[idx] if idx < len(weather_codes) else "情報なし",
                        "weather": weathers[idx] if idx < len(weathers) else "情報なし",
                        "temp": temps[idx] if idx < len(temps) else "情報なし",
                        "pop": pops[idx] if idx < len(pops) else "情報なし",
                    }
                    weather_dict[date].append(forecast)
    
    return weather_dict

def main(page: ft.Page):
    page.title = "天気予報アプリ (DB版)"
    page.bgcolor = "#f0f8ff"
    page.padding = 30

    # データベース初期化
    weather_db = WeatherDatabase()

    parent_dropdown = ft.Dropdown(label="地方を選択", width=350)
    child_dropdown = ft.Dropdown(label="地名を選択", disabled=True, width=350)
    date_picker = ft.DatePicker(
        first_date=datetime.now(),
        last_date=datetime.now() + timedelta(days=14)
    )
    result_listview = ft.ListView(width=400, height=400, spacing=10, padding=20)

    region_mapping = {}
    area_mapping = {}

    def update_child_dropdown(e):
        child_dropdown.options.clear()
        selected_parent = parent_dropdown.value
        if selected_parent in region_mapping:
            for area_name in region_mapping[selected_parent]:
                child_dropdown.options.append(ft.dropdown.Option(area_name))
        child_dropdown.disabled = False
        child_dropdown.update()

    parent_dropdown.on_change = update_child_dropdown

    def fetch_areas():
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
                        # エリア情報をデータベースに保存
                        weather_db.insert_area(region_name, area_name, child_code)
                        
                        region_mapping[region_name].append(area_name)
                        area_mapping[area_name] = {"code": child_code}
            parent_dropdown.update()
        except requests.RequestException as e:
            result_listview.controls.append(ft.Text(f"地域情報の取得に失敗しました: {e}", color="red"))
            page.update()

    def fetch_weather(e):
        selected_name = child_dropdown.value
        if not selected_name:
            result_listview.controls.append(ft.Text("地名を選択してください。", color="red"))
            page.update()
            return

        try:
            region_code = area_mapping[selected_name]["code"]
            weather_data = fetch_weather_data(region_code)
            weather_dict = parse_weather_data(weather_data)
            if not weather_dict:
                result_listview.controls.append(ft.Text("天気情報が見つかりませんでした。", color="red"))
                page.update()
                return

            # 天気予報情報をデータベースに保存
            for date, forecasts in weather_dict.items():
                for forecast in forecasts:
                    weather_db.insert_weather_forecast(
                        area_code=region_code,
                        forecast_date=date,
                        forecast_time=forecast['datetime'],
                        weather_code=forecast['weather_code'],
                        weather=forecast['weather'],
                        temperature=forecast['temp'],
                        precipitation_probability=forecast['pop']
                    )

            result_listview.controls.clear()
            result_listview.controls.append(
                ft.Text(f"{selected_name} の天気情報", size=20, weight="bold", color="#0d9488")
            )

            for date, forecasts in weather_dict.items():
                result_listview.controls.append(
                    ft.Text(f"日付: {date}", size=16, weight="bold", color="#6d28d9")
                )
                for forecast in forecasts:
                    result_listview.controls.append(
                        ft.Card(
                            content=ft.Container(
                                content=ft.Column([
                                    ft.Text(f"時間: {forecast['datetime']}", size=14, color="#374151"),
                                    ft.Text(f"天気: {forecast['weather']}", size=14, color="#1e40af"),
                                    ft.Text(f"気温: {forecast['temp']}℃", size=14, color="#d97706"),
                                    ft.Text(f"降水確率: {forecast['pop']}%", size=14, color="#dc2626"),
                                ], spacing=5),
                                padding=10
                            ),
                            width=350,
                            elevation=2
                        )
                    )
            page.update()
        except Exception as e:
            result_listview.controls.append(ft.Text(f"天気情報の取得に失敗しました: {e}", color="red"))
            page.update()

    def show_past_forecasts(e):
        # 過去の予報を表示する機能
        selected_name = child_dropdown.value
        if not selected_name:
            result_listview.controls.append(ft.Text("地名を選択してください。", color="red"))
            page.update()
            return

        try:
            region_code = area_mapping[selected_name]["code"]
            
            # 日付選択ダイアログを表示
            page.overlay.append(date_picker)
            date_picker.pick_date()
            
            def on_date_selected(e):
                selected_date = date_picker.value.strftime('%Y-%m-%d')
                past_forecasts = weather_db.get_weather_forecasts(
                    area_code=region_code, 
                    start_date=selected_date,
                    end_date=selected_date
                )
                
                result_listview.controls.clear()
                result_listview.controls.append(
                    ft.Text(f"{selected_name} の {selected_date} の天気情報", 
                            size=20, weight="bold", color="#0d9488")
                )
                
                if not past_forecasts:
                    result_listview.controls.append(
                        ft.Text("選択された日付の予報データがありません。", color="red")
                    )
                else:
                    for forecast in past_forecasts:
                        result_listview.controls.append(
                            ft.Card(
                                content=ft.Container(
                                    content=ft.Column([
                                        ft.Text(f"時間: {forecast[3]}", size=14, color="#374151"),
                                        ft.Text(f"天気: {forecast[5]}", size=14, color="#1e40af"),
                                        ft.Text(f"気温: {forecast[6]}℃", size=14, color="#d97706"),
                                        ft.Text(f"降水確率: {forecast[7]}%", size=14, color="#dc2626"),
                                    ], spacing=5),
                                    padding=10
                                ),
                                width=350,
                                elevation=2
                            )
                        )
                page.update()
            
            date_picker.on_change = on_date_selected
        except Exception as e:
            result_listview.controls.append(ft.Text(f"過去の予報取得に失敗しました: {e}", color="red"))
            page.update()

    fetch_button = ft.ElevatedButton(
        text="天気を取得", on_click=fetch_weather,
        style=ft.ButtonStyle(color=ft.colors.WHITE, bgcolor=ft.colors.CYAN_500),
        width=350, height=50
    )

    past_forecast_button = ft.ElevatedButton(
        text="過去の予報を表示", on_click=show_past_forecasts,
        style=ft.ButtonStyle(color=ft.colors.WHITE, bgcolor=ft.colors.TEAL_500),
        width=350, height=50
    )

    page.add(
        ft.Column(
            [
                ft.Text("気象庁 天気予報アプリ +DB ", size=30, weight="bold", color="#1e3a8a"),
                ft.Text(size=14, color="#4b5563"),
                ft.Row([parent_dropdown, child_dropdown], alignment="center", spacing=20),
                ft.Row([fetch_button, past_forecast_button], alignment="center", spacing=20),
                result_listview,
            ],
            alignment="center",
            spacing=20
        )
    )
    fetch_areas()

ft.app(target=main)



