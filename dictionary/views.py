from django.views.generic import ListView, TemplateView
from django.http import Http404, HttpResponse
from django.views.decorators.http import require_http_methods
from .data import crops_data

class CropListView(TemplateView):
    template_name = 'dictionary/crop_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['crops'] = crops_data
        return context

class CropDetailView(TemplateView):
    template_name = 'dictionary/crop_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        crop_id = kwargs.get('pk')
        
        # Find the crop with the matching ID
        crop = next((item for item in crops_data if item["id"] == crop_id), None)
        
        if crop is None:
            raise Http404("Crop not found")
            
        context['crop'] = crop
        context['diseases'] = crop.get('diseases', [])
        return context

@require_http_methods(["GET"])
def populate_database(request):
    """
    Deprecated: Data is now hardcoded for presentation.
    """
    return HttpResponse(
        "<h1>Data is Hardcoded</h1>"
        "<p>The application is currently using static data for presentation purposes. No database population is required.</p>"
        "<p><a href='/dictionary/'>View Dictionary</a></p>",
        content_type="text/html"
    )

