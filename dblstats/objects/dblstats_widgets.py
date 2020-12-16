# -*- coding: utf-8 -*-
# MIT License
# Copyright (c) 2020 Arthur
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from enum import Enum

from .exceptions import InvalidProperty
from ..utils.kwargs_parser import get_value


class WidgetType(Enum):
    """
    The allowed types of widgets.

    :property servers: The property that you use when you want to fetch the bot its servers widget.
    :property total_votes: The property that you use when you want to fetch the bot its total votes widget.
    :property monthly_votes: The property that you use when you want to fetch the bot its monthly votes widget.
    :property shard_count: The property that you use when you want to fetch the bot its shards widget.
    :property ranks: The property that gets used by the RanksWidget object.
    """
    servers = "servers"
    total_votes = "totalVotes"
    monthly_votes = "monthlyVotes"
    shard_count = "shardCount"
    ranks = "ranks"


class WidgetBase:
    """
    The base object for widgets. This gets inherited by the Widget and RanksWidget object.

    :param widget_type: The widget type you want it to be.
    :param background_color: (optional) The background color for the widget. Default is site provided.
    :param width: (optional) The width of the widget. Default is 400.
    :param height: (optional) The height of the widget. Default is 150.
    """

    def __init__(self, widget_type: WidgetType, **kwargs):
        if not isinstance(widget_type, WidgetType):
            raise TypeError(f"Expected 'dblstats.widgets.WidgetType' not `{type(widget_type)}`")

        self.widget_type = widget_type
        self.background_color = get_value("background_color", None, **kwargs)
        self.width = get_value("width", 400, **kwargs)
        self.height = get_value("height", 150, **kwargs)

        self.base_params = {
            'backgroundColor': self.background_color,
            'width': self.width,
            'height': self.height
        }


class Widget(WidgetBase):
    """
    A dblstatistics.com widget. This represents an object that can be reused and customized. This object inherits
    WidgetBase. (see in its **kwargs)

    :param title_font_size: (optional) The fontsize for the widget title. Default is 12.
    :param label_font_size: (optional) The fontsize for the widget labels. Default is 12.
    :param text_color: (optional) The hex color of the widget text. Default is site provided.
    :param line_color: (optional) The hex color of the widget lines (eg graphs ect).
    """

    def __init__(self, widget_type: WidgetType, **kwargs):
        if widget_type == WidgetType.ranks:
            raise InvalidProperty("'widget_type' must not be a 'ranks' property.")

        super().__init__(widget_type, **kwargs)

        self.title_font_size = get_value("title_font_size", 12, **kwargs)
        self.label_font_size = get_value("label_font_size", 12, **kwargs)
        self.text_color = get_value("text_color", None, **kwargs)
        self.line_color = get_value("line_color", None, **kwargs)

        self.params = {
            'titleFontSize': self.title_font_size,
            'labelFontSize': self.label_font_size,
            'textColor': self.text_color,
            'lineColor': self.line_color,
            **self.base_params
        }


class RanksWidget(WidgetBase):
    """
    A dblstatistics.com ranks widget. This represents an object that can be reused and customized. This object inherits
    WidgetBase. (see in its **kwargs)

    :param title_color: (optional) The hex color for the widget title. Default is site provided.
    :param rank_back_color: (optional) The hex color for the rank background in the widget. Default is site provided.
    :param rank_color: (optional) The hex color for the rank in the widget. Default is site provided.
    :param border_color: (optional) The hex color of the widget its border color. Default is site provided.
    """

    def __init__(self, **kwargs):
        super().__init__(WidgetType.ranks, **kwargs)

        self.title_color = get_value("title_color", None, **kwargs)
        self.rank_back_color = get_value("rank_background_color", None, **kwargs)
        self.rank_color = get_value("rank_color", None, **kwargs)
        self.border_color = get_value("border_color", None, **kwargs)

        self.params = {
            'titleColor': self.title_color,
            'rankBackColor': self.rank_back_color,
            'rankColor': self.rank_color,
            'borderColor': self.border_color,
            **self.base_params
        }
