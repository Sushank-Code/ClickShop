from kartapp.models import Category

def category_links(request):
    links = Category.objects.all()
    return dict(links = links)         # context processor want the dict  =  always retun in dict