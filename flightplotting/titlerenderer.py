from plotly.io._base_renderers import BrowserRenderer, open_html_in_browser
from plotly.io._renderers import renderers


class TitleBrowserRenderer(BrowserRenderer):
    def __init__(
        self,
        config=None,
        auto_play=False,
        using=None,
        new=0,
        autoraise=True,
        post_script=None,
        animation_opts=None,
    ):
        super().__init__(
            config, auto_play, using, new, autoraise, post_script, animation_opts
        )

    browser_tab_title = "Undefined"

    def render(self, fig_dict):
        from plotly.io import to_html

        html = (
            """
<title>
"""
            + self.browser_tab_title
            + """
</title>
"""
            + to_html(
                fig_dict,
                config=self.config,
                auto_play=self.auto_play,
                include_plotlyjs=True,
                include_mathjax="cdn",
                post_script=self.post_script,
                full_html=True,
                animation_opts=self.animation_opts,
                default_width="100%",
                default_height="100%",
                validate=False,
            )
        )
        open_html_in_browser(html, self.using, self.new, self.autoraise)


renderers["titleBrowser"] = TitleBrowserRenderer()