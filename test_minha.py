import requests, time

r = requests.get('https://minhareceita.org/?cnae=4120400&uf=ES', timeout=20)
data = r.json()
c1 = data['cursor']
print('P1 ok, count:', len(data['data']), 'cursor:', c1)

time.sleep(2)
r2 = requests.get(f'https://minhareceita.org/?cnae=4120400&uf=ES&cursor={c1}', timeout=20)
print('P2 status:', r2.status_code)
if r2.status_code == 200:
    d2 = r2.json()
    print('P2 count:', len(d2['data']), 'cursor:', d2['cursor'])
