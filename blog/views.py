from django.shortcuts import render, get_object_or_404, redirect, HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, DetailView
from django.http import HttpResponseRedirect, Http404, HttpResponseForbidden
from django.http import JsonResponse
from django.core.urlresolvers import reverse, reverse_lazy
from .models import BlogPost, Upvote, Tag, CommentUpvote, Comments
from .forms import CommentForm
from log.models import UserProfile, Notification
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone


from django.views.generic import DetailView
from django.views.generic.edit import DeleteView

from .forms import BlogAddForm, PostAddForm
# Create your views here.

class BlogListView(ListView):
	model = BlogPost
	template_name = 'post/post_list.html'
	context_object_name = 'blogs'
#
# class BlogDetailView(DetailView):
# 	model = BlogPost
# 	template_name = 'blog/blog_detail.html'
# 	context_object_name = 'blog_detail'

def postDetailView(request, slug):
	# print("sulg = ", slug)

	user=None
	if request.user.is_authenticated():
		user = UserProfile.objects.get(user=request.user)

	blog = get_object_or_404(BlogPost, slug=slug)
	blog.upvotes = len(Upvote.objects.filter( title = blog.title ))
	blog.state = len(Upvote.objects.filter(title = blog.title , username = request.user))
	comments = blog.comments.filter(active=True, reply_for=None)
	try:
		for comment in comments:
			comment.upvotes_len = len(comment.upvotes.all())
			comment.state = len(comment.upvotes.filter(username=request.user.username))

		user = UserProfile.objects.get(user=request.user)
		if request.method == 'POST':
			comment_form = CommentForm(data=request.POST)
			if comment_form.is_valid():
				new_comment = comment_form.save(commit=False)
				new_comment.comment_author = request.user.username
				new_comment.post = blog
				new_comment.save()
				return redirect('blog:post-detail', slug=slug)
		else:
			comment_form = CommentForm()
		return render(request, 'post/post_detail_single.html', {'blog_detail': blog, 'form': comment_form, 'comments': comments})

	except:
		return render(request, 'post/post_detail_single.html', {'blog_detail': blog, 'comments': comments })


@login_required
def post_new(request):
	user = UserProfile.objects.get(user=request.user)

	if request.method == "POST":
		form = PostAddForm(request.POST, request.FILES)
		user = UserProfile.objects.get(user=request.user)
		if form.is_valid():
			post = form.save(commit=False)
			post.author = user.user.username
			post.club = user.club
			post.isblog = False

			if 'image' in request.FILES:
				post.image = request.FILES['image']

			post.save()
			return HttpResponseRedirect(reverse('community:index'))


	form = PostAddForm()
	return render(request, 'post/post_add_form.html', {'form':form})


@login_required
def post_edit(request, slug):
	user = UserProfile.objects.get(user=request.user)
	post = get_object_or_404(BlogPost, slug=slug)
	if request.user.username == post.author:
		if request.method == "POST":
			form = PostAddForm(request.POST, request.FILES ,instance=post)

			if form.is_valid():
				post = form.save(commit=False)
				post.author = str(user)
				post.club = str(user.club)
				post.date = timezone.now()

				if 'image' in request.FILES:
					post.image = request.FILES['image']

				post.save()
				return redirect('blog:post-detail', slug=post.slug)

		form = PostAddForm(instance=post)
		return render(request, 'post/post_edit_form.html', {'form': form})
	else:
		return redirect('home:index')

def blogDetailView(request, slug):
	# print("sulg = ", slug)

	blog = get_object_or_404(BlogPost, slug=slug)

	user=None
	if request.user.is_authenticated():
		user = UserProfile.objects.get(user=request.user)
		if request.user.username == blog.author:
			Notification.objects.filter(user=user, post=blog).delete()

	blog.upvotes = len(Upvote.objects.filter( title = blog.title ))
	blog.state = len(Upvote.objects.filter(title = blog.title , username = request.user))
	comments = blog.comments.filter(active=True, reply_for=None)
	try:
		for comment in comments:
			comment.upvotes_len = len(comment.upvotes.all())
			comment.state = len(comment.upvotes.filter(username=request.user.username))

		user = UserProfile.objects.get(user=request.user)
		if request.method == 'POST':
			comment_form = CommentForm(data=request.POST)
			if comment_form.is_valid():
				new_comment = comment_form.save(commit=False)
				new_comment.comment_author = request.user.username
				new_comment.post = blog
				new_comment.save()

				if request.user.username != blog.author:
					Notification.objects.create(
						user=UserProfile.objects.get(user__username=blog.author),
						type=Notification.comment_notification,
						post=blog
					)

				return redirect('blog:blog-detail', slug=slug)
		else:
			comment_form = CommentForm()
		return render(request, 'post/blog_detail_single.html', {'blog_detail': blog, 'form': comment_form, 'comments': comments})

	except:
		return render(request, 'post/blog_detail_single.html', {'blog_detail': blog, 'comments': comments })



@login_required
def blog_new(request):
	user = UserProfile.objects.get(user=request.user)

	if request.method == "POST":
		form = BlogAddForm(request.POST, request.FILES)
		user = UserProfile.objects.get(user=request.user)
		print("invalid form")
		if form.is_valid():
			post = form.save(commit=False)
			post.author = user.user.username
			post.club = user.club
			post.isblog = True


			if 'image' in request.FILES:
				post.image = request.FILES['image']

			post.save()
			blog = BlogPost.objects.get(title = post.title)
			for tag in form.cleaned_data['tags']:
				t = Tag.objects.get(word = tag)
				blog.tags.add(t)
			return HttpResponseRedirect(reverse('community:index'))


	form = BlogAddForm()
	return render(request, 'post/blog_add_form.html', {'form':form})



@login_required
def blog_edit(request, slug):
	print("start")
	user = UserProfile.objects.get(user=request.user)
	post = get_object_or_404(BlogPost, slug=slug)
	if request.user.username == post.author:
		if request.method == "POST":
			form = BlogAddForm(request.POST, request.FILES ,instance=post)
			print("okkkk")
			if form.is_valid():
				print("valid form")
				post = form.save(commit=False)
				post.author = str(user)
				post.club = str(user.club)
				post.date = timezone.now()

				if 'image' in request.FILES:
					post.image = request.FILES['image']

				post.save()
				blog = BlogPost.objects.get(title=post.title)
				blog.tags.clear()
				for tag in form.cleaned_data['tags']:
					t = Tag.objects.get(word=tag)
					blog.tags.add(t)
				print("done")
				return redirect('blog:blog-detail', slug=post.slug)

		form = BlogAddForm(instance=post)
		return render(request, 'post/blog_edit_form.html', {'form': form})

	else:
		return redirect('home:index')


class BlogDelete(LoginRequiredMixin, DeleteView):
	model = BlogPost
	success_url = reverse_lazy('community:index')

	def delete(self, request, *args, **kwargs):
		#the Post object
		self.object = self.get_object()
		print(self.object.author, "==", request.user)
		if str(self.object.author) == str(request.user):
			print(self.object.author, "==", request.user)

			success_url = self.get_success_url()
			self.object.delete()
			return HttpResponseRedirect(success_url)
		else:
			return HttpResponseForbidden("Cannot delete other's posts")


@login_required
def toggleCommentUpvote(request) :

    if (request.method == "POST") :

        comment_id = request.POST['id']
        comment_state = int(request.POST['state'])
        comment = get_object_or_404(Comments, id = comment_id)

        if (comment_state == 0) :
            CommentUpvote.objects.create( username = request.user , comment = comment )
        else :
            CommentUpvote.objects.get( username = request.user , comment = comment ).delete()
        upvotes = len(CommentUpvote.objects.filter(comment = comment))
        data = {'state': not comment_state, 'upvotes': upvotes}
    return JsonResponse(data)


@login_required
def replyComment(request):
	if request.method == "POST":
		comment_id = request.POST['id']
		comment = get_object_or_404(Comments, id=comment_id)
		comment_form = CommentForm(request.POST)
		if comment_form.is_valid():
			new_comment = comment_form.save(commit=False)
			new_comment.comment_author = request.user.username
			new_comment.post = comment.post
			new_comment.reply_for = comment
			new_comment.save()
		return redirect('blog:blog-detail', slug=comment.post.slug)
	return redirect('home:index')
