import os, glob, gi, widgets
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk

FINDING_HEADER = 0
FINDING_TAGS = 1

# 言語
lang = os.environ["LANG"].split("_")[0]

entries = []

if __name__ == "__main__":
    # デスクトップエントリの検索
    entryfilelist = glob.glob("/usr/share/applications/*.desktop")
    # entryfilelist = sorted(entryfilelist)
    # print("\n".join(entryfilelist))

    # デスクトップエントリの解析
    for entry in entryfilelist:
        with open(entry, "r") as f:
            phase = FINDING_HEADER
            name = None
            comment = None
            icon = None
            command = None
            nodisplay = False
            for line in f:
                line = line.lstrip().rstrip()
                # コメントなら無視する
                if line[:1] == "#":
                    continue
                # ヘッダを探す
                if phase == FINDING_HEADER:
                    if line == "[Desktop Entry]":
                        phase = FINDING_TAGS
                        continue
                # タグを探す
                elif phase == FINDING_TAGS:
                    # ヘッダなら終了
                    if line[:1] == "[":
                        break

                    param = line.split("=")[0]
                    value = line[len(param) + 1:].lstrip()
                    param = param.rstrip()
                    # 名前
                    if param == f"Name[{lang}]":
                        name = value
                    elif param == "Name":
                        name = value if name == None else name
                    # コメント
                    elif param == f"Comment[{lang}]":
                        comment = value
                    elif param == "Comment":
                        comment = value if comment == None else comment
                    # アイコン
                    elif param == "Icon":
                        icon = value
                    # コマンド
                    elif param == "Exec":
                        command = value.replace(" %f", "").replace("%F", "").replace(" %u", "").replace(" %U", "")
                    elif param == "NoDisplay" and value == "true":
                        nodisplay = True
            # 配列に追加
            if nodisplay == False:
                entries.append(widgets.DesktopEntry(name, comment, icon, command))
                # print(f"Name = {name}\nComment = {comment}\nIcon = {icon}\nExec = {command}\n")
    
    entries = sorted(entries, key=lambda t: t.name)

    # CSSの適用
    cssprovider = Gtk.CssProvider()
    cssprovider.load_from_path("/home/mine/easylauncher/gtk.css")
    Gtk.StyleContext.add_provider_for_screen(
        Gdk.Screen.get_default(),
        cssprovider,
        Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
    )
    # ウィンドウの生成
    menuwindow = widgets.MenuWindow(entries)
    menuwindow.connect("destroy", Gtk.main_quit)
    menuwindow.show_all()
    Gtk.main()
