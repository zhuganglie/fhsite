from fasthtml.common import *
import functools
from datetime import datetime
from dateutil import parser
import pytz
import pathlib
import urllib.parse
import yaml

__all__ = ['blog_header', 'blog_post', "blog_footer", "tag",
           "tag_with_count", "markdown_page", "Layout", "layout"]

def convert_dtstr_to_dt(date_str):
    """
    Convert a naive or non-naive date/datetime string to a datetime object.
    Naive datetime strings are assumed to be in GMT (UTC) timezone.
    
    Args:
        date_str (str): The date or datetime string to convert.
        
    Returns:
        datetime: The corresponding datetime object.
    """
    try:
        dt = parser.parse(date_str)
        if dt.tzinfo is None:
            # If the datetime object is naive, set it to GMT (UTC)
            dt = dt.replace(tzinfo=pytz.UTC)
        return dt
    except (ValueError, TypeError) as e:
        print(f"Error parsing date string: {e}")
        return None

def format_datetime(dt: datetime):
    if dt is None:
        return "Datetime object cannot be None"
    
    # Format the datetime object
    formatted_date = dt.strftime("%d/%m/%Y")
    formatted_time = dt.strftime("%I:%M%p").lstrip('0').lower()
    
    return f"{formatted_date} at {formatted_time}"


def blog_header():
    return (
        Socials(site_name="zhuganglie",
                title="zhuganglie",
                description="A personal blog",
                url="https://zhuganglie.vercel.app",
                image="/public/images/zhuganglie.svg",
                ),
        Header(
            A(Img(
                cls='borderCircle', alt='zhuganglie', src='/public/images/zhuganglie.svg', width='108', height='108')
                , href='/'),
             A(H2('zhuganglie'), href="/"),
            P(
                A('About', href='/about'),'|', 
                A('Articles', href='/posts'), '|',
                A('Tags', href='/tags'), '|',
                A('Search', href='/search')
            ), style="text-align: center;"
        ))

def blog_post(title: str, slug: str, timestamp: str, description: str):
     # Convert the timestamp
    dt = convert_dtstr_to_dt(timestamp)
    
    # Format the timestamp or display an error message
    formatted_timestamp = format_datetime(dt) 

    return Span(
                H2(A(title, href=f"/posts/{slug}")),
                P(description, Br(), Small(Time(format_datetime(convert_dtstr_to_dt(timestamp))))),
        )

def blog_footer():
    return Footer(Hr(), P(
            A('Email', href='mailto:pyrrhonianpig@gmail.com'), '|',
            A('Github', href='https://github.com/zhuganglie/'), '|',
            A('Twitter', href='https://twitter.com/zhugangliet'), '|',
          
        ),
        P(f'All rights reserved {datetime.now().year}, zhuganglie')
    )

def tag(slug: str):
    return A(slug, href=f"/tags/{slug}")

def tag_with_count(slug: str, count: int):
    return A(Span(slug), Small(f"({count})"), href=f"/tags/{slug}")

def markdown_page(slug: str):
    try:
        text = pathlib.Path(f"pages/{slug}.md").read_text()
    except FileNotFoundError:
        return Response("Page not found", status_code=404) 
    content = ''.join(text.split("---")[2:])
    metadata = yaml.safe_load(text.split("---")[1])
    return (Title(metadata.get('title', slug)),
        A("← Back to home", href="/"),
        Section(
            Div(content,cls="marked")
        )
    )

def Layout(title: str, *args, **kwargs):
    """Layout for the blog, but can be adapted to anything"""
    return Title(title), blog_header(), Main(*args, **kwargs), blog_footer()

def layout(view_function):
    """Decorator to wrap a view function with a layout"""
    @functools.wraps(view_function)
    def _wrapper(*args, **kwargs):
        result = view_function(*args, **kwargs)
        # If there's a Title() in the result at the top level, use it, otherwise use the default
        title = next((ele[1] for ele in result if ele[0] == "title"), "zhuganglie")
        return Layout(title, *result)
    return _wrapper
