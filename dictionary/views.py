from django.views.generic import ListView, DetailView
from .models import Crop

class CropListView(ListView):
    model = Crop
    template_name = 'dictionary/crop_list.html'
    context_object_name = 'crops'
    ordering = ['name']

class CropDetailView(DetailView):
    model = Crop
    template_name = 'dictionary/crop_detail.html'
    context_object_name = 'crop'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add diseases related to this crop
        context['diseases'] = self.object.diseases.all()
        return context
