#import necessary headers
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.shortcuts import render
from django.forms import modelformset_factory
from django.contrib.auth import authenticate, login, logout
from django.views.generic import View

from .models import *
from .forms import *

#upload display page
def upload(request):
    if not request.user.is_staff or not request.user.is_superuser:
        raise Http404
    return render(request,"upload/upload.html")

def aboutme(request):
    return render(request,"mine/aboutme.html")
#mainpage
def userpage(request, id=None):

    queryset_list = Blog.objects.all()
    image_list = AddImage.objects.all()
    mainimage_list = MainImage.objects.all()

    paginator = Paginator(queryset_list, 3)
    page_req_var = "page"
    page = request.GET.get(page_req_var)
    queryset = paginator.get_page(page)

    pag = Paginator(image_list,3)
    page_request_var = "pge"
    page_var = request.GET.get(page_request_var)
    imageset = pag.get_page(page_var)

    context = {
        "image_list": imageset,
        "mainimage_list":mainimage_list,
        "page_req_var":page_req_var,
        "object_list":queryset,
        "page_request_var": page_request_var,
    }

    return render(request,"user/index.html", context)

#upload image page
def image(request):
    if not request.user.is_staff or not request.user.is_superuser:
        raise Http404
    form1 = ImagePostForm(request.POST or None, request.FILES or None)
    form2 = ImageForm(request.POST or None, request.FILES or None)
    files = request.FILES.getlist('image')
    if form2.is_valid() and form1.is_valid():
        post_form = form1.save(commit=False)
        post_form.save()
        for f in files:
            photo = Images(image=f,post=post_form,)
            photo.save()
        return HttpResponseRedirect(post_form.get_absolute_url())
    else:
        messages.error(request,"Not Created")
    context = {
        "form1":form1,
        "form2":form2,
    }
    return render(request, 'upload/uploadimage.html',context)

def mainimage(request):
    if not request.user.is_staff or not request.user.is_superuser:
        raise Http404
    form = MainImageForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        instance = form.save(commit=False)
        instance.save()
		# messages.success(request, "<a href='#'>Item</a> saved",extra_tags='html_safe')
		# return HttpResponseRedirect(instance.get_absolute_url())
    context = {
			"form": form,
		}
    return render(request,"upload/mainimage.html",context)

#upload blog page
def blog(request):
    if not request.user.is_staff or not request.user.is_superuser:
        raise Http404
    form1 = BlogForm(request.POST or None, request.FILES or None)
    form2 = BlogImageForm(request.POST or None, request.FILES or None)
    files = request.FILES.getlist('image')
    if form2.is_valid() and form1.is_valid():
        post_form = form1.save(commit=False)
        post_form.save()
        for f in files:
            photo = BlogImages(image=f,post=post_form,)
            photo.save()
        return HttpResponseRedirect(post_form.get_url())
    else:
        messages.error(request,"Not Created")
    context = {
        "form1":form1,
        "form2":form2,
    }
    return render(request, 'upload/uploadblog.html',context)

#list of blogs
def blogs(request):
    queryset_list = Blog.objects.all()
    paginator = Paginator(queryset_list, 5)
    page_req_var = "page"
    page = request.GET.get(page_req_var)
    queryset = paginator.get_page(page)


    context = {
        "object_list": queryset,
        "page_req_var": page_req_var,
    }

    return render(request, 'user/blogs.html', context)

#list of images
def images(request):
    queryset_list = AddImage.objects.all()
    paginator = Paginator(queryset_list, 6)
    page_req_var = "page"
    page = request.GET.get(page_req_var)
    queryset = paginator.get_page(page)


    context = {
        "object_list": queryset,
        "page_req_var": page_req_var,
    }
    return render(request, 'user/images.html', context)

#image list by id
def image_list(request, id=None):
    instance_post = get_object_or_404(AddImage, id=id)
    all_images = Images.objects.filter(post=instance_post.id)
    queryset_list = ImageCaption.objects.all()

    context={
        "title": instance_post.place,
        "instance": instance_post,
        'image_list':all_images,
        "object_list": queryset_list,
    }
    return render(request, 'user/imagelist.html',context)

#blog list by id
def blog_list(request, id=None):
    instance_post = get_object_or_404(Blog, id=id)
    all_images = BlogImages.objects.filter(post=instance_post.id)
    queryset_list = Caption.objects.all()

    context={
        "title": instance_post.place,
        "instance": instance_post,
        'image_list':all_images,
        "object_list": queryset_list,
    }
    return render(request, 'user/bloglist.html',context)

#image individual detail
def imagedetail(request, id=None):
    if not request.user.is_staff or not request.user.is_superuser:
        instance_image = get_object_or_404(Images, id=id)
        queryset_list = ImageCaption.objects.filter(postimage=instance_image.id).order_by('-id')
        form = OrderForm(request.POST or None, request.FILES or None)
        username = request.POST.get('Name')
        phonenumber = request.POST.get('Phone')

        if form.is_valid():
            order = Buyers(Name= username, Phone= phonenumber, image_id=instance_image.image)
            order.save()

            return HttpResponseRedirect(order.get_absolute_url())
        context={
            "instance": instance_image,
            "form":form,
            "object_list": queryset_list,
            "id" : id,
        }
        return render(request, 'user/imagedetail.html',context)
    instance_image = get_object_or_404(Images, id=id)
    queryset_list = ImageCaption.objects.filter(postimage=instance_image.id).order_by('-id')

    form = ImageCaptionForm(request.POST or None, request.FILES or None)
    caption = request.POST.get('image_caption')
    if form.is_valid():
        add_caption = ImageCaption(image_caption=caption, postimage=instance_image, id=instance_image.id)
        add_caption.save()

        return HttpResponseRedirect(add_caption.get_url())
    else:
        messages.error(request,"Not Created")
    context={
        "instance": instance_image,
        "form":form,
        "object_list": queryset_list,
    }
    return render(request, 'upload/addimagecaption.html',context)

def blogdetail(request, id=None):
    if not request.user.is_staff or not request.user.is_superuser:
        instance_image = get_object_or_404(BlogImages, id=id)
        queryset_list = Caption.objects.filter(post=instance_image.id).order_by('-id')
        form = OrderForm(request.POST or None, request.FILES or None)
        username = request.POST.get('Name')
        phonenumber = request.POST.get('Phone')

        if form.is_valid():
            order = Buyers(Name= username, Phone= phonenumber, image_id=instance_image.image)
            order.save()

            return HttpResponseRedirect(order.get_absolute_url())
        context={
            "instance": instance_image,
            "form":form,
            "object_list": queryset_list,
            "id" : id,
        }
        return render(request, 'user/blogdetail.html',context)
    instance_image = get_object_or_404(BlogImages, id=id)
    queryset_list = Caption.objects.filter(post=instance_image.id).order_by('-id')

    form = CaptionForm(request.POST or None, request.FILES or None)
    caption = request.POST.get('image_caption')
    if form.is_valid():
        add_caption = Caption(image_caption=caption, post=instance_image, id=instance_image.id)
        add_caption.save()

        return HttpResponseRedirect(add_caption.get_url())
    else:
        messages.error(request,"Not Created")
    context={
        "instance": instance_image,
        "form":form,
        "object_list": queryset_list,
    }
    return render(request, 'upload/addimagecaption.html',context)



#admin sign in
class sign_in(View):
    def get(self, request):
        form = LoginForm()
        context = {
            'form': form,
        }
        return render(request, 'user/login.html', context)

    def post(self, request):
        form = LoginForm(request.POST or None)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user and user.is_active:
                messages.success(request, "Logged In Successfully")
                login(request, user)
                return redirect('chitrakatha:upload')
        messages.warning(request, "Log In Failure")
        context = {
            'form': form,
        }
        return render(request, 'user/login.html', context)

#admin sign out
def sign_out(request):
    logout(request)
    return redirect('chitrakatha:login')

def mainpage(request):
    if not request.user.is_staff or not request.user.is_superuser:
        raise Http404
    return render(request,"upload/upload.html")

def viewpage(request):
    if not request.user.is_superuser or not request.user.is_staff:
	       raise Http404
    image_list = AddImage.objects.all()
    blog_list = Blog.objects.all()

    paginator = Paginator(image_list, 4)
    page_req_var = "page"
    page = request.GET.get(page_req_var)
    queryset = paginator.get_page(page)

    pag = Paginator(blog_list, 4)
    page_request_var = "page"
    page = request.GET.get(page_request_var)
    querylist = pag.get_page(page)


    context = {
        "image_list": queryset,
        "object_list": querylist,
        "page_req_var": page_req_var,
        "page_request_var": page_request_var,
        "blog_list": blog_list,
    }



    return render(request, 'chitrakatha/viewpage.html', context)

def mainimagedetail(request, id=None):
    if not request.user.is_staff or not request.user.is_superuser:
        instance_image = get_object_or_404(MainImage, id=id)
        form = OrderForm(request.POST or None, request.FILES or None)
        username = request.POST.get('Name')
        phonenumber = request.POST.get('Phone')

        if form.is_valid():
            order = Buyers(Name= username, Phone= phonenumber, image_id=instance_image.image)
            order.save()

            return HttpResponseRedirect(order.get_absolute_url())
        context={
            "instance": instance_image,
            "form":form,
            "id" : id,
        }
        return render(request, 'user/detailimage.html',context)
    queryset_list = Blog.objects.all()
    image_list = AddImage.objects.all()
    mainimage_list = MainImage.objects.all()

    context = {
        "object_list": queryset_list,
        "image_list": image_list,
        "mainimage_list":mainimage_list,
    }

    return render(request,"user/index.html", context)

def thankyou(request):
    return render(request,"user/thankyou.html")

def orders(request):
    if not request.user.is_staff or not request.user.is_superuser:
        raise Http404

    queryset_list = Buyers.objects.all().order_by("-id")
    paginator = Paginator(queryset_list, 10)
    page_req_var = "page"
    page = request.GET.get(page_req_var)
    queryset = paginator.get_page(page)


    context = {
        "object_list": queryset,
        "page_req_var": page_req_var,
    }

    return render(request,"chitrakatha/orders.html",context)

def deleteimage(request, id=None):
    if not request.user.is_superuser or not request.user.is_staff:
	       raise Http404
    instance_post = get_object_or_404(AddImage, id=id)
    all_images = Images.objects.filter(post=instance_post.id)
    queryset_list = ImageCaption.objects.all()

    context={
        "title": instance_post.place,
        "instance": instance_post,
        'image_list':all_images,
        "object_list": queryset_list,
        "id": instance_post.id,
    }
    return render(request, 'chitrakatha/deleteimage.html',context)

def deleteblog(request, id=None):
    if not request.user.is_superuser or not request.user.is_staff:
	       raise Http404
    instance_post = get_object_or_404(Blog, id=id)
    all_images = BlogImages.objects.filter(post=instance_post.id)
    queryset_list = Caption.objects.all()

    context={
        "title": instance_post.place,
        "instance": instance_post,
        'image_list':all_images,
        "object_list": queryset_list,
        "id": instance_post.id,
    }
    return render(request, 'chitrakatha/deleteblog.html',context)

def imagedelete(request, id=None):
	if not request.user.is_superuser or not request.user.is_staff:
	       raise Http404
	instance = get_object_or_404(AddImage, id=id)
	instance.delete()
	messages.success(request, "Successfully deleted")
	return redirect("chitrakatha:viewpage")

def blogdelete(request, id=None):
	if not request.user.is_superuser or not request.user.is_staff:
            raise Http404
	instance = get_object_or_404(Blog, id=id)
	instance.delete()
	messages.success(request, "Successfully deleted")
	return redirect("chitrakatha:viewpage")

def updateblog(request, id=None):
    if not request.user.is_staff or not request.user.is_superuser:
        raise Http404
    instance = get_object_or_404(Blog, id=id)
    form1 = BlogForm(request.POST or None, request.FILES or None,instance=instance)
    form2 = BlogImageForm(request.POST or None, request.FILES or None,instance=instance)
    files = request.FILES.getlist('image')
    if form2.is_valid() and form1.is_valid():
        post_form = form1.save(commit=False)
        post_form.save()
        for f in files:
            photo = BlogImages(image=f,post=post_form,)
            photo.save()
        return HttpResponseRedirect(post_form.get_url())
    else:
        messages.error(request,"Not Created")
    context = {
        "form1":form1,
        "form2":form2,
    }
    return render(request, 'chitrakatha/updateblog.html',context)
