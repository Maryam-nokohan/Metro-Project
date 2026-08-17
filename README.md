# متروی قم — از قم تا نیویورک

سامانه‌ی مسیریابی و مدیریت شبکه‌ی متروی قم؛ پروژه‌ی درس طراحی الگوریتم‌ها.

## پیش‌نیازها

- Python 3.10 یا بالاتر

## نصب و اجرا

```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

سپس در مرورگر باز کنید:

```
http://127.0.0.1:8000
```

### اجرای تست‌ها

```bash
python -m unittest discover -s tests -v
```

## ساختار پروژه

```
models/         ساختمان‌داده‌های پایه: Graph, Station, Edge, Train, Passenger
algorithms/     پیاده‌سازی الگوریتم‌ها (BFS/DFS, Dijkstra, Kruskal/Prim, DAG,
                Bellman-Ford, Max-Flow, Floyd-Warshall, Articulation Points,
                Dominating Set, Levenshtein, Bidirectional Dijkstra)
utils/          لودر داده، صف اولویت، Disjoint-Set، تحلیل داده‌های عملیاتی
simulation/     شبیه‌سازی ورود مسافران
data/           داده‌ی ایستگاه‌ها، مسیرها و ظرفیت‌های شبکه‌ی قم
tests/          تست‌های واحد (unittest)
main.py         سرور FastAPI و تمام API endpointها
templates/      رابط کاربری وب (index.html)
```

## دورهای پروژه

| دور | موضوع |
|---|---|
| ۱ | مدل‌سازی گراف، دسترسی‌پذیری (BFS/DFS)، کوتاه‌ترین مسیر (Dijkstra) |
| ۲ | MST (Kruskal/Prim)، خط اکسپرس (DAG)، تشخیص چرخه‌ی منفی (Bellman-Ford) |
| ۳ | زمان‌بندی سکو، صف اعزام قطار، تحلیل داده، شبیه‌سازی مسافر |
| ۴ | Floyd-Warshall، Max-Flow، نقاط بحرانی، Dominating Set، جست‌وجوی تایپی |
| ۵ | Bidirectional Dijkstra (نوآوری) |