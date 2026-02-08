from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.widget import Widget
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.graphics import Color, Line, Rectangle, Ellipse, StencilPush, StencilUse, StencilUnUse, StencilPop
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.core.window import Window
from kivy.core.text import Label as CoreLabel
import math

def parse_k_b(text):
    s = (text or '').replace(' ', '').replace('*', '')
    if s.lower().startswith('y='):
        s = s[2:]
    if s == '':
        return None, None
    if 'x' in s:
        parts = s.split('x')
        k_str = parts[0]
        b_str = parts[1] if len(parts) > 1 else ''
        try:
            if k_str == '' or k_str == '+':
                k = 1.0
            elif k_str == '-':
                k = -1.0
            else:
                k = float(k_str)
            b = float(b_str) if b_str != '' else 0.0
            return k, b
        except:
            return None, None
    else:
        try:
            b = float(s)
            return 0.0, b
        except:
            return None, None

class FocusableTextInput(TextInput):
    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            root = App.get_running_app().root
            root.set_current_target(self)
            self.focus = True
            return super().on_touch_down(touch)
        return super().on_touch_down(touch)

class SimplePlot(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.scale = dp(30)
        self.offset_x = 0.0
        self.offset_y = 0.0
        self.k = 1.0
        self.b = 0.0
        self._last_touch = None
        self.marker_pos = None
        self.bind(pos=self.request_redraw, size=self.request_redraw)
        Clock.schedule_once(lambda dt: self.redraw(), 0)

    def request_redraw(self, *a):
        Clock.schedule_once(lambda dt: self.redraw(), 0)

    def func_to_pixel(self, x, y):
        cx = self.x + self.width / 2 + self.offset_x
        cy = self.y + self.height / 2 + self.offset_y
        px = cx + x * self.scale
        py = cy + y * self.scale
        return px, py

    def pixel_to_func(self, px, py):
        cx = self.x + self.width / 2 + self.offset_x
        cy = self.y + self.height / 2 + self.offset_y
        x = (px - cx) / self.scale
        y = (py - cy) / self.scale
        return x, y

    def redraw(self):
        self.canvas.clear()
        w, h = self.width, self.height
        if w <= 0 or h <= 0:
            return

        left_x, top_y = self.pixel_to_func(self.x, self.y + h)
        right_x, bottom_y = self.pixel_to_func(self.x + w, self.y)

        with self.canvas:
            Color(1, 1, 1)
            Rectangle(pos=self.pos, size=self.size)

        self.canvas.add(StencilPush())
        self.canvas.add(Rectangle(pos=self.pos, size=self.size))
        self.canvas.add(StencilUse())

        with self.canvas:
            Color(0.91, 0.91, 0.91)
            start = int(math.floor(left_x)) - 1
            end = int(math.ceil(right_x)) + 1
            for xi in range(start, end + 1):
                px, _ = self.func_to_pixel(xi, 0)
                Line(points=[px, self.y, px, self.y + h], width=1)
            start2 = int(math.floor(bottom_y)) - 1
            end2 = int(math.ceil(top_y)) + 1
            for yi in range(start2, end2 + 1):
                _, py = self.func_to_pixel(0, yi)
                Line(points=[self.x, py, self.x + w, py], width=1)

        cx = self.x + w / 2 + self.offset_x
        cy = self.y + h / 2 + self.offset_y
        with self.canvas:
            Color(0, 0, 0)
            Line(points=[self.x, cy, self.x + w, cy], width=1.2)
            Line(points=[cx, self.y, cx, self.y + h], width=1.2)

        ux0, uy0 = 0.0, 0.0
        ux1, uy1 = 1.0, 0.0
        if (left_x <= ux1 and right_x >= ux0) and (bottom_y <= 0 <= top_y):
            p0 = self.func_to_pixel(ux0, uy0)
            p1 = self.func_to_pixel(ux1, uy1)
            with self.canvas:
                Color(0, 0, 1)
                Line(points=[p0[0], p0[1], p1[0], p1[1]], width=2)
                Line(points=[p0[0], p0[1] - dp(4), p0[0], p0[1] + dp(4)], width=1)
                Line(points=[p1[0], p1[1] - dp(4), p1[0], p1[1] + dp(4)], width=1)
            midx = (p0[0] + p1[0]) / 2
            lbl = CoreLabel(text='1', font_size=dp(12))
            lbl.refresh()
            tex = lbl.texture
            lx = midx + dp(6)
            ly = cy + dp(4)
            with self.canvas:
                Rectangle(texture=tex, pos=(lx, ly), size=tex.size)

        k = self.k; b = self.b
        points = []
        for xv in (left_x, right_x):
            yv = k * xv + b
            if bottom_y <= yv <= top_y:
                points.append((xv, yv))
        if abs(k) > 1e-9:
            for yv in (top_y, bottom_y):
                xv = (yv - b) / k
                if left_x <= xv <= right_x:
                    points.append((xv, yv))
        if points:
            pts = sorted(list({(round(x, 6), round(y, 6)) for x, y in points}), key=lambda t: t[0])
            x_left, y_left = pts[0]
            x_right, y_right = pts[-1]
            p_left = self.func_to_pixel(x_left, y_left)
            p_right = self.func_to_pixel(x_right, y_right)
            with self.canvas:
                Color(1, 0, 0)
                Line(points=[p_left[0], p_left[1], p_right[0], p_right[1]], width=2)

        if getattr(self, 'marker_pos', None) is not None:
            mx, my = self.marker_pos
            if mx is not None and not (isinstance(mx, str)):
                px, py = self.func_to_pixel(mx, my)
                r = dp(6)
                with self.canvas:
                    Color(0, 0.5, 0)
                    Ellipse(pos=(px - r / 2, py - r / 2), size=(r, r))

        self.canvas.add(StencilUnUse())
        self.canvas.add(StencilPop())

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self._last_touch = touch.pos
            return True
        return super().on_touch_down(touch)

    def on_touch_move(self, touch):
        if self._last_touch is not None:
            dx = touch.pos[0] - self._last_touch[0]
            dy = touch.pos[1] - self._last_touch[1]
            self.offset_x += dx
            self.offset_y += dy
            self._last_touch = touch.pos
            self.redraw()
            return True
        return super().on_touch_move(touch)

    def on_touch_up(self, touch):
        self._last_touch = None
        return super().on_touch_up(touch)

class SimpleKeyboard(GridLayout):
    def __init__(self, on_update, **kwargs):
        super().__init__(cols=4, spacing=dp(6), size_hint_y=None, height=dp(180), **kwargs)
        self.on_update = on_update
        keys = ['7', '8', '9', 'Back',
                '4', '5', '6', 'C',
                '1', '2', '3', 'x',
                '.', '0', '+', '-']
        for k in keys:
            btn = Button(text=k, font_size=dp(20))
            btn.bind(on_release=self.pressed)
            self.add_widget(btn)

    def pressed(self, btn):
        key = btn.text
        root = App.get_running_app().root
        target = getattr(root, 'current_target', None)
        if not target:
            return
        txt = target.text or ''
        if getattr(target, 'is_func', False):
            if not txt.startswith('y ='):
                txt = 'y ='
            prefix = 'y ='
            body = txt[3:]
        else:
            prefix = ''
            body = txt
        if key == 'Back':
            body = body[:-1]
        elif key == 'C':
            body = ''
        else:
            body = body + key
        new_text = prefix + body
        target.text = new_text
        target.cursor = (len(new_text), 0)
        if self.on_update:
            self.on_update(target)

class Root(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', spacing=dp(6), padding=dp(6), **kwargs)
        self.current_target = None

        self.plot = SimplePlot(size_hint=(1, 1))
        self.add_widget(self.plot)

        row = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50), spacing=dp(6))
        prefix = Label(text='при y =', size_hint_x=None, width=dp(80), halign='left', valign='middle')
        prefix.bind(size=lambda w, s: setattr(w, 'text_size', s))
        row.add_widget(prefix)

        self.y_input = FocusableTextInput(text='0', multiline=False, size_hint_x=None, width=dp(120))
        self.y_input.name = 'y_input'
        self.y_input.bind(text=self.on_y_text)
        row.add_widget(self.y_input)

        row.add_widget(Label(text=',', size_hint_x=None, width=dp(10)))
        x_pref = Label(text='x =', size_hint_x=None, width=dp(30), halign='left', valign='middle')
        x_pref.bind(size=lambda w, s: setattr(w, 'text_size', s))
        row.add_widget(x_pref)

        self.x_label = Label(text='0.00', halign='left', valign='middle')
        self.x_label.bind(size=lambda w, s: setattr(w, 'text_size', (s[0] - dp(8), None)))
        row.add_widget(self.x_label)

        self.add_widget(row)

        self.func_input = FocusableTextInput(text='y =', multiline=False, size_hint_y=None, height=dp(50))
        self.func_input.name = 'func_input'
        self.func_input.is_func = True
        self.func_input.bind(text=self.on_func_text)
        self.add_widget(self.func_input)

        self.kb = SimpleKeyboard(on_update=self.on_keyboard_update)
        self.add_widget(self.kb)

        btn = Button(text='Построить график', size_hint_y=None, height=dp(48))
        btn.bind(on_release=self.build_plot)
        self.add_widget(btn)

        Clock.schedule_once(lambda dt: self.build_plot(), 0.1)

    def set_current_target(self, widget):
        self.current_target = widget
        widget.background_color = (1, 1, 0.95, 1)

    def clear_current_target(self, widget):
        if self.current_target is widget:
            self.current_target = None
        widget.background_color = (1, 1, 1, 1)

    def on_keyboard_update(self, widget):
        if getattr(widget, 'is_func', False):
            self.apply_func_text(widget.text)
            self.recompute_x()
        elif widget is self.y_input:
            self.apply_y_text(widget.text)

    def on_func_text(self, instance, text):
        if not text.startswith('y ='):
            text = 'y =' + text
            instance.text = text
            instance.cursor = (len(text), 0)
        self.apply_func_text(text)
        self.recompute_x()

    def apply_func_text(self, text):
        kb = parse_k_b(text)
        if kb != (None, None):
            k, b = kb
            self.plot.k = k
            self.plot.b = b
            self.plot.redraw()

    def on_y_text(self, instance, text):
        self.apply_y_text(text)

    def apply_y_text(self, text):
        try:
            y_val = float(text)
        except:
            return
        k = getattr(self.plot, 'k', None)
        b = getattr(self.plot, 'b', None)
        if k is None or b is None:
            self.x_label.text = '?'
            return
        if abs(k) < 1e-9:
            if abs(y_val - b) < 1e-9:
                x_str = 'любое'
                marker_x = None
            else:
                x_str = '∞'
                marker_x = None
        else:
            x = (y_val - b) / k
            x_str = f"{x:.2f}"
            marker_x = x
        self.x_label.text = x_str
        if marker_x is None:
            self.plot.marker_pos = None
        else:
            self.plot.marker_pos = (marker_x, y_val)
        self.plot.redraw()

    def recompute_x(self):
        try:
            y_val = float(self.y_input.text)
        except:
            y_val = 0.0
        self.apply_y_text(str(y_val))

    def build_plot(self, *args):
        self.apply_func_text(self.func_input.text)

class LinearApp(App):
    def build(self):
        Window.size = (380, 760)
        return Root()

if __name__ == '__main__':
    LinearApp().run()