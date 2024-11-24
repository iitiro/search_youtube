import os
import pandas as pd
from googleapiclient.discovery import build
from datetime import datetime

# Функція для читання API-ключа з файлу
def get_api_key(file_path):
    try:
        with open(file_path, 'r') as file:
            api_key = file.read().strip()
        return api_key
    except FileNotFoundError:
        print(f"Файл {file_path} не знайдено.")
        return None

# Функція для читання ключових слів з файлу
def get_search_queries(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            queries = [line.strip() for line in file.readlines()]
        return queries
    except FileNotFoundError:
        print(f"Файл {file_path} не знайдено.")
        return []

# Функція для отримання хендлу каналу за його ідентифікатором
def get_channel_handle(youtube, channel_id):
    request = youtube.channels().list(
        part='snippet',
        id=channel_id
    )
    response = request.execute()
    items = response.get('items', [])
    if items:
        custom_url = items[0]['snippet'].get('customUrl')
        if custom_url:
            return f"@{custom_url}"
    return None

# Функція для виконання пошуку відео на YouTube
def youtube_search(query, api_key, max_results):
    youtube = build('youtube', 'v3', developerKey=api_key)
    
    videos = []
    next_page_token = None
    total_results = 0

    while total_results < max_results:
        request = youtube.search().list(
            q=query,
            part='snippet',
            type='video',
            maxResults=min(50, max_results - total_results),
            pageToken=next_page_token
        )
        response = request.execute()

        # Обробка результатів
        for item in response['items']:
            channel_id = item['snippet']['channelId']
            channel_url = f"https://www.youtube.com/channel/{channel_id}"
            channel_handle = get_channel_handle(youtube, channel_id)
            channel_handle_url = f"https://www.youtube.com/{channel_handle}" if channel_handle else channel_url

            # Отримання поточного часу для фіксації дати та часу запиту
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            video_data = {
                'title': item['snippet']['title'],
                'description': item['snippet']['description'],
                'channel': item['snippet']['channelTitle'],
                'video_id': item['id']['videoId'],
                'url': f"https://www.youtube.com/watch?v={item['id']['videoId']}",
                'channel_url': channel_url,
                'channel_handle_url': channel_handle_url,
                'timestamp': timestamp
            }
            videos.append(video_data)
        
        total_results += len(response['items'])
        next_page_token = response.get('nextPageToken')

        if not next_page_token:
            break
    
    return videos

# Функція для збереження даних в Excel-файл
def save_to_excel(videos, query):
    output_folder = "!search_youtube"
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Отримання поточної дати і часу для назви файлу
    current_time = datetime.now().strftime('%Y-%m-%d %H-%M')
    
    # Формуємо назву файлу з додаванням дати і часу
    file_name = os.path.join(output_folder, f"{query}_{current_time}.xlsx")
    df = pd.DataFrame(videos)
    df.to_excel(file_name, index=False)
    print(f"Результати збережено у файл: {file_name}")

# Основна програма
if __name__ == '__main__':
    # Читання API-ключа з файлу
    api_key_path = "/Users/ikudinov/Documents/Code/keys/api_yt_2.txt"
    api_key = get_api_key(api_key_path)
    
    if api_key:
        # Читання ключових слів з файлу
        queries_file_path = "keywords.txt"
        queries = get_search_queries(queries_file_path)
        
        if queries:
            # Вкажіть, скільки результатів ви хочете отримати (наприклад, 200)
            max_results = 50
            
            for query in queries:
                # Пропуск ключових слів, що починаються з #
                if query.startswith("#"):
                    print(f"Пропуск ключового слова: {query}")
                    continue
                
                print(f"Пошук за ключовим словом: {query}")
                videos = youtube_search(query, api_key, max_results)
                save_to_excel(videos, query)
        else:
            print("Файл із ключовими словами порожній або не знайдено.")
    else:
        print("Не вдалося отримати API-ключ.")