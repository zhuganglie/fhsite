from fasthtml.common import *
import functools
from datetime import datetime
from dateutil import parser
import pytz
import pathlib
import urllib.parse
import yaml

__all__ = ["blog_header", "blog_post", "blog_footer", "tag",
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
                image="/public/images/zhuganglie_transparent.svg",
                ),
        Header(
            A(Img(
                cls='borderCircle', alt='zhuganglie', src='/public/images/zhuganglie_transparent.svg', width='108', height='108')
                , href='/'),
             A(H2('ZHUGANGLIE'), href="/"),
            P(
                A('About', href='/about', data_page="about"), '|', 
                A('Articles', href='/posts', data_page="posts"), '|',
                A('Tags', href='/tags', data_page="tags"), '|',
                A('Search', href='/search', data_page="search")
            ), style="text-align: center;"
        ))


def blog_post(title: str, slug: str, timestamp: str, description: str):
     # Convert the timestamp
    dt = convert_dtstr_to_dt(timestamp)
    
    # Format the timestamp or display an error message
    formatted_timestamp = format_datetime(dt) 

    decoded_title = urllib.parse.unquote(title)


    return Span(
                Small(Time(format_datetime(convert_dtstr_to_dt(timestamp)))),
                H2(A(decoded_title, href=f"/posts/{slug}")),
                P(description), Br(),
               
        )

def blog_footer():
    return Footer(Hr(), P(
            A('Email', href='mailto:pyrrhonianpig@gmail.com'), '|',
            A('FreeFrom', href='https://freefrom.space/zhuganglie'), '|',
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
        
        Section(
            Div(content,cls="marked")
        ),
        A("← Back to home", href="/")
    )

def Layout(title: str, *args, **kwargs):
    """Layout for the blog, but can be adapted to anything"""
    return (
        Title(title), 
        blog_header(), 
        Main(*args, **kwargs), 
        blog_footer(), 
        Script("""
        function setActiveLink() {
          const currentPath = window.location.pathname;
          const links = document.querySelectorAll('a[data-page]');
          
          links.forEach(link => {
            if (currentPath.includes(link.getAttribute('data-page'))) {
              link.classList.add('active-link');
            } else {
              link.classList.remove('active-link');
            }
          });
        }
        document.addEventListener('DOMContentLoaded', setActiveLink);
        """)
    )

def layout(view_function):
    """Decorator to wrap a view function with a layout"""
    @functools.wraps(view_function)
    def _wrapper(*args, **kwargs):
        result = view_function(*args, **kwargs)
        # If there's a Title() in the result at the top level, use it, otherwise use the default
       ### title = next((ele[1] for ele in result if ele[0] == "title"), "zhuganglie")
        title = "zhuganglie"  #Default
        # Check if result is iterable and contains Title()
        if isinstance(result, (list, tuple)):
            for ele in result:
                if isinstance(ele, tuple) and ele[0] == "title":
                    title = ele[1]
                    break
        return Layout(title, *result)
    return _wrapper