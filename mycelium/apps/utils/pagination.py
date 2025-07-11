from typing import Dict, List, Any
from django.core.paginator import Paginator

# Pagination Configuration Constants
DEFAULT_PER_PAGE = 10
MAX_PAGES_WITHOUT_ELLIPSIS = 7
PAGES_TO_SHOW_AT_EDGES = 5
PAGES_AROUND_CURRENT = 1


def get_pagination_data(page_obj, paginator, request) -> Dict[str, Any]:
    """
    Generate pagination data for templates.
    
    Args:
        page_obj: The current page object from Django's paginator
        paginator: The paginator object
        request: The HTTP request object
        
    Returns:
        Dictionary containing all pagination data needed for templates
    """
    if not page_obj or not paginator:
        return {}
    
    current_page = page_obj.number
    total_pages = paginator.num_pages
    
    # Generate page range with ellipsis logic
    page_range = []
    show_ellipsis_start = False
    show_ellipsis_end = False
    
    if total_pages <= MAX_PAGES_WITHOUT_ELLIPSIS:
        # Show all pages if MAX_PAGES_WITHOUT_ELLIPSIS or fewer
        page_range = list(range(1, total_pages + 1))
    else:
        # Complex logic for showing pages with ellipsis
        if current_page <= PAGES_TO_SHOW_AT_EDGES - 1:
            # Show first PAGES_TO_SHOW_AT_EDGES pages + ellipsis + last page
            page_range = list(range(1, PAGES_TO_SHOW_AT_EDGES + 1)) + [total_pages]
            show_ellipsis_end = True
        elif current_page >= total_pages - (PAGES_TO_SHOW_AT_EDGES - 2):
            # Show first page + ellipsis + last PAGES_TO_SHOW_AT_EDGES pages
            page_range = [1] + list(range(total_pages - (PAGES_TO_SHOW_AT_EDGES - 1), total_pages + 1))
            show_ellipsis_start = True
        else:
            # Show first page + ellipsis + current-PAGES_AROUND_CURRENT, current, current+PAGES_AROUND_CURRENT + ellipsis + last page
            page_range = [1, current_page - PAGES_AROUND_CURRENT, current_page, current_page + PAGES_AROUND_CURRENT, total_pages]
            show_ellipsis_start = True
            show_ellipsis_end = True
    
    # Build pagination data
    pagination_data = {
        'has_previous': page_obj.has_previous(),
        'has_next': page_obj.has_next(),
        'previous_page_number': page_obj.previous_page_number() if page_obj.has_previous() else None,
        'next_page_number': page_obj.next_page_number() if page_obj.has_next() else None,
        'current_page': current_page,
        'total_pages': total_pages,
        'total_count': paginator.count,
        'start_index': page_obj.start_index(),
        'end_index': page_obj.end_index(),
        'page_range': page_range,
        'show_ellipsis_start': show_ellipsis_start,
        'show_ellipsis_end': show_ellipsis_end,
        'show_pagination': total_pages > 1,
    }
    
    return pagination_data


def paginate_queryset(queryset, request, per_page=DEFAULT_PER_PAGE):
    """
    Helper function to paginate a queryset and return both the page object
    and pagination data.
    
    Args:
        queryset: The queryset to paginate
        request: The HTTP request object
        per_page: Number of items per page (default: DEFAULT_PER_PAGE)
        
    Returns:
        Tuple of (page_obj, pagination_data)
    """
    from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
    
    paginator = Paginator(queryset, per_page)
    page = request.GET.get('page')
    
    try:
        page_obj = paginator.page(page)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)
    
    pagination_data = get_pagination_data(page_obj, paginator, request)
    
    return page_obj, pagination_data 