import gi
import threading

gi.require_version("Gtk", "3.0")

from gi.repository import GLib, Gtk

class GtkCorkSplash(Gtk.Window):
    def ignore(self, *args):
        return Gtk.TRUE
    def __init__(self, icon):

        super().__init__(title="Cork")
        self.set_default_size(380, 240)
        self.set_resizable(False)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_border_width(16)

        self.set_deletable(False)
        self.connect('delete_event', self.ignore)

        self.image = Gtk.Image.new_from_icon_name(icon, Gtk.IconSize.DIALOG)
        self.image.set_pixel_size(112)
        self.image.set_hexpand(True)

        self.progressbar = Gtk.ProgressBar()
        self.progressbar.set_pulse_step(0.05)

        self.label = Gtk.Label(label="")
        self.label.set_hexpand(True)

        self.grid = Gtk.Grid()

        self.grid.attach(self.image, 1, 0, 1, 2)
        self.grid.attach_next_to(
            self.progressbar, self.image, Gtk.PositionType.BOTTOM, 1, 1
        )
        self.grid.attach_next_to(
            self.label, self.image, Gtk.PositionType.BOTTOM, 1, 1
        )
        self.grid.set_row_homogeneous(True)

        self.add(self.grid)
        self.show_all()
        self.activity_mode = False
        self.timeout_id = GLib.timeout_add(50, self.on_timeout, None)
    
    def set_text(self, text):
        if self.label.get_label() != text:
            self.label.set_text(text)
    
    def set_progress(self, progress):
        if self.progressbar.get_fraction() != progress:
            self.progressbar.set_fraction(progress)
    
    def set_progress_mode(self, mode):
        if mode == False and self.activity_mode == True:
            self.progressbar.set_fraction(0)
        
        self.activity_mode = mode
    
    def on_timeout(self, user_data):
        if self.activity_mode:
            self.progressbar.pulse()
        
        return True

class CorkSplash():
    def __init__(self):
        self.is_showing = False
    
    def show(self, icon):
        self.is_showing = True

        self.gtk_splash = GtkCorkSplash(icon)
        def gtk_function():
            Gtk.main()
        
        self.gtk_thread = threading.Thread(target=gtk_function, daemon=True)
        self.gtk_thread.start()
    
    def set_text(self, text):
        if self.gtk_splash is None:
            return

        self.gtk_splash.set_text(text)
    
    def set_progress(self, progress):
        if self.gtk_splash is None:
            return

        self.gtk_splash.set_progress(progress)
    
    def set_progress_mode(self, mode):
        if self.gtk_splash is None:
            return

        self.gtk_splash.set_progress_mode(mode)
    
    def close(self):
        self.is_showing = False
        
        self.gtk_splash.destroy()
        Gtk.main_quit()