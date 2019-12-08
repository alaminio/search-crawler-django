from django.shortcuts import render
import requests
from bs4 import BeautifulSoup


def search(request):
    if request.GET:
        s = request.GET["search"]
    else:
        s = False

    context = {'s': s}

    if s:
        url = 'https://www.bing.com/search?q={}'.format(s)
        print(url)
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Safari/537.36',
        }
        page = requests.get(url, timeout=5, headers=headers)
        soup = BeautifulSoup(page.content, 'html.parser')
        ol = soup.find('ol', id='b_results')
        results = list()
        li = ol.find_all('li', class_='b_algo')
        for elm in li:
            result = dict()
            a = elm.find('a')

            if a:
                if a['href']:
                    result['a'] = a['href']
                if a.text:
                    result['title'] = a.text

            p = elm.find('p')
            if p and len(p.text) > 0:
                result['text'] = p.text
            results.append(result)

        context = {
            's': s,
            'results': results
        }

    return render(request, 'search/search.html', context)
