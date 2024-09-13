from django.shortcuts import render
from django.http import HttpResponse
from .forms import UploadFileForm
from .utils import extract_text_from_pdf, preprocess_text, extract_key_points, summarize_text
from django.views.decorators.http import require_http_methods
from django.core.files.storage import FileSystemStorage
from website.summarizer import summarize_pdf

@require_http_methods(["GET", "POST"])
def upload_and_summarize(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                pdf_file = request.FILES['pdf_file']
                fs = FileSystemStorage()
                filename = fs.save(pdf_file.name, pdf_file)
                file_path = fs.path(filename)
                
                summary = summarize_pdf(file_path)
                key_points = extract_key_points(summary)
                
                fs.delete(filename)
                
                context = {
                    'form': form,
                    'summary': summary,
                    'key_points': key_points,
                }
                return render(request, 'upload.html', context)
            except Exception as e:
                return render(request, 'upload.html', {'form': form, 'summary': summary})
    else:
        form = UploadFileForm()
    return render(request, 'User/upload.html', {'form': form})
