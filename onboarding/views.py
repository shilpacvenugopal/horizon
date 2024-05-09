from rest_framework.response import Response
from django.shortcuts import render
from django.conf import settings
from rest_framework.views import APIView
from django.core.files.base import ContentFile
from .models import Product, Category
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponse
import io
import os
import csv
import pandas as pd
import shutil


#CURD operation of Category
class CategoryAPIView(APIView):
    def get(self, request):
        if request.GET.get('id'):
           category_obj=Category.objects.filter(id=request.GET['id']).first()
           return Response({'category': {"id":category_obj.id,"name":category_obj.name}})
        else:
            category_list=[]
            default_page_size = 10
            default_page = 1
            category = Category.objects.all().order_by('name')
            search_query = request.GET.get('search')
            if search_query:
                category = category.filter(
                    Q(name__icontains=search_query)
                ).distinct()
            page_number = request.GET.get('page', default_page)
            page_size = request.GET.get('page_size', default_page_size)
            paginated_category=pagination(category,page_number,page_size)
            for category in paginated_category:
                category_list.append({"id":category.id,"name":category.name})
            return render(request, 'category.html', {
                'categories': category_list,
                'pagination': paginated_category,
                'request': request
            })

    def post(self,request):
        try:
            name = request.data['name']
        except KeyError as e:
            return Response({'error': f'Missing parameter: {e}'}, status=400)
        if request.data.get('id'):
            category_obj=Category.objects.filter(id=request.data['id']).update(name=name)
            return Response({'message': 'Category updated successfully'}, status=201)
        else:
            category = Category(name=name)
            category.save()
            return Response({'message': 'Category created successfully'}, status=201)

    def delete(self,request):
        if request.GET.get('id'):
            category=Category.objects.filter(id=request.GET['id']).first()
            if category:
                category.delete()
                return Response({'message': 'Category Deleted successfully'}, status=201)
            else:
                return Response({'message': 'Id not found'}, status=201)


#CURD operation of Product
class ProductAPIView(APIView):
    default_page_size = 10
    default_page = 1
    def get(self, request):
        category_id = request.GET.get('category_id')
        search_query = request.GET.get('search')
        product_list =[]
        products = Product.objects.filter(deleted_at=None).order_by('code')
        if category_id:
            products = products.filter(category__id=category_id)
        if search_query:
            products = products.filter(
                Q(name__icontains=search_query) |
                Q(code__icontains=search_query) |
                Q(price__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(category__name__icontains=search_query)
            ).distinct()
        page_number = request.GET.get('page', self.default_page)
        page_size = request.GET.get('page_size', self.default_page_size)
        paginated_products=pagination(products,page_number,page_size)
        for product in paginated_products:
            product_list.append(self.create_resp_dict(product))
        categories = Category.objects.all()
        return render(request, 'product_list.html', {
            'products': product_list,
            'categories': categories,
            'pagination': paginated_products,
            'request': request
        })




    def post(self,request):
        try:
            name = request.data['name']
            code = request.data['code']
            description = request.data['description']
            price = request.data['price']
            category = request.data['category']
            image = request.data.get('image')
        except KeyError as e:
            return Response({'error': f'Missing parameter: {e}'}, status=400)
        if request.data.get('id'):
            product=Product.objects.filter(id=request.data['id']).first()
            if product and product.image:
                product.image.delete(save=False)
            product.name = name
            product.code = code
            product.description = description
            product.price = price
            product.category = category
            product.image = image
            product.save()
            return Response({'message': 'Product updated successfully'}, status=201)
        else:
            product = Product(name=name, code=code, description=description, price=price, category_id=category, image=image)
            product.save()
            return Response({'message': 'Product created successfully'}, status=201)

    def delete(self,request):
        if request.GET.get('id'):
            product=Product.objects.filter(id=request.GET['id']).first()
            product.delete()
            return Response({'message': 'Product Deleted successfully'}, status=201)
        else:
            return Response({'message': 'Something went wrong'}, status=400)




    def create_resp_dict(self,product):
        return({'id': product.id,
                'name': product.name if product.name else '',
                'code': product.code if product.code else '',
                'description': product.description if product.description else '',
                'price': str(product.price) if product.price else '',
                'category': product.category.name if product and product.category else '',
                'image_url': product.image.url if product and product.image else '' })

#Import data to Product
class ProductUploadAPIView(APIView):
    def post(self, request):
        if 'file' not in request.FILES:
            return Response({'error': 'No file provided'}, status=400)
        uploaded_file = request.FILES['file']
        file_extension = uploaded_file.name.split('.')[-1].lower()
        if file_extension not in ['csv', 'xlsx']:
            return Response({'error': 'Unsupported file format'}, status=400)
        try:
            if file_extension == 'csv':
                df = pd.read_csv(uploaded_file)
            elif file_extension == 'xlsx':
                df = pd.read_excel(uploaded_file)
        except Exception as e:
            return Response({'error': f'Error reading file: {str(e)}'}, status=400)
        failed = []
        csv_errors = []
        for index, row in df.iterrows():
            error_message=[]
            product = Product()
            category = row.get('category')
            category_obj=Category.objects.filter(name__iexact=category).first()
            if category_obj:
                product.category = category_obj
            else:
                error_message.append('category not found')
            product.name = row.get('name')
            if Product.objects.filter(code=row.get('code')).first():
               error_message.append('code was already added before')
            if Product.objects.filter(code=row.get('code'),deleted_at=None).first():
               error_message.append('code already exist in the table')
            image_path = row.get('image_path')
            if error_message:
                failed.append({'name': row.get('name'), 'msg': ", ".join(error_message)})
                csv_errors.append(self.csv_error_reason(row.get('name'),error_message))
                continue
            product.code = row.get('code')
            product.description = row.get('description')
            product.price = row.get('price')
            if image_path:
                if os.path.exists(image_path):
                    # Open the image file and read its content
                    with open(image_path, 'rb') as file:
                        file_content = file.read()

                # Copy the image file from local to server
                        product.image.save(os.path.basename(image_path), ContentFile(file_content))

            product.save()
        if len(failed) > 0:
            return Response({"failed":failed,"csv_error_message":csv_errors,"csv_headers":self.csv_headers()})
        return Response({'message': 'Products uploaded successfully'}, status=201)

    def csv_error_reason(self, data, reason):
        data_dict = {"data": data}
        data_dict["reason"] = reason
        return data_dict


    def csv_headers(self):
        return  [
                    'name','code','description','price','category','image_path'
                ]

#Export sample template from Product

class ExportCSVTemplateAPIView(APIView):
    def get(self, request, format=None):
        response = HttpResponse(content_type='application/csv')
        response['Content-Disposition'] = 'attachment; filename=product.csv'
        writer = csv.writer(response)
        writer.writerow(ProductUploadAPIView().csv_headers())
        return response

# Pagination funcation
def pagination(products,page_number,page_size):
    paginator = Paginator(products, page_size)
    try:
        paginated_products = paginator.page(page_number)
    except PageNotAnInteger:
        paginated_products = paginator.page(1)
    except EmptyPage:
        paginated_products = paginator.page(paginator.num_pages)
    return paginated_products

# redirect to add_product template
def add_product(request):
    return render(request, 'add_product.html')

# redirect to  product_creation template
def product_creation(request):
    categories = Category.objects.all()
    return render(request, 'product_creation.html', {'categories': categories})