import pathlib
import urllib.parse

from fasthtml.common import *
from components import *
from contents import *

from datetime import datetime

hdrs = (
    Script(src="https://unpkg.com/htmx.org@next/dist/htmx.min.js"),
    MarkdownJS(),
    HighlightJS(langs=['python', 'javascript', 'html', 'css']),
    Link(rel='stylesheet', href='https://cdn.jsdelivr.net/npm/normalize.css@8.0.1/normalize.min.css', type='text/css'),
    Link(rel='stylesheet', href='https://cdn.jsdelivr.net/npm/sakura.css/css/sakura.css', type='text/css'),    
    Link(rel='stylesheet', href='/public/style.css', type='text/css'),    
)

def not_found(response):
    response.status = 404
    return Titled("Not Found", H1("404 Not Found"), P("The page you are looking for does not exist."))

exception_handlers = {
    404: not_found
}

app, rt = fast_app(hdrs=hdrs, default_hdrs=False, debug=True,)

@rt("/")
@layout
def get():
    posts = [blog_post(title=x["title"],slug=x["slug"],timestamp=x["date"],description=x.get("description", "")) for x in list_posts()]
    popular = [blog_post(title=x["title"],slug=x["slug"],timestamp=x["date"],description=x.get("description", "")) for x in list_posts() if x.get("popular", False)]    
    return (
        Title("zhuganglie"),
        Section(
                H1('Recent Writings'),
                *posts[:3]
            ),
        Hr(),
        Section(
                H1('Popular Writings'),
                *popular
        ),
       
    )
    

@rt("/posts")
@layout
def get():
    posts = [blog_post(title=x["title"],slug=x["slug"],timestamp=x["date"],description=x.get("description", "")) for x in list_posts()]
    duration = round((datetime.now() - datetime(2020, 8, 6)).days / 365.25, 2)
    return (
            Title("All posts"),
            Section(
            H1(f'All Articles ({len(posts)})'),
            P(f'Everything written for the past {duration} years.'),
            *posts,
            A("← Back to home", href="/"),
        ),)

@rt("/posts/{slug}")
@layout
def get(slug: str):
    # post = [x for x in filter(lambda x: x["slug"] == slug, list_posts())][0]
    content, metadata = get_post(slug)
    # content = pathlib.Path(f"posts/{slug}.md").read_text().split("---")[2]
    # metadata = yaml.safe_load(pathlib.Path(f"posts/{slug}.md").read_text().split("---")[1])    
    tags = [tag(slug=x) for x in metadata.get("tags", [])]
    return (
        Title(metadata['title']),
        Section(
            H1(metadata["title"]),
            Div(content,cls="marked"),
            P(Span("Tags: "), *tags),
            A("← Back to all articles", href="/"),
        ),
    )

@rt("/tags")
@layout
def get():
    tags = [tag_with_count(slug=x[0], count=x[1]) for x in list_tags().items()]
    return (Title("Tags"),
        Section(
            H1('Tags'),
            P('All tags used in the blog'),
            *tags,
            Br(), Br(),
            A("← Back home", href="/"),
        )
    )

@rt("/tags/{slug}")
@layout
def get(slug: str):
    posts = [blog_post(title=x["title"],slug=x["slug"],timestamp=x["date"],description=x.get("description", "")) for x in list_posts() if slug in x.get("tags", [])]
    return (Title(f"Tag: {urllib.parse.unquote(slug)}"),
        Section(
            H1(f'Posts tagged with "{urllib.parse.unquote(slug)}" ({len(posts)})'), # moved len(posts) calculation here
            *posts,            A("← Back home", href="/"),
        )
    )

@rt("/search")
def get(q: str = ""):
    def _s(obj: dict, name: str, q: str):
        content =  obj.get(name, "")
        if isinstance(content, list):
            content = " ".join(content)
        return q.lower().strip() in content.lower().strip()

    posts = []
    if q:
        posts = [blog_post(title=x["title"],slug=x["slug"],timestamp=x["date"],description=x.get("description", "")) for x in list_posts() if
                    any(_s(x, name, q) for name in ["title", "description", "content", "tags"])]
        
    if posts:
        messages = [H2(f"Search results on '{q}'"), P(f"Found {len(posts)} results")]
    elif q:
        messages = [P("No results found")]
    else:
        messages = []
    return Title("Search"), blog_header(), Body(Main(
        Form(Input(name="q", value=q, id="search", type="search"), Button("Search"), style="text-align: center;"),
        Section(
            *messages,
            *posts,
            A("← Back home", href="/"),
        )
    ), onload="document.getElementById('search').focus()"), blog_footer()

@rt("/{slug}")
@layout
def get(slug: str):
    return markdown_page(slug)
    
@rt("/{slug_1}/{slug_2}")
@layout
def get(slug_1: str, slug_2: str):
    return markdown_page(slug_1 + "/" + slug_2)


serve()