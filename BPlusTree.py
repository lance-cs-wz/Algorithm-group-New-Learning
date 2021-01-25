'''
建立元素为整数的B+树，从小到大排列。
自下而上建立树。
节点使用「数组」：内存空间连续；利用内存操作解决插入后数据平移的问题。
'''
import random
import time


class BPlusNodeData(object):
    def __init__(self, value=None, node=None):
        self._value = value  # 可以不缓存，则查询时间为logn
        self._node = node

    def value(self):
        return self._value

    def node(self):
        return self._node

    def clear(self):
        self._value = None
        self._node = None

    def empty(self):
        return self._value == None and self._node == None


class BPlusNode(object):
    '''
    非叶子节点
    '''

    def __init__(self, m):
        assert (m > 2)  # 让 m - 1 至少为2
        self.data = [BPlusNodeData()] * m  # 记录起始数值对应的区块

    def len(self):
        return len(self.data)

    def value(self):
        return self.data[0].value()

    def full(self):
        return not self.data[-1].empty()

    def empty(self):
        return self.data[0].empty()

    def insert(self, node, start_idx=0):
        if node.empty():  # 空节点不插入
            return

        if self.full():  # 满了不插入
            return

        for idx, data in enumerate(self.data):
            if idx < start_idx:
                continue

            self.data[idx] = BPlusNodeData(node.value(), node)
            # 数据为空，直接插入并结束
            if data.empty():
                break

            if isinstance(data, BPlusLeafNode):
                node = data

            if isinstance(data, BPlusNodeData):
                node = data.node()

    def split(self):
        node_new = BPlusNode(self.len())

        m_len = self.len() // 2  # 分离一半的数据出去。

        for idx in range(m_len, self.len()):
            node_new.data[idx - m_len] = self.data[idx]
            self.data[idx] = BPlusNodeData()  # 删除被分离出去的数据。

        return node_new


class BPlusLeafNode(object):
    '''
    叶子节点
    '''

    def __init__(self, m):
        self.M = m
        self.data = [None] * self.M  # 记录起始数值对应的区块
        self.next = None

    def len(self):
        return self.M

    def value(self):
        return self.data[0]

    def full(self):
        return self.data[-1] != None  # 满了

    def empty(self):
        return self.data[0] == None

    def insert(self, value):
        if self.full():
            return

        for idx, data in enumerate(self.data):
            if data == None:
                self.data[idx] = value
                break

            if value < data:
                self.data[idx] = value
                value = data

    def split(self):
        node_new = BPlusLeafNode(self.len())

        node_new.next = self.next
        self.next = node_new

        m_len = self.len() // 2
        for idx in range(m_len, self.len()):
            node_new.data[idx - m_len] = self.data[idx]
            self.data[idx] = None

        return node_new

    def scan(self):
        return [data for data in self.data if data != None]


class BPlusTree(object):
    '''
    B+树，单个叶子节点的数据储存为 M - 1 的实现。
    这个版本没有实现删除、查询。
    可以支持数字。
    '''
    '''
    初始化的时候，有且只有一个数据，为叶子节点。
    '''

    def __init__(self, m=3):
        self.M = m
        self.root_node = BPlusLeafNode(self.M)  # 根节点先插入一个叶子节点
        self.data_node = self.root_node  # 指向第一个数据节点

    def find_leaf_node(self, value, node=None):
        if node == None:
            node = self.root_node  # 从根结点找起

        if isinstance(node, BPlusLeafNode):
            return node, []

        leaf_node = None
        leaf_idx = 0
        paths = []

        for idx, data in enumerate(node.data):

            # 最后一个节点，或者后面一个节点为空节点
            if idx == node.len() - 1 or node.data[idx + 1].empty():
                leaf_node, paths = self.find_leaf_node(value, data.node())
                leaf_idx = idx
                break

            # 非最后一个节点，看后面一个节点是否更大
            if node.data[idx + 1].value() >= value:
                leaf_node, paths = self.find_leaf_node(value, data.node())
                leaf_idx = idx
                break

        # 返回 叶子节点，父亲节点、叶子在父亲节点中的位置
        return leaf_node, [(node, leaf_idx)] + paths

    def insert(self, value):
        leaf_node, leaf_paths = self.find_leaf_node(value)  # leaf_node叶子节点，leaf_paths寻找到叶子节点的链路

        leaf_node.insert(value)
        if not leaf_node.full():  # 未满
            return

        leaf_node_new = leaf_node.split()  # 如果叶子节点满了，进行拆分。
        self.split_node(leaf_paths, leaf_node, leaf_node_new)

    def split_node(self, paths, node, node_new):

        if len(paths) == 0:  # 路径为空，即根路径
            self.root_node = BPlusNode(self.M + 1)
            self.root_node.insert(node)
            self.root_node.insert(node_new, 1)
            return

        parent_node, child_idx = paths[-1]

        parent_node.insert(node_new, start_idx=child_idx + 1)

        if not parent_node.full():
            return

        parent_node_new = parent_node.split()
        self.split_node(paths[:-1], parent_node, parent_node_new)

    def scan(self):  # begin=-1, end=-1):
        data_node = self.data_node
        out = []

        while data_node != None:
            out += data_node.scan()
            data_node = data_node.next

        return out


tree_node_size = 32
b = BPlusTree(tree_node_size)

size = 128
st = 1
ed = 128
values = [random.randint(st, ed)] * size

print(values)

for idx, value in enumerate(values):
    b.insert(value)

st_t = time.time()
out = b.scan()

assert out == sorted(values), 'Not Sorted'

print(out)
