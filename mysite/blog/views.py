from django.shortcuts import render, get_object_or_404, redirect
from .models import Post, Comment
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import ListView
from .forms import EmailPostForm, CommentForm
from django.core.mail import send_mail
from taggit.models import Tag
from django.views.decorators.http import require_POST
from django.db.models import Count

class PostListView(ListView):
    queryset = Post.published.all()
    context_object_name = 'posts'
    paginate_by = 3
    template_name = 'blog/post/list.html'

# 폼에 맞게 작성한 글을 이메일로 보내는 메서드
def post_share(request, post_id):
    post = get_object_or_404(Post, id = post_id, status = Post.Status.PUBLISHED) # 조건에 맞지 않으면 404 오류 반환

    sent = False
    if request.method == 'POST':
        form = EmailPostForm(request.POST)
        if form.is_valid(): # 폼이 유효하지 않은 경우 제출된 데이터를 가지고 다시 렌더링
            cd = form.cleaned_data
            post_url = request.build_absolute_uri(post.get_absolute_url())
            subject = f"{cd['name']} recommends you read "\
                      f"{post.title}"
            message = f"Read {post.title} at {post_url}\n\n"\
                      f"{cd['name']}\'s comments: {cd['comments']}"
            send_mail(subject, message, 'gmdt1998@gmail.com',[cd['to']])
            sent = True

    else :
        form = EmailPostForm() # 요청이 get 인경우(처음 폼을 보여주는게 되니까) 빈 폼을 생성하여 보여줌
        # post : 현재 공유하려는 게시물, form : 사용자가 입력할 수 있는 이메일 , sent : 전송여부
    return render(request, 'blog/post/share.html', {'post':post, 'form':form, 'sent':sent})

#
def post_list(request, tag_slug=None) :
    post_list = Post.published.all()
    tag = None
    if tag_slug:
        tag = get_object_or_404(Tag, slug = tag_slug)
        post_list = post_list.filter(tags__in=[tag])
    paginator = Paginator(post_list, 3)
    page_number = request.GET.get('page', 1)

    try:
        posts = paginator.page(page_number)
    except PageNotAnInteger:
        posts = Paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)

    return render(request, 'blog/post/list.html', {'posts' : posts, 'tag' : tag} ) # 복수

def post_detail(request, year, month, day, post) :
    post = get_object_or_404(Post,
                             publish__year = year,
                             publish__month = month,
                             publish__day = day,
                             slug = post,
                             status = Post.Status.PUBLISHED) # 404는 예외처리 함수
    comments = post.comments.filter(active = True)

    form = CommentForm()

    # List of similar posts
    post_tags_ids = post.tags.values_list('id', flat = True)
    similar_posts = Post.published.filter(tags__in = post_tags_ids)\
                                    .exclude(id=post.id)
    similar_posts = similar_posts.annotate(same_tags=Count('tags'))\
                                    .order_by('-same_tags', '-publish')[:4]

    return render(request, 'blog/post/detail.html', {'post' : post,
                                                                          'comments' : comments,
                                                                          'form' : form,
                                                                          'similar_posts' : similar_posts}) # 단수


def post_comment(request, post_id):
    post = get_object_or_404(Post, id = post_id, status = Post.Status.PUBLISHED)

    comment = None
    form = CommentForm(data = request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.save()
        return render(request, 'blog/post/comment.html',{'post' : post, 'form' : form, 'comment' : comment})

