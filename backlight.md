## Fix of OLED Backlight

- Install ddcci_backlight 
- add ddcci module

TODO: Findout which module converts to the gamma values

## Sync Backlight with external screens
- Install https://gitlab.com/ddcci-driver-linux/ddcci-driver-linux
- Add/Edit /etc/sudoers.d/reload_ddcci
  Add:
  `fkunzweiler ALL=(ALL) NOPASSWD: /sbin/modprobe -r ddcci_backlight`
  `fkunzweiler ALL=(ALL) NOPASSWD: /sbin/modprobe ddcci_backlight`
- Run sync_backlight.py
