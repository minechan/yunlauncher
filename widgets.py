import os, subprocess, glob, gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Pango, Gdk

# デスクトップエントリ用クラス
class DesktopEntry:
    def __init__(self, name, comment, icon, command):
        self.__name = name
        self.__comment = comment
        self.__icon = icon
        self.__command = command

    @property
    def name(self):
        return self.__name

    @property
    def comment(self):
        return self.__comment

    @property
    def icon(self):
        return self.__icon

    @property
    def command(self):
        return self.__command

# ランチャー用ボタンのクラス
class LauncherButton(Gtk.Button):
    def __init__(self, entry):
        super().__init__(self, label=None)
        self.__entry = entry

        # ボタン用のボックス
        __button_box = Gtk.Box(spacing=2, orientation=Gtk.Orientation.VERTICAL)
        __icon = Gtk.Image.new_from_icon_name(self.__entry.icon, 3)
        __icon.set_pixel_size(48)
        __button_box.pack_start(__icon, True, True, 0)
        __label = Gtk.Label()
        __label.set_text(self.__entry.name)
        __label.set_ellipsize(Pango.EllipsizeMode.END)
        __button_box.pack_start(__label, True, True, 0)

        self.add(__button_box)
        self.connect("clicked", self.execute)

    def execute(self, widget):
        subprocess.Popen(self.__entry.command, shell=True)
        Gtk.main_quit()

COLUMN = 6
ROW = 5
WIDTH = 150
HEIGHT = 80
PADDING = 10

# ウィンドウのクラス
class MenuWindow(Gtk.Window):
    def __init__(self, entries):
        super().__init__()
        self.set_default_size(COLUMN * WIDTH + PADDING * 2, ROW * HEIGHT + PADDING * 2)
        self.set_position(Gtk.WindowPosition.CENTER_ALWAYS)

        self.__searchentry = Gtk.SearchEntry()
        self.set_titlebar(self.__searchentry)

        mainbox = Gtk.Box(spacing=2, orientation=Gtk.Orientation.VERTICAL)
        self.add(mainbox)

        stack = Gtk.Stack()
        stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT_RIGHT)
        stack.set_transition_duration(500)
        mainbox.pack_start(stack, True, True, 0)

        self.__pagenum = len(entries) // (COLUMN * ROW) + 1

        for page in range(len(entries) // (COLUMN * ROW) + 1):
            grid = Gtk.Grid()
            grid.set_column_spacing(COLUMN)
            grid.set_column_homogeneous(False)
            grid.set_row_spacing(ROW)
            grid.set_row_homogeneous(False)
            grid.add_events(Gdk.EventMask.SCROLL_MASK)
            grid.connect("scroll-event", self.scroll)
            for i in range(ROW):
                for j in range(COLUMN):
                    if (COLUMN * ROW * page) + (i * COLUMN) + j >= len(entries):
                        continue
                    button = LauncherButton(entries[(COLUMN * ROW * page) + (i * COLUMN) + j])
                    grid.attach(button, j, i, 1, 1)
            stack.add_titled(grid, str(page + 1), str(page + 1))

        stackswitcher = Gtk.StackSwitcher()
        stackswitcher.set_stack(stack)
        mainbox.pack_start(stackswitcher, True, True, 0)

        self.connect("focus-out-event", Gtk.main_quit)
        self.set_skip_taskbar_hint(True)

    def scroll(widget, event, user_data):
        print("scrolled")
        if event.direction == Gdk.ScrollDirection.UP:
            self.set_visible_child_name(str(math.max(1, int(self.get_visible_child_name()) - 1)))
        elif event.direction == Gdk.ScrollDirection.DOWN:
            self.set_visible_child_name(str(math.min(self.__pagenum, int(self.get_visible_child_name()) + 1)))
