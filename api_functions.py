from requests_html import *
from jsonpath_ng import parse
from database_functions import *


def api_is_online(channel_data):
    jpath = parse('result.channel.channel_is_live')
    for match in jpath.find(channel_data):
        return match.value

        
def api_title(channel_data):
    jpath = parse('result.media_container.media_container_name')
    for match in jpath.find(channel_data):
        return match.value


def api_category(channel_data):
    jpath = parse('result.media_container.game.game_name')
    for match in jpath.find(channel_data):
        return match.value


