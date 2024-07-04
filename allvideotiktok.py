"""
Instagram: @ajose19
"""

import os
import time
import pickle
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import yt_dlp as youtube_dl

def login_tiktok():
    options = Options()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=options)
    driver.get("https://www.tiktok.com/login")
    print("Por favor, inicia sesión en TikTok en la ventana abierta...")
    time.sleep(60)  # Espera 60 segundos para que el usuario inicie sesión manualmente

    cookies = driver.get_cookies()
    with open("tiktok_cookies.pkl", "wb") as f:
        pickle.dump(cookies, f)
    
    driver.quit()

def load_cookies(driver):
    with open("tiktok_cookies.pkl", "rb") as f:
        cookies = pickle.load(f)
        for cookie in cookies:
            driver.add_cookie(cookie)

def handle_captcha(driver):
    try:
        captcha = driver.find_element(By.XPATH, '//div[contains(@class, "captcha")]')
        if captcha.is_displayed():
            print("Captcha detectado. Tienes 30 segundos para resolverlo.")
            time.sleep(30)  # Espera 30 segundos para que el usuario resuelva el captcha
    except:
        pass

def scroll_to_load_videos(driver):
    SCROLL_PAUSE_TIME = 2
    last_height = driver.execute_script("return document.body.scrollHeight")
    
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(SCROLL_PAUSE_TIME)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

def get_tiktok_video_urls(driver, username):
    print(f"Iniciando proceso para el usuario: {username}")
    driver.get(f"https://www.tiktok.com/@{username}")
    time.sleep(5)  # Espera a que la página cargue completamente

    handle_captcha(driver)
    scroll_to_load_videos(driver)

    video_urls = []
    video_elements = driver.find_elements(By.XPATH, '//a[contains(@href, "/video/")]')
    for video in video_elements:
        href = video.get_attribute('href')
        if href and '/video/' in href:
            video_urls.append(href)

    print(f"Total de videos encontrados: {len(video_urls)}")
    return video_urls

def download_videos(driver, video_urls, download_path):
    if not os.path.exists(download_path):
        os.makedirs(download_path)

    ydl_opts = {
        'outtmpl': os.path.join(download_path, '%(title)s.%(ext)s'),
        'format': 'best'
    }

    total_downloaded = 0
    for i, video_url in enumerate(video_urls, start=1):
        print(f"\nVIDEO {i}:")
        print("*" * 150)
        print(f"Procesando video: {video_url}")

        driver.get(video_url)
        time.sleep(5)  # Espera a que la página del video cargue

        handle_captcha(driver)

        try:
            print(f"Descargando el video: {video_url}")
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                ydl.download([video_url])
            print(f"Video descargado: {video_url}")
            total_downloaded += 1
        except Exception as e:
            print(f"Error al descargar el video {video_url}: {str(e)}")
        
        print("*" * 150)
    
    return total_downloaded

if __name__ == "__main__":
    login_choice = input("¿Necesitas iniciar sesión en TikTok? (s/n): ")
    if login_choice.lower() == 's':
        login_tiktok()

    username = input("Ingresa el nombre de usuario de TikTok del cual deseas descargar los videos: ").strip('@')
    download_path = os.path.join(os.getcwd(), username)

    options = Options()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=options)

    driver.get("https://www.tiktok.com/")
    load_cookies(driver)
    driver.refresh()
    time.sleep(5)  # Espera a que las cookies se apliquen

    video_urls = get_tiktok_video_urls(driver, username)
    
    if video_urls:
        total_downloaded = download_videos(driver, video_urls, download_path)
        print(f"\nProceso completado. Total de videos descargados: {total_downloaded}")
    else:
        print("No se encontraron videos o hubo un error.")
    
    driver.quit()
