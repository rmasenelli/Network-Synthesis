class Link:

    def __init__(self, id, id_src, id_dst, name):
        self.id = id
        self.id_src = id_src
        self.id_dst = id_dst
        self.name = name[:-1]