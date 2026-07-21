from django.http import JsonResponse
from django.views import View
from django.shortcuts import render
from PIL import Image

from .search import search_similar
from store.models import Product

class VisualSearchView(View):

    def post(self, request, *args, **kwargs):
        uploaded = request.FILES.get("image")
        if not uploaded:
            return JsonResponse(
                {"error": "No image file provided. Send a file under the 'image' field."},
                status=400,
            )

        try:
            pil_image = Image.open(uploaded).convert("RGB")
        except Exception as exc:
            return JsonResponse(
                {"error": f"Could not open the uploaded image: {exc}"},
                status=400,
            )

        try:
            product_ids = search_similar(pil_image)
        except FileNotFoundError as exc:
            return JsonResponse({"error": str(exc)}, status=503)
        except Exception as exc:
            return JsonResponse(
                {"error": f"Search failed: {exc}"},
                status=500,
            )

        if not product_ids:
            return JsonResponse({"results": []})

        products_by_id = {
            p.pk: p
            for p in Product.objects.filter(pk__in=product_ids)
        }

        results = []
        for pid in product_ids:
            product = products_by_id.get(pid)
            if product is None:
                continue

            image_url = ""
            if product.image:
                image_url = request.build_absolute_uri(product.image.url)

            results.append({
                "id": product.pk,
                "name": product.product_name,
                "price": str(product.price),
                "image_url": image_url,
                "detail_url": product.get_url(),
            })

        return JsonResponse({"results": results})


class VisualSearchPageView(View):
   
    def get(self, request, *args, **kwargs):
        return render(request, "visual_search/search.html")