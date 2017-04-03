from django.core.urlresolvers import reverse
from django.shortcuts import render, get_object_or_404
from django.views.generic.edit import CreateView
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.views.generic.edit import UpdateView
from django.http import Http404

from digitalmarket.mixins import (
    LoginRequiredMixin,
    MultiSlugMixin,
    StaffRequiredMixin,
    SubmitBtnMixin,
)

from .forms import ProductAddForm, ProductModelForm
from .mixins import ProductManagerMixin
from .models import Product


class ProductCreateView(LoginRequiredMixin, SubmitBtnMixin, CreateView):
    model = Product
    template_name = "form.html"
    form_class = ProductModelForm
    # success_url = "/products/"
    submit_btn = "Add Product"

    def form_valid(self, form):
        user = self.request.user
        form.instance.user = user
        valid_data = super(ProductCreateView, self).form_valid(form)
        form.instance.managers.add(user)
        # add all default users
        return valid_data
    #
    # def get_success_url(self):
    #     return reverse("products:list")

class ProductUpdateView(ProductManagerMixin, SubmitBtnMixin, MultiSlugMixin, UpdateView):
    model = Product
    template_name = "form.html"
    form_class = ProductModelForm
    success_url = "/products/"
    submit_btn = "Update Product"


class ProductDetailView(MultiSlugMixin, DetailView):
    model = Product


class ProductListView(ListView):
    model = Product

    def get_queryset(self, *args, **kwargs):
        qs = super(ProductListView, self).get_queryset(**kwargs)
        # qs = qs.filter(title__icontains="asdfasdf")
        return qs


# Create your views here.
def create_view(request):
    # FORM
    form = ProductModelForm(request.POST or None)
    if form.is_valid():
        instance = form.save(commit=False)
        instance.sale_price = instance.price
        instance.save()
    template = "form.html"
    context = {
        "form": form,
        "submit_btn": "Save Product"
    }
    return render(request, template, context)


def update_view(request, object_id=None):
    print request
    product = get_object_or_404(Product, id=object_id)
    form = ProductModelForm(request.POST or None, instance=product)
    if form.is_valid():
        instance = form.save(commit=False)
        # instance.sale_price = instance.price
        instance.save()
    template = "form.html"
    context = {
        'object': product,
        'form': form,
        "submit_btn": "Update Product"
    }
    return render(request, template, context)


def detail_slug_view(request, slug=None):
    print request
    try:
        product = get_object_or_404(Product, slug=slug)
    except Product.MultipleObjectsReturned:
        product = Product.objects.filter(slug=slug).order_by('-title').first()
    #print slug
    #product = 1
    template = "detail_view.html"
    context = {'object': product}
    return render(request, template, context)


def detail_view(request, object_id):
    print request
    if object_id is not None:
        product = get_object_or_404(Product, id=object_id)
        template = "detail_view.html"
        context = {'object': product}
        return render(request, template, context)
    else:
        raise Http404


def list_view(request):
    print request
    queryset = Product.objects.all().first()
    template = "list_view.html"
    context = {"queryset": queryset}
    return render(request, template, context)