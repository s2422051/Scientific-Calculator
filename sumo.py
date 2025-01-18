import requests
from bs4 import BeautifulSoup
from retry import retry
import time
import logging
import sqlite3
import csv
from datetime import datetime

# ロギング設定
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='scraping.log'
)

# ヘッダー設定
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

# SUUMOの東京23区の物件検索URL
url = 'https://suumo.jp/jj/chintai/ichiran/FR301FC001/?ar=030&bs=040&ta=13&sc=13101&sc=13102&sc=13103&sc=13104&sc=13105&sc=13113&sc=13106&sc=13107&sc=13108&sc=13118&sc=13121&sc=13122&sc=13123&sc=13109&sc=13110&sc=13111&sc=13112&sc=13114&sc=13115&sc=13120&sc=13116&sc=13117&sc=13119&cb=0.0&ct=9999999&mb=0&mt=9999999&et=9999999&cn=9999999&shkr1=03&shkr2=03&shkr3=03&shkr4=03&sngz=&po1=25&pc=50&page={}'

def init_database():
    """データベースの初期化"""
    conn = sqlite3.connect('suumo_properties_focused.db')
    cursor = conn.cursor()
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS properties (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        scrape_date TEXT,
        nearest_station1 TEXT,
        nearest_station2 TEXT
    )
    ''')
    
    conn.commit()
    return conn, cursor

def insert_to_database(conn, cursor, data_samples):
    """データベースへの挿入"""
    scrape_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    insert_query = '''
    INSERT INTO properties (
        scrape_date, nearest_station1, nearest_station2
    ) VALUES (?, ?, ?)
    '''
    
    insert_data = [
        (
            scrape_date,
            sample['station1'],
            sample['station2']
        )
        for sample in data_samples
    ]
    
    cursor.executemany(insert_query, insert_data)
    conn.commit()

def save_to_csv(data_samples):
    """CSVファイルに保存"""
    keys = ['scrape_date', 'station1', 'station2']
    with open('suumo_properties.csv', 'a', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=keys)
        if file.tell() == 0:  # ファイルが空の場合、ヘッダーを書き込む
            writer.writeheader()
        writer.writerows(data_samples)

@retry(tries=3, delay=10, backoff=2)
def load_page(url):
    """ページの読み込み"""
    try:
        html = requests.get(url, headers=headers, timeout=20)  # タイムアウトを20秒に設定
        html.raise_for_status()
        return BeautifulSoup(html.content, 'html.parser')
    except requests.exceptions.RequestException as e:
        logging.error(f"ページ読み込みエラー: {e}")
        raise

def get_total_pages(soup):
    """総ページ数の取得"""
    try:
        page_links = soup.find('div', class_='pagination-parts').find_all('a')
        return int(page_links[-2].text)
    except:
        return 100  # デフォルト値

def extract_property_data(property_item):
    """物件データの抽出"""
    property_data = []
    
    try:
        # 最寄り駅情報
        station_info = property_item.find(class_='cassetteitem_detail-col2')
        stations = station_info.find_all(class_='cassetteitem_detail-text')
        station1 = stations[0].text if stations else '不明'
        station2 = stations[1].text if len(stations) > 1 else '不明'
        
        # 部屋情報の取得
        rooms = property_item.find(class_='cassetteitem_other')
        for room in rooms.find_all(class_='js-cassette_link'):
            room_data = {
                'station1': station1,
                'station2': station2
            }
            
            property_data.append(room_data)
    
    except Exception as e:
        logging.error(f"物件データ抽出エラー: {e}")
    
    return property_data

def main():
    conn, cursor = init_database()
    
    try:
        # 最初のページで総ページ数を取得
        first_page_soup = load_page(url.format(1))
        max_page = get_total_pages(first_page_soup)
        
        for page in range(1, max_page + 1):
            # ページ間隔を設定（サーバー負荷に配慮）
            time.sleep(2)  # リクエスト間隔を2秒に変更
            
            try:
                soup = load_page(url.format(page))
            except Exception as e:
                logging.error(f"ページ {page} の取得に失敗しました: {e}")
                continue  # 次のページに進む
            
            properties = soup.find_all(class_='cassetteitem')
            
            all_data = []
            for prop in properties:
                property_data = extract_property_data(prop)
                all_data.extend(property_data)
            
            # データベースに保存
            insert_to_database(conn, cursor, all_data)
            
            # CSVに保存
            save_to_csv(all_data)
            
            # 進捗表示
            print(f'ページ {page}/{max_page} 完了 ({round(page/max_page*100, 2)}%)')
            logging.info(f'ページ {page} 完了')

    except Exception as e:
        logging.error(f"スクレイピング中にエラー発生: {e}")
        print(f"エラー: {e}")
    
    finally:
        conn.close()
        logging.info('データベース接続終了')

if __name__ == "__main__":
    main()
