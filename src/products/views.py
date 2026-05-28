from django.contrib import messages
from django.db.models import Avg, Count
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CommentForm
from .models import Category, Comment, Product


def product_list(request, category_slug=None):
    """Display a list of all products, optionally filtered by category.

    Args:
        request: The HTTP request object.
        category_slug: Optional slug to filter products by category.

    Returns:
        HttpResponse: Rendered product list page.
    """
    categories = Category.objects.all()
    products = Product.objects.select_related("category").annotate(
        avg_rating=Avg("comments__rating"), total_ratings=Count("comments")
    )
    if category_slug:
        products = products.filter(category__slug=category_slug)
    return render(request, "products.html", {"categories": categories, "products": products})


def product_detail(request, category_slug, pk):
    """Display the detail page for a single product, and handle comment submission.

    Args:
        request: The HTTP request object.
        category_slug: The slug of the product's category.
        pk: The primary key of the product.

    Returns:
        HttpResponse: Rendered product detail page, or a redirect after successful form submission.
    """
    product = get_object_or_404(
        Product.objects.select_related("category").annotate(
            avg_rating=Avg("comments__rating"), total_ratings=Count("comments")
        ),
        pk=pk,
        category__slug=category_slug,
    )

    related_products = (
        Product.objects.filter(category=product.category)
        .exclude(pk=product.pk)
        .annotate(avg_rating=Avg("comments__rating"), total_ratings=Count("comments"))
        .order_by("-avg_rating", "-total_ratings", "name")[:8]
    )

    comments = product.comments.select_related("user").order_by("-created_at")

    if request.method == "POST":
        form = CommentForm(request.POST, initial={"user": request.user if request.user.is_authenticated else None})
        if form.is_valid():
            rating = form.cleaned_data["rating"]
            text = form.cleaned_data.get("text", "")

            if request.user.is_authenticated:
                # Upsert: update existing comment or create a new one
                comment, created = Comment.objects.get_or_create(
                    product=product, user=request.user, defaults={"rating": rating, "text": text}
                )
                if not created:
                    comment.rating = rating
                    comment.text = text
                    comment.save()
                messages.success(request, "Your rating was {}.".format("submitted" if created else "updated"))
            else:
                # Guest: create a new comment (no uniqueness constraint)
                comment = form.save(commit=False)
                comment.product = product
                comment.save()
                messages.success(request, "Thank you for your rating.")

            return redirect("product_detail", category_slug=category_slug, pk=product.pk)
    else:
        form = CommentForm()

    return render(
        request,
        "product.html",
        {"product": product, "comments": comments, "related_products": related_products, "form": form},
    )