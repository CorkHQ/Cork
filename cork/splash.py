import gi
import threading

gi.require_version("Gtk", "3.0")
gi.require_version('GdkPixbuf', '2.0')

from gi.repository.GdkPixbuf import Pixbuf
from gi.repository import Gtk

class GtkCorkSplash(Gtk.Window):
    def __init__(self, icon):

        super().__init__(title="Cork")
        self.set_default_size(450, 300)
        self.set_resizable(False)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_decorated(False)
        self.set_border_width(16)

        self.set_deletable(False)

        self.image = Gtk.Image()
        self.image.set_from_pixbuf(
            Gtk.IconTheme.get_default().load_icon(icon, 112, 0))
        self.image.set_hexpand(True)

        self.spinner = Gtk.Spinner()
        self.spinner.set_hexpand(True)

        self.label = Gtk.Label(label="")
        self.label.set_hexpand(True)

        self.grid = Gtk.Grid()

        self.grid.attach(self.image, 1, 0, 1, 3)
        self.grid.attach_next_to(
            self.spinner, self.image, Gtk.PositionType.BOTTOM, 1, 1
        )
        self.grid.attach_next_to(
            self.label, self.spinner, Gtk.PositionType.BOTTOM, 1, 1
        )
        self.grid.set_row_homogeneous(True)

        self.add(self.grid)
        self.spinner.start()
        self.show_all()
    
    def set_text(self, text):
        self.label.set_text(text)

class CorkSplash():
    def __init__(self):
        pass
    
    def show(self, icon):
        self.gtk_splash = GtkCorkSplash(icon)
        def gtk_function():
            Gtk.main()
        
        self.gtk_thread = threading.Thread(target=gtk_function)
        self.gtk_thread.start()
    
    def set_text(self, text):
        if self.gtk_splash is None:
            return

        self.gtk_splash.set_text(text)
    
    def close(self):
        self.gtk_splash.destroy()
        Gtk.main_quit()