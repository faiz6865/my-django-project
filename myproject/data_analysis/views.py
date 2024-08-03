from django.shortcuts import render
from .forms import UploadFileForm
import pandas as pd
import matplotlib.pyplot as plt
import io
import base64
import urllib.parse
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

def index(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = request.FILES['file']
            file_name = default_storage.save(uploaded_file.name, ContentFile(uploaded_file.read()))
            request.session['file_name'] = file_name  
            return HttpResponseRedirect(reverse('results'))
    else:
        form = UploadFileForm()
    return render(request, 'index.html', {'form': form})

def results(request):
    file_name = request.session.get('file_name', None)
    if not file_name:
        return HttpResponseRedirect(reverse('index')) 
    file_path = default_storage.path(file_name)
    df = pd.read_csv(file_path, encoding='utf-8')
    first_rows = df.head().to_html()
    missing_values = df.isnull().sum().to_frame('Missing Values').to_html()
    plt.figure(figsize=(10, 6))
    df.hist(figsize=(10, 6))
    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    string = base64.b64encode(buf.read())
    uri = 'data:image/png;base64,' + urllib.parse.quote(string)

    return render(request, 'results.html', {
        'first_rows': first_rows,
        'missing_values': missing_values,
        'histogram': uri
    })
