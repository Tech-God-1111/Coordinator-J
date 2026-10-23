import tkinter as tk
from tkinter import ttk
from tkinter import font as tkfont
from datetime import datetime

from coordinator import Coordinator


# ============================================================
# COORDINATOR-J DESKTOP APP
# Version 1.0  -  "Midnight Punch" interface
# Built with Python's built-in Tkinter
#
# Only the INTERFACE was restyled. Every handler, the
# Coordinator calls, the tables, the console, the uptime
# clock and the navigation all behave exactly as before.
# ============================================================

APP_NAME = "Coordinator-J"
APP_VERSION = "1.0.0"

FONT = "Segoe UI"
SYMBOL_FONT = "Segoe UI Symbol"

COLORS = {
    # ---- your uploaded palette --------------------------------
    "palette_white": "#F9F7F7",
    "palette_mist": "#DBE2EF",
    "palette_blue": "#3F72AF",
    "palette_navy": "#112D4E",
    # ---- surfaces built from the palette ----------------------
    "background": "#0B1D33",     # deep navy canvas
    "panel": "#112D4E",          # cards
    "panel_header": "#163A63",
    "console": "#0D2441",
    "field": "#0D2441",
    "border": "#24496F",
    "sidebar": "#163A63",
    # ---- brand + text -----------------------------------------
    "primary": "#3F72AF",
    "primary_hover": "#5B8CC8",
    "navy": "#112D4E",
    "text": "#F9F7F7",
    "muted": "#8FA9C9",
    # ---- lively accents mixed in for the wow ------------------
    "sky": "#7FB6F5",
    "mint": "#5ED3B6",
    "amber": "#FFC857",
    "coral": "#FF7F6E",
    "lavender": "#B8A9F2",
    # ---- status colours ---------------------------------------
    "success": "#5ED3B6",
    "warning": "#FFC857",
    "error": "#FF6B6B",
}


# ============================================================
# SMALL DRAWING HELPERS
# ============================================================

def blend(c1, c2, t):
    """Mix two #RRGGBB colours. t=0 -> c1, t=1 -> c2."""
    a = [int(c1[i:i + 2], 16) for i in (1, 3, 5)]
    b = [int(c2[i:i + 2], 16) for i in (1, 3, 5)]
    mixed = [round(x + (y - x) * t) for x, y in zip(a, b)]
    return "#{:02X}{:02X}{:02X}".format(*mixed)


def round_rect(canvas, x1, y1, x2, y2, r, **kw):
    r = max(0, min(r, (x2 - x1) / 2, (y2 - y1) / 2))
    pts = [
        x1 + r, y1, x1 + r, y1, x2 - r, y1, x2 - r, y1,
        x2, y1, x2, y1 + r, x2, y1 + r, x2, y2 - r,
        x2, y2 - r, x2, y2, x2 - r, y2, x2 - r, y2,
        x1 + r, y2, x1 + r, y2, x1, y2, x1, y2 - r,
        x1, y2 - r, x1, y1 + r, x1, y1 + r, x1, y1,
    ]
    return canvas.create_polygon(pts, smooth=True, **kw)


class RoundCard(tk.Canvas):
    """A rounded card. Put children inside `.body`."""

    def __init__(
        self,
        parent,
        parent_bg,
        fill,
        outline="",
        radius=22,
        pad=0,
        autoheight=False,
        autowidth=False,
        width=10,
        height=10,
    ):
        super().__init__(
            parent,
            bg=parent_bg,
            highlightthickness=0,
            bd=0,
            width=width,
            height=height,
        )
        self.fill = fill
        self.outline = outline
        self.radius = radius
        self.pad = pad
        self.autoheight = autoheight
        self.autowidth = autowidth

        self.body = tk.Frame(self, bg=fill)
        self._win = self.create_window(
            pad, pad, window=self.body, anchor="nw"
        )

        self.bind("<Configure>", self._redraw)

        if autoheight or autowidth:
            self.body.bind("<Configure>", self._fit)
            self.after_idle(self._fit)

    def _redraw(self, event=None):
        w, h = self.winfo_width(), self.winfo_height()
        if w < 4 or h < 4:
            return

        self.delete("card")
        round_rect(
            self,
            1,
            1,
            w - 1,
            h - 1,
            self.radius,
            fill=self.fill,
            outline=self.outline or self.fill,
            width=1,
            tags="card",
        )
        self.tag_lower("card")
        self.itemconfigure(
            self._win,
            width=max(1, w - 2 * self.pad),
            height=max(1, h - 2 * self.pad),
        )

    def _fit(self, event=None):
        options = {}
        if self.autoheight:
            options["height"] = self.body.winfo_reqheight() + 2 * self.pad
        if self.autowidth:
            options["width"] = self.body.winfo_reqwidth() + 2 * self.pad
        if options:
            self.configure(**options)


class RoundButton(tk.Canvas):
    """A rounded, hoverable button (pill or tile layout)."""

    def __init__(
        self,
        parent,
        parent_bg,
        text="",
        command=None,
        fill="#3F72AF",
        hover=None,
        fg="#FFFFFF",
        radius=16,
        mode="pill",
        icon="",
        subtitle="",
        font=None,
        width=100,
        height=40,
    ):
        super().__init__(
            parent,
            bg=parent_bg,
            highlightthickness=0,
            bd=0,
            width=width,
            height=height,
            cursor="hand2" if command else "",
        )
        self.text = text
        self.command = command
        self.radius = radius
        self.mode = mode
        self.icon = icon
        self.subtitle = subtitle
        self.font = font or (FONT, 10, "bold")
        self.fill = fill
        self.hover = hover or blend(fill, "#FFFFFF", 0.15)
        self.fg = fg
        self._hovering = False

        self.bind("<Configure>", lambda e: self.redraw())

        if command:
            self.bind("<Enter>", self._on_enter)
            self.bind("<Leave>", self._on_leave)
            self.bind("<Button-1>", self._on_click)

    def set_style(self, fill, hover, fg):
        self.fill, self.hover, self.fg = fill, hover, fg
        self.redraw()

    def _on_enter(self, event):
        self._hovering = True
        self.redraw()

    def _on_leave(self, event):
        self._hovering = False
        self.redraw()

    def _on_click(self, event):
        if self.command:
            self.command()

    def redraw(self):
        w, h = self.winfo_width(), self.winfo_height()
        if w < 4 or h < 4:
            return

        self.delete("all")
        colour = self.hover if self._hovering else self.fill
        round_rect(self, 1, 1, w - 1, h - 1, self.radius,
                   fill=colour, outline=colour)

        if self.mode == "tile":
            self.create_text(
                w / 2, h * 0.30, text=self.icon,
                fill=self.fg, font=(SYMBOL_FONT, 20, "bold"),
            )
            self.create_text(
                w / 2, h * 0.62, text=self.text,
                fill=self.fg, font=(FONT, 11, "bold"),
            )
            self.create_text(
                w / 2, h * 0.82, text=self.subtitle,
                fill=blend(self.fg, colour, 0.30), font=(FONT, 8),
            )
        else:
            label = f"{self.icon}  {self.text}" if self.icon else self.text
            self.create_text(
                w / 2, h / 2, text=label, fill=self.fg, font=self.font,
            )


class GradientBar(tk.Canvas):
    """Thin multi-colour accent line across the top of the window."""

    STOPS = ["#3F72AF", "#7FB6F5", "#5ED3B6", "#FFC857", "#FF7F6E"]

    def __init__(self, parent, height=4):
        super().__init__(
            parent, height=height, highlightthickness=0, bd=0,
            bg=COLORS["background"],
        )
        self.bind("<Configure>", self._draw)

    def _draw(self, event=None):
        w, h = self.winfo_width(), self.winfo_height()
        if w < 4:
            return
        self.delete("all")
        segments = len(self.STOPS) - 1
        for x in range(0, w, 3):
            pos = x / max(1, w - 1) * segments
            i = min(int(pos), segments - 1)
            colour = blend(self.STOPS[i], self.STOPS[i + 1], pos - i)
            self.create_rectangle(x, 0, x + 3, h, fill=colour, outline="")


class CoordinatorDesktopApp:
    def __init__(self, root):
        self.root = root
        self.coordinator = Coordinator()
        self.started_at = datetime.now()
        self.total_commands = 0

        self.root.title(f"{APP_NAME} | Independent Agent Core")
        self.root.geometry("1440x900")
        self.root.minsize(1100, 700)
        self.root.configure(bg=COLORS["background"])

        self.setup_styles()
        self.build_interface()
        self.write_startup_messages()
        self.refresh_dashboard()

        self.root.bind("<Return>", self.on_enter)
        self.root.after(1000, self.update_uptime)

    # --------------------------------------------------------
    # STYLING
    # --------------------------------------------------------

    def setup_styles(self):
        style = ttk.Style()

        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        # Remove the default light border around tables.
        style.layout(
            "Treeview",
            [("Treeview.treearea", {"sticky": "nswe"})],
        )

        style.configure(
            "Treeview",
            background=COLORS["console"],
            fieldbackground=COLORS["console"],
            foreground=COLORS["text"],
            rowheight=32,
            borderwidth=0,
            relief="flat",
            font=(FONT, 10),
        )

        style.configure(
            "Treeview.Heading",
            background=COLORS["panel_header"],
            foreground=COLORS["sky"],
            font=(FONT, 10, "bold"),
            padding=8,
            relief="flat",
            borderwidth=0,
        )

        style.map(
            "Treeview",
            background=[("selected", COLORS["primary"])],
            foreground=[("selected", "#FFFFFF")],
        )
        style.map(
            "Treeview.Heading",
            background=[("active", COLORS["border"])],
        )

        style.configure(
            "TEntry",
            padding=10,
            font=(FONT, 11),
        )

        style.configure(
            "Vertical.TScrollbar",
            background=COLORS["border"],
            troughcolor=COLORS["console"],
            bordercolor=COLORS["console"],
            lightcolor=COLORS["border"],
            darkcolor=COLORS["border"],
            arrowcolor=COLORS["muted"],
            borderwidth=0,
            arrowsize=14,
        )
        style.map(
            "Vertical.TScrollbar",
            background=[("active", COLORS["primary"])],
        )

    # --------------------------------------------------------
    # GENERAL UI HELPERS
    # --------------------------------------------------------

    def make_panel(
        self,
        parent,
        title,
        icon="",
        subtitle="",
        accent=None,
        autoheight=False,
    ):
        outer = RoundCard(
            parent,
            COLORS["background"],
            COLORS["panel"],
            outline=COLORS["border"],
            radius=24,
            pad=2,
            autoheight=autoheight,
        )

        heading = tk.Frame(outer.body, bg=COLORS["panel"])
        heading.pack(fill="x", padx=18, pady=(16, 8))

        if icon:
            tk.Label(
                heading,
                text=icon,
                bg=COLORS["panel"],
                fg=accent or COLORS["sky"],
                font=(SYMBOL_FONT, 13, "bold"),
            ).pack(side="left", padx=(0, 8))

        tk.Label(
            heading,
            text=title,
            bg=COLORS["panel"],
            fg=COLORS["text"],
            font=(FONT, 13, "bold"),
        ).pack(side="left")

        if subtitle:
            tk.Label(
                heading,
                text=subtitle,
                bg=COLORS["panel"],
                fg=COLORS["muted"],
                font=(FONT, 9),
            ).pack(side="left", padx=(10, 0), pady=(3, 0))

        body = tk.Frame(outer.body, bg=COLORS["panel"])
        body.pack(fill="both", expand=True, padx=12, pady=(0, 14))

        return outer, body

    def make_button(self, parent, text, command, primary=False):
        if primary:
            fill, fg = COLORS["coral"], COLORS["navy"]
            hover = blend(COLORS["coral"], "#FFFFFF", 0.18)
        else:
            fill, fg = COLORS["panel_header"], COLORS["text"]
            hover = COLORS["border"]

        font = (FONT, 10, "bold")
        width = tkfont.Font(family=FONT, size=10, weight="bold").measure(
            text
        ) + 38

        return RoundButton(
            parent,
            COLORS["panel"],
            text=text,
            command=command,
            fill=fill,
            hover=hover,
            fg=fg,
            radius=17,
            font=font,
            width=width,
            height=34,
        )

    # --------------------------------------------------------
    # MAIN LAYOUT
    # --------------------------------------------------------

    def build_interface(self):
        self.root.grid_rowconfigure(3, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        GradientBar(self.root).grid(row=0, column=0, sticky="ew")

        self.build_header()
        self.build_hero()
        self.build_workspace()
        self.build_footer()

    # --------------------------------------------------------
    # TOP BAR  (brand, navigation pills, status)
    # --------------------------------------------------------

    def build_header(self):
        header = tk.Frame(self.root, bg=COLORS["background"])
        header.grid(row=1, column=0, sticky="ew", padx=28, pady=(14, 6))
        header.grid_columnconfigure(2, weight=1)

        # ---- brand ----
        branding = tk.Frame(header, bg=COLORS["background"])
        branding.grid(row=0, column=0, sticky="w", padx=(0, 22))

        RoundButton(
            branding,
            COLORS["background"],
            text="CJ",
            fill=COLORS["primary"],
            fg="#FFFFFF",
            radius=15,
            font=(FONT, 14, "bold"),
            width=46,
            height=46,
        ).pack(side="left", padx=(0, 12))

        base, _, tail = APP_NAME.partition("-")
        tail = f"-{tail}" if tail else ""

        tk.Label(
            branding,
            text=base,
            bg=COLORS["background"],
            fg=COLORS["text"],
            font=(FONT, 19, "bold"),
        ).pack(side="left")

        tk.Label(
            branding,
            text=tail,
            bg=COLORS["background"],
            fg=COLORS["coral"],
            font=(FONT, 19, "bold"),
        ).pack(side="left")

        # ---- navigation pills ----
        nav_card = RoundCard(
            header,
            COLORS["background"],
            COLORS["panel"],
            outline=COLORS["border"],
            radius=26,
            pad=6,
            autoheight=True,
            autowidth=True,
        )
        nav_card.grid(row=0, column=1, sticky="w")

        navigation = [
            ("⌂", "Dashboard", self.show_dashboard),
            ("⚒", "Tools", self.show_tools),
            ("◷", "History", self.show_history),
            ("⚙", "Settings", self.show_settings),
            ("ⓘ", "About", self.show_about),
        ]

        self.nav_buttons = {}
        measure = tkfont.Font(family=FONT, size=10, weight="bold").measure

        for icon, name, callback in navigation:
            button = RoundButton(
                nav_card.body,
                COLORS["panel"],
                text=name,
                icon=icon,
                command=callback,
                fill=COLORS["panel"],
                fg=COLORS["muted"],
                radius=19,
                font=(FONT, 10, "bold"),
                width=measure(f"{icon}  {name}") + 36,
                height=38,
            )
            button.pack(side="left", padx=2)
            self.nav_buttons[name] = button

        self.select_navigation("Dashboard")

        # ---- online chip ----
        chip = RoundCard(
            header,
            COLORS["background"],
            COLORS["panel"],
            outline=COLORS["border"],
            radius=22,
            autoheight=True,
            autowidth=True,
        )
        chip.grid(row=0, column=3, sticky="e")

        tk.Label(
            chip.body,
            text="●",
            bg=COLORS["panel"],
            fg=COLORS["success"],
            font=(FONT, 10),
        ).pack(side="left", padx=(16, 6), pady=10)
        tk.Label(
            chip.body,
            text="ONLINE",
            bg=COLORS["panel"],
            fg=COLORS["text"],
            font=(FONT, 10, "bold"),
        ).pack(side="left", padx=(0, 16), pady=10)

    # --------------------------------------------------------
    # HERO  (greeting, title, system status chips)
    # --------------------------------------------------------

    def build_hero(self):
        hero = tk.Frame(self.root, bg=COLORS["background"])
        hero.grid(row=2, column=0, sticky="ew", padx=34, pady=(14, 8))
        hero.grid_columnconfigure(0, weight=1)

        hour = datetime.now().hour
        greeting = (
            "GOOD MORNING"
            if hour < 12
            else "GOOD AFTERNOON"
            if hour < 18
            else "GOOD EVENING"
        )

        left = tk.Frame(hero, bg=COLORS["background"])
        left.grid(row=0, column=0, sticky="w")

        tk.Label(
            left,
            text=greeting,
            bg=COLORS["background"],
            fg=COLORS["sky"],
            font=(FONT, 9, "bold"),
        ).pack(anchor="w")

        title_row = tk.Frame(left, bg=COLORS["background"])
        title_row.pack(anchor="w")

        for word, colour in (
            ("Live ", COLORS["text"]),
            ("command", COLORS["coral"]),
            (" terminal", COLORS["text"]),
        ):
            tk.Label(
                title_row,
                text=word,
                bg=COLORS["background"],
                fg=colour,
                font=(FONT, 32, "bold"),
            ).pack(side="left")

        # ---- system status as chips (same data as before) ----
        chips = tk.Frame(hero, bg=COLORS["background"])
        chips.grid(row=0, column=1, sticky="e")

        self.status_labels = {}

        status_items = [
            ("Coordinator-J", "Online", COLORS["success"]),
            ("AI Planner", "Not Connected", COLORS["muted"]),
            ("SmartDoor", "Not Connected", COLORS["muted"]),
        ]

        for name, status, color in status_items:
            chip = RoundCard(
                chips,
                COLORS["background"],
                COLORS["panel"],
                outline=COLORS["border"],
                radius=22,
                autoheight=True,
                autowidth=True,
            )
            chip.pack(side="left", padx=(8, 0))

            tk.Label(
                chip.body,
                text="●",
                fg=color,
                bg=COLORS["panel"],
                font=(FONT, 10),
            ).pack(side="left", padx=(14, 6), pady=9)

            tk.Label(
                chip.body,
                text=name,
                fg=COLORS["text"],
                bg=COLORS["panel"],
                font=(FONT, 9, "bold"),
            ).pack(side="left")

            status_label = tk.Label(
                chip.body,
                text=status,
                fg=color,
                bg=COLORS["panel"],
                font=(FONT, 9),
            )
            status_label.pack(side="left", padx=(6, 14))
            self.status_labels[name] = status_label

    def build_workspace(self):
        workspace = tk.Frame(self.root, bg=COLORS["background"])
        workspace.grid(
            row=3,
            column=0,
            sticky="nsew",
            padx=28,
            pady=(6, 12),
        )

        workspace.grid_rowconfigure(0, weight=1)
        workspace.grid_columnconfigure(0, weight=3, minsize=520)
        workspace.grid_columnconfigure(1, weight=2, minsize=430)

        self.build_console_area(workspace)
        self.build_right_column(workspace)

    # --------------------------------------------------------
    # CENTRAL CONSOLE  (task console + command bar)
    # --------------------------------------------------------

    def build_console_area(self, parent):
        card = RoundCard(
            parent,
            COLORS["background"],
            COLORS["panel"],
            outline=COLORS["border"],
            radius=26,
            pad=2,
        )
        card.grid(row=0, column=0, sticky="nsew", padx=(0, 16))

        body = card.body
        body.grid_rowconfigure(1, weight=1)
        body.grid_columnconfigure(0, weight=1)

        # ---- header: title, tagline, Clear ----
        heading = tk.Frame(body, bg=COLORS["panel"])
        heading.grid(row=0, column=0, sticky="ew", padx=20, pady=(16, 10))
        heading.grid_columnconfigure(2, weight=1)

        tk.Label(
            heading,
            text="●",
            bg=COLORS["panel"],
            fg=COLORS["success"],
            font=(FONT, 10),
        ).grid(row=0, column=0, padx=(0, 8))

        tk.Label(
            heading,
            text="Task Console",
            bg=COLORS["panel"],
            fg=COLORS["text"],
            font=(FONT, 13, "bold"),
        ).grid(row=0, column=1, sticky="w")

        tk.Label(
            heading,
            text="Your AI Orchestrator. Always On.",
            bg=COLORS["panel"],
            fg=COLORS["muted"],
            font=(FONT, 10, "italic"),
        ).grid(row=0, column=2, sticky="e", padx=(0, 14))

        self.make_button(
            heading,
            "Clear",
            self.clear_console,
        ).grid(row=0, column=3, sticky="e")

        # ---- console text ----
        console_card = RoundCard(
            body,
            COLORS["panel"],
            COLORS["console"],
            outline=COLORS["border"],
            radius=18,
            pad=8,
        )
        console_card.grid(
            row=1, column=0, sticky="nsew", padx=16, pady=(0, 12)
        )

        self.console = tk.Text(
            console_card.body,
            bg=COLORS["console"],
            fg=COLORS["text"],
            font=("Consolas", 10),
            wrap="word",
            relief="flat",
            bd=0,
            highlightthickness=0,
            padx=12,
            pady=10,
            spacing1=4,
            spacing3=5,
            state="disabled",
            insertbackground=COLORS["text"],
            selectbackground=COLORS["primary"],
        )
        self.console.pack(fill="both", expand=True)

        self.console.tag_configure(
            "time",
            foreground=COLORS["muted"],
        )
        self.console.tag_configure(
            "success",
            foreground=COLORS["success"],
        )
        self.console.tag_configure(
            "warning",
            foreground=COLORS["warning"],
        )
        self.console.tag_configure(
            "error",
            foreground=COLORS["error"],
        )
        self.console.tag_configure(
            "heading",
            foreground=COLORS["sky"],
            font=("Consolas", 11, "bold"),
        )

        # ---- command bar ----
        command_bar = tk.Frame(body, bg=COLORS["panel"])
        command_bar.grid(
            row=2, column=0, sticky="ew", padx=16, pady=(0, 4)
        )
        command_bar.grid_columnconfigure(0, weight=1)

        self.command_var = tk.StringVar()

        entry_card = RoundCard(
            command_bar,
            COLORS["panel"],
            COLORS["field"],
            outline=COLORS["border"],
            radius=24,
            height=48,
        )
        entry_card.grid(row=0, column=0, sticky="ew", padx=(0, 10))

        self.command_entry = tk.Entry(
            entry_card.body,
            textvariable=self.command_var,
            font=(FONT, 11),
            bg=COLORS["field"],
            fg=COLORS["text"],
            insertbackground=COLORS["coral"],
            selectbackground=COLORS["primary"],
            selectforeground="#FFFFFF",
            relief="flat",
            bd=0,
            highlightthickness=0,
        )
        self.command_entry.pack(fill="both", expand=True, padx=20, pady=8)

        RoundButton(
            command_bar,
            COLORS["panel"],
            text="Send  ➤",
            command=self.submit_command,
            fill=COLORS["coral"],
            hover=blend(COLORS["coral"], "#FFFFFF", 0.18),
            fg=COLORS["navy"],
            radius=24,
            font=(FONT, 11, "bold"),
            width=116,
            height=48,
        ).grid(row=0, column=1, sticky="e")

        tk.Label(
            body,
            text="Enter a command and press Enter or Send.",
            bg=COLORS["panel"],
            fg=COLORS["muted"],
            font=(FONT, 9),
        ).grid(row=3, column=0, sticky="w", padx=26, pady=(4, 14))

    # --------------------------------------------------------
    # RIGHT COLUMN: QUICK COMMANDS, TOOLS AND HISTORY
    # --------------------------------------------------------

    def run_quick_command(self, text):
        self.command_var.set(text)
        self.submit_command()

    def build_right_column(self, parent):
        right = tk.Frame(parent, bg=COLORS["background"])
        right.grid(row=0, column=1, sticky="nsew")

        right.grid_columnconfigure(0, weight=1)
        right.grid_rowconfigure(1, weight=1)
        right.grid_rowconfigure(2, weight=1)

        # ---- quick commands (tiles reuse existing actions) ----
        quick_panel, quick_body = self.make_panel(
            right,
            "Quick commands",
            "⚡",
            subtitle="tap to run",
            accent=COLORS["amber"],
            autoheight=True,
        )
        quick_panel.grid(row=0, column=0, sticky="ew", pady=(0, 14))

        tiles = [
            ("?", "Help", "What can you do?",
             COLORS["coral"], COLORS["navy"],
             lambda: self.run_quick_command("help")),
            ("⌂", "Dashboard", "Refresh data",
             COLORS["primary"], "#FFFFFF", self.show_dashboard),
            ("⚒", "Tools", "Registered tools",
             COLORS["mint"], COLORS["navy"], self.show_tools),
            ("◷", "History", "Task log",
             COLORS["amber"], COLORS["navy"], self.show_history),
            ("⚙", "Settings", "Preferences",
             COLORS["palette_mist"], COLORS["navy"], self.show_settings),
            ("ⓘ", "About", "System info",
             COLORS["lavender"], COLORS["navy"], self.show_about),
        ]

        for column in range(3):
            quick_body.grid_columnconfigure(column, weight=1, uniform="tile")

        for index, (icon, title, subtitle, fill, fg, action) in enumerate(
            tiles
        ):
            RoundButton(
                quick_body,
                COLORS["panel"],
                text=title,
                icon=icon,
                subtitle=subtitle,
                command=action,
                fill=fill,
                fg=fg,
                radius=18,
                mode="tile",
                width=110,
                height=90,
            ).grid(
                row=index // 3,
                column=index % 3,
                sticky="ew",
                padx=4,
                pady=4,
            )

        # ---- registered tools ----
        tools_panel, tools_body = self.make_panel(
            right,
            "Registered Tools",
            "⚒",
            accent=COLORS["mint"],
        )
        tools_panel.grid(
            row=1,
            column=0,
            sticky="nsew",
            pady=(0, 14),
        )

        tools_body.grid_rowconfigure(0, weight=1)
        tools_body.grid_columnconfigure(0, weight=1)

        self.tools_table = ttk.Treeview(
            tools_body,
            columns=("name", "access", "description"),
            show="headings",
            height=4,
        )

        self.tools_table.heading("name", text="Tool Name")
        self.tools_table.heading("access", text="Access")
        self.tools_table.heading("description", text="Description")

        self.tools_table.column("name", width=110, minwidth=85)
        self.tools_table.column("access", width=110, minwidth=80)
        self.tools_table.column(
            "description",
            width=180,
            minwidth=110,
        )

        tools_scroll = ttk.Scrollbar(
            tools_body,
            orient="vertical",
            command=self.tools_table.yview,
            style="Vertical.TScrollbar",
        )
        self.tools_table.configure(
            yscrollcommand=tools_scroll.set
        )

        self.tools_table.grid(
            row=0,
            column=0,
            sticky="nsew",
        )
        tools_scroll.grid(row=0, column=1, sticky="ns")

        # ---- task history ----
        history_panel, history_body = self.make_panel(
            right,
            "Task History",
            "◷",
            accent=COLORS["amber"],
        )
        history_panel.grid(
            row=2,
            column=0,
            sticky="nsew",
        )

        history_body.grid_rowconfigure(0, weight=1)
        history_body.grid_columnconfigure(0, weight=1)

        self.history_table = ttk.Treeview(
            history_body,
            columns=("id", "request", "status"),
            show="headings",
            height=5,
        )

        self.history_table.heading("id", text="Task ID")
        self.history_table.heading("request", text="Request")
        self.history_table.heading("status", text="Status")

        self.history_table.column("id", width=90, minwidth=70)
        self.history_table.column(
            "request", width=105, minwidth=80
        )
        self.history_table.column(
            "status", width=105, minwidth=85
        )

        history_scroll = ttk.Scrollbar(
            history_body,
            orient="vertical",
            command=self.history_table.yview,
            style="Vertical.TScrollbar",
        )
        self.history_table.configure(
            yscrollcommand=history_scroll.set
        )

        self.history_table.grid(
            row=0,
            column=0,
            sticky="nsew",
        )
        history_scroll.grid(row=0, column=1, sticky="ns")

        self.history_table.bind(
            "<<TreeviewSelect>>",
            self.on_history_select,
        )

    # --------------------------------------------------------
    # FOOTER
    # --------------------------------------------------------

    def build_footer(self):
        footer = tk.Frame(
            self.root,
            bg=COLORS["background"],
            highlightbackground=COLORS["border"],
            highlightthickness=0,
        )
        footer.grid(row=4, column=0, sticky="ew")
        footer.grid_columnconfigure(1, weight=1)

        tk.Frame(footer, bg=COLORS["border"], height=1).grid(
            row=0, column=0, columnspan=3, sticky="ew"
        )

        tk.Label(
            footer,
            text=f"{APP_NAME} v{APP_VERSION}  |  Ready when you are.",
            bg=COLORS["background"],
            fg=COLORS["muted"],
            font=(FONT, 10),
            padx=28,
            pady=10,
        ).grid(row=1, column=0, sticky="w")

        tk.Label(
            footer,
            text="Building a smarter, safer tomorrow.",
            bg=COLORS["background"],
            fg=COLORS["sky"],
            font=(FONT, 10, "italic"),
        ).grid(row=1, column=1)

        self.footer_status = tk.Label(
            footer,
            text="● Online",
            bg=COLORS["background"],
            fg=COLORS["success"],
            font=(FONT, 10, "bold"),
            padx=28,
        )
        self.footer_status.grid(row=1, column=2, sticky="e")

    # --------------------------------------------------------
    # CONSOLE OPERATIONS
    # --------------------------------------------------------

    def log(self, message, tag=None):
        timestamp = datetime.now().strftime("%H:%M:%S")

        self.console.configure(state="normal")
        self.console.insert(
            "end",
            f"[{timestamp}] ",
            "time",
        )

        self.console.insert(
            "end",
            f"{message}\n",
            tag if tag else (),
        )

        self.console.see("end")
        self.console.configure(state="disabled")

    def write_startup_messages(self):
        self.log(
            f"{APP_NAME} v{APP_VERSION} started...",
            "heading",
        )
        self.log("Loading Coordinator core...")
        self.log("Loading registered tools...")
        self.log("Ready.", "success")
        self.log("")
        self.log(f"Welcome to {APP_NAME}!", "heading")
        self.log("Type 'help' to see available commands.")
        self.log("")

    def clear_console(self):
        self.console.configure(state="normal")
        self.console.delete("1.0", "end")
        self.console.configure(state="disabled")
        self.log("Console cleared.", "heading")

    # --------------------------------------------------------
    # COMMAND EXECUTION
    # --------------------------------------------------------

    def on_enter(self, event):
        if self.root.focus_get() == self.command_entry:
            self.submit_command()
            return "break"

    def submit_command(self):
        request = self.command_var.get().strip()

        if not request:
            return

        if request.lower() == "exit":
            self.root.destroy()
            return

        self.command_var.set("")
        self.total_commands += 1

        self.log(f"You: {request}", "heading")

        try:
            task, message = self.coordinator.handle_request(request)

            self.log(
                f"Task #{task.task_id[:8]} | "
                f"Status: {task.status.value}"
            )

            if task.selected_tool:
                self.log(f"Tool: {task.selected_tool}")

            result_tag = (
                "success"
                if task.status.value == "completed"
                else (
                    "warning"
                    if task.status.value == "unsupported"
                    else "error"
                    if task.status.value == "failed"
                    else None
                )
            )

            self.log(f"JARVIS: {message}", result_tag)
            self.log("")

            self.refresh_dashboard()

        except Exception as exc:
            self.log(
                f"Application error: {type(exc).__name__}: {exc}",
                "error",
            )

        self.command_entry.focus_set()

    # --------------------------------------------------------
    # LIVE DASHBOARD DATA
    # --------------------------------------------------------

    def refresh_dashboard(self):
        self.refresh_tools()
        self.refresh_history()

    def refresh_tools(self):
        for item in self.tools_table.get_children():
            self.tools_table.delete(item)

        for tool in self.coordinator.tools.list_tools():
            access = (
                "STATE-CHANGING"
                if tool.changes_state
                else "READ-ONLY"
            )

            self.tools_table.insert(
                "",
                "end",
                values=(
                    tool.name,
                    access,
                    tool.description,
                ),
            )

    def refresh_history(self):
        for item in self.history_table.get_children():
            self.history_table.delete(item)

        recent_tasks = list(
            self.coordinator.tasks.values()
        )[-100:]

        for task in reversed(recent_tasks):
            self.history_table.insert(
                "",
                "end",
                values=(
                    task.task_id[:8],
                    task.request,
                    task.status.value,
                ),
            )

    def update_uptime(self):
        elapsed = datetime.now() - self.started_at
        total_seconds = int(elapsed.total_seconds())

        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)

        self.footer_status.configure(
            text=f"● Online  |  Uptime {hours:02}:{minutes:02}:{seconds:02}"
        )

        self.root.after(1000, self.update_uptime)

    # --------------------------------------------------------
    # NAVIGATION
    # --------------------------------------------------------

    def select_navigation(self, selected):
        for name, button in self.nav_buttons.items():
            if name == selected:
                button.set_style(
                    COLORS["primary"],
                    COLORS["primary_hover"],
                    "#FFFFFF",
                )
            else:
                button.set_style(
                    COLORS["panel"],
                    COLORS["panel_header"],
                    COLORS["muted"],
                )

    def show_dashboard(self):
        self.select_navigation("Dashboard")
        self.refresh_dashboard()
        self.log("Dashboard refreshed.", "heading")

    def show_tools(self):
        self.select_navigation("Tools")
        self.refresh_tools()
        self.log("Registered tools refreshed.", "heading")

    def show_history(self):
        self.select_navigation("History")
        self.refresh_history()
        self.log("Task history refreshed.", "heading")

    def show_settings(self):
        self.select_navigation("Settings")
        self.log(
            "Settings page is planned for a future milestone.",
            "warning",
        )

    def show_about(self):
        self.select_navigation("About")
        self.log(
            f"{APP_NAME} v{APP_VERSION} — Independent Agent Core.",
            "heading",
        )
        self.log("AI planner: not connected.")
        self.log("SmartDoor: not connected.")
        self.log("No external AI or hardware actions are enabled.")

    def on_history_select(self, event):
        selection = self.history_table.selection()

        if not selection:
            return

        values = self.history_table.item(
            selection[0],
            "values",
        )

        if values:
            task_id_prefix = values[0]

            task = next(
                (
                    item
                    for item in self.coordinator.tasks.values()
                    if item.task_id.startswith(task_id_prefix)
                ),
                None,
            )

            if task:
                self.log(
                    f"Selected task: {task.request}",
                    "heading",
                )
                self.log(f"Status: {task.status.value}")

                for result in task.results:
                    self.log(f"Result: {result}")


def main():
    root = tk.Tk()
    CoordinatorDesktopApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()