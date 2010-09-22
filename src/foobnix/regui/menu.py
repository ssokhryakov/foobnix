'''
Created on Sep 22, 2010

@author: ivan
'''
import gtk
from foobnix.util import LOG
import sys
from foobnix.util.configuration import FConfiguration
class MenuWidget():
    def __init__(self):
        """TOP menu constructor"""
        
        top = TopMenu()
        """File"""
        file = top.append("File")
        file.add_image_item("Add File(s)", gtk.STOCK_OPEN)
        file.add_image_item("Add Folder(s)", gtk.STOCK_OPEN)     
        file.separator()   
        file.add_image_item("Quit", gtk.STOCK_QUIT, self.on_save)
        
        
        """View"""
        view = top.append("View")
        self.view_music_tree = view.add_ckeck_item("Music Tree")
        view.add_ckeck_item("Search Panel", True)
        view.separator()
        view.add_ckeck_item("Lyric Panel", True)
        view.add_ckeck_item("Info Panel", False)
        view.separator()
        view.add_image_item("Preferences", gtk.STOCK_PREFERENCES)        
        
        """Playback"""
        playback = top.append("Playback")      
        
        """Playback - Order"""
        order = playback.add_text_item("Order")
        linear = order.add_radio_item("Linear", None, True)
        order.add_radio_item("Random", linear, True)
        order.separator()
        order.add_image_item("Shuffle", gtk.STOCK_UNDELETE)
        
        """Playback - Repeat"""      
        repeat = playback.add_text_item("Repeat")
        all = repeat.add_radio_item("All", None, True) 
        repeat.add_radio_item("Single", all, True)
        repeat.add_radio_item("Disable", all, True)
        
        """Help"""
        help = top.append("Help")
        help.add_image_item("About", gtk.STOCK_ABOUT)
        help.add_image_item("Help", gtk.STOCK_HELP)
        
        top.decorate()        
        self.widget = top.widget
        
        self.on_load()
    
    def on_load(self):
        self.view_music_tree.set_active(FConfiguration().view_tree_panel)
    
    def on_save(self):
        FConfiguration().view_tree_panel = self.view_music_tree.get_active()
        FConfiguration().save()
        sys.exit(1)
        
        
        

"""My custom menu class for helping buildings"""
class MyMenu(gtk.Menu):
    def __init__(self):
        gtk.Menu.__init__(self)
    
    def add_image_item(self, title, gtk_stock, func=None, param=None):
        item = gtk.ImageMenuItem(title)
        item.show()
        img = gtk.image_new_from_stock(gtk_stock, gtk.ICON_SIZE_MENU)
        item.set_image(img) 
        
        LOG.debug("Menu-Image-Activate", title, gtk_stock, func, param)
        if param:             
            item.connect("activate", lambda * a: func(param))
        else:
            item.connect("activate", lambda * a: func())            
                
        self.append(item)
    
    def separator(self):
        separator = gtk.SeparatorMenuItem()
        separator.show()
        self.append(separator)
    
    def add_ckeck_item(self, title, active=False):
        check = gtk.CheckMenuItem(title)
        check.show()
        check.set_active(active)
        self.append(check)
        return check        
    
    def add_radio_item(self, title, group, active):
        check = gtk.RadioMenuItem(group, title)
        check.show()
        check.set_active(active)
        self.append(check)
        return check
    
    def add_text_item(self, title):
        sub = gtk.MenuItem(title)
        sub.show()
        self.append(sub)
        
        menu = MyMenu()
        menu.show()        
        sub.set_submenu(menu)
        
        return menu

"""My top menu bar helper"""
class TopMenu():
    def __init__(self):
        rc_st = '''
            style "menubar-style" { 
                GtkMenuBar::shadow_type = none
                GtkMenuBar::internal-padding = 0
                }
            class "GtkMenuBar" style "menubar-style"
        '''
        gtk.rc_parse_string(rc_st)
                
        self.menu_bar = gtk.MenuBar()
        self.menu_bar.show()
       
        self.widget = self.menu_bar
    
    def decorate(self):
        label = gtk.Label()
        style = label.get_style()
        background_color = style.bg[gtk.STATE_NORMAL]
        text_color = style.fg[gtk.STATE_NORMAL]
       
        self.menu_bar.modify_bg(gtk.STATE_NORMAL, background_color)

        # making main menu look a bit better
        for item in self.menu_bar.get_children():
            current = item.get_children()[0]
            current.modify_fg(gtk.STATE_NORMAL, text_color)
        
    def append(self, title):
        menu = MyMenu()
        menu.show()
        
        file_item = gtk.MenuItem(title)
        file_item.show()
        
        file_item.set_submenu(menu)
        
        self.menu_bar.append(file_item)
        
        return menu
    
        