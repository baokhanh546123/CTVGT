import matplotlib.pyplot as plt
import networkx as nx

# Định nghĩa lớp cho cây nhị phân
class TreeNode:
    def __init__(self, value):
        self.value = value
        self.left = None
        self.right = None

# Hàm thêm phần tử vào cây nhị phân tìm kiếm
def insert(root, x):
    if root is None:
        return TreeNode(x)
    if x < root.value:
        root.left = insert(root.left, x)
    elif x > root.value:
        root.right = insert(root.right, x)
    return root

# Hàm tìm giá trị nhỏ nhất trong cây (dùng trong delete)
def minvalue(root):
    while root.left is not None:
        root = root.left
    return root.value

# Hàm xóa một phần tử trong cây nhị phân tìm kiếm
def delete(root, x):
    if root is None:
        return root
    if x < root.value:
        root.left = delete(root.left, x)
    elif x > root.value:
        root.right = delete(root.right, x)
    else:
        # Trường hợp nút cần xóa có một hoặc không có con
        if root.left is None:
            return root.right
        elif root.right is None:
            return root.left
        # Trường hợp nút cần xóa có cả hai con
        root.value = minvalue(root.right)
        root.right = delete(root.right, root.value)
    return root

# Hàm vẽ cây nhị phân lên màn hình
def draw_tree(root):
    # Khởi tạo một đồ thị không có hướng
    G = nx.DiGraph()

    # Hàm đệ quy để thêm các nút và các cạnh vào đồ thị
    def add_edges(node, pos, x=0, y=0, layer=1):
        if node is not None:
            G.add_node(node.value, pos=(x, y))  # Thêm nút vào đồ thị
            if node.left:
                G.add_edge(node.value, node.left.value)  # Thêm cạnh với con trái
                l_x = x - 1 / layer
                add_edges(node.left, pos, x=l_x, y=y-1, layer=layer+1)
            if node.right:
                G.add_edge(node.value, node.right.value)  # Thêm cạnh với con phải
                r_x = x + 1 / layer
                add_edges(node.right, pos, x=r_x, y=y-1, layer=layer+1)

    add_edges(root, pos={})
    
    # Vẽ cây sử dụng matplotlib
    pos = nx.get_node_attributes(G, 'pos')  # Lấy tọa độ của các nút
    plt.figure(figsize=(8, 6))
    nx.draw(G, pos, with_labels=True, node_size=2000, node_color='skyblue', font_size=15, font_weight='bold', arrows=True)
    plt.title("Binary Tree Visualization")
    plt.show()


if __name__ == '__main__':
# Tạo cây với giá trị ban đầu
    root = TreeNode(19)  # Khởi tạo cây với giá trị 19

    # Thêm các phần tử vào cây
    root = insert(root, 45)
    root = insert(root, 10)
    root = insert(root, 25)
    root = insert(root, 5)
    root = insert(root, 15)
    root = delete(root,10)
    # Vẽ cây
    draw_tree(root)