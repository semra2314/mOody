import customtkinter as ctk
from tkinter import ttk, messagebox
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import pygame
from io import BytesIO
import requests
import threading
import subprocess
import sys
from urllib.parse import quote
import webbrowser
from PIL import Image, ImageTk
import os
from playsound3 import playsound
import threading
from youtube_search import YoutubeSearch
import random
import cv2
import time
from deepface import DeepFace
from collections import Counter
from googlesearch import search
from spotipy.oauth2 import SpotifyOAuth
import mediapipe as mp

# Spotify API bilgileri
CLIENT_ID = "73ace5159f9a4a149ba22fd9948dba9d"
CLIENT_SECRET = "a06f38e025ad43caadf098c017167ebd"
REDIRECT_URI = "https://127.0.0.1:8888/callback"

client_credentials_manager = SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

# Pygame başlat
pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=4096)

# CustomTkinter tema ayarları
ctk.set_appearance_mode("dark")  # Dark mode
ctk.set_default_color_theme("dark-blue")  # Dark blue theme


class SpotifyApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Spotify Şarkı Listesi ve Çalıcı")
        self.root.geometry("1200x900")

        # Pencere boyutunu ekrana göre ayarla
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        self.root.geometry(f"{int(screen_width * 0.8)}x{int(screen_height * 0.8)}")

        self.loading = False
        self.current_sound = None

        # Arka plan rengi
        self.bg_color = "#121212"
        self.secondary_bg = "#1E1E1E"
        self.text_color = "#FFFFFF"
        self.accent_color = "#1DB954"  # Spotify yeşili
        self.search_frame = ctk.CTkFrame(root, fg_color=self.secondary_bg)
        self.search_frame.pack(pady=5, padx=300, fill="x")
        self.song_label = ctk.CTkLabel(self.search_frame, text="Şarkı Adı:", text_color=self.text_color)
        self.song_label.grid(row=0, column=0, padx=(0, 5))  # Sağ padding 5

        self.song_entry = ctk.CTkEntry(
            self.search_frame,
            width=200,
            fg_color="#2A2A2A",
            border_color="#444",
            text_color=self.text_color
        )
        self.song_entry.grid(row=0, column=1, padx=5)
        self.song_entry.insert(0, "feel it")

        self.search_button = ctk.CTkButton(
            self.search_frame,
            text="Şarkı Ara",
            command=self.search_track,
            fg_color="red",
            hover_color="#1ED760"
        )
        self.search_button.grid(row=0, column=2, padx=5)

        self.deep_button = ctk.CTkButton(
            self.search_frame,
            text="Şarkı Öner",
            command=self.deep,
            fg_color=self.accent_color,
            hover_color="#1ED760"
        )
        self.deep_button.grid(row=0, column=3, padx=(5, 0))  # Sol padding 5

        # Beğenilenleri listele butonu
        self.liked_button = ctk.CTkButton(root, text="Beğenilenleri Listele", command=self.list_liked_songs,
                                          fg_color="#535353", hover_color="#666")
        self.liked_button.pack(pady=5)

        # Sonuçlar için Treeview
        self.tree_frame = ctk.CTkFrame(root, fg_color=self.secondary_bg)
        self.tree_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Treeview için stil oluştur
        style = ttk.Style()
        style.theme_use("default")

        # Treeview stil ayarları
        style.configure("Treeview",
                        background="#2A2A2A",
                        foreground=self.text_color,
                        rowheight=25,
                        fieldbackground="#2A2A2A",
                        borderwidth=0)
        style.map('Treeview', background=[('selected', '#535353')])

        style.configure("Treeview.Heading",
                        background="#1E1E1E",
                        foreground=self.text_color,
                        relief="flat")
        style.map("Treeview.Heading", background=[('active', '#444')])

        columns = ("Şarkı", "Sanatçı", "Albüm", "Çıkış Tarihi", "İndirilmiş", "Popülerlik", "Platform")
        self.tree = ttk.Treeview(self.tree_frame, columns=columns, show="headings", style="Treeview")

        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150 if col != "Şarkı" and col != "Albüm" else 200)

        scrollbar = ttk.Scrollbar(self.tree_frame, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(fill="both", expand=True)

        self.selected_track = None
        self.tree.bind("<ButtonRelease-1>", self.on_tree_select)

        self.album_main_frame = ctk.CTkFrame(root, fg_color=self.bg_color)
        self.album_main_frame.pack(pady=10, fill="x")

        self.album_cover_frame = ctk.CTkFrame(self.album_main_frame, fg_color=self.bg_color, width=200, height=200)
        self.album_cover_frame.pack(side="left", padx=20, pady=10)
        self.album_cover_label = ctk.CTkLabel(self.album_cover_frame, text="")
        self.album_cover_label.pack()
        self.album_cover_image = None

        self.album_info_frame = ctk.CTkFrame(self.album_main_frame, fg_color=self.bg_color)
        self.album_info_frame.pack(side="right", padx=20, pady=10, fill="both", expand=True)
        self.labelkontrol = ctk.CTkLabel(
            self.album_info_frame,
            text="",
            text_color=self.accent_color,
            font=('Arial', 16, 'bold'),
            anchor="w"
        )
        self.labelkontrol.pack(anchor="w", pady=(0, 5))

        self.song_title_label = ctk.CTkLabel(
            self.album_info_frame,
            text="Şarkı: ",
            text_color=self.accent_color,
            font=('Arial', 16, 'bold'),
            anchor="w"
        )
        self.song_title_label.pack(anchor="w", pady=(0, 5))

        self.artist_label = ctk.CTkLabel(
            self.album_info_frame,
            text="Sanatçı: ",
            text_color=self.text_color,
            font=('Arial', 14),
            anchor="w"
        )
        self.artist_label.pack(anchor="w", pady=(0, 5))

        self.album_label = ctk.CTkLabel(
            self.album_info_frame,
            text="Albüm: ",
            text_color=self.text_color,
            font=('Arial', 14),
            anchor="w"
        )
        self.album_label.pack(anchor="w", pady=(0, 5))

        # Kontrol butonları frame'i (sağ taraf, bilgilerin altında)
        self.control_buttons_frame = ctk.CTkFrame(self.album_info_frame, fg_color=self.bg_color)
        self.control_buttons_frame.pack(pady=10, fill="x")

        self.play_button = ctk.CTkButton(
            self.control_buttons_frame,
            text="▶ Çal",
            command=self.play_preview_thread,
            fg_color=self.accent_color,
            hover_color="#1ED760",
            width=80
        )
        self.play_button.pack(side="left", padx=5)

        # Durdur butonu
        self.stop_button = ctk.CTkButton(
            self.control_buttons_frame,
            text="⏹ Durdur",
            command=self.stop_preview,
            fg_color="#FF4B4B",
            hover_color="#FF6B6B",
            width=80
        )
        self.stop_button.pack(side="left", padx=5)

        # Spotify'da aç butonu
        self.open_spotify_button = ctk.CTkButton(
            self.control_buttons_frame,
            text="Spotify'da Aç",
            command=self.open_in_spotify,
            fg_color="#535353",
            hover_color="#666",
            width=100
        )
        self.open_spotify_button.pack(side="left", padx=5)
        self.open_spotify_button.configure(state="disabled")

        self.open_youtube_button = ctk.CTkButton(
            self.control_buttons_frame,
            text="Youtube'da Aç",
            command=self.open_in_youtube,
            fg_color="#535353",
            hover_color="#666",
            width=100
        )
        self.open_youtube_button.pack(side="left", padx=5)
        self.open_youtube_button.configure(state="disabled")
        # İndir butonu
        self.down_button = ctk.CTkButton(
            self.control_buttons_frame,
            text="İndir",
            command=self.down_in_spotify,
            fg_color="#535353",
            hover_color="#666",
            width=80
        )
        self.down_button.pack(side="left", padx=5)
        self.down_button.configure(state="disabled")

        # Ses kontrolü
        self.volume_frame = ctk.CTkFrame(root, fg_color=self.secondary_bg)
        self.volume_frame.pack(pady=5, padx=10, fill="x")

        self.volume_label = ctk.CTkLabel(self.volume_frame, text="Ses Seviyesi:", text_color=self.text_color)
        self.volume_label.pack(side="left")

        self.volume_scale = ctk.CTkSlider(self.volume_frame, from_=0, to=1, number_of_steps=10, fg_color="#444",
                                          button_color=self.accent_color, button_hover_color="#1ED760")
        self.volume_scale.set(0.7)
        self.volume_scale.pack(side="left", padx=5, fill="x", expand=True)

        # Durum bilgisi
        self.status_label = ctk.CTkLabel(root, text="", text_color="#1DB954")
        self.status_label.pack()

        self.search_track()

    def set_volume(self, val):
        if self.current_sound:
            self.current_sound.set_volume(float(val))

    def list_liked_songs(self):
        def get_existing_mp3s():
            download_path = "C:\\Users\\Melih\\Desktop\\Bython\\mOody\\downloads"
            mp3_files = []
            try:
                # Klasör yoksa oluştur
                os.makedirs(download_path, exist_ok=True)
                for file in os.listdir(download_path):
                    if file.lower().endswith('.mp3'):
                        mp3_files.append(file[:-4])
            except Exception as e:
                print(f"MP3 dosyaları taranırken hata: {e}")
            return mp3_files

        def is_song_downloaded(song_name, artist_name):
            existing_files = get_existing_mp3s()
            search_string = f"{artist_name} - {song_name}".lower().strip()
            for file in existing_files:
                if search_string in file.lower().strip():
                    return True
            return False

        try:
            results = sp.current_user_saved_tracks(limit=50)

            for item in self.tree.get_children():
                self.tree.delete(item)

            for item in results['items']:
                track = item['track']
                song = track['name']
                artists = ", ".join([artist['name'] for artist in track['artists']])
                album = track['album']['name']
                release_date = track['album']['release_date']
                popularity = track['popularity']
                platform = "spotify"
                has_preview = "✅" if is_song_downloaded(song, artists) else "❌"
                self.tree.insert("", "end",
                                 values=(song, artists, album, release_date, has_preview, popularity, platform),
                                 tags=(track['id'],))
            self.status_label.configure(text=f"{len(results['items'])} beğenilen şarkı listelendi.")

        except Exception as e:
            messagebox.showerror("Hata", f"Beğenilen şarkılar alınamadı: {str(e)}")

    def deep(self):
        # Duygu analizi için gerekli fonksiyonlar
        def kamera_ile_duygu_tahmini():
            """Kameradan yüz ifadesi analizi yaparak duygu tahmini."""
            detector_backend = 'mtcnn'
            cap = cv2.VideoCapture(0)

            if not cap.isOpened():
                print("Kamera açılamadı!")
                return "sakin"

            analysis_duration = 5
            start_time = time.time()
            emotions = []
            confidence_threshold = 0.85

            # MediaPipe el tespiti #
            mp_hands = mp.solutions.hands
            hands = mp_hands.Hands(
                static_image_mode=False,
                max_num_hands=2,
                min_detection_confidence=0.7,
                min_tracking_confidence=0.5
            )

            print(f"Kamera {analysis_duration} saniye boyunca duygu analizi yapıyor...")

            motivasyon_modu = False  #
            romantik_mod = False  #

            while (time.time() - start_time) < analysis_duration:
                ret, frame = cap.read()
                if not ret:
                    print("Görüntü alınamıyor!")
                    break

                try:
                    frame = cv2.resize(frame, (640, 480))
                    frame = cv2.flip(frame, 1)
                    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  #

                    # Önce el tespiti
                    hand_results = hands.process(rgb_frame)
                    if hand_results.multi_hand_landmarks:
                        num_hands = len(hand_results.multi_hand_landmarks)
                        for hand_landmarks in hand_results.multi_hand_landmarks:
                            mp.solutions.drawing_utils.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

                        if num_hands == 1 and not motivasyon_modu:
                            cv2.putText(frame, "MOTIVASYON MODU!", (50, 50),
                                        cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 3)
                            motivasyon_modu = True

                        elif num_hands == 2 and not romantik_mod:
                            cv2.putText(frame, "ROMANTIK MOD!", (50, 50),
                                        cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 3)
                            romantik_mod = True
                    if not motivasyon_modu and not romantik_mod:
                        result = DeepFace.analyze(
                            img_path=frame,
                            actions=['emotion'],
                            enforce_detection=False,
                            silent=True,
                            detector_backend=detector_backend
                        )

                        if isinstance(result, list) and len(result) > 0:
                            dominant_emotion = result[0]['dominant_emotion']
                            emotion_confidence = result[0]['emotion'][dominant_emotion]

                            if emotion_confidence > confidence_threshold:
                                emotions.append(dominant_emotion)
                                if 'region' in result[0]:
                                    x, y, w, h = result[0]['region']['x'], result[0]['region']['y'], \
                                    result[0]['region']['w'], \
                                        result[0]['region']['h']
                                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                                    cv2.putText(frame, f"{dominant_emotion} ({emotion_confidence:.2f})", (x, y - 10),
                                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

                    countdown = int(analysis_duration - (time.time() - start_time))
                    cv2.putText(frame, f"Kalan Süre: {countdown}s", (10, 30),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                    cv2.imshow('Duygu Analizi', frame)

                    if cv2.waitKey(1) == ord('q'):  # ???
                        break

                except Exception as e:
                    print(f"Hata: {str(e)}")
                    continue

            cap.release()
            cv2.destroyAllWindows()

            if motivasyon_modu:
                return "motivasyon"
            elif romantik_mod:
                return "romantik"
            elif emotions:
                most_common_emotion = Counter(emotions).most_common(1)[0][0]
                print(f"\nDominant Duygu: {most_common_emotion}")
                return most_common_emotion
            else:
                print("\n⚠ Duygu tespiti yapılamadı. Varsayılan olarak 'sakin' mod seçildi.")
                return "sakin"

        def duygu_eslestir(deepface_duygusu):
            """DeepFace duygu çıktısını sistem için uygun duyguyla eşleştirir."""
            custom_emotions = {
                "happy": "mutlu",
                "sad": "üzgün",
                "angry": "sinirli",
                "neutral": "sakin",
                "motivasyon": "motivasyon",
                "romantik": "romantik"
            }
            return custom_emotions.get(deepface_duygusu, "sakin")

        def spotifydan_sarki_oynat(duygu):
            """Spotify'dan duyguya uygun şarkı çalar."""
            try:
                sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
                    client_id="73ace5159f9a4a149ba22fd9948dba9d",
                    client_secret="a06f38e025ad43caadf098c017167ebd",
                    redirect_uri="https://127.0.0.1:8888/callback",
                    scope="user-read-playback-state,user-modify-playback-state,user-read-currently-playing"
                ))

                kelime = random.choice(duygu_anahtar_kelimeleri.get(duygu, ["pop music"]))
                sonuç = sp.search(q=kelime, type='track', limit=10)
                if sonuç['tracks']['items']:
                    parca = random.choice(sonuç['tracks']['items'])
                    uri = parca['uri']
                    ad = parca['name']
                    sanatci = parca['artists'][0]['name']
                    print(f"🎵 Spotify'da çalınıyor: {ad} - {sanatci}")
                    sp.start_playback(uris=[uri])
                else:
                    print("Spotify'da sonuç bulunamadı.")
            except Exception as e:
                print(f"Spotify hatası: {str(e)}")

        def youtubedan_sarki_ac(duygu):
            """YouTube Music'ten duyguya uygun şarkı açar."""
            try:
                kelime = random.choice(duygu_anahtar_kelimeleri.get(duygu, ["pop music"])) + " site:music.youtube.com"
                print(f"🔎 YouTube Music'te aranıyor: {kelime}")

                # Sadece music.youtube.com linklerini al
                arama_sonuclari = [link for link in search(kelime, num_results=5, advanced=True)
                                   if 'music.youtube.com' in link.url]

                if arama_sonuclari:
                    link = random.choice(arama_sonuclari).url
                    print(f"🎵 YouTube Music'te açılıyor: {link}")
                    webbrowser.open(link)
                else:
                    print("YouTube Music sonucu bulunamadı.")
            except Exception as e:
                print(f"YouTube arama hatası: {str(e)}")

        # Duygu analizini başlat
        messagebox.showinfo("Bilgi", "Lütfen kameraya net bir şekilde bakın ve yüzünüzün tamamen görünmesini sağlayın.")
        deepface_duygusu = kamera_ile_duygu_tahmini()
        sistem_duygusu = duygu_eslestir(deepface_duygusu)

        print(f"\n🎯 Sistem için seçilen duygu: {sistem_duygusu.capitalize()}")

        # Duyguya göre şarkı öner
        duygu_anahtar_kelimeleri = {
            "mutlu": ["feel it - d4vd", "happy pop", "feel good music", "summer hits", "upbeat hits"],
            "üzgün": ["sad acoustic", "melancholy", "breakup songs"],
            "sinirli": ["rock", "heavy metal", "rage music"],
            "sakin": ["chill vibes", "lofi beats", "relaxing piano"],
            "romantik": ["romantic songs", "love ballads", "slow dance"],
            "motivasyon": ["motivational phonk", "gym workout music", "energy booster", "sport motivation mix"]
        }

        # Kullanıcıya seçenek sun
        choice = messagebox.askquestion("Müzik Kaynağı",
                                        "Spotify'dan mı çalmak istersiniz? (Hayır derseniz YouTube Music kullanılacak)")

        if choice == 'yes':
            spotifydan_sarki_oynat(sistem_duygusu)
        else:
            youtubedan_sarki_ac(sistem_duygusu)

    def search_track(self):
        def get_existing_mp3s():
            download_path = "C:\\Users\\Melih\\Desktop\\Bython\\mOody\\downloads"
            mp3_files = []
            try:
                # Klasör yoksa oluştur
                os.makedirs(download_path, exist_ok=True)
                for file in os.listdir(download_path):
                    if file.lower().endswith('.mp3'):
                        mp3_files.append(file[:-4])
            except Exception as e:
                print(f"MP3 dosyaları taranırken hata: {e}")
            return mp3_files

        def is_song_downloaded(song_name, artist_name):
            existing_files = get_existing_mp3s()
            search_string = f"{artist_name} - {song_name}".lower().strip()
            for file in existing_files:
                if search_string in file.lower().strip():
                    return True
            return False

        song_name = self.song_entry.get()

        if not song_name:
            messagebox.showwarning("Uyarı", "Lütfen bir şarkı adı girin")
            return

        for item in self.tree.get_children():
            self.tree.delete(item)

        query = f'track:{song_name}'

        try:
            self.status_label.configure(text="Arama yapılıyor...")
            self.root.update()

            results = sp.search(q=query, type='track', limit=50)

            if not results['tracks']['items']:
                self.status_label.configure(text="Sonuç bulunamadı")
                messagebox.showinfo("Bilgi", "Sonuç bulunamadı")
                return

            tracks_with_preview = []
            tracks_without_preview = []

            for track in results['tracks']['items']:
                if track['preview_url']:
                    tracks_with_preview.append(track)
                else:
                    tracks_without_preview.append(track)

            sorted_tracks = tracks_with_preview + tracks_without_preview
            for track in sorted_tracks:
                song = track['name']
                artists = ", ".join([artist['name'] for artist in track['artists']])
                album = track['album']['name']
                release_date = track['album']['release_date']
                has_preview = "✅" if is_song_downloaded(song, artists) else "❌"
                popularity = track['popularity']
                platform = "spotify"
                self.tree.insert("", "end",
                                 values=(song, artists, album, release_date, has_preview, popularity, platform),
                                 tags=(track['id'],))

            found_count = len(results['tracks']['items'])
            preview_count = len(tracks_with_preview)
            self.status_label.configure(text=f"{found_count} şarkı bulundu ({preview_count} tanesinde önizleme var)")

        except Exception as e:
            self.status_label.configure(text="Arama hatası")
            print(e)
            messagebox.showerror("Hata", f"Arama sırasında hata oluştu: {str(e)}")

    def on_tree_select(self, event):
        def get_existing_mp3s():
            download_path = "C:\\Users\\Melih\\Desktop\\Bython\\mOody\\downloads"
            mp3_files = []
            try:
                # Klasör yoksa oluştur
                os.makedirs(download_path, exist_ok=True)
                for file in os.listdir(download_path):
                    if file.lower().endswith('.mp3'):
                        mp3_files.append(file[:-4])
            except Exception as e:
                print(f"MP3 dosyaları taranırken hata: {e}")
            return mp3_files

        def is_song_downloaded(song_name, artist_name):
            existing_files = get_existing_mp3s()
            search_string = f"{artist_name} - {song_name}".lower().strip()
            for file in existing_files:
                if search_string in file.lower().strip():
                    return True
            return False

        self.open_spotify_button.configure(state="disabled")
        self.open_youtube_button.configure(state="enabled")
        self.down_button.configure(state="enabled")
        selected_item = self.tree.focus()
        if not selected_item:
            return

        track_id = self.tree.item(selected_item, "tags")[0]
        track_info = self.tree.item(selected_item, "values")

        try:
            track_data = sp.track(track_id)

            self.selected_track = {
                'id': track_id,
                'name': track_info[0],
                'artist': track_info[1],
                'album': track_info[2],
                'has_preview': "✅" if is_song_downloaded(track_info[0], track_info[1]) else "❌",
                'popularity': track_data['popularity'],
                'spotify_url': track_data['external_urls']['spotify']
            }

            # Şarkı bilgilerini güncelle

            self.song_title_label.configure(text=f"Şarkı: {track_info[0]}")
            self.artist_label.configure(text=f"Sanatçı: {track_info[1]}")
            self.album_label.configure(text=f"Albüm: {track_info[2]}")

            if is_song_downloaded(track_info[0], track_info[1]):
                self.status_label.configure(text="Şarkı seçildi - Çalmaya hazır", text_color="#1DB954")
                self.play_button.configure(state="normal")
                self.down_button.configure(state="normal")
            else:
                self.status_label.configure(text="Bu şarkı için önizleme bulunamadı", text_color="#FF4B4B")
                # self.play_button.configure(state="disabled")

            if self.selected_track['spotify_url']:
                self.open_spotify_button.configure(state="normal")
            else:
                self.open_spotify_button.configure(state="disabled")

            # Albüm kapağını güncelle
            album_images = track_data['album']['images']
            if album_images:
                album_url = album_images[0]['url']
                self.update_album_cover(album_url)
            else:
                self.clear_album_cover()

        except Exception as e:
            messagebox.showerror("Hata", f"Şarkı bilgileri alınırken hata oluştu: {str(e)}")

    def update_album_cover(self, url):
        try:
            response = requests.get(url)
            response.raise_for_status()
            image_data = response.content
            image = Image.open(BytesIO(image_data))
            image = image.resize((200, 200))  # Daha küçük boyut
            self.album_cover_image = ImageTk.PhotoImage(image)
            self.album_cover_label.configure(image=self.album_cover_image)
        except Exception as e:
            print(f"Albüm resmi yüklenemedi: {e}")
            self.clear_album_cover()

    def clear_album_cover(self):
        self.album_cover_label.configure(image="")
        self.album_cover_image = None

    def play_preview_thread(self):
        download_path = f"C:\\Users\\Melih\\Desktop\\Bython\\mOody\\downloads\\{self.selected_track['artist']} - {self.selected_track['name']}.mp3"
        playsound(download_path)

    def play_preview(self):
        try:
            self.stop_preview()

            self.status_label.configure(text="Şarkı indiriliyor...")
            self.root.update()

            preview_url = self.selected_track['preview_url']
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(preview_url, headers=headers, timeout=15)
            response.raise_for_status()

            temp_file = BytesIO()
            temp_file.write(response.content)
            temp_file.seek(0)

            self.status_label.configure(text="Şarkı hazırlanıyor...")
            self.root.update()

            sound = pygame.mixer.Sound(temp_file)
            self.current_sound = sound
            sound.set_volume(self.volume_scale.get())
            sound.play()

            self.status_label.configure(text=f"Çalıyor: {self.selected_track['name']}", text_color="#1DB954")

        except Exception as e:
            self.status_label.configure(text=f"Hata: {str(e)}", text_color="#FF4B4B")
        finally:
            self.loading = False
            self.play_button.configure(state="normal")

    def stop_preview(self):
        if self.current_sound:
            try:
                self.current_sound.stop()
                self.status_label.configure(text="Durduruldu", text_color="#FFFFFF")
            except:
                pass
            self.current_sound = None

    def open_in_spotify(self):
        if self.selected_track and self.selected_track.get("spotify_url"):
            webbrowser.open(self.selected_track["spotify_url"])

    def open_in_youtube(self):
        sarki_adi = self.selected_track.get("name") + self.selected_track.get("artist")
        results = YoutubeSearch(sarki_adi, max_results=1).to_dict()
        url_suffix = results[0]['url_suffix']
        youtube_url = f"https://www.youtube.com{url_suffix}"
        webbrowser.open(youtube_url)

    def down_in_spotify(self):
        self.labelkontrol.configure(text="indirme başlatıldı")
        download_path = "C:\\Users\\Melih\\Desktop\\Bython\\mOody\\downloads"
        # Klasör yoksa oluştur
        os.makedirs(download_path, exist_ok=True)
        subprocess.run([sys.executable, "-m", "spotdl", "--output",
                        download_path, self.selected_track.get('spotify_url')], check=False)
        print("\n✅ Şarkı(lar) başarıyla indirildi!")
        self.labelkontrol.configure(text="indirme başarılı")
        print(self.selected_track.get('spotify_url'))


if __name__ == "__main__":
    try:
        pygame.mixer.quit()
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=8192)

        root = ctk.CTk()
        app = SpotifyApp(root)
        root.mainloop()
    except Exception as e:
        messagebox.showerror("Başlatma Hatası", f"Uygulama başlatılamadı:\n{str(e)}")