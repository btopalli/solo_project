from django.shortcuts import render
from django.db import models

def index(request):
    return  render(request, 'index.html')
