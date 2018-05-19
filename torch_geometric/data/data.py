import torch
from torch_geometric.utils import (get_num_nodes, contains_isolated_nodes,
                                   contains_self_loops, is_undirected)


class Data(object):
    def __init__(self,
                 x=None,
                 edge_index=None,
                 edge_attr=None,
                 y=None,
                 pos=None):
        self.x = x
        self.edge_index = edge_index
        self.edge_attr = edge_attr
        self.y = y
        self.pos = pos

    @staticmethod
    def from_dict(dictionary):
        data = Data()
        for key, item in dictionary.items():
            data[key] = item
        return data

    def __getitem__(self, key):
        return getattr(self, key)

    def __setitem__(self, key, item):
        setattr(self, key, item)

    @property
    def keys(self):
        return [key for key in self.__dict__.keys() if self[key] is not None]

    def __len__(self):
        return len(self.keys)

    def __contains__(self, key):
        return key in self.keys

    def __iter__(self):
        for key in sorted(self.keys):
            yield key, self[key]

    def __call__(self, *keys):
        for key in sorted(self.keys) if not keys else keys:
            if self[key] is not None:
                yield key, self[key]

    def cat_dim(self, key):
        return -1 if self[key].dtype == torch.long else 0

    @property
    def num_nodes(self):
        for key, item in self('x', 'pos'):
            return item.size(self.cat_dim(key))
        if self.edge_index is not None:
            return get_num_nodes(self.edge_index)
        return None

    @property
    def num_edges(self):
        for key, item in self('edge_index', 'edge_attr'):
            return item.size(self.cat_dim(key))
        return None

    @property
    def contains_isolated_nodes(self):
        return contains_isolated_nodes(self.edge_index)

    @property
    def contains_self_loops(self):
        return contains_self_loops(self.edge_index)

    @property
    def is_undirected(self):
        return is_undirected(self.edge_index, self.num_nodes)

    @property
    def is_directed(self):
        return not self.is_undirected

    def apply(self, func, *keys):
        for key, item in self(*keys):
            self[key] = func(item)
        return self

    def contiguous(self, *keys):
        return self.apply(lambda x: x.contiguous(), *keys)

    def to(self, device, *keys):
        return self.apply(lambda x: x.to(device), *keys)

    def __repr__(self):
        info = ['{}={}'.format(key, list(item.size())) for key, item in self]
        return '{}({})'.format(self.__class__.__name__, ', '.join(info))
