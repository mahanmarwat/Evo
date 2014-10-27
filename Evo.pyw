from gi.repository import Gtk, GdkPixbuf
from base import *

import threading
import time
import re
import os
import sys
import config

conf = config.conf['Custom']
pattern = (r'^https?://(www[.].+[.]|' +
           r'\d{1,3}[.]\d{1,3}[.]\d{1,3}[.]\d{1,3})')
server_pattern  = re.compile(pattern, re.IGNORECASE)
timeout_pattern = re.compile(r'^(None|[1-9]\d*)$', re.IGNORECASE)
wait_pattern    = re.compile(r'^[1-9]\d*$', re.IGNORECASE)

# Help File.
help_file = file('doc' + os.sep + 'Evo.html', False)

# Signal Images.
data_path = 'data' + os.sep
signal_0 = GdkPixbuf.Pixbuf.new_from_file(file(data_path + 'signal_0.gif'))
signal_1 = GdkPixbuf.Pixbuf.new_from_file(file(data_path + 'signal_1.gif'))
signal_2 = GdkPixbuf.Pixbuf.new_from_file(file(data_path + 'signal_2.gif'))
signal_3 = GdkPixbuf.Pixbuf.new_from_file(file(data_path + 'signal_3.gif'))
signal_4 = GdkPixbuf.Pixbuf.new_from_file(file(data_path + 'signal_4.gif'))
signal_5 = GdkPixbuf.Pixbuf.new_from_file(file(data_path + 'signal_5.gif'))

class PassDialog(Gtk.Dialog):
    def __init__(self, parent):
        Gtk.Dialog.__init__(self, "Password", parent, Gtk.DialogFlags.MODAL,
                            (Gtk.STOCK_OK, Gtk.ResponseType.OK))
        
        self.set_decorated(False)

        label = Gtk.Label('Password: ')
        self.pass_entry = Gtk.Entry()
        
        box = self.get_content_area()
        box2 = Gtk.Box(Gtk.Orientation.HORIZONTAL)
        box2.pack_start(label, True, True, 0)
        box2.pack_start(self.pass_entry, True, True, 0)
        box.add(box2)
        self.show_all()


class Main:
    """Main GUI class of Evo app."""
    def __init__(self):
        builder = Gtk.Builder()
        builder.add_from_file(file('Evo.glade'))

        self.window = builder.get_object('window')
        self.window.connect('destroy', self.main_quit)
        self.window.set_decorated(config.DECORATED)

        self.about = builder.get_object('about')

        self.notebook = builder.get_object('content')

        self.btn_connect = builder.get_object('btn_connect')
        self.btn_connect.connect('clicked', self.set_page, 0)
        btn_stat = builder.get_object('btn_stat')
        btn_stat.connect('clicked', self.set_page, 1)
        btn_setting = builder.get_object('btn_setting')
        btn_setting.connect('clicked', self.set_page, 2)
        btn_setting = builder.get_object('btn_about')
        btn_setting.connect('clicked', self.show_about)
        btn_setting = builder.get_object('btn_help')
        btn_setting.connect('clicked', self.show_help)

        # ____Page 1: Main
        # Left part.
        self.signal_tree = builder.get_object('signal_tree')
        renderer = Gtk.CellRendererText()
        column = builder.get_object('signal_column1')
        column.pack_start(renderer, True)
        column.add_attribute(renderer, 'text', 0)

        column = builder.get_object('signal_column2')
        column.pack_start(renderer, True)
        column.add_attribute(renderer, 'text', 1)

        renderer_pixbuf = Gtk.CellRendererPixbuf()
        column = builder.get_object('signal_column3')
        column.pack_start(renderer_pixbuf, True)
        column.add_attribute(renderer_pixbuf, 'pixbuf', 2)

        self.signal_store = builder.get_object('signal_store')
        self.signal_iter = self.signal_store.append([None, None, signal_0])
        self.signal_tree.set_model(self.signal_store)

        # Right part.
        self.conn_tree = builder.get_object('conn_tree')
        self.wlan_tree = builder.get_object('wlan_tree')
        renderer_bold = Gtk.CellRendererText()
        renderer_bold.props.weight = 600
        column = builder.get_object('treeviewcolumn3')
        column.pack_start(renderer_bold, True)
        column.add_attribute(renderer_bold, 'text', 0)

        column = builder.get_object('treeviewcolumn4')
        column.pack_start(renderer, True)
        column.add_attribute(renderer, 'text', 1)

        column = builder.get_object('treeviewcolumn5')
        column.pack_start(renderer_bold, True)
        column.add_attribute(renderer_bold, 'text', 0)

        column = builder.get_object('treeviewcolumn6')
        column.pack_start(renderer, True)
        column.add_attribute(renderer, 'text', 1)

        self.conn_store = builder.get_object('conn_store')
        self.conn_iter1 = self.conn_store.append(['Sent/Received', '0 B/0 B'])
        self.conn_iter2 = self.conn_store.append(['Duration', '00:00:00'])

        self.wlan_store = builder.get_object('wlan_store')
        self.wlan_iter1 = self.wlan_store.append(['WLAN Status', 'OFF'])
        self.wlan_iter2 = self.wlan_store.append(['Current WIFI User', '0/5'])

        self.conn_tree.set_model(self.conn_store)
        self.wlan_tree.set_model(self.wlan_store)
        # __________

        # ____Page 2: Stats
        self.device_tree = builder.get_object('device_tree')
        column = builder.get_object('device_column1')
        column.pack_start(renderer, True)
        column.add_attribute(renderer, 'text', 0)

        column = builder.get_object('device_column2')
        column.pack_start(renderer, True)
        column.add_attribute(renderer, 'text', 1)

        self.device_store = builder.get_object('device_store')
        threading.Thread(target=self.fill_store,
                         args=(self.device_store, device_info)).start()

        self.device_tree.set_model(self.device_store)

        # We dont need it yet.
        builder.get_object('stat_notebook').remove_page(1)
        
        self.stat_tree = builder.get_object('stat_tree')
        column = builder.get_object('stat_column1')
        column.pack_start(renderer, True)
        column.add_attribute(renderer, 'text', 0)

        column = builder.get_object('stat_column2')
        column.pack_start(renderer, True)
        column.add_attribute(renderer, 'text', 1)

        column = builder.get_object('stat_column3')
        column.pack_start(renderer, True)
        column.add_attribute(renderer, 'text', 2)

        self.stat_store = builder.get_object('stat_store')
        threading.Thread(target=self.fill_store,
                         args=(self.stat_store, statistics)).start()

        self.stat_tree.set_model(self.stat_store)
        # __________

        # ____Page 3: Settings
        self.theme_store = builder.get_object('theme_store')
        self.theme_combo = builder.get_object('theme_combo')
        self.theme_combo.set_model(self.theme_store)
        self.theme_combo.pack_start(renderer, True)
        self.theme_combo.add_attribute(renderer, "text", 0)
        self.theme_combo.set_active(config.THEME)

        self.btn_deco = builder.get_object('btn_deco')
        self.btn_deco.set_sensitive(True)
        self.btn_deco.set_active(config.DECORATED)

        self.btn_pass = builder.get_object('btn_pass')
        self.btn_pass.set_active(config.PASSWORD_PROTECTED)
        self.btn_pass.connect('toggled', self.activate_fields)

        self.pass_box = builder.get_object('pass_box')
        btn_change_pass = builder.get_object('btn_change_pass')
        btn_change_pass.connect('clicked', self.change_pass)

        self.old_pass = builder.get_object('old_pass')
        self.new_pass = builder.get_object('new_pass')

        btn_general = builder.get_object('btn_general')
        btn_general.connect('clicked', self.general_setting)

        self.entry_server = builder.get_object('entry_server')
        self.entry_server.set_text(config.CONNECTION_CHECKING_SERVER)
        self.entry_timeout = builder.get_object('entry_timeout')
        self.entry_timeout.set_text(str(config.RESPONSE_WAIT))
        self.entry_wait = builder.get_object('entry_wait')
        self.entry_wait.set_text(str(config.REQUEST_WAIT))

        btn_conn = builder.get_object('btn_conn')
        btn_conn.connect('clicked', self.conn_setting)
        # __________

        # Change theme of the app.
        themes = ['Default', 'Greybird']
        setting = Gtk.Settings.get_default()
        setattr(setting.props, 'gtk-theme-name', themes[config.THEME])
        
        self.window.show_all()
        if config.PASSWORD_PROTECTED:
            builder.get_object('main_content').hide()
            self.pass_dialog()
            builder.get_object('main_content').show()
            # Activate self.pass_box if password protected.
            self.activate_fields(self.btn_pass)

        self.exit_thread = False
        self.conn_thread = threading.Thread(target=self.check_conn)
        self.conn_thread.start()
        
        self.stat1_thread = threading.Thread(target=self.update_stat1)
        self.stat1_thread.start()
        
        self.stat2_thread = threading.Thread(target=self.update_stat2)
        self.stat2_thread.start()

    def main_quit(self, signal):
        self.exit_thread = True
        Gtk.main_quit()

    def set_page(self, widget=None, data=None):
        self.notebook.set_current_page(data)

    def show_about(self, widget=None, data=None):
        self.about.get_action_area().forall(lambda w, d: w.set_label('Close'),
                                            None)
        self.about.show_all()
        self.about.run()
        self.about.hide()

    def show_help(self, widget=None, data=None):
        if sys.platform.startswith('win'):
            os.startfile(help_file)
        else:
            self.msg_dialog('Documentation is in Doc dir.',
                            r'Evo\Doc\Evo.html',
                            'info')

    def fill_store(self, store, func):
        if func.__name__ == 'device_info':
            func = lambda: sorted(device_info())
        for i in func():
            store.append(i)

    def activate_fields(self, widget, data=None):
        is_active = widget.get_active()
        if is_active:
            self.pass_box.set_sensitive(True)
        else:
            self.pass_box.set_sensitive(False)

    def make_setting(self):
        with open(file('config.ini'), 'w') as cf:
            config.conf.write(cf)

    def change_icon(self, widget, data=None):
        '''
        img = Gtk.Image()
        if widget.get_label().upper() == 'GTK-OK':
            img.set_from_stock(Gtk.STOCK_YES, 16)
        else:
            img.set_from_stock(Gtk.STOCK_NO, 16)
        widget.set_image(img)
        '''
        widget.set_label('OK')

    def msg_dialog(self, msg='', s_msg='', type_='info'):
        if type_ == 'info':
            msg_type = Gtk.MessageType.INFO
            #msg_btn  = Gtk.ButtonsType.OK
        elif type_ == 'warn':
            msg_type = Gtk.MessageType.WARNING
            #msg_btn  = Gtk.ButtonsType.OK_CANCEL
        elif type_ == 'err':
            msg_type = Gtk.MessageType.ERROR
            #msg_btn  = Gtk.ButtonsType.CANCEL
        else:
            msg_type = Gtk.MessageType.QUESTION
            #msg_btn  = Gtk.ButtonsType.YES_NO
        msg_btn  = Gtk.ButtonsType.OK
        dialog = Gtk.MessageDialog(self.window, 0, msg_type,
                                   msg_btn, msg)
        dialog.get_action_area().forall(self.change_icon, None)
        dialog.format_secondary_text(s_msg)
        dialog.set_decorated(False)
        dialog.run()
        dialog.destroy()

    def pass_dialog(self):
        while True:
            dialog = PassDialog(self.window)
            dialog.get_action_area().forall(self.change_icon, None)
            response = dialog.run()
            if response == Gtk.ResponseType.OK:
                password = pass_hash(dialog.pass_entry.get_text())
                if password == config.PASSWORD:
                    break
                else:
                    dialog.destroy()
                    continue
        dialog.destroy()

    def change_pass(self, widget, data=None):
        old_pass = self.old_pass.get_text()
        new_pass = self.new_pass.get_text()
        if old_pass == '' or new_pass == '':
            self.msg_dialog('Password Field Empty', '', 'err')
        elif pass_hash(old_pass) != config.PASSWORD:
            self.msg_dialog('Wrong Password', '', 'warn')
        else:
            conf['hash'] = pass_hash(new_pass)
            self.make_setting()
            self.msg_dialog('Password Successfully Changed', '', 'info')

    def general_setting(self, widget, data=None):
        theme = self.theme_combo.get_active()
        decorated = self.btn_deco.get_active()
        password_protected = self.btn_pass.get_active()
        conf['theme'] = str(theme)
        conf['decorated'] = str(decorated)
        conf['password_protected'] = str(password_protected)
        self.make_setting()
        self.msg_dialog('Setting Successfully Made', '', 'info')

    def conn_setting(self, widget, data=None):
        server  = self.entry_server.get_text()
        timeout = self.entry_timeout.get_text()
        wait    = self.entry_wait.get_text()
        if not server_pattern.match(server):
            self.msg_dialog('Server Field Error', '', 'err')
            return
        if not timeout_pattern.match(timeout):
            self.msg_dialog('Timeout Field Error', '', 'err')
            return
        if not wait_pattern.match(wait):
            self.msg_dialog('Request Field Error', '', 'err')
            return
        conf['connection_checking_server'] = server
        conf['response_wait'] = str(timeout)
        conf['request_wait'] = str(wait)
        self.make_setting()
        self.msg_dialog('Setting Successfully Made', '', 'info')

    def update_stat1(self):
        while not self.exit_thread:
            data = sent_received()
            if data:
                self.conn_store[self.conn_iter1][1] = data[0]
                self.conn_store[self.conn_iter2][1] = data[1]
            time.sleep(.100)

    def update_stat2(self):
        while not self.exit_thread:
            stat = status()
            if stat:
                wifi = 'ON' if stat['wifi_status'] == '1' else 'OFF'
                user = stat['current_user'] + '/' + stat['total_user']
                self.wlan_store[self.wlan_iter1][1] = wifi
                self.wlan_store[self.wlan_iter2][1] = user
                self.signal_store[self.signal_iter][0] = stat['network']
                self.signal_store[self.signal_iter][1] = stat['signal']
                icon = stat['signal_icon']
                if   icon == '0': signal_icon = signal_0
                elif icon == '1': signal_icon = signal_1
                elif icon == '2': signal_icon = signal_2
                elif icon == '3': signal_icon = signal_3
                elif icon == '4': signal_icon = signal_4
                elif icon == '5': signal_icon = signal_5
                self.signal_store[self.signal_iter][2] = signal_icon
            time.sleep(.100)

    def check_conn(self):
        while not self.exit_thread:
            if connect(server=config.CONNECTION_CHECKING_SERVER,
                       timeout=config.RESPONSE_WAIT):
                if self.btn_connect.props.stock_id == Gtk.STOCK_YES:
                    pass
                else:
                    self.btn_connect.set_stock_id(Gtk.STOCK_YES)
            else:
                if self.btn_connect.props.stock_id == Gtk.STOCK_NO:
                    pass
                else:
                    self.btn_connect.set_stock_id(Gtk.STOCK_NO)
            if self.exit_thread: break
            time.sleep(config.REQUEST_WAIT)


if __name__ == '__main__':
    main = Main()
    Gtk.main()
