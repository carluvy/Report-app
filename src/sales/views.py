import pandas as pd
from django.shortcuts import render, get_object_or_404

# Create your views here.
from django.views.generic import ListView, DetailView

from sales.forms import SalesSearchForm
from sales.models import Sale
from .utils import get_salesman_from_id, get_customer_from_id, get_chart


def home_view(request):
    sales_df = None
    positions_df = None
    merged_df = None
    df = None
    chart = None

    form = SalesSearchForm(request.POST or None)

    if request.method == 'POST':
        date_from = request.POST.get('date_from')
        date_to = request.POST.get('date_to')
        chart_type = request.POST.get('chart_type')

        sales_qs = Sale.objects.filter(created__date__lte=date_to, created__date__gte=date_from)
        # customer_data = Sale.objects.filter(customer_name)
        if len(sales_qs) > 0:
            sales_df = pd.DataFrame(sales_qs.values())
            sales_df['customer_id'] = sales_df['customer_id'].apply(get_customer_from_id)
            sales_df['salesman_id'] = sales_df['salesman_id'].apply(get_salesman_from_id)
            sales_df['created'] = sales_df['created'].apply(lambda x: x.strftime('%Y-%m-%d '))
            sales_df['updated'] = sales_df['updated'].apply(lambda x: x.strftime('%Y-%m-%d'))
            sales_df.rename({'customer_id': 'customer', 'salesman_id': 'salesman', 'id': 'sales_id',
                             }, axis=1, inplace=True)
            # sales_df['sales_id'] = sales_df['id']
            positions_data = []
            for sale in sales_qs:
                for pos in sale.get_positions():
                    obj = {
                        'position_id': pos.id,
                        'product': pos.product.name,
                        'quantity': pos.quantity,
                        'price': pos.price,
                        'sales_id': pos.get_sales_id(),

                    }
                    positions_data.append(obj)
            positions_df = pd.DataFrame(positions_data)
            merged_df = pd.merge(sales_df, positions_df, on='sales_id')
            df = merged_df.groupby('transaction_id', as_index=False)['price'].agg('sum')
            chart = get_chart(chart_type, df, labels=df['transaction_id'].values)

            sales_df = sales_df.to_html(index=False)
            positions_df = positions_df.to_html(index=False)
            merged_df = merged_df.to_html(index=False)
            df = df.to_html(index=False)


        else:
            print("nothing")
    context = {
        'form': form,
        'sales_df': sales_df,
        'positions_df': positions_df,
        'merged_df': merged_df,
        'df': df,
        'chart': chart,

    }
    # print(type(sales_df))
    return render(request, 'sales/home.html', context)


class SalesListView(ListView):
    model = Sale
    template_name = 'sales/main.html'


class SaleDetailView(DetailView):
    model = Sale
    template_name = 'sales/detail.html'


def sale_list_view(request):
    # we can use filters
    query_set = Sale.objects.all()
    return render(request, 'sales/main.html', {'object_list': query_set})


def sale_detail_view(request, **kwargs):
    # we can use filters
    pk = kwargs.get('pk')
    obj = Sale.objects.get(pk=pk)
    obje = get_object_or_404(Sale, pk=pk)
    return render(request, 'sales/main.html', {'object': obj})
