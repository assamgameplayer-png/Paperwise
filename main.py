"""
PaperWise — Research Paper Organizer
Cross-platform: Android, Windows, Linux, macOS

Features:
  - Add / view / delete research papers
  - Search/filter your local library
  - APA & MLA citation generator with clipboard copy
  - Open Google Scholar or Shodhganga in the system browser
  - Persistent storage via JSON (kivy JsonStore)
  - Keyword / tag support per paper
  - DOI and URL fields
"""

import webbrowser
import uuid
from urllib.parse import quote_plus

from kivy.app import App
from kivy.clock import Clock
from kivy.core.clipboard import Clipboard
from kivy.metrics import dp
from kivy.storage.jsonstore import JsonStore
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.scrollview import ScrollView

from kivymd.app import MDApp
from kivymd.uix.button import MDFlatButton, MDRaisedButton, MDIconButton
from kivymd.uix.card import MDCard
from kivymd.uix.dialog import MDDialog
from kivymd.uix.label import MDLabel
from kivymd.uix.screen import MDScreen
from kivymd.uix.screenmanager import MDScreenManager
from kivymd.uix.snackbar import Snackbar
from kivymd.uix.tab import MDTabsBase, MDTabs
from kivymd.uix.textfield import MDTextField
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.chip import MDChip
from kivymd.uix.selectioncontrol import MDCheckbox
from kivymd.uix.list import (
    MDList,
    TwoLineIconListItem,
    IconLeftWidget,
)

from kivy.uix.widget import Widget


# ─────────────────────────────────────────
#  Helper: generate citation strings
# ─────────────────────────────────────────
def make_citation(paper: dict, style: str) -> str:
    title   = paper.get("title", "").strip()
    author  = paper.get("author", "").strip() or "Unknown Author"
    year    = paper.get("year", "").strip()   or "n.d."
    journal = paper.get("journal", "").strip()
    doi     = paper.get("doi", "").strip()
    url     = paper.get("url", "").strip()

    source = ""
    if doi:
        source = f"https://doi.org/{doi}"
    elif url:
        source = url

    if style == "APA":
        parts = [f"{author} ({year}). {title}."]
        if journal:
            parts.append(f" {journal}.")
        if source:
            parts.append(f" {source}")
        return "".join(parts)
    else:  # MLA
        parts = [f'{author}. "{title}."']
        if journal:
            parts.append(f" {journal},")
        parts.append(f" {year}.")
        if source:
            parts.append(f" {source}.")
        return "".join(parts)


# ─────────────────────────────────────────
#  Paper Card widget
# ─────────────────────────────────────────
class PaperCard(MDCard):
    def __init__(self, paper: dict, on_delete, on_cite, **kwargs):
        super().__init__(**kwargs)
        self.paper = paper
        self.orientation = "vertical"
        self.size_hint   = (1, None)
        self.height      = dp(160)
        self.padding     = dp(14)
        self.spacing     = dp(6)
        self.radius      = [dp(16)] * 4
        self.elevation   = 2
        self.ripple_behavior = True

        # ── Top row: title + delete icon ──────────────────
        top = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(68))

        text_col = BoxLayout(orientation="vertical", spacing=dp(2))
        title_label = MDLabel(
            text=paper.get("title", "No Title"),
            font_style="Subtitle1",
            theme_text_color="Primary",
            bold=True,
            shorten=True,
            shorten_from="right",
        )
        meta_label = MDLabel(
            text=f"{paper.get('author','?')}  •  {paper.get('year','n/a')}  •  {paper.get('journal','') or '—'}",
            font_style="Caption",
            theme_text_color="Secondary",
        )
        text_col.add_widget(title_label)
        text_col.add_widget(meta_label)

        delete_btn = MDIconButton(
            icon="delete-outline",
            theme_text_color="Custom",
            text_color=(0.8, 0.2, 0.2, 1),
            size_hint=(None, None),
            size=(dp(40), dp(40)),
            on_release=lambda _: on_delete(paper["id"]),
        )

        top.add_widget(text_col)
        top.add_widget(delete_btn)
        self.add_widget(top)

        # ── Tag chips (keywords) ──────────────────────────
        keywords = paper.get("keywords", [])
        if isinstance(keywords, str):
            keywords = [k.strip() for k in keywords.split(",") if k.strip()]

        if keywords:
            chips_row = BoxLayout(
                orientation="horizontal",
                size_hint_y=None,
                height=dp(32),
                spacing=dp(6),
            )
            for kw in keywords[:4]:
                chip = MDChip(text=kw.upper(), size_hint=(None, None))
                chips_row.add_widget(chip)
            self.add_widget(chips_row)

        # ── Citation buttons ──────────────────────────────
        btn_row = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(38),
            spacing=dp(10),
        )
        apa_btn = MDRaisedButton(
            text="APA Citation",
            on_release=lambda _: on_cite(paper, "APA"),
        )
        mla_btn = MDRaisedButton(
            text="MLA Citation",
            on_release=lambda _: on_cite(paper, "MLA"),
        )
        btn_row.add_widget(apa_btn)
        btn_row.add_widget(mla_btn)
        self.add_widget(btn_row)


# ─────────────────────────────────────────
#  Main Screen — Library tab
# ─────────────────────────────────────────
class LibraryScreen(MDScreen):
    def __init__(self, app_ref, **kwargs):
        super().__init__(name="library", **kwargs)
        self.app_ref = app_ref
        self._build_ui()

    def _build_ui(self):
        root = FloatLayout()

        # Vertical stack: toolbar + search + list
        vbox = BoxLayout(orientation="vertical", size_hint=(1, 1))

        # Toolbar
        toolbar = MDTopAppBar(
            title="PaperWise",
            right_action_items=[["information-outline", lambda x: self.app_ref.show_about()]],
            elevation=4,
        )
        vbox.add_widget(toolbar)

        # Search bar
        self.search_field = MDTextField(
            hint_text="Search title, author or keyword…",
            mode="round",
            size_hint=(0.95, None),
            height=dp(52),
            pos_hint={"center_x": 0.5},
            on_text_validate=self._on_search,
        )
        self.search_field.bind(text=self._on_search_text)
        vbox.add_widget(self.search_field)

        # Scrollable paper list
        scroll = ScrollView(size_hint=(1, 1))
        self.list_layout = BoxLayout(
            orientation="vertical",
            spacing=dp(12),
            padding=[dp(12), dp(12), dp(12), dp(80)],
            size_hint_y=None,
        )
        self.list_layout.bind(minimum_height=self.list_layout.setter("height"))
        scroll.add_widget(self.list_layout)
        vbox.add_widget(scroll)

        root.add_widget(vbox)

        # FAB — add paper
        from kivymd.uix.button import MDFloatingActionButton
        fab = MDFloatingActionButton(
            icon="plus",
            pos_hint={"right": 0.96, "y": 0.04},
            elevation=6,
            on_release=lambda _: self.app_ref.show_add_dialog(),
        )
        root.add_widget(fab)

        self.add_widget(root)

    def _on_search(self, instance):
        self.app_ref.refresh_library(instance.text.strip())

    def _on_search_text(self, instance, value):
        self.app_ref.refresh_library(value.strip())

    def refresh(self, papers: list):
        self.list_layout.clear_widgets()

        if not papers:
            self.list_layout.add_widget(
                MDLabel(
                    text="No papers yet — tap + to add one!",
                    halign="center",
                    theme_text_color="Hint",
                    size_hint_y=None,
                    height=dp(80),
                )
            )
            return

        for paper in papers:
            card = PaperCard(
                paper=paper,
                on_delete=self.app_ref.delete_paper,
                on_cite=self.app_ref.show_citation_dialog,
            )
            self.list_layout.add_widget(card)


# ─────────────────────────────────────────
#  Discover Screen — Search external sources
# ─────────────────────────────────────────
class DiscoverScreen(MDScreen):
    def __init__(self, app_ref, **kwargs):
        super().__init__(name="discover", **kwargs)
        self.app_ref = app_ref
        self._build_ui()

    def _build_ui(self):
        vbox = BoxLayout(orientation="vertical")

        toolbar = MDTopAppBar(title="Discover Papers", elevation=4)
        vbox.add_widget(toolbar)

        content = BoxLayout(
            orientation="vertical",
            padding=dp(20),
            spacing=dp(18),
            size_hint_y=None,
        )
        content.bind(minimum_height=content.setter("height"))

        # ── Search input ──────────────────────────────────
        self.query_field = MDTextField(
            hint_text="Enter research topic…",
            mode="fill",
        )
        content.add_widget(self.query_field)

        # ── Google Scholar button ─────────────────────────
        scholar_card = MDCard(
            orientation="vertical",
            padding=dp(16),
            radius=[dp(16)] * 4,
            elevation=2,
            size_hint_y=None,
            height=dp(120),
            ripple_behavior=True,
        )
        scholar_card.add_widget(
            MDLabel(
                text="[b]Google Scholar[/b]",
                markup=True,
                font_style="H6",
                theme_text_color="Primary",
            )
        )
        scholar_card.add_widget(
            MDLabel(
                text="Scholarly articles, journals & citations",
                font_style="Caption",
                theme_text_color="Secondary",
            )
        )
        scholar_card.add_widget(
            MDRaisedButton(
                text="Search on Google Scholar",
                on_release=lambda _: self._open_scholar(),
            )
        )
        content.add_widget(scholar_card)

        # ── Shodhganga button ─────────────────────────────
        shodh_card = MDCard(
            orientation="vertical",
            padding=dp(16),
            radius=[dp(16)] * 4,
            elevation=2,
            size_hint_y=None,
            height=dp(120),
            ripple_behavior=True,
        )
        shodh_card.add_widget(
            MDLabel(
                text="[b]Shodhganga[/b]",
                markup=True,
                font_style="H6",
                theme_text_color="Primary",
            )
        )
        shodh_card.add_widget(
            MDLabel(
                text="Indian Ph.D. theses & dissertations",
                font_style="Caption",
                theme_text_color="Secondary",
            )
        )
        shodh_card.add_widget(
            MDRaisedButton(
                text="Search on Shodhganga",
                on_release=lambda _: self._open_shodhganga(),
            )
        )
        content.add_widget(shodh_card)

        # ── Tip box ───────────────────────────────────────
        tip = MDCard(
            orientation="vertical",
            padding=dp(16),
            radius=[dp(16)] * 4,
            elevation=0,
            md_bg_color=(0.9, 0.95, 1, 1),
            size_hint_y=None,
            height=dp(100),
        )
        tip.add_widget(
            MDLabel(
                text="[b]Tip[/b]",
                markup=True,
                font_style="Subtitle2",
                theme_text_color="Custom",
                text_color=(0.1, 0.35, 0.7, 1),
            )
        )
        tip.add_widget(
            MDLabel(
                text='Use AND/OR operators for better results, e.g. "machine learning AND healthcare"',
                font_style="Caption",
                theme_text_color="Secondary",
            )
        )
        content.add_widget(tip)

        scroll = ScrollView(size_hint=(1, 1))
        scroll.add_widget(content)
        vbox.add_widget(scroll)
        self.add_widget(vbox)

    def _open_scholar(self):
        q = self.query_field.text.strip()
        if not q:
            Snackbar(text="Please enter a search topic first").open()
            return
        url = f"https://scholar.google.com/scholar?q={quote_plus(q)}"
        webbrowser.open(url)

    def _open_shodhganga(self):
        q = self.query_field.text.strip()
        if not q:
            Snackbar(text="Please enter a search topic first").open()
            return
        url = f"https://shodhganga.inflibnet.ac.in/simple-search?query={quote_plus(q)}"
        webbrowser.open(url)


# ─────────────────────────────────────────
#  Main App
# ─────────────────────────────────────────
class PaperWiseApp(MDApp):
    dialog = None

    def build(self):
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.accent_palette  = "Indigo"
        self.theme_cls.theme_style     = "Light"

        self.store = JsonStore("paperwise_papers.json")

        # Screen manager with bottom nav
        self.sm = MDScreenManager()
        self.library_screen  = LibraryScreen(app_ref=self)
        self.discover_screen = DiscoverScreen(app_ref=self)
        self.sm.add_widget(self.library_screen)
        self.sm.add_widget(self.discover_screen)

        root = BoxLayout(orientation="vertical")

        root.add_widget(self.sm)

        # Bottom navigation bar
        from kivymd.uix.bottomnavigation import MDBottomNavigation, MDBottomNavigationItem
        # We use a simple toolbar-style bottom bar for compatibility
        nav_bar = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(56),
        )

        lib_btn = MDFlatButton(
            text="Library",
            on_release=lambda _: self._switch_screen("library"),
        )
        disc_btn = MDFlatButton(
            text="Discover",
            on_release=lambda _: self._switch_screen("discover"),
        )
        nav_bar.add_widget(lib_btn)
        nav_bar.add_widget(disc_btn)
        root.add_widget(nav_bar)

        return root

    def on_start(self):
        self.refresh_library()

    def _switch_screen(self, name: str):
        self.sm.current = name

    # ── Data helpers ───────────────────────────────────────

    def _all_papers(self) -> list:
        papers = []
        for key in self.store.keys():
            try:
                papers.append(dict(self.store.get(key)))
            except Exception:
                pass
        # Newest first
        papers.sort(key=lambda p: p.get("date_added", 0), reverse=True)
        return papers

    def refresh_library(self, query: str = ""):
        papers = self._all_papers()
        if query:
            q = query.lower()
            papers = [
                p for p in papers
                if q in p.get("title", "").lower()
                or q in p.get("author", "").lower()
                or q in p.get("keywords", "").lower()
                or q in p.get("journal", "").lower()
            ]
        self.library_screen.refresh(papers)

    def delete_paper(self, paper_id: str):
        try:
            self.store.delete(paper_id)
        except Exception:
            pass
        self.refresh_library()
        Snackbar(text="Paper removed from library").open()

    # ── Add Paper dialog ───────────────────────────────────

    def show_add_dialog(self, *args):
        if self.dialog:
            self.dialog.dismiss()

        content = BoxLayout(
            orientation="vertical",
            spacing=dp(10),
            size_hint_y=None,
            height=dp(440),
        )

        self._f_title   = MDTextField(hint_text="Title *",   mode="fill")
        self._f_author  = MDTextField(hint_text="Author *",  mode="fill")
        self._f_year    = MDTextField(hint_text="Year",      mode="fill", input_filter="int", max_text_length=4)
        self._f_journal = MDTextField(hint_text="Journal",   mode="fill")
        self._f_doi     = MDTextField(hint_text="DOI (optional)",  mode="fill")
        self._f_url     = MDTextField(hint_text="URL (optional)",  mode="fill")
        self._f_keywords= MDTextField(hint_text="Keywords (comma-separated)", mode="fill")

        for f in (self._f_title, self._f_author, self._f_year,
                  self._f_journal, self._f_doi, self._f_url, self._f_keywords):
            content.add_widget(f)

        self.dialog = MDDialog(
            title="Add Research Paper",
            type="custom",
            content_cls=content,
            buttons=[
                MDFlatButton(
                    text="CANCEL",
                    on_release=lambda _: self.dialog.dismiss(),
                ),
                MDRaisedButton(
                    text="SAVE",
                    on_release=lambda _: self._save_paper(),
                ),
            ],
        )
        self.dialog.open()

    def _save_paper(self):
        title  = self._f_title.text.strip()
        author = self._f_author.text.strip()

        if not title or not author:
            Snackbar(text="Title and Author are required").open()
            return

        paper_id = str(uuid.uuid4())
        self.store.put(
            paper_id,
            id=paper_id,
            title=title,
            author=author,
            year=self._f_year.text.strip(),
            journal=self._f_journal.text.strip(),
            doi=self._f_doi.text.strip(),
            url=self._f_url.text.strip(),
            keywords=self._f_keywords.text.strip(),
            date_added=int(__import__("time").time()),
        )

        self.dialog.dismiss()
        self.refresh_library()
        Snackbar(text="Paper saved successfully!").open()

    # ── Citation dialog ────────────────────────────────────

    def show_citation_dialog(self, paper: dict, style: str = "APA"):
        if self.dialog:
            self.dialog.dismiss()

        citation_text = make_citation(paper, style)

        content = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            height=dp(120),
            padding=dp(8),
        )
        content.add_widget(
            MDLabel(
                text=citation_text,
                font_style="Body2",
                theme_text_color="Primary",
            )
        )

        self.dialog = MDDialog(
            title=f"{style} Citation",
            type="custom",
            content_cls=content,
            buttons=[
                MDFlatButton(
                    text="CLOSE",
                    on_release=lambda _: self.dialog.dismiss(),
                ),
                MDRaisedButton(
                    text="COPY",
                    on_release=lambda _: self._copy_citation(citation_text),
                ),
            ],
        )
        self.dialog.open()

    def _copy_citation(self, text: str):
        Clipboard.copy(text)
        self.dialog.dismiss()
        Snackbar(text="Citation copied to clipboard!").open()

    # ── About dialog ───────────────────────────────────────

    def show_about(self, *args):
        if self.dialog:
            self.dialog.dismiss()

        total = len(self.store.keys())
        content = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            height=dp(120),
            spacing=dp(8),
            padding=dp(8),
        )
        content.add_widget(MDLabel(text="Research paper organizer for students.", font_style="Body2"))
        content.add_widget(MDLabel(text=f"Papers in library: {total}", font_style="Body1", bold=True))
        content.add_widget(MDLabel(text="Data stored locally on device (paperwise_papers.json)", font_style="Caption", theme_text_color="Hint"))

        self.dialog = MDDialog(
            title="PaperWise v2.0",
            type="custom",
            content_cls=content,
            buttons=[MDRaisedButton(text="OK", on_release=lambda _: self.dialog.dismiss())],
        )
        self.dialog.open()


if __name__ == "__main__":
    PaperWiseApp().run()
