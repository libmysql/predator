import pygame
import keyboard
import os
import time
from threading import Thread

# Инициализация
pygame.mixer.init(frequency=44100, size=-16, channels=4, buffer=512)
pygame.mixer.set_num_channels(4)  # 4 канала: 0-короткий, 1-длинный, 2-сирена, 3-короткий поверх сирены

class SoundPlayer:
    def __init__(self):
        self.sounds = {
            'short': None,
            'short_slower': None,
            'long': None,
            'siren': None,
            'short_over_siren': None,
            'short_slower_over_siren': None
        }
        self.channels = {
            'short': pygame.mixer.Channel(0),
            'long': pygame.mixer.Channel(1),
            'siren': pygame.mixer.Channel(2),
            'short_over_siren': pygame.mixer.Channel(3)
        }
        self.current_short = 'short'  # Текущий выбранный звук для короткого сигнала
        self.load_sounds()
        self.running = True
        self.key_states = {
            '1': False,
            '2': False,
            '3': False,
            'm': False
        }
        self.siren_active = False
        self.short_over_siren_playing = False
        
    def load_sounds(self):
        """Загрузка звуков с проверкой"""
        sound_files = {
            'short': 'short.wav',
            'short_slower': 'short_slower.wav',
            'long': 'manual.wav',
            'siren': 'short_siren.wav',
            'short_over_siren': 'short.wav',
            'short_slower_over_siren': 'short_slower.wav'
        }
        
        for name, file in sound_files.items():
            if os.path.exists(file):
                self.sounds[name] = pygame.mixer.Sound(file)
                print(f"[Загружено] {file}")
            else:
                print(f"[Ошибка] Файл не найден: {file}")
    
    def play_sound(self, sound_type, loop=False, channel=None):
        """Воспроизведение звука с возможностью зацикливания"""
        if not channel:
            # Для коротких звуков всегда используем канал 'short' или 'short_over_siren'
            if sound_type in ['short', 'short_slower']:
                channel = self.channels['short']
            elif sound_type in ['short_over_siren', 'short_slower_over_siren']:
                channel = self.channels['short_over_siren']
            else:
                channel = self.channels[sound_type]
        
        # Если звук уже играет - не перезапускаем
        if channel.get_busy():
            return
            
        if self.sounds[sound_type]:
            channel.play(
                self.sounds[sound_type], 
                loops=-1 if loop else 0
            )
    
    def stop_sound(self, sound_type, fade=50):
        """Остановка звука с fadeout для плавности"""
        # Для коротких звуков всегда используем канал 'short' или 'short_over_siren'
        if sound_type in ['short', 'short_slower']:
            channel = self.channels['short']
        elif sound_type in ['short_over_siren', 'short_slower_over_siren']:
            channel = self.channels['short_over_siren']
        else:
            channel = self.channels[sound_type]
            
        # Если звук не играет - не останавливаем
        if channel.get_busy():
            channel.fadeout(fade)
    
    def toggle_short_sound(self):
        """Переключение между короткими звуками"""
        if self.current_short == 'short':
            self.current_short = 'short_slower'
            print("Короткий звук изменен на short_slower.wav")
        else:
            self.current_short = 'short'
            print("Короткий звук изменен на short.wav")
        
        # Если звук уже играет - перезапускаем с новым звуком
        if self.key_states['1']:
            if self.siren_active:
                self.short_over_siren_playing = True
                self.stop_sound('short_over_siren')
                sound_to_play = f"{self.current_short}_over_siren"
                self.play_sound(sound_to_play, loop=True)
            else:
                self.short_over_siren_playing = False
                self.stop_sound('long')
                self.stop_sound('siren')
                self.play_sound(self.current_short, loop=True)
    
    def check_keys(self):
        """Проверка состояния клавиш в отдельном потоке"""
        while self.running:
            # Проверка кнопки M (переключение звука)
            if keyboard.is_pressed('m'):
                if not self.key_states['m']:
                    self.key_states['m'] = True
                    self.toggle_short_sound()
            else:
                if self.key_states['m']:
                    self.key_states['m'] = False
            
            # Проверка кнопки 3 (сирена)
            if keyboard.is_pressed('3'):
                if not self.key_states['3']:
                    self.key_states['3'] = True
                    self.siren_active = True
                    self.stop_sound('long')
                    self.stop_sound(self.current_short)
                    self.play_sound('siren', loop=True)
            else:
                if self.key_states['3']:
                    self.key_states['3'] = False
                    self.siren_active = False
                    self.stop_sound('siren')
                    if self.short_over_siren_playing:
                        self.stop_sound('short_over_siren')
                        self.play_sound(self.current_short, loop=True)
            
            # Проверка кнопки 2 (длинный)
            if keyboard.is_pressed('2'):
                if not self.key_states['2']:
                    self.key_states['2'] = True
                    self.siren_active = False
                    self.stop_sound(self.current_short)
                    self.stop_sound('siren')
                    self.play_sound('long', loop=True)
            else:
                if self.key_states['2']:
                    self.key_states['2'] = False
                    self.stop_sound('long')
            
            # Проверка кнопки 1 (короткий)
            if keyboard.is_pressed('1'):
                if not self.key_states['1']:
                    self.key_states['1'] = True
                    if self.siren_active:
                        self.short_over_siren_playing = True
                        sound_to_play = f"{self.current_short}_over_siren"
                        self.play_sound(sound_to_play, loop=True)
                    else:
                        self.short_over_siren_playing = False
                        self.stop_sound('long')
                        self.stop_sound('siren')
                        self.play_sound(self.current_short, loop=True)
            else:
                if self.key_states['1']:
                    self.key_states['1'] = False
                    if self.siren_active:
                        self.short_over_siren_playing = False
                        self.stop_sound('short_over_siren')
                    else:
                        self.stop_sound(self.current_short)
            
            time.sleep(0.01)
    
    def run(self):
        """Запуск основного цикла"""
        print("PREDATOR VANTABLACK X1 – ПРОФЕССИОНАЛЬНЫЙ СИМУЛЯТОР СГУ")
        print(" [1] — Короткий сигнал (удерживать)")
        print("       (работает даже при активной сирене!)")
        print(" [2] — Длинный сигнал (удерживать)")
        print(" [3] — Сирена (удерживать)")
        print(" [M] — Переключить звук короткого сигнала")
        print(" [Esc] — Выход")
        print(f"\nТекущий звук короткого сигнала: {self.current_short}.wav")
        
        thread = Thread(target=self.check_keys)
        thread.daemon = True
        thread.start()
        
        while self.running:
            if keyboard.is_pressed('esc'):
                self.running = False
            time.sleep(0.1)
        
        for channel in self.channels.values():
            channel.stop()
        pygame.mixer.quit()
        print("Программа завершена")

if __name__ == "__main__":
    player = SoundPlayer()
    player.run()