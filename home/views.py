from django.shortcuts import render,HttpResponse
from django.contrib.auth.decorators import login_required

from .models import Club#, Contact, Association
from blog.models import BlogPost

# Create your views here.

def index(request):
	blogs = BlogPost.objects.order_by('-date')[:5]
	#clubs
	club_objects = Club.objects.all()
	app_urls = ['codeschool:index','cogitans:index','droidclub:index','ecell:index','electrotech:index','oslc:index','renderedusict:index','turingai:index']
	clubs = zip(club_objects,app_urls)
	#associations
	# assocs = Association.objects.all()

	return render(request, 'home/index.html', {'clubs':clubs, 'blogs':blogs})

#
# def contactSubmit(request):
# 	if request.method == 'POST':
# 		name = request.POST['name']
# 		email = request.POST['email']
# 		content = request.POST['content']
# 		app_name = request.POST['app_name']
#
# 		Contact.objects.create(
# 			name = name,
# 			app_name = app_name,
# 			email = email,
# 			content = content
# 			)
# 	return HttpResponse('')
