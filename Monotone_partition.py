import tkinter as tk



def cross(a, b, c):
    return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])


def above(p, q):
    return p[1] < q[1] or (p[1] == q[1] and p[0] < q[0])


def area(pts):
    s = 0
    for i in range(len(pts)):
        x1, y1 = pts[i]
        x2, y2 = pts[(i + 1) % len(pts)]
        s += x1 * y2 - x2 * y1
    return s / 2


def segments_cross(a, b, c, d):
    d1, d2 = cross(c, d, a), cross(c, d, b)
    d3, d4 = cross(a, b, c), cross(a, b, d)
    return d1 * d2 < 0 and d3 * d4 < 0


def is_simple(pts):
    n = len(pts)
    for i in range(n):
        for j in range(i + 2, n):
            if i == 0 and j == n - 1:
                continue  
            if segments_cross(pts[i], pts[(i + 1) % n], pts[j], pts[(j + 1) % n]):
                return False
    return True

def vertex_type(pts, i):
    prev = pts[i - 1]
    v = pts[i]
    nxt = pts[(i + 1) % len(pts)]
    angle_less_180 = cross(prev, v, nxt) < 0    

    if above(v, prev) and above(v, nxt):       
        return "start" if angle_less_180 else "split"
    if above(prev, v) and above(nxt, v):       
        return "end" if angle_less_180 else "merge"
    return "regular"


def x_on_edge(pts, e, y):
    """x точки ребра e на высоте y."""
    a = pts[e]
    b = pts[(e + 1) % len(pts)]
    if a[1] == b[1]:
        return min(a[0], b[0])
    return a[0] + (y - a[1]) * (b[0] - a[0]) / (b[1] - a[1])


def find_diagonals(pts):
    n = len(pts)
    types = [vertex_type(pts, i) for i in range(n)]

    order = sorted(range(n), key=lambda i: (pts[i][1], pts[i][0]))

    status = []
    helper = {}
    diagonals = []

    def edge_left_of(i):
        x, y = pts[i]
        best = None
        for e in status:
            xe = x_on_edge(pts, e, y)
            if xe <= x and (best is None or xe > x_on_edge(pts, best, y)):
                best = e
        return best

    for i in order:
        t = types[i]
        prev_edge = (i - 1) % n          

        if t == "start":
            status.append(i)
            helper[i] = i

        elif t == "end":
            if types[helper[prev_edge]] == "merge":
                diagonals.append((i, helper[prev_edge]))
            status.remove(prev_edge)

        elif t == "split":
            e = edge_left_of(i)
            diagonals.append((i, helper[e]))   
            helper[e] = i
            status.append(i)
            helper[i] = i

        elif t == "merge":
            if types[helper[prev_edge]] == "merge":
                diagonals.append((i, helper[prev_edge]))
            status.remove(prev_edge)
            e = edge_left_of(i)
            if types[helper[e]] == "merge":
                diagonals.append((i, helper[e]))
            helper[e] = i                     

        else:  
            if above(pts[i - 1], pts[i]):
                if types[helper[prev_edge]] == "merge":
                    diagonals.append((i, helper[prev_edge]))
                status.remove(prev_edge)
                status.append(i)
                helper[i] = i
            else:
                e = edge_left_of(i)
                if types[helper[e]] == "merge":
                    diagonals.append((i, helper[e]))
                helper[e] = i

    return diagonals

def cut_polygon(n, diagonals):
    parts = [list(range(n))]
    for a, b in diagonals:
        for part in parts:
            if a in part and b in part:
                i, j = sorted((part.index(a), part.index(b)))
                piece1 = part[i:j + 1]
                piece2 = part[j:] + part[:i + 1]
                parts.remove(part)
                parts += [piece1, piece2]
                break
    return parts

COLORS = ["#ffd6a5", "#caffbf", "#9bf6ff", "#bdb2ff",
          "#ffc6ff", "#fdffb6", "#a0c4ff", "#ffadad"]

points = []
closed = False

root = tk.Tk()
root.title("Разбиение полигона на монотонные части")
canvas = tk.Canvas(root, width=900, height=600, bg="white")
canvas.pack()
label = tk.Label(root, text="ЛКМ — вершина, ПКМ — замкнуть и разбить")
label.pack()


def draw_point(p):
    canvas.create_oval(p[0] - 3, p[1] - 3, p[0] + 3, p[1] + 3, fill="black")


def on_left_click(event):
    if closed:
        return
    p = (event.x, event.y)
    if points:
        canvas.create_line(points[-1], p, width=2)
    points.append(p)
    draw_point(p)


def on_right_click(event):
    global points, closed
    if closed or len(points) < 3:
        return
    if not is_simple(points):
        label.config(text="Полигон самопересекается! Нажмите «Очистить».")
        return

    if area(points) > 0:
        points.reverse()
    closed = True

    diagonals = find_diagonals(points)
    parts = cut_polygon(len(points), diagonals)
    canvas.delete("all")
    for k, part in enumerate(parts):
        canvas.create_polygon([points[i] for i in part],
                              fill=COLORS[k % len(COLORS)], outline="")
    canvas.create_polygon(points, fill="", outline="black", width=2)
    for a, b in diagonals:
        canvas.create_line(points[a], points[b], fill="red", width=2, dash=(6, 4))
    for p in points:
        draw_point(p)

    label.config(text=f"Диагоналей: {len(diagonals)}, монотонных частей: {len(parts)}")


def clear():
    global points, closed
    points = []
    closed = False
    canvas.delete("all")
    label.config(text="ЛКМ — вершина, ПКМ — замкнуть и разбить")


tk.Button(root, text="Очистить", command=clear).pack(pady=4)
canvas.bind("<Button-1>", on_left_click)
canvas.bind("<Button-3>", on_right_click)
root.mainloop()