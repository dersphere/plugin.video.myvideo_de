#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#     Copyright (C) 2012 Tristan Fischer (sphere@dersphere.de)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program. If not, see <http://www.gnu.org/licenses/>.
#

from xbmcswift2 import Plugin, xbmc
import resources.lib.scraper as scraper

STRINGS = {
    'page': 30000,
    'search': 30001,
}

plugin = Plugin()


@plugin.route('/')
def show_categories():
    items = [{
        'label': category['title'],
        'path': plugin.url_for(
            endpoint='show_subcategories',
            path=category['path']
        )
    } for category in scraper.get_categories()]
    items.append({
        'label': _('search'),
        'path': plugin.url_for('video_search')}
    )
    return plugin.finish(items)


@plugin.route('/search/')
def video_search():
    search_string = __keyboard(_('search'))
    if search_string:
        __log('search gots a string: "%s"' % search_string)
        url = plugin.url_for(
            endpoint='video_search_result',
            search_string=search_string
        )
        plugin.redirect(url)


@plugin.route('/search/<search_string>/')
def video_search_result(search_string):
    items = scraper.get_search_result(search_string)
    return __add_items(items)


@plugin.route('/category/<path>/')
def show_subcategories(path):
    categories = scraper.get_sub_categories(path)
    items = [{
        'label': category['title'],
        'path': plugin.url_for(
            endpoint='show_path',
            path=category['path']
        )
    } for category in categories]
    return plugin.finish(items)


@plugin.route('/<path>/')
def show_path(path):
    items = scraper.get_path(path)
    return __add_items(items)


def __add_items(entries):
    items = []
    update_on_pageswitch = plugin.get_setting('update_on_pageswitch') == 'true'
    has_icons = False
    is_update = False
    for entry in entries:
        if not has_icons and entry.get('thumb'):
            has_icons = True
        if entry.get('pagenination'):
            if entry['pagenination'] == 'PREV':
                if update_on_pageswitch:
                    is_update = True
                title = '<< %s %s <<' % (_('page'), entry['title'])
            elif entry['pagenination'] == 'NEXT':
                title = '>> %s %s >>' % (_('page'), entry['title'])
            items.append({
                'label': title,
                'icon': 'DefaultFolder.png',
                'path': plugin.url_for(
                    endpoint='show_path',
                    path=entry['path']
                )
            })
        elif entry['is_folder']:
            items.append({
                'label': entry['title'],
                'icon': entry.get('thumb', 'DefaultFolder.png'),
                'path': plugin.url_for(
                    endpoint='show_path',
                    path=entry['path']
                )
            })
        else:
            items.append({
                'label': entry['title'],
                'icon': entry.get('thumb', 'DefaultVideo.png'),
                'info': {
                    'duration': entry.get('length', '0:00'),
                    'plot': entry.get('description', ''),
                    'studio': entry.get('username', ''),
                    'date': entry.get('date', ''),
                    'year': int(entry.get('year', 0)),
                    'rating': float(entry.get('rating', 0)),
                    'votes': unicode(entry.get('votes')),
                    'views': unicode(entry.get('views', 0))
                },
                'is_playable': True,
                'path': plugin.url_for(
                    endpoint='watch_video',
                    video_id=entry['video_id']
                )
            })
    finish_kwargs = {
        #'sort_methods': ('UNSORTED', 'RATING', 'RUNTIME'),
        'update_listing': is_update
    }
    if has_icons and plugin.get_setting('force_viewmode') == 'true':
        finish_kwargs['view_mode'] = 'thumbnail'
    return plugin.finish(items, **finish_kwargs)


@plugin.route('/video/<video_id>/')
def watch_video(video_id):
    video_url = scraper.get_video(video_id)
    __log('watch_video finished with url: %s' % video_url)
    return plugin.set_resolved_url(video_url)


def __keyboard(title, text=''):
    keyboard = xbmc.Keyboard(text, title)
    keyboard.doModal()
    if keyboard.isConfirmed() and keyboard.getText():
        return keyboard.getText()


def _(string_id):
    if string_id in STRINGS:
        return plugin.get_string(STRINGS[string_id])
    else:
        plugin.log.warning('String is missing: %s' % string_id)
        return string_id


def __log(text):
    plugin.log.info(text)


if __name__ == '__main__':
    plugin.run()
