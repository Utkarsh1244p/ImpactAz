from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.contrib import messages
from django.utils import timezone
from datetime import datetime
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from app.models import (
    GeneralInfo, 
    Service, 
    Testimonial, 
    FrequentlyAskedQuestion,
    ContactFormLog,
    Blog
)

# Create your views here.
def index(request):
    general_info = GeneralInfo.objects.first()
    services = Service.objects.all()
    testimonials = Testimonial.objects.all()
    faqs = FrequentlyAskedQuestion.objects.all() 
    recent_blogs = Blog.objects.all().order_by("-created_at")[:3]
    # for blog in recent_blogs:
    #     print(f"blog : {blog}")
    #     print(f"blog.created_at : {blog.created_at}")
    #     print(f"blog.author : {blog.author}")
    #     print(f"blog.author.country : {blog.author.country}")
    #     print("")
    default_value = ''

    context = {
        'company_name' : getattr(general_info, 'company_name', default_value),
        'location' : getattr(general_info, 'location', default_value),
        'email' : getattr(general_info, 'email', default_value),
        'phone' : getattr(general_info, 'phone', default_value),
        'open_hours' : getattr(general_info, 'open_hours', default_value),
        'video_url' : getattr(general_info, 'video_url', default_value),
        'twitter_url' : getattr(general_info, 'twitter_url', default_value),
        'facebook_url' : getattr(general_info, 'facebook_url', default_value),
        'instagram_url' : getattr(general_info, 'instagram_url', default_value),
        'linkedin_url' : getattr(general_info, 'linkedin_url', default_value),
        
        'services' : services,
        'testimonials' : testimonials,
        'faqs' : faqs,
        'blogs' : recent_blogs,
    }
    return render(request, 'index.html', context)

def blogs(request):
    all_blogs = Blog.objects.all()
    paginator = Paginator(all_blogs, 3)
    page = request.GET.get('page')
    try:
        blogs = paginator.page(page)
    except PageNotAnInteger:
        blogs = paginator.page(1)
    except EmptyPage:
        blogs = paginator.page(paginator.num_pages)

    # print(f"paginator.num_pages : {paginator.num_pages}")
    context = {
        'blogs' : blogs,
        'paginator' : paginator
    }
    return render(request, 'blogs.html', context)

def blog_details(request, blog_id):
    blog = Blog.objects.get(id=blog_id)
    recent_blogs = Blog.objects.all().exclude(id=blog_id).order_by("-created_at")[:2]

    context = {
        'blog' : blog,
        'recent_blogs' : recent_blogs
    }
    return render(request, 'blog-details.html', context)

def submit_form(request):

    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')


        context = {
            'name' : name,
            'email' : email,
            'subject' : subject,
            'message' : message,
        }

        html_content = render_to_string('email.html', context)

        is_success = False
        is_error = False
        error_message = ""


        try:
            send_mail(
                subject = subject,
                message = None,
                html_message= html_content, 
                from_email = settings.EMAIL_HOST_USER,
                recipient_list = [settings.EMAIL_HOST_USER],
                fail_silently = False,
            )
        except Exception as e:
            is_error = True
            error_message = str(e)
            messages.error(request, "There is an error, could not send email.")
        else:
            is_success = True
            messages.success(request, "Email sent successfully.")

        ContactFormLog.objects.create(
            name = name,
            email = email,
            subject = subject,
            message = message,
            action_time = timezone.now(),
            is_success = is_success,
            is_error = is_error,
            error_message = error_message,
        )


    return redirect('home')