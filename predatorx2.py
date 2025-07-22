import pygame
import keyboard
import os
import time
from threading import Thread

# Инициализация
pygame.mixer.init(frequency=44100, size=-16, channels=4, buffer=512)
pygame.mixer.set_num_channels(4)  # 4 канала: 0-короткий, 1-длинный, 2-сирена, 3-короткий поверх

class SoundPlayer:
    def __init__(self):
        self.sounds = {
            'short': None,
            'short_slower': None,
            'long': None,
            'siren': None,
            'short_over': None,
            'short_slower_over': None
        }
        self.channels = {
            'long': pygame.mixer.Channel(1),
            'siren': pygame.mixer.Channel(2),
            'short_over': pygame.mixer.Channel(3)  # Канал для короткого поверх других сигналов
        }
        self.current_short = 'short'
        self.load_sounds()
        self.running = True
        self.key_states = {
            '1': False,
            '2': False,
            '3': False,
            'm': False
        }
        self.background_active = None  # 'siren' или 'long' - что сейчас играет на фоне
        
    def load_sounds(self):
        """Загрузка звуков с проверкой"""
        sound_files = {
            'short': 'short.wav',
            'short_slower': 'short_slower.wav',
            'long': 'manual.wav',
            'siren': 'short_siren.wav',
            'short_over': 'short.wav',
            'short_slower_over': 'short_slower.wav'
        }
        
        for name, file in sound_files.items():
            if os.path.exists(file):
                self.sounds[name] = pygame.mixer.Sound(file)
                print(f"[Загружено] {file}")
            else:
                print(f"[Ошибка] Файл не найден: {file}")
    
    def play_sound(self, sound_type, loop=False, channel=None):
        """Улучшенное воспроизведение звуков"""
        if not channel:
            if sound_type in ['short_over', 'short_slower_over']:
                channel = self.channels['short_over']
            else:
                channel = self.channels.get(sound_type, None)
        
        if channel and self.sounds[sound_type] and not channel.get_busy():
            channel.play(self.sounds[sound_type], loops=-1 if loop else 0)
    
    def stop_sound(self, sound_type, fade=50):
        """Остановка звука с fadeout"""
        channel = None
        if sound_type in ['short_over', 'short_slower_over']:
            channel = self.channels['short_over']
        else:
            channel = self.channels.get(sound_type, None)
            
        if channel and channel.get_busy():
            channel.fadeout(fade)
    
    def toggle_short_sound(self):
        """Переключение между короткими звуками"""
        self.current_short = 'short_slower' if self.current_short == 'short' else 'short'
        print(f"Короткий звук изменен на {self.current_short}.wav")
        
        # Если короткий сигнал активен - перезапускаем его
        if self.key_states['1']:
            self.stop_sound('short_over')
            sound_to_play = f"{self.current_short}_over" if self.background_active else self.current_short
            self.play_sound(sound_to_play, loop=True)
    
    def check_keys(self):
        """Проверка состояния клавиш"""
        while self.running:
            # Переключение типа короткого звука
            if keyboard.is_pressed('m') and not self.key_states['m']:
                self.key_states['m'] = True
                self.toggle_short_sound()
            elif not keyboard.is_pressed('m') and self.key_states['m']:
                self.key_states['m'] = False
            
            # Сирена (3)
            if keyboard.is_pressed('3') and not self.key_states['3']:
                self.key_states['3'] = True
                self.background_active = 'siren'
                self.stop_sound('long')
                self.play_sound('siren', loop=True)
            elif not keyboard.is_pressed('3') and self.key_states['3']:
                self.key_states['3'] = False
                if self.background_active == 'siren':
                    self.background_active = None
                    self.stop_sound('siren')
                    # Если был активен короткий поверх - переключаем на обычный короткий
                    if self.key_states['1']:
                        self.stop_sound('short_over')
                        self.play_sound(self.current_short, loop=True)
            
            # Длинный сигнал (2)
            if keyboard.is_pressed('2') and not self.key_states['2']:
                self.key_states['2'] = True
                self.background_active = 'long'
                self.stop_sound('siren')
                self.play_sound('long', loop=True)
            elif not keyboard.is_pressed('2') and self.key_states['2']:
                self.key_states['2'] = False
                if self.background_active == 'long':
                    self.background_active = None
                    self.stop_sound('long')
                    # Если был активен короткий поверх - переключаем на обычный короткий
                    if self.key_states['1']:
                        self.stop_sound('short_over')
                        self.play_sound(self.current_short, loop=True)
            
            # Короткий сигнал (1)
            if keyboard.is_pressed('1') and not self.key_states['1']:
                self.key_states['1'] = True
                # Останавливаем фоновые звуки если они не активны
                if not self.background_active:
                    self.stop_sound('long')
                    self.stop_sound('siren')
                # Выбираем какой звук воспроизводить
                sound_to_play = f"{self.current_short}_over" if self.background_active else self.current_short
                self.play_sound(sound_to_play, loop=True)
            elif not keyboard.is_pressed('1') and self.key_states['1']:
                self.key_states['1'] = False
                self.stop_sound('short_over')
                self.stop_sound(self.current_short)
            
            time.sleep(0.01)
    
    def run(self):
        """Запуск программы"""
        print("PREDATOR VANTABLACK X1 – ПРОФЕССИОНАЛЬНЫЙ СИМУЛЯТОР СГУ")
        print(" [1] — Короткий сигнал (удерживать)")
        print("       (работает поверх сирены и длинного сигнала!)")
        print(" [2] — Длинный сигнал (удерживать)")
        print(" [3] — Сирена (удерживать)")
        print(" [M] — Переключить звук короткого сигнала")
        print(" [Esc] — Выход")
        print(f"\nТекущий звук короткого сигнала: {self.current_short}.wav")
        
        Thread(target=self.check_keys, daemon=True).start()
        
        while self.running:
            if keyboard.is_pressed('esc'):
                self.running = False
            time.sleep(0.1)
        
        pygame.mixer.quit()
        print("Программа завершена")

if __name__ == "__main__":
    player = SoundPlayer()
    player.run()