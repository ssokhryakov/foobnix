#-*- coding: utf-8 -*-
'''
Created on 25 сент. 2010

@author: ivan
'''

import re
import gtk
import logging

from foobnix.fc.fc import FC
from foobnix.util import const
from foobnix.helpers.menu import Popup
from foobnix.util.tag_util import edit_tags
from foobnix.util.converter import convert_files
from foobnix.util.audio import get_mutagen_audio
from foobnix.util.file_utils import open_in_filemanager
from foobnix.regui.treeview.common_tree import CommonTreeControl
from foobnix.util.key_utils import KEY_RETURN, is_key, KEY_DELETE
from foobnix.util.mouse_utils import is_double_left_click, is_rigth_click_release, \
    is_rigth_click



class PlaylistTreeControl(CommonTreeControl):
    def __init__(self, controls):
        CommonTreeControl.__init__(self, controls)
        
        self.set_headers_visible(True)
        self.set_headers_clickable(True)
        
        """Column icon"""
        icon = gtk.TreeViewColumn(None, gtk.CellRendererPixbuf(), stock_id=self.play_icon[0])
        icon.set_fixed_width(5)
        icon.set_min_width(5)
        self.append_column(icon)
        
        """track number"""
        tracknumber = gtk.TreeViewColumn("№", gtk.CellRendererText(), text=self.tracknumber[0])
        tracknumber.set_clickable(True)
        num_label = gtk.Label("№")
        num_label.show()
        tracknumber.set_widget(num_label)
        
        self.append_column(tracknumber)
        
        num_button = num_label.get_parent().get_parent().get_parent()
        num_button.menu = Popup()
        self.num_order = gtk.RadioMenuItem(None, _("Numering by order"))
        self.num_order.connect("button-press-event", self.on_toggled_num)
        self.num_tags = gtk.RadioMenuItem(self.num_order, _("Numering by tags"))
        self.num_tags.connect("button-press-event", self.on_toggled_num)
        
        num_button.menu.append(self.num_order)
        num_button.menu.append(self.num_tags)
        num_button.connect("button-press-event", self.on_click_header)
        
        
        """column artist title"""
        description = gtk.TreeViewColumn('Track', gtk.CellRendererText(), text=self.text[0], font=self.font[0])
        #description.set_sizing(gtk.TREE_VIEW_COLUMN_AUTOSIZE)
        description.set_expand(True)
        description.set_resizable(True)
        self.append_column(description)
                
        """column artist (NOT USED)"""
        artist = gtk.TreeViewColumn('Artist', gtk.CellRendererText(), text=self.artist[0])
        artist.set_sizing(gtk.TREE_VIEW_COLUMN_AUTOSIZE)
        #self.append_column(artist)
        
        """column title (NOT USED)"""
        title = gtk.TreeViewColumn('Title', gtk.CellRendererText(), text=self.title[0])
        title.set_sizing(gtk.TREE_VIEW_COLUMN_AUTOSIZE)
        #self.append_column(title)

        """column time"""
        time = gtk.TreeViewColumn('Time', gtk.CellRendererText(), text=self.time[0])
        
        self.append_column(time)

        self.configure_send_drug()
        self.configure_recive_drug()
        
        self.set_playlist_plain()
        
        self.connect("button-release-event", self.on_button_release)
        
        self.on_load()
    
    def set_playlist_tree(self):
        self.rebuild_as_tree()
        
    def set_playlist_plain(self):
        self.rebuild_as_plain()
        
    def on_key_release(self, w, e):
        if is_key(e, KEY_RETURN):
            self.controls.play_selected_song()
        elif is_key(e, KEY_DELETE):
            self.delete_selected()     
        elif is_key(e, 'Left'):
            self.controls.seek_down()
        elif is_key(e, 'Right'):
            self.controls.seek_up()
    
    def common_single_random(self):
        logging.debug("Repeat state" + str(FC().repeat_state))
        if FC().repeat_state == const.REPEAT_SINGLE:
            return self.get_current_bean_by_UUID();
        
        if FC().is_order_random:               
            bean = self.get_random_bean()
            self.set_play_icon_to_bean(bean)
            return bean
    
    def next(self):
        bean = self.common_single_random()       
        if bean:
            return bean
        
        bean = self.get_next_bean(FC().repeat_state == const.REPEAT_ALL)
        
        if not bean:
            return
        
        self.set_play_icon_to_bean(bean)
           
        self.scroll_follow_play_icon()            
        
        logging.debug("Next bean" + str(bean) + bean.text)
        
        return bean

    def prev(self):
        bean = self.common_single_random()       
        if bean:
            return bean
    
        bean = self.get_prev_bean(FC().repeat_state == const.REPEAT_ALL)
        
        if not bean:
            return
                
        self.set_play_icon_to_bean(bean)
        
        self.scroll_follow_play_icon() 
        
        return bean
    
    def scroll_follow_play_icon(self):
        paths = [(i,) for i, row in enumerate(self.model)]
        for row, path in zip(self.model, paths):
            if row[self.play_icon[0]]:
                start_path, end_path = self.get_visible_range()
                if path > end_path or path < start_path:
                    self.scroll_to_cell(path)
    
    def append(self, bean):
        return super(PlaylistTreeControl, self).append(bean)

    def on_button_press(self, w, e):
        #self.controls.notetabs.set_active_tree(self)
        if is_rigth_click(e):
            """to avoid unselect all selected items"""
            self.stop_emission('button-press-event')
        if is_double_left_click(e):
            self.controls.play_selected_song()
            
    def on_button_release(self, w, e):
        if is_rigth_click_release(e):
            """to select item under cursor"""
            try:
                path, col, cellx, celly = self.get_path_at_pos(int(e.x), int(e.y))
                self.get_selection().select_path(path)
            except TypeError:
                pass
            #menu.add_item('Save as', gtk.STOCK_SAVE_AS, self.controls.save_beans_to, self.get_all_selected_beans())
            
            beans = self.get_selected_beans()
            
            if beans:
                menu = Popup()
                menu.add_item(_('Play'), gtk.STOCK_MEDIA_PLAY, self.controls.play_selected_song, None)
                menu.add_item(_('Download'), gtk.STOCK_ADD, self.controls.dm.append_tasks, self.get_all_selected_beans())
                menu.add_item(_('Download To...'), gtk.STOCK_ADD, self.controls.dm.append_tasks_with_dialog, self.get_all_selected_beans())
                menu.add_separator()
                paths = [bean.path for bean in beans]
                if paths[0]:
                    menu.add_item(_('Edit Tags'), gtk.STOCK_EDIT, edit_tags, (self.controls, paths))
                    menu.add_item(_('Format Converter'), gtk.STOCK_CONVERT, convert_files, paths)
                text = self.get_selected_bean().text
                menu.add_item(_('Copy To Search Line'), gtk.STOCK_COPY, self.controls.searchPanel.set_search_text, text)
                menu.add_separator()
                menu.add_item(_('Copy №-Title-Time'), gtk.STOCK_COPY, self.copy_info_to_clipboard)
                menu.add_item(_('Copy Artist-Title-Album'), gtk.STOCK_COPY, self.copy_info_to_clipboard, True)
                menu.add_separator()
                menu.add_item(_('Love This Track(s)'), None, self.controls.love_this_tracks, self.get_all_selected_beans())
                menu.add_separator()
                if paths[0]:
                    menu.add_item(_("Open In File Manager"), None, open_in_filemanager, paths[0])
                menu.show(e)
            
    def on_click_header(self, w, e):
        if is_rigth_click(e):
            w.menu.show(e)
            
    def on_toggled_num(self, *a):
        FC().numbering_by_order = not FC().numbering_by_order
        if FC().numbering_by_order:
            self.rebuild_as_plain()
            return
        for row in self.model:
            if row[self.is_file[0]]:
                audio = get_mutagen_audio(row[self.path[0]])
                if audio and audio.has_key('tracknumber'):
                    row[self.tracknumber[0]] = re.search('\d*', audio['tracknumber'][0]).group()
                if audio and audio.has_key('trkn'):
                    row[self.tracknumber[0]] = re.search('\d*', audio["trkn"][0]).group()
    
    def on_load(self):
        if FC().numbering_by_order:
            self.num_order.set_active(True)
        else:
            self.num_tags.set_active(True)