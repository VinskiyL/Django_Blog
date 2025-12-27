from django.shortcuts import render, get_object_or_404, redirect
from taggit.models import Tag
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.contrib import messages
from django.http import Http404
from .models import Post
from .forms import CommentForm, PostForm


def post_list(request, tag_slug=None):
    post_list = Post.published.all()
    tag = None
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        post_list = post_list.filter(tags__in=[tag])
    paginator = Paginator(post_list, 3)
    page_number = request.GET.get('page', 1)
    try:
        page = paginator.page(page_number)
    except PageNotAnInteger:
        page = paginator.page(1)
    except EmptyPage:
        page = paginator.page(paginator.num_pages)
    return render(request, 'blog/post/list.html', {'page': page, 'tag': tag})


def post_detail(request, year, month, day, post):
    post = get_object_or_404(
        Post,
        slug=post,
        publish__year=year,
        publish__month=month,
        publish__day=day
    )

    if post.status == Post.Status.DRAFT:
        if not request.user.is_authenticated or (request.user != post.author and not request.user.is_superuser):
            raise Http404()

    comments = post.comments.filter(active=True)

    if request.method == 'POST':
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.post = post
            new_comment.save()
            return redirect(post.get_absolute_url())
    else:
        comment_form = CommentForm()

    post_tags_ids = post.tags.values_list('id', flat=True)
    similar_posts = Post.published.filter(tags__in=post_tags_ids).exclude(id=post.id)
    similar_posts = similar_posts.annotate(same_tags=Count('tags')).order_by('-same_tags', '-publish')[:4]

    return render(
        request,
        'blog/post/detail.html',
        {
            'post': post,
            'comments': comments,
            'form': comment_form,
            'similar_posts': similar_posts
        }
    )


@login_required
def post_create(request):
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            form.save_m2m()
            messages.success(request, "Пост успешно создан")
            return redirect(post.get_absolute_url())
    else:
        form = PostForm()
    return render(request, 'blog/post/create.html', {'form': form})


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if request.user != post.author and not request.user.is_superuser:
        messages.error(request, "Вы не можете редактировать этот пост")
        return redirect('blog:post_list')

    if request.method == 'POST':
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, "Пост успешно обновлен")
            return redirect(post.get_absolute_url())
    else:
        form = PostForm(instance=post)

    return render(request, 'blog/post/edit.html', {'form': form, 'post': post})


@login_required
def post_delete(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if request.user != post.author and not request.user.is_superuser:
        messages.error(request, "Вы не можете удалить этот пост")
        return redirect('blog:post_list')

    post.delete()
    messages.success(request, "Пост успешно удален")
    return redirect('blog:post_list')


@login_required
def draft_list(request):
    drafts = Post.objects.filter(
        status=Post.Status.DRAFT,
        author=request.user
    ).order_by('-publish')

    return render(request, 'blog/post/draft_list.html', {'drafts': drafts})


@login_required
def publish_draft(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if request.user != post.author and not request.user.is_superuser:
        messages.error(request, "Вы не можете опубликовать этот пост")
        return redirect('blog:post_list')

    if post.status == Post.Status.DRAFT:
        post.status = Post.Status.PUBLISHED
        post.save()
        messages.success(request, "Пост опубликован")

    return redirect(post.get_absolute_url())