import os
import time
from math import floor



class BacklightSync(object):
    def __init__(self, quiet_mode=False):
        self.quiet = quiet_mode
        print('BacklightSync instantiated')

    def update_ext_display_list(self):
        self.display_list = os.listdir('/sys/class/backlight')
        self.display_list.remove('intel_backlight')

    def get_display_setting(self, display_name):
        base_path = '/sys/class/backlight'
        backlight_path = os.path.join(base_path, display_name)
        max_brightness_path = os.path.join(backlight_path, 'max_brightness')

        with open(max_brightness_path, 'rt') as max_file:
            max_brightness = int(max_file.read())

        settings = {
            'brightness_path': os.path.join(backlight_path, 'brightness'),
            'max_brightness': max_brightness
        }
        return settings

    def get_display_settings(self):
        self.update_ext_display_list()
        self.display_settings = {}
        
        for display_name in self.display_list:
            try:
                self.display_settings[display_name] = self.get_display_setting(display_name)
            except Exception as e:
                print(e)
                print('Something went wrong when reading the settings')

    def reload_ddcci_backlight(self):
        os.system('sudo modprobe -r ddcci_backlight && sudo modprobe ddcci_backlight')

    def sync(self, sleep_time):
        print('Start syncing...')
        
        base_path = '/sys/class/backlight'
        backlight_path = os.path.join(base_path, 'intel_backlight')
        max_path = os.path.join(backlight_path, 'max_brightness')
        actual_path = os.path.join(backlight_path, 'actual_brightness')

        self.get_display_settings()
        
        old_brightness = None
    
        while True:
            with open(str(max_path), 'rt') as max_file, open(str(actual_path), 'rt') as actual_file:
                max_brightness = int(max_file.read())
                actual_brightness = int(actual_file.read())

            if not actual_brightness == old_brightness:
                brightness = actual_brightness / max_brightness
                output_str = f'New brightness: {int(brightness*100)}%'

                if self.display_list == []:
                    self.reload_ddcci_backlight()
                    self.get_display_settings()
                
                for i, (display_name, display) in enumerate(self.display_settings.items()):
                
                    brightness_ext = int(floor(brightness * display['max_brightness']))

                    if brightness_ext > display['max_brightness']:
                        brightness_ext = display['max_brightness']
                    
                    # Set the minimum brightness of the OLED Screen,
                    # below the brightness of the external display is set to zero
                    min_brightness = 0.35
                    min_brightness_ext = min_brightness * display['max_brightness']

                    if brightness <= min_brightness:
                        brightness_ext = 0
                    else:
                        # Now account for this offset and linearly scale brightness to 100%
                        brightness_ext_unscaled = brightness_ext - min_brightness_ext
                        scale = display['max_brightness'] / (display['max_brightness'] - min_brightness_ext)

                        brightness_ext = int(brightness_ext_unscaled * scale)

                    try:
                        with open(display['brightness_path'], 'wt') as ext_display_brightness_file:
                            ext_display_brightness_file.write(f'{brightness_ext}')
                    except Exception as e:
                        print(e)
                        print('Something went wrong when writing the brightness settings, reload display settings...')
                        
                        self.reload_ddcci_backlight()
                        self.get_display_settings()
                        break

                    
                    output_str += f' | Screen {i}: {brightness_ext}%'
                    
                old_brightness = actual_brightness

                if not self.quiet:
                    print(output_str)
            
            time.sleep(sleep_time)

def main():
    import argparse

    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-s', '--sleep-time', type=float, default=2, help='Time between two brightness updates')
    parser.add_argument('--no-quiet', dest='quiet', action='store_false', help='Quietmode')

    args = parser.parse_args()

    Syncer = BacklightSync(quiet_mode=args.quiet)

    Syncer.sync(args.sleep_time)
    
    return 0

if __name__ == '__main__':
    import sys
    sys.exit( main() )
